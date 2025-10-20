"""File logger backend implementation."""

import logging
from pathlib import Path
from typing import Any, Optional

from x_scanner_commons.infrastructure.logger.interface import LoggerBackendInterface
from x_scanner_commons.infrastructure.logger.models import LogLevel


class FileBackend(LoggerBackendInterface):
    """File logger backend that outputs to a file."""
    
    def __init__(self) -> None:
        """Initialize file backend."""
        self.handler: Optional[logging.FileHandler] = None
        self.min_level = LogLevel.INFO
        self.formatter: Optional[logging.Formatter] = None
        self.file_path: Optional[Path] = None
    
    async def initialize(self, **kwargs: Any) -> None:
        """Initialize the file backend.
        
        Args:
            **kwargs: Configuration options
                - file_path: Path to log file
                - level: Minimum log level
                - mode: File open mode (default: 'a')
                - encoding: File encoding (default: 'utf-8')
        """
        file_path = kwargs.get("file_path")
        if not file_path:
            raise ValueError("file_path is required for FileBackend")
        
        self.file_path = Path(file_path)
        
        # Create directory if needed
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create handler
        mode = kwargs.get("mode", "a")
        encoding = kwargs.get("encoding", "utf-8")
        level = kwargs.get("level", "INFO")
        
        self.handler = logging.FileHandler(
            filename=str(self.file_path),
            mode=mode,
            encoding=encoding,
        )
        
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
        """Log a message to file.
        
        Args:
            level: Log level
            message: Log message
            extra: Additional fields
            exc_info: Exception information
        """
        if not self.handler:
            raise RuntimeError("FileBackend not initialized")
        
        # Create log record
        logger = logging.getLogger("file")
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
        
        self.handler.emit(record)
    
    async def flush(self) -> None:
        """Flush the file output."""
        if self.handler:
            self.handler.flush()
    
    async def close(self) -> None:
        """Close the file backend."""
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
    
    async def rotate(self, max_bytes: int = 10485760, backup_count: int = 5) -> None:
        """Configure log rotation.
        
        Args:
            max_bytes: Maximum file size before rotation
            backup_count: Number of backup files to keep
        """
        if self.handler:
            await self.close()
        
        if not self.file_path:
            raise RuntimeError("FileBackend not initialized")
        
        # Use RotatingFileHandler for rotation
        from logging.handlers import RotatingFileHandler
        
        self.handler = RotatingFileHandler(
            filename=str(self.file_path),
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8",
        )
        
        self.handler.setLevel(self.min_level.to_int())
        
        if self.formatter:
            self.handler.setFormatter(self.formatter)