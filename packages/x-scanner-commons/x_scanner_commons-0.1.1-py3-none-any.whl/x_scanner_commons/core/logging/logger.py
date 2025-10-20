"""Unified logging configuration."""

import contextvars
import json
import logging
import sys
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Optional, Union
from uuid import uuid4

# Context variable for request ID tracking
request_id_var: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "request_id", default=None
)


class JSONFormatter(logging.Formatter):
    """JSON log formatter for structured logging."""

    def __init__(
        self,
        service_name: str = "x-scanner",
        include_traceback: bool = True,
    ) -> None:
        """Initialize JSON formatter.

        Args:
            service_name: Service name for logs
            include_traceback: Include exception traceback
        """
        super().__init__()
        self.service_name = service_name
        self.include_traceback = include_traceback

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON.

        Args:
            record: Log record

        Returns:
            JSON formatted log string
        """
        log_data: dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "service": self.service_name,
        }

        # Add request ID if available
        request_id = get_request_id()
        if request_id:
            log_data["request_id"] = request_id

        # Add source location
        log_data["source"] = {
            "file": record.pathname,
            "line": record.lineno,
            "function": record.funcName,
        }

        # Add extra fields
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)

        # Add exception info
        if record.exc_info and self.include_traceback:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info),
            }

        return json.dumps(log_data, default=str)


class ColoredFormatter(logging.Formatter):
    """Colored text formatter for console output."""

    COLORS = {
        "DEBUG": "\033[36m",    # Cyan
        "INFO": "\033[32m",     # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",    # Red
        "CRITICAL": "\033[35m", # Magenta
    }
    RESET = "\033[0m"

    def __init__(self, fmt: Optional[str] = None, datefmt: Optional[str] = None) -> None:
        """Initialize colored formatter.

        Args:
            fmt: Log format string
            datefmt: Date format string
        """
        if fmt is None:
            fmt = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        if datefmt is None:
            datefmt = "%Y-%m-%d %H:%M:%S"
        super().__init__(fmt, datefmt)

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors.

        Args:
            record: Log record

        Returns:
            Colored log string
        """
        # Add request ID to message if available
        request_id = get_request_id()
        if request_id:
            record.msg = f"[{request_id[:8]}] {record.msg}"

        # Apply color
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{self.RESET}"

        formatted = super().format(record)

        # Reset levelname
        record.levelname = levelname

        return formatted


class LoggerAdapter(logging.LoggerAdapter):
    """Logger adapter with extra fields support."""

    def process(
        self, msg: Any, kwargs: dict[str, Any]
    ) -> tuple[Any, dict[str, Any]]:
        """Process log message and kwargs.

        Args:
            msg: Log message
            kwargs: Keyword arguments

        Returns:
            Processed message and kwargs
        """
        # Add extra fields to record
        extra = kwargs.get("extra", {})
        if "extra_fields" in kwargs:
            extra["extra_fields"] = kwargs.pop("extra_fields")
        kwargs["extra"] = extra

        return msg, kwargs


# Global logger cache
_loggers: dict[str, LoggerAdapter] = {}
_setup_done = False


def setup_logging(
    level: Union[str, int] = logging.INFO,
    format_type: str = "json",
    service_name: str = "x-scanner",
    log_file: Optional[str] = None,
    console: bool = True,
) -> None:
    """Setup logging configuration.

    Args:
        level: Log level
        format_type: Format type (json or text)
        service_name: Service name for logs
        log_file: Optional log file path
        console: Enable console output
    """
    global _setup_done

    if _setup_done:
        return

    # Convert string level to int
    if isinstance(level, str):
        level = getattr(logging, level.upper())

    # Create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Remove existing handlers
    root_logger.handlers.clear()

    # Create formatter
    if format_type == "json":
        formatter = JSONFormatter(service_name=service_name)
    else:
        formatter = ColoredFormatter()

    # Add console handler
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(level)
        root_logger.addHandler(console_handler)

    # Add file handler
    if log_file:
        add_file_handler(log_file, level, formatter)

    # Set third-party loggers to WARNING
    for name in ["urllib3", "asyncio", "aiohttp"]:
        logging.getLogger(name).setLevel(logging.WARNING)

    _setup_done = True


def add_file_handler(
    log_file: str,
    level: Union[str, int] = logging.INFO,
    formatter: Optional[logging.Formatter] = None,
) -> None:
    """Add file handler to root logger.

    Args:
        log_file: Log file path
        level: Log level
        formatter: Log formatter
    """
    # Convert string level to int
    if isinstance(level, str):
        level = getattr(logging, level.upper())

    # Create log directory if needed
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # Create file handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(level)

    # Set formatter
    if formatter is None:
        formatter = JSONFormatter()
    file_handler.setFormatter(formatter)

    # Add to root logger
    logging.getLogger().addHandler(file_handler)


def get_logger(name: str) -> LoggerAdapter:
    """Get logger instance.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Logger adapter instance
    """
    if name not in _loggers:
        # Ensure logging is setup
        if not _setup_done:
            setup_logging()

        # Create logger adapter
        logger = logging.getLogger(name)
        _loggers[name] = LoggerAdapter(logger, {})

    return _loggers[name]


def set_log_level(level: Union[str, int], logger_name: Optional[str] = None) -> None:
    """Set log level.

    Args:
        level: Log level
        logger_name: Optional specific logger name
    """
    # Convert string level to int
    if isinstance(level, str):
        level = getattr(logging, level.upper())

    if logger_name:
        logging.getLogger(logger_name).setLevel(level)
    else:
        logging.getLogger().setLevel(level)


def get_request_id() -> Optional[str]:
    """Get current request ID from context.

    Returns:
        Request ID or None
    """
    return request_id_var.get()


def set_request_id(request_id: Optional[str] = None) -> str:
    """Set request ID in context.

    Args:
        request_id: Request ID (generates new if None)

    Returns:
        Request ID that was set
    """
    if request_id is None:
        request_id = str(uuid4())
    request_id_var.set(request_id)
    return request_id


def clear_request_id() -> None:
    """Clear request ID from context."""
    request_id_var.set(None)


# Convenience function for structured logging
def log_event(
    logger: LoggerAdapter,
    level: int,
    event: str,
    **fields: Any,
) -> None:
    """Log structured event.

    Args:
        logger: Logger instance
        level: Log level
        event: Event name
        **fields: Event fields
    """
    logger.log(level, event, extra_fields=fields)
