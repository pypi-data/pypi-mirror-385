

Welcome to Django setup configuration's documentation!
======================================================

:Version: 0.11.0
:Source: https://github.com/maykinmedia/django-setup-configuration
:Keywords: Configuration
:PythonVersion: 3.10

|build-status| |code-quality| |black| |coverage| |docs|

|python-versions| |django-versions| |pypi-version|

Manage your configuration via django command.

.. contents::

.. section-numbering::

Features
========

This library will allow you to define one or more "configuration steps" which declare a set of
expected configuration values and hooks which can be used to configure some part of your
project based on those settings. The steps can be run programmatically or via an
included Django management command.

It's intended usage is larger Django projects that require a significant amount of
configuration to be provisioned, as well as a way to store configuration in an
agnostic format (such as yaml) that is not tightly coupled to your Django models.

Installation
============

Requirements
------------

* Python 3.10 or above
* Django 3.2 or above
* Pydantic 2 or above
* Pydantic-settings 2.2 or above


Install
-------

1. Install from PyPI

.. code-block:: bash

    pip install django-setup-configuration

2. Add ``django_setup_configuration`` to the ``INSTALLED_APPS`` setting.


Usage
=====

Key Concepts
------------

- **Configuration Model**: A `Pydantic <https://docs.pydantic.dev/>`_ model defining the structure and validation rules for your configuration.
- **Configuration Step**: A class that implements the actual configuration logic using the validated configuration model.


Define a Configuration Model
----------------------------

.. code-block:: python

    from pydantic import Field
    from django_setup_configuration import ConfigurationModel, DjangoModelRef

    class UserConfigurationModel(ConfigurationModel):
        # A regular Pydantic field
        add_to_groups: list[str] = Field(
            default_factory=list,
            description="Groups to add the user to"
        )

        # Reference Django model fields with automatic type inference
        username = DjangoModelRef("auth.User", "username", default="admin")

        # You can optionally override the inferred type (overriding the type is
        # required for fields that can not be unambiguously mapped to a Python type,
        # such as relational fields or third-party fields).
        is_staff: Optional[int] = DjangoModelRef("auth.User", "username", default=0)
        
        # If you have no need for overriding any of the inferred attributes, you can reference model fields in a Meta class
        class Meta:
            django_model_refs = {
                User: ["password"]
            }


Field Defaults
^^^^^^^^^^^^^^

For regular Pydantic fields, you must explicitly configure defaults using  `Field
(default=...)` or `Field(default_factory=lambda: ...)` as specified in  the  `Pydantic
documentation <https://docs.pydantic.dev/2.10/concepts/fields/#default-values>`_.

**NOTE:** Marking a field as ``Optional`` or using ``... | None`` does *not* automatically 
set the field's default to `None`. You must set this explicitly if you want the field to
be optional:

.. code-block:: python

    from pydantic import Field

    class ConfigModel(ConfigurationModel):
        optional_field: int | None = DjangoModelRef(SomeModel, "some_field", default=None)

For ``DjangoModelRef``, the default value handling follows these rules:

You can provide explicit defaults using the ``default`` or ``default_factory`` kwargs,
similar to regular Pydantic fields:

.. code-block:: python

    class ConfigModel(ConfigurationModel):
        # Explicit string default
        field_with_explicit_default = DjangoModelRef(SomeModel, "some_field", default="foobar")
        
        # Explicit default factory for a list
        field_with_explicit_default_factory: list[str] = DjangoModelRef(
            SomeModel, "some_other_field", default_factory=list
        )

When no explicit default is provided, the default is derived from the referenced Django field:

1. If the Django field has an explicit default, that default will be used.

2. If no explicit default is set but the field has ``null=True`` set:
        
        a. The default will be set to ``None``
        b. The field will be optional

3. If no explicit default is provided and the field is not nullable, but has ``blank=True`` **and** it is a string-type field:

        a. The default will be an empty string
        b. The field will be optional


Create a Configuration Step
---------------------------

.. code-block:: python

    from django_setup_configuration import BaseConfigurationStep
    from django.contrib.auth.models import Group, User

    class UserConfigurationStep(BaseConfigurationStep[UserConfigurationModel]):
        """Configure initial user accounts"""

        config_model = UserConfigurationModel
        enable_setting = "user_configuration_enabled"
        namespace = "user_configuration"
        verbose_name = "User Configuration"

        def execute(self, model: UserConfigurationModel) -> None:
            # Idempotent user creation and configuration
            user_qs = User.objects.filter(username=model.username)
            if user_qs.exists():
                user = user_qs.get()
                if not user.check_password(model.password):
                    user.set_password(model.password)
                    user.save()
            else:
                user = User.objects.create_user(
                    username=model.username,
                    password=model.password,
                    is_superuser=True,
                )
            
            for group_name in model.add_to_groups:
                group = Group.objects.get(name=group_name)
                group.user_set.add(user)

Configuration Source
--------------------

Create a YAML configuration file with your settings:

.. code-block:: yaml

    user_configuration_enabled: true 
    user_configuration:
        username: alice
        password: supersecret
        add_to_groups:
            - moderators
            - editors

    some_other_step_enabled_flag: true
    some_other_step:
        foo: bar
        bar: baz

Note that you can combine settings for multiple steps in a single file. The root level
keys are exclusively used for the steps' ``enable_setting`` key, and the ``namespace``
key which encapsulates the configuration model's attributes.

Environment Variable Substitution
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can reference environment variables in your YAML configuration using the 
``value_from`` pattern. This allows you to keep sensitive values like passwords out of
your configuration files:

.. code-block:: yaml

    user_configuration_enabled: true 
    user_configuration:
        username: alice
        password:
            value_from:
                env: USER_PASSWORD
        add_to_groups:
            - moderators
            - editors

This pattern can be used for any field in your configuration model. The environment
variable ``USER_PASSWORD`` must be set when the configuration is loaded, or an error
will be raised with guidance on how to fix the issue.

You can also provide an optional default value that will be used when the environment
variable is not set:

.. code-block:: yaml

    user_configuration_enabled: true 
    user_configuration:
        username: alice
        password:
            value_from:
                env: USER_PASSWORD
                default: default_password
        timeout:
            value_from:
                env: REQUEST_TIMEOUT
                default: 30

You can also use this pattern for non-sensitive configuration that varies between
environments:

.. code-block:: yaml

    database_configuration_enabled: true
    database_configuration:
        host:
            value_from:
                env: DB_HOST
        port:
            value_from:
                env: DB_PORT
        name: myapp_db

For optional configuration that should fall back to model defaults when the 
environment variable is not set, use the ``required`` flag:

.. code-block:: yaml

    user_configuration_enabled: true 
    user_configuration:
        username: alice
        timeout:
            value_from:
                env: USER_TIMEOUT
                required: false
        debug_mode:
            value_from:
                env: DEBUG_ENABLED
                required: false

If absent, ``required`` is treated as ``true``. When ``required: false`` is specified
and the environment variable is not found, the field is omitted from the configuration
entirely, allowing the model's default value to be used instead. If no model default is
defined, a validation error will occur.

Note that ``required`` and ``default`` cannot both be specified, as they would
conflict with each other.

Step Registration
-----------------

Register your configuration steps in Django settings:

.. code-block:: python

    SETUP_CONFIGURATION_STEPS = [
        "myapp.configuration_steps.user_configuration.UserConfigurationStep",
    ]

Note that steps will be executed in the order in which they are defined.

Execution
---------

Command Line
^^^^^^^^^^^^

.. code-block:: bash

    python manage.py setup_configuration --yaml-file /path/to/config.yaml

You can also validate that the configuration source can be successfully loaded,
without actually running the steps, by adding the ``validate-only`` flag:

.. code-block:: bash

    python manage.py setup_configuration --yaml-file /path/to/config.yaml --validate-only

The command will either return 0 and a success message if the configuration file can
be loaded without issues, otherwise it will return a non-zero exit code and print any
validation errors. This can be useful e.g. in CI to confirm that your sources are
valid without actually running any steps.

Programmatically
^^^^^^^^^^^^^^^^

.. code-block:: python

    from django_setup_configuration.runner import SetupConfigurationRunner

    runner = SetupConfigurationRunner(
        steps=["myapp.configuration_steps.user_configuration.UserConfigurationStep"],
        yaml_source="/path/to/config.yaml"
    )
    # Validate that the configuration settings can be loaded from the source
    runner.validate_all_requirements() 

    # Execute all steps
    runner.execute_all()

Note that regardless of the execution method, only *enabled* steps will be executed. By
default, steps are **not enabled**, so you will have to explicitly set the ``enable_setting``
flag to true for each step you intend to run.

Testing
-------

Direct Model Instantiation
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    def test_execute_step():
        config_model = UserConfigurationModel(
            username="alice", 
            password="supersecret", 
            add_to_groups=["moderators", "editors"]
        )
        step = UserConfigurationStep()
        step.execute(config_model)

        # Add assertions

Model Instantiation from an object or YAML
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python
    
    from django_setup_configuration.test_utils import build_step_config_from_sources

    def test_execute_step():
        config =  {
            'user_configuration_enabled': True,
            'user_configuration': {
                'username': 'alice',
                'password': 'supersecret',
                'groups': ['moderators', 'editors']
            }
        }
        config_model = build_step_config_from_sources(UserConfigurationStep, 
            object_source=config,
            # or yaml_source="/path/to/file.yaml"
            )   
        step = UserConfigurationStep()
        step.execute(config_model_instance)

        # Add assertions

Using Test Helpers
^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from django_setup_configuration.test_utils import execute_single_step

    def test_execute_step():
        execute_single_step(
            UserConfigurationStep, 
            yaml_source="/path/to/test_config.yaml"
        )

        # Add assertions

Note that when using ``execute_single_step``, the enabled flag in your setting source
will be ignored and the step will be executed regardless of its presence or value.

Best Practices
==============

- **Idempotency**: Design steps that can be run multiple times without unintended side effects.
- **Validation**: You can use the full range of Pydantic's validation capabilities.
- **Modularity**: Break complex configurations into focused, manageable steps based on your domain in a way that will make sense to your users.


Local development
=================

To install and develop the library locally, use:

.. code-block:: bash

    pip install -e .[tests,coverage,docs,release]

When running management commands via ``django-admin``, make sure to add the root
directory to the python path (or use ``python -m django <command>``):

.. code-block:: bash

    export PYTHONPATH=. DJANGO_SETTINGS_MODULE=testapp.settings
    django-admin check
    # or other commands like:
    # django-admin makemessages -l nl


.. |build-status| image:: https://github.com/maykinmedia/django-setup-configuration/workflows/Run%20CI/badge.svg
    :alt: Build status
    :target: https://github.com/maykinmedia/django-setup-configuration/actions?query=workflow%3A%22Run+CI%22

.. |code-quality| image:: https://github.com/maykinmedia/django-setup-configuration/workflows/Code%20quality%20checks/badge.svg
     :alt: Code quality checks
     :target: https://github.com/maykinmedia/django-setup-configuration/actions?query=workflow%3A%22Code+quality+checks%22

.. |black| image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black

.. |coverage| image:: https://codecov.io/gh/maykinmedia/django-setup-configuration/branch/main/graph/badge.svg
    :target: https://codecov.io/gh/maykinmedia/django-setup-configuration
    :alt: Coverage status

.. |docs| image:: https://readthedocs.org/projects/django_setup_configuration/badge/?version=latest
    :target: https://django_setup_configuration.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. |python-versions| image:: https://img.shields.io/pypi/pyversions/django_setup_configuration.svg

.. |django-versions| image:: https://img.shields.io/pypi/djversions/django_setup_configuration.svg

.. |pypi-version| image:: https://img.shields.io/pypi/v/django_setup_configuration.svg
    :target: https://pypi.org/project/django_setup_configuration/
