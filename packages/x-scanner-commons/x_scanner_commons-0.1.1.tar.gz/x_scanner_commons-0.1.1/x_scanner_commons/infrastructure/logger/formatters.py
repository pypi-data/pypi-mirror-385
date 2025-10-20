"""Log formatters for different output formats."""

import json
import logging
import traceback
from datetime import datetime
from typing import Any, Optional

from x_scanner_commons.infrastructure.logger.models import LogEntry


class BaseFormatter(logging.Formatter):
    """Base formatter class."""
    
    def __init__(
        self,
        service_name: Optional[str] = None,
        version: Optional[str] = None,
        environment: Optional[str] = None,
    ) -> None:
        """Initialize formatter.
        
        Args:
            service_name: Service name for logs
            version: Service version
            environment: Environment name
        """
        super().__init__()
        self.service_name = service_name or "x-scanner"
        self.version = version
        self.environment = environment


class JSONFormatter(BaseFormatter):
    """JSON log formatter for structured logging."""
    
    def __init__(
        self,
        service_name: Optional[str] = None,
        version: Optional[str] = None,
        environment: Optional[str] = None,
        include_traceback: bool = True,
    ) -> None:
        """Initialize JSON formatter.
        
        Args:
            service_name: Service name for logs
            version: Service version
            environment: Environment name
            include_traceback: Include exception traceback
        """
        super().__init__(service_name, version, environment)
        self.include_traceback = include_traceback
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON.
        
        Args:
            record: Log record
            
        Returns:
            JSON formatted log string
        """
        # Build LogEntry
        log_entry = LogEntry(
            level=record.levelname,
            logger_name=record.name,
            message=record.getMessage(),
            service_name=self.service_name,
            version=self.version,
            environment=self.environment,
        )
        
        # Add source location
        log_entry.source = {
            "file": record.pathname,
            "line": record.lineno,
            "function": record.funcName,
        }
        
        # Add extra fields from record
        if hasattr(record, "request_id"):
            log_entry.request_id = record.request_id
        
        if hasattr(record, "user"):
            log_entry.user = record.user
        
        if hasattr(record, "extra_fields"):
            log_entry.extra = record.extra_fields
        
        # Add exception info
        if record.exc_info and self.include_traceback:
            log_entry.exception = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info),
            }
        
        return json.dumps(log_entry.model_dump(exclude_none=True), default=str)


class TextFormatter(BaseFormatter):
    """Text formatter with optional colors for console output."""
    
    COLORS = {
        "DEBUG": "\033[36m",    # Cyan
        "INFO": "\033[32m",     # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",    # Red
        "CRITICAL": "\033[35m", # Magenta
    }
    RESET = "\033[0m"
    
    def __init__(
        self,
        service_name: Optional[str] = None,
        version: Optional[str] = None,
        environment: Optional[str] = None,
        use_colors: bool = True,
        fmt: Optional[str] = None,
        datefmt: Optional[str] = None,
    ) -> None:
        """Initialize text formatter.
        
        Args:
            service_name: Service name for logs
            version: Service version
            environment: Environment name
            use_colors: Enable colored output
            fmt: Log format string
            datefmt: Date format string
        """
        # Initialize parent first
        super().__init__(service_name, version, environment)
        
        self.use_colors = use_colors
        self.version = version or "unknown"
        
        if fmt is None:
            # Include service info in format
            fmt = f"%(asctime)s - {self.service_name} - {self.version} - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"
        
        if datefmt is None:
            datefmt = "%Y-%m-%d %H:%M:%S"
        
        # Set format for logging.Formatter
        self._style = logging.PercentStyle(fmt)
        self._fmt = self._style._fmt
        self.datefmt = datefmt
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with optional colors.
        
        Args:
            record: Log record
            
        Returns:
            Formatted log string
        """
        # Add request_id to message if available
        if hasattr(record, "request_id") and record.request_id:
            record.msg = f"[{record.request_id[:8]}] {record.msg}"
        
        # Add user to message if available
        if hasattr(record, "user") and record.user:
            record.msg = f"[{record.user}] {record.msg}"
        
        # Apply color if enabled
        original_levelname = record.levelname
        if self.use_colors and original_levelname in self.COLORS:
            record.levelname = f"{self.COLORS[original_levelname]}{original_levelname}{self.RESET}"
        
        formatted = super().format(record)
        
        # Reset levelname
        record.levelname = original_levelname
        
        return formatted


class StructuredFormatter(BaseFormatter):
    """Structured formatter for machine-readable logs."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as structured text.
        
        Args:
            record: Log record
            
        Returns:
            Structured log string
        """
        parts = [
            f"timestamp={datetime.utcnow().isoformat()}",
            f"level={record.levelname}",
            f"logger={record.name}",
            f"service={self.service_name}",
        ]
        
        if self.version:
            parts.append(f"version={self.version}")
        
        if self.environment:
            parts.append(f"environment={self.environment}")
        
        if hasattr(record, "request_id") and record.request_id:
            parts.append(f"request_id={record.request_id}")
        
        if hasattr(record, "user") and record.user:
            parts.append(f"user={record.user}")
        
        parts.extend([
            f"file={record.pathname}:{record.lineno}",
            f"function={record.funcName}",
            f'message="{record.getMessage()}"',
        ])
        
        if record.exc_info:
            exc_type, exc_value, _ = record.exc_info
            parts.append(f"exception={exc_type.__name__}: {exc_value}")
        
        return " ".join(parts)