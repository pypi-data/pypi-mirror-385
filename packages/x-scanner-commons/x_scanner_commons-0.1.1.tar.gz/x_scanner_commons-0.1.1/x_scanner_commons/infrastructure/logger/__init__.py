"""Logger infrastructure module for X-Scanner Commons."""

from x_scanner_commons.infrastructure.logger.decorators import (
    log_performance,
    log_request,
    with_request_context,
)
from x_scanner_commons.infrastructure.logger.logger import (
    Logger,
    LoggerManager,
    clear_request_context,
    get_logger,
    get_request_context,
    get_request_id,
    set_request_context,
    set_request_id,
    setup_logging,
)
from x_scanner_commons.infrastructure.logger.models import LogEntry, LoggerConfig, LogLevel

__all__ = [
    # Main classes
    "Logger",
    "LoggerManager",
    # Models
    "LogEntry",
    "LoggerConfig",
    "LogLevel",
    # Functions
    "get_logger",
    "setup_logging",
    # Context management
    "set_request_context",
    "get_request_context",
    "clear_request_context",
    "set_request_id",
    "get_request_id",
    # Decorators
    "log_request",
    "log_performance",
    "with_request_context",
]