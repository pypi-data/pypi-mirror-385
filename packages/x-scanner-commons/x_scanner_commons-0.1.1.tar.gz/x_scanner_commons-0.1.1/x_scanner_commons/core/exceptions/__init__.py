"""Common exceptions module."""

from x_scanner_commons.core.exceptions.base import (
    AlreadyExistsError,
    AuthenticationError,
    BaseError,
    ConfigurationError,
    NetworkError,
    NotFoundError,
    PermissionError,
    RateLimitError,
    TimeoutError,
    ValidationError,
)

__all__ = [
    "BaseError",
    "ConfigurationError",
    "ValidationError",
    "NotFoundError",
    "AlreadyExistsError",
    "PermissionError",
    "AuthenticationError",
    "RateLimitError",
    "TimeoutError",
    "NetworkError",
]
