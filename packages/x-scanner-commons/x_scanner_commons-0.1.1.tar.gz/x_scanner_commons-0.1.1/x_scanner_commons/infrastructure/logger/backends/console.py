"""Console logger backend implementation."""

import logging
import sys
from typing import Any, Optional

from x_scanner_commons.infrastructure.logger.interface import LoggerBackendInterface
from x_scanner_commons.infrastructure.logger.models import LogLevel


class ConsoleBackend(LoggerBackendInterface):
    """Console logger backend that outputs to stdout/stderr."""
    
    def __init__(self) -> None:
        """Initialize console backend."""
        self.handler: Optional[logging.StreamHandler] = None
        self.min_level = LogLevel.INFO
        self.formatter: Optional[logging.Formatter] = None
    
    async def initialize(self, **kwargs: Any) -> None:
        """Initialize the console backend.
        
        Args:
            **kwargs: Configuration options
                - stream: Output stream (stdout or stderr)
                - level: Minimum log level
        """
        stream = kwargs.get("stream", sys.stdout)
        level = kwargs.get("level", "INFO")
        
        self.handler = logging.StreamHandler(stream)
        self.set_level(level)
        
        if self.formatter:
            self.handler.setFormatter(self.formatter)
    
    async def log(
        self,
        level: str,
        message: str,
        extra: Optional[dict[str, Any]] = None,
        exc_info: Optional[tuple] = None,
    ) -> None:
        """Log a message to console.
        
        Args:
            level: Log level
            message: Log message
            extra: Additional fields
            exc_info: Exception information
        """
        if not self.handler:
            await self.initialize()
        
        # Create log record
        logger = logging.getLogger("console")
        log_level = LogLevel.from_string(level)
        
        # Check if level meets minimum
        if log_level.to_int() < self.min_level.to_int():
            return
        
        # Create and emit record
        record = logger.makeRecord(
            name=logger.name,
            level=log_level.to_int(),
            fn="",
            lno=0,
            msg=message,
            args=(),
            exc_info=exc_info,
        )
        
        # Add extra fields to record
        if extra:
            for key, value in extra.items():
                setattr(record, key, value)
        
        if self.handler:
            self.handler.emit(record)
    
    async def flush(self) -> None:
        """Flush the console output."""
        if self.handler:
            self.handler.flush()
    
    async def close(self) -> None:
        """Close the console backend."""
        if self.handler:
            self.handler.close()
            self.handler = None
    
    def set_level(self, level: str) -> None:
        """Set the minimum log level.
        
        Args:
            level: Minimum log level
        """
        self.min_level = LogLevel.from_string(level)
        if self.handler:
            self.handler.setLevel(self.min_level.to_int())
    
    def set_formatter(self, formatter: Any) -> None:
        """Set the log formatter.
        
        Args:
            formatter: Formatter instance
        """
        self.formatter = formatter
        if self.handler:
            self.handler.setFormatter(formatter)