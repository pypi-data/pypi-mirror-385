"""Base configuration classes."""

from enum import Enum
from typing import Any, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings as PydanticBaseSettings
from pydantic_settings import SettingsConfigDict

from x_scanner_commons.config.validators import validate_port


class Environment(str, Enum):
    """Environment types."""

    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"

    @classmethod
    def from_string(cls, value: str) -> "Environment":
        """Create from string value."""
        value = value.lower()
        if value in ("dev", "development"):
            return cls.DEVELOPMENT
        elif value in ("test", "testing"):
            return cls.TESTING
        elif value in ("stage", "staging"):
            return cls.STAGING
        elif value in ("prod", "production"):
            return cls.PRODUCTION
        else:
            raise ValueError(f"Invalid environment: {value}")


class LogLevel(str, Enum):
    """Log level types."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class BaseSettings(PydanticBaseSettings):
    """Base settings using pydantic-settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        case_sensitive=False,
        extra="ignore",
    )


class BaseConfig(BaseSettings):
    """Base configuration with common settings."""

    # Service information
    service_name: str = Field(
        default="x-scanner-service",
        description="Service name for identification",
    )
    service_version: str = Field(
        default="0.1.0",
        description="Service version",
    )
    service_description: str = Field(
        default="X-Scanner microservice",
        description="Service description",
    )

    # Environment
    environment: Environment = Field(
        default=Environment.DEVELOPMENT,
        description="Runtime environment",
    )
    debug: bool = Field(
        default=False,
        description="Debug mode",
    )

    # Server settings
    host: str = Field(
        default="0.0.0.0",
        description="Server host",
    )
    port: int = Field(
        default=8000,
        description="Server port",
    )
    workers: int = Field(
        default=1,
        description="Number of worker processes",
    )
    reload: bool = Field(
        default=False,
        description="Auto-reload on code changes",
    )

    # Logging
    log_level: LogLevel = Field(
        default=LogLevel.INFO,
        description="Logging level",
    )
    log_format: str = Field(
        default="json",
        description="Log format (json or text)",
    )
    log_file: Optional[str] = Field(
        default=None,
        description="Log file path",
    )

    # CORS settings
    cors_enabled: bool = Field(
        default=True,
        description="Enable CORS",
    )
    cors_origins: list[str] = Field(
        default_factory=lambda: ["*"],
        description="Allowed CORS origins",
    )
    cors_methods: list[str] = Field(
        default_factory=lambda: ["*"],
        description="Allowed CORS methods",
    )
    cors_headers: list[str] = Field(
        default_factory=lambda: ["*"],
        description="Allowed CORS headers",
    )

    # Security
    secret_key: str = Field(
        default="change-me-in-production",
        description="Secret key for signing",
    )
    algorithm: str = Field(
        default="HS256",
        description="JWT algorithm",
    )
    access_token_expire_minutes: int = Field(
        default=30,
        description="Access token expiration in minutes",
    )

    vault_url: str = Field(
        default="http://localhost:8200",
        description="Vault server URL",
    )
    vault_token: Optional[str] = Field(
        default=None,
        description="Vault authentication token",
    )
    vault_mount_point: str = Field(
        default="secret",
        description="Vault KV mount point",
    )


    @field_validator("port")
    @classmethod
    def validate_port_range(cls, v: int) -> int:
        """Validate port is in valid range."""
        return validate_port(v)

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: Any) -> Environment:
        """Validate and convert environment."""
        if isinstance(v, str):
            return Environment.from_string(v)
        return v

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment == Environment.DEVELOPMENT

    @property
    def is_testing(self) -> bool:
        """Check if running in testing environment."""
        return self.environment == Environment.TESTING

    @property
    def is_staging(self) -> bool:
        """Check if running in staging environment."""
        return self.environment == Environment.STAGING

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == Environment.PRODUCTION

    def to_dict(self, exclude_secrets: bool = True) -> dict[str, Any]:
        """Convert to dictionary.

        Args:
            exclude_secrets: Exclude sensitive fields

        Returns:
            Configuration dictionary
        """
        data = self.model_dump()

        if exclude_secrets:
            secret_fields = {
                "secret_key",
                "database_url",
                "redis_password",
                "vault_token",
            }
            for field in secret_fields:
                if field in data:
                    data[field] = "***"

        return data

    def validate_config(self) -> None:
        """Validate configuration consistency."""
        # Add custom validation logic here
        if self.is_production:
            if self.debug:
                raise ValueError("Debug mode should not be enabled in production")
            if self.secret_key == "change-me-in-production":
                raise ValueError("Secret key must be changed in production")
            if self.cors_origins == ["*"]:
                raise ValueError("CORS origins should be restricted in production")

    model_config = SettingsConfigDict(
        use_enum_values=True,
        validate_assignment=True,
    )
