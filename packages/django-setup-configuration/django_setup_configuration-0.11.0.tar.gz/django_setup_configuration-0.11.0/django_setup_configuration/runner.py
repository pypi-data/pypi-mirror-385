import inspect
import logging
from dataclasses import dataclass
from functools import partial
from os import PathLike
from pathlib import Path
from typing import Any, Generator

from django.conf import settings
from django.db import transaction
from django.utils.module_loading import import_string

from pydantic import ValidationError

from django_setup_configuration.configuration import BaseConfigurationStep
from django_setup_configuration.exceptions import (
    ConfigurationException,
    ConfigurationRunFailed,
    ImproperlyConfigured,
    PrerequisiteFailed,
    ValidateRequirementsFailure,
)
from django_setup_configuration.model_utils import (
    ConfigSourceModels,
    create_config_source_models,
)
from django_setup_configuration.models import ConfigurationModel

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class StepExecutionResult:
    step: BaseConfigurationStep
    is_enabled: bool = False
    has_run: bool = False
    run_exception: BaseException | None = None
    config_model: ConfigurationModel | None = None


class SetupConfigurationRunner:
    """
    A utility class to validate and run one or more BaseConfigurationSteps.
    """

    configured_steps: list[BaseConfigurationStep]
    yaml_source: PathLike | None
    object_source: dict | None

    _config_source_models_for_step: dict[BaseConfigurationStep, ConfigSourceModels]
    _config_for_step: dict[BaseConfigurationStep, ConfigurationModel]

    def __init__(
        self,
        *,
        steps: list[type[BaseConfigurationStep] | str] | None = None,
        yaml_source: PathLike | str | None = None,
        object_source: dict | None = None,
    ):
        if not (configured_steps := steps or settings.SETUP_CONFIGURATION_STEPS):
            raise ImproperlyConfigured(
                "You must provide one or more steps, or configure these steps via "
                "`settings.SETUP_CONFIGURATION_STEPS`"
            )

        self.configured_steps = self._initialize_steps(configured_steps)
        if yaml_source:
            self.yaml_source = (
                Path(yaml_source) if isinstance(yaml_source, str) else yaml_source
            )
            self.yaml_source = self.yaml_source.resolve()
            if not self.yaml_source.exists():
                raise ConfigurationException(
                    f"YAML source is not an existing file path: {self.yaml_source}"
                )

        self._config_source_models_for_step = {}
        self._config_for_step = {}
        for step in self.configured_steps:
            config_source_models = create_config_source_models(
                enable_setting_key=step.enable_setting,
                namespace=step.namespace,
                config_model=step.config_model,  # type: ignore
                yaml_file=yaml_source,
            )
            self._config_source_models_for_step[step] = config_source_models

        self.object_source = object_source

    @classmethod
    def _initialize_steps(cls, steps: list[type[BaseConfigurationStep] | str]):
        step_classes = []
        for step in steps:
            try:
                step_classes.append(
                    import_string(step) if isinstance(step, str) else step
                )
            except ImportError:
                raise ConfigurationException(
                    f"Your configured steps contain `{step}`, which cannot be imported"
                )

        initialized_steps = []
        for step_cls in step_classes:
            if not inspect.isclass(step_cls) or not isinstance(step_cls, type):
                raise ConfigurationException(
                    f"Your configured steps contain `{step_cls}`, which is not a "
                    "class: did you perhaps provide an instance?"
                )

            if not issubclass(step_cls, BaseConfigurationStep):
                raise ConfigurationException(
                    f"Your configured steps contain {step_cls.__name__}` which is not "
                    f"a subclass of `{BaseConfigurationStep.__name__}`"
                )

            step = step_cls()
            initialized_steps.append(step)

        return initialized_steps

    def _validate_requirements_for_step(self, step: BaseConfigurationStep):
        if step not in self.configured_steps:
            raise ConfigurationRunFailed(
                f"Step {step} is not configured for this runner"
            )

        try:
            # Load the model from the source (yaml, environment)
            settings_object = self.object_source or {}
            model_settings_instance = self._config_source_models_for_step[
                step
            ].config_settings_source(**settings_object)
        except ValidationError as exc:
            raise PrerequisiteFailed(step=step, validation_error=exc)

        # The step's model is located under the namespace key at the root
        return getattr(model_settings_instance, step.namespace)

    def _execute_step(
        self, step: BaseConfigurationStep, *, ignore_enabled: bool = False
    ):
        if step not in self.configured_steps:
            raise ConfigurationRunFailed(
                f"Step {step} is not configured for this runner"
            )

        result_factory = partial(
            StepExecutionResult,
            step=step,
            config_model=None,
            is_enabled=False,
            has_run=False,
        )
        if not (is_enabled := step in self.enabled_steps) and not ignore_enabled:
            return result_factory()

        result_factory = partial(result_factory, is_enabled=True)

        # Validate first
        config_model = self._validate_requirements_for_step(step)

        result_factory = partial(
            result_factory, is_enabled=is_enabled, config_model=config_model
        )

        has_run = False
        step_exc = None

        try:
            with transaction.atomic():
                step.execute(config_model)
        except BaseException as exc:
            step_exc = exc
        finally:
            has_run = True

        return result_factory(run_exception=step_exc, has_run=has_run)

    @property
    def enabled_steps(self) -> list[BaseConfigurationStep]:
        steps = []
        settings_object = self.object_source or {}
        for step in self.configured_steps:
            enable_settings_instance = self._config_source_models_for_step[
                step
            ].enable_setting_source(**settings_object)
            enable_flag = getattr(enable_settings_instance, step.enable_setting)

            if enable_flag:
                steps.append(step)

        return steps

    @property
    def disabled_steps(self) -> list[BaseConfigurationStep]:
        return [
            step for step in self.configured_steps if step not in self.enabled_steps
        ]

    def validate_all_requirements(self):
        """
        Validate that the configuration models for each step can be constructed from the
        provided sources.

        Raises:
            ValidateRequirementsFailure: If the provided sources yielded invalid
                configuration values for one or more steps.
        """
        exceptions = []
        for step in self.enabled_steps:
            try:
                self._validate_requirements_for_step(step)
            except PrerequisiteFailed as exc:
                exceptions.append(exc)

        if exceptions:
            raise ValidateRequirementsFailure(exceptions)

    def execute_all_iter(self) -> Generator[StepExecutionResult, Any, None]:
        """
        Lazily execute all configured and enabled steps.

        Yields:
            Generator[StepExecutionResult, Any, None]: The results of each step's
                execution.
        """

        # Not the most elegant approach to rollbacks, but it's preferable to the
        # pitfalls of manual transaction management. We want all steps to run and only
        # rollback at the end, hence intra-step exceptions are caught and persisted.
        class Rollback(BaseException):
            pass

        try:
            with transaction.atomic():
                results = []
                for step in self.enabled_steps:
                    result = self._execute_step(step)
                    results.append(result)

                if any(result.run_exception for result in results):
                    raise Rollback  # Trigger the rollback
        except Rollback:
            pass

        for result in results:
            yield result

    def execute_all(self) -> list[StepExecutionResult]:
        """
        Execute all configured and enabled steps.

        Returns:
            list[StepExecutionResult]: The results of each step's execution.
        """
        return list(self.execute_all_iter())
