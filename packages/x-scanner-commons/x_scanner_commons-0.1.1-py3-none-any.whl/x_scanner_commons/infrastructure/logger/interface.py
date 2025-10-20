"""Logger interface definition for unified logging operations."""

from abc import ABC, abstractmethod
from typing import Any, Optional


class LoggerBackendInterface(ABC):
    """
    Abstract base class defining the logger backend interface.
    
    All logger backends must implement these methods to ensure
    consistent behavior across different logging mechanisms.
    """
    
    @abstractmethod
    async def initialize(self, **kwargs: Any) -> None:
        """
        Initialize the logger backend.
        
        Args:
            **kwargs: Backend-specific configuration
        """
        pass
    
    @abstractmethod
    async def log(
        self,
        level: str,
        message: str,
        extra: Optional[dict[str, Any]] = None,
        exc_info: Optional[tuple] = None,
    ) -> None:
        """
        Log a message with the specified level.
        
        Args:
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            message: Log message
            extra: Additional fields to include in the log
            exc_info: Exception information tuple
        """
        pass
    
    @abstractmethod
    async def flush(self) -> None:
        """
        Flush any buffered log messages.
        
        Ensures all pending log messages are written to the destination.
        """
        pass
    
    @abstractmethod
    async def close(self) -> None:
        """
        Close the logger backend and release resources.
        """
        pass
    
    @abstractmethod
    def set_level(self, level: str) -> None:
        """
        Set the minimum log level for this backend.
        
        Args:
            level: Minimum log level to process
        """
        pass
    
    @abstractmethod
    def set_formatter(self, formatter: Any) -> None:
        """
        Set the log formatter for this backend.
        
        Args:
            formatter: Formatter instance
        """
        pass
    
    async def batch_log(self, logs: list[dict[str, Any]]) -> None:
        """
        Log multiple messages in batch.
        
        Default implementation logs individually.
        Backends can override for better performance.
        
        Args:
            logs: List of log entries
        """
        for log_entry in logs:
            await self.log(
                level=log_entry.get("level", "INFO"),
                message=log_entry.get("message", ""),
                extra=log_entry.get("extra"),
                exc_info=log_entry.get("exc_info"),
            )