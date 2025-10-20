"""Base exception classes."""

from typing import Any, Optional


class BaseError(Exception):
    """Base exception class for X-Scanner Commons."""

    def __init__(
        self,
        message: str = "An error occurred",
        code: Optional[str] = None,
        status_code: int = 500,
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        """Initialize base error.

        Args:
            message: Error message
            code: Error code for identification
            status_code: HTTP status code
            details: Additional error details
        """
        super().__init__(message)
        self.message = message
        self.code = code or self.__class__.__name__
        self.status_code = status_code
        self.details = details or {}

    def to_dict(self) -> dict[str, Any]:
        """Convert exception to dictionary.

        Returns:
            Dictionary representation
        """
        result = {
            "error": self.code,
            "message": self.message,
            "status_code": self.status_code,
        }

        if self.details:
            result["details"] = self.details

        return result

    def __str__(self) -> str:
        """String representation."""
        if self.details:
            return f"{self.message} (code={self.code}, details={self.details})"
        return f"{self.message} (code={self.code})"

    def __repr__(self) -> str:
        """Debug representation."""
        return (
            f"{self.__class__.__name__}("
            f"message={self.message!r}, "
            f"code={self.code!r}, "
            f"status_code={self.status_code}, "
            f"details={self.details!r})"
        )


class ConfigurationError(BaseError):
    """Configuration error."""

    def __init__(
        self,
        message: str = "Configuration error",
        code: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        """Initialize configuration error."""
        super().__init__(
            message=message,
            code=code or "CONFIGURATION_ERROR",
            status_code=500,
            details=details,
        )


class ValidationError(BaseError):
    """Validation error."""

    def __init__(
        self,
        message: str = "Validation error",
        code: Optional[str] = None,
        field: Optional[str] = None,
        value: Any = None,
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        """Initialize validation error.

        Args:
            message: Error message
            code: Error code
            field: Field that failed validation
            value: Invalid value
            details: Additional details
        """
        if field:
            details = details or {}
            details["field"] = field
            if value is not None:
                details["value"] = value

        super().__init__(
            message=message,
            code=code or "VALIDATION_ERROR",
            status_code=400,
            details=details,
        )


class NotFoundError(BaseError):
    """Resource not found error."""

    def __init__(
        self,
        message: str = "Resource not found",
        code: Optional[str] = None,
        resource: Optional[str] = None,
        resource_id: Any = None,
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        """Initialize not found error.

        Args:
            message: Error message
            code: Error code
            resource: Resource type
            resource_id: Resource identifier
            details: Additional details
        """
        if resource:
            details = details or {}
            details["resource"] = resource
            if resource_id is not None:
                details["resource_id"] = resource_id

        super().__init__(
            message=message,
            code=code or "NOT_FOUND",
            status_code=404,
            details=details,
        )


class AlreadyExistsError(BaseError):
    """Resource already exists error."""

    def __init__(
        self,
        message: str = "Resource already exists",
        code: Optional[str] = None,
        resource: Optional[str] = None,
        resource_id: Any = None,
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        """Initialize already exists error.

        Args:
            message: Error message
            code: Error code
            resource: Resource type
            resource_id: Resource identifier
            details: Additional details
        """
        if resource:
            details = details or {}
            details["resource"] = resource
            if resource_id is not None:
                details["resource_id"] = resource_id

        super().__init__(
            message=message,
            code=code or "ALREADY_EXISTS",
            status_code=409,
            details=details,
        )


class PermissionError(BaseError):
    """Permission denied error."""

    def __init__(
        self,
        message: str = "Permission denied",
        code: Optional[str] = None,
        action: Optional[str] = None,
        resource: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        """Initialize permission error.

        Args:
            message: Error message
            code: Error code
            action: Action that was denied
            resource: Resource being accessed
            details: Additional details
        """
        if action or resource:
            details = details or {}
            if action:
                details["action"] = action
            if resource:
                details["resource"] = resource

        super().__init__(
            message=message,
            code=code or "PERMISSION_DENIED",
            status_code=403,
            details=details,
        )


class AuthenticationError(BaseError):
    """Authentication error."""

    def __init__(
        self,
        message: str = "Authentication failed",
        code: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        """Initialize authentication error."""
        super().__init__(
            message=message,
            code=code or "AUTHENTICATION_FAILED",
            status_code=401,
            details=details,
        )


class RateLimitError(BaseError):
    """Rate limit exceeded error."""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        code: Optional[str] = None,
        limit: Optional[int] = None,
        reset_at: Optional[int] = None,
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        """Initialize rate limit error.

        Args:
            message: Error message
            code: Error code
            limit: Rate limit value
            reset_at: Timestamp when limit resets
            details: Additional details
        """
        if limit or reset_at:
            details = details or {}
            if limit:
                details["limit"] = limit
            if reset_at:
                details["reset_at"] = reset_at

        super().__init__(
            message=message,
            code=code or "RATE_LIMIT_EXCEEDED",
            status_code=429,
            details=details,
        )


class TimeoutError(BaseError):
    """Operation timeout error."""

    def __init__(
        self,
        message: str = "Operation timed out",
        code: Optional[str] = None,
        timeout: Optional[float] = None,
        operation: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        """Initialize timeout error.

        Args:
            message: Error message
            code: Error code
            timeout: Timeout value in seconds
            operation: Operation that timed out
            details: Additional details
        """
        if timeout or operation:
            details = details or {}
            if timeout:
                details["timeout"] = timeout
            if operation:
                details["operation"] = operation

        super().__init__(
            message=message,
            code=code or "TIMEOUT",
            status_code=504,
            details=details,
        )


class NetworkError(BaseError):
    """Network error."""

    def __init__(
        self,
        message: str = "Network error occurred",
        code: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[int] = None,
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        """Initialize network error.

        Args:
            message: Error message
            code: Error code
            host: Target host
            port: Target port
            details: Additional details
        """
        if host or port:
            details = details or {}
            if host:
                details["host"] = host
            if port:
                details["port"] = port

        super().__init__(
            message=message,
            code=code or "NETWORK_ERROR",
            status_code=503,
            details=details,
        )
