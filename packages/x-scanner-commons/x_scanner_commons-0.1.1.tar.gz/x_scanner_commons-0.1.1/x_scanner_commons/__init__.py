"""X-Scanner Commons - Shared utilities for X-Scanner microservices."""

__version__ = "0.1.0"

# Export main interfaces
from x_scanner_commons.config.base import BaseConfig, BaseSettings
from x_scanner_commons.core.exceptions.base import BaseError, ConfigurationError
from x_scanner_commons.core.logging.logger import get_logger, setup_logging

__all__ = [
    "__version__",
    "BaseConfig",
    "BaseSettings",
    "BaseError",
    "ConfigurationError",
    "get_logger",
    "setup_logging",
]
