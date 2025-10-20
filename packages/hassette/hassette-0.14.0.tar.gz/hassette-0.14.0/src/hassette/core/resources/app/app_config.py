from typing import TypeVar

from pydantic_settings import BaseSettings, SettingsConfigDict

from hassette.const.misc import LOG_LEVELS


class AppConfig(BaseSettings):
    """Base configuration class for applications in the Hassette framework.

    This default class does not define any fields, allowing anyone who prefers to not use
    this functionality to ignore it. It also allows all extras, so arbitrary additional
    configuration data can be passed without needing to define a custom subclass.

    Fields can be set on subclasses and extra can be overriden by assigning a new value to `model_config`."""

    model_config = SettingsConfigDict(extra="allow", arbitrary_types_allowed=True, env_file=["/config/.env", ".env"])

    instance_name: str = ""
    """Name for the instance of the app."""

    log_level: LOG_LEVELS = "INFO"
    """Log level for the app instance. Defaults to 'INFO'."""


AppConfigT = TypeVar("AppConfigT", bound=AppConfig)
"""Type variable for app configuration classes."""
