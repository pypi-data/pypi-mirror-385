"""Main logger implementation with multi-backend support."""

import contextvars
import logging
import os
from typing import Any, Optional
from uuid import uuid4

from x_scanner_commons.infrastructure.logger.backends.console import ConsoleBackend
from x_scanner_commons.infrastructure.logger.backends.file import FileBackend
from x_scanner_commons.infrastructure.logger.formatters import (
    JSONFormatter,
    StructuredFormatter,
    TextFormatter,
)
from x_scanner_commons.infrastructure.logger.interface import LoggerBackendInterface
from x_scanner_commons.infrastructure.logger.models import LogEntry, LoggerConfig, LogLevel


# Context variable for request tracking
request_context: contextvars.ContextVar[dict[str, Any]] = contextvars.ContextVar(
    "request_context", default={}
)


class Logger:
    """Main logger class with multi-backend support."""
    
    def __init__(self, name: str, config: Optional[LoggerConfig] = None) -> None:
        """Initialize logger.
        
        Args:
            name: Logger name
            config: Logger configuration
        """
        self.name = name
        self.config = config or LoggerConfig()
        self.backends: list[LoggerBackendInterface] = []
        self.python_logger = logging.getLogger(name)
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize all configured backends."""
        if self._initialized:
            return
        
        # Set Python logger level
        level = self.config.level
        if isinstance(level, str):
            level = LogLevel.from_string(level)
        self.python_logger.setLevel(level.to_int())
        self.python_logger.propagate = False
        
        # Clear existing handlers
        self.python_logger.handlers.clear()
        
        # Create formatter based on format type
        if self.config.format == "json":
            formatter = JSONFormatter(
                service_name=self.config.service_name,
                version=self.config.version,
                environment=self.config.environment,
            )
        elif self.config.format == "structured":
            formatter = StructuredFormatter(
                service_name=self.config.service_name,
                version=self.config.version,
                environment=self.config.environment,
            )
        else:  # text
            formatter = TextFormatter(
                service_name=self.config.service_name,
                version=self.config.version,
                environment=self.config.environment,
                use_colors=True,
            )
        
        # Get level string for backends
        level_str = self.config.level.value if hasattr(self.config.level, 'value') else str(self.config.level)
        
        # Initialize console backend
        if self.config.console_enabled:
            console_backend = ConsoleBackend()
            console_backend.set_formatter(formatter)
            await console_backend.initialize(level=level_str)
            self.backends.append(console_backend)
        
        # Initialize file backend
        if self.config.file_enabled and self.config.file_path:
            file_backend = FileBackend()
            file_backend.set_formatter(formatter)
            await file_backend.initialize(
                file_path=self.config.file_path,
                level=level_str,
            )
            self.backends.append(file_backend)
        
        # Initialize Aliyun SLS backend if configured
        if self.config.sls_enabled and self.config.level != LogLevel.DEBUG:
            try:
                from x_scanner_commons.infrastructure.logger.backends.aliyun_sls import (
                    AliyunSLSBackend,
                )
                
                sls_backend = AliyunSLSBackend()
                sls_backend.set_formatter(formatter)
                await sls_backend.initialize(
                    endpoint=self.config.sls_endpoint,
                    access_key_id=self.config.sls_access_key_id,
                    access_key_secret=self.config.sls_access_key_secret,
                    project=self.config.sls_project,
                    logstore=self.config.sls_logstore,
                    queue_size=self.config.sls_queue_size,
                    batch_size=self.config.sls_batch_size,
                    put_wait=self.config.sls_put_wait,
                    level=LogLevel.INFO.value,  # SLS only logs INFO and above
                )
                self.backends.append(sls_backend)
                print("Info: Aliyun SLS logger backend initialized successfully")
            except ImportError:
                print("Warning: Aliyun SLS backend not available, using console only")
            except Exception as e:
                print(f"Warning: Failed to initialize Aliyun SLS backend: {e}")
        
        # Configure third-party loggers
        for logger_name in self.config.third_party_loggers:
            third_party_logger = logging.getLogger(logger_name)
            third_party_logger.setLevel(self.config.third_party_level.to_int())
            third_party_logger.propagate = False
        
        self._initialized = True
    
    async def _log(
        self,
        level: LogLevel,
        message: str,
        extra: Optional[dict[str, Any]] = None,
        exc_info: Optional[tuple] = None,
    ) -> None:
        """Internal log method.
        
        Args:
            level: Log level
            message: Log message
            extra: Additional fields
            exc_info: Exception information
        """
        if not self._initialized:
            await self.initialize()
        
        # Get context data
        context = request_context.get()
        
        # Merge context with extra
        log_extra = {}
        if context:
            log_extra.update(context)
        if extra:
            log_extra.update(extra)
        
        # Log to all backends
        for backend in self.backends:
            try:
                await backend.log(
                    level=level.value,
                    message=message,
                    extra=log_extra,
                    exc_info=exc_info,
                )
            except Exception as e:
                # Log backend errors to console
                print(f"Error in logger backend: {e}")
    
    async def debug(self, message: str, **kwargs: Any) -> None:
        """Log debug message."""
        await self._log(LogLevel.DEBUG, message, extra=kwargs)
    
    async def info(self, message: str, **kwargs: Any) -> None:
        """Log info message."""
        await self._log(LogLevel.INFO, message, extra=kwargs)
    
    async def warning(self, message: str, **kwargs: Any) -> None:
        """Log warning message."""
        await self._log(LogLevel.WARNING, message, extra=kwargs)
    
    async def error(
        self,
        message: str,
        exc_info: Optional[tuple] = None,
        **kwargs: Any,
    ) -> None:
        """Log error message."""
        await self._log(LogLevel.ERROR, message, extra=kwargs, exc_info=exc_info)
    
    async def critical(
        self,
        message: str,
        exc_info: Optional[tuple] = None,
        **kwargs: Any,
    ) -> None:
        """Log critical message."""
        await self._log(LogLevel.CRITICAL, message, extra=kwargs, exc_info=exc_info)
    
    async def flush(self) -> None:
        """Flush all backends."""
        for backend in self.backends:
            try:
                await backend.flush()
            except Exception:
                pass
    
    async def close(self) -> None:
        """Close all backends."""
        for backend in self.backends:
            try:
                await backend.close()
            except Exception:
                pass
        self.backends.clear()
        self._initialized = False
    
    def set_level(self, level: LogLevel) -> None:
        """Set logger level.
        
        Args:
            level: New log level
        """
        self.config.level = level
        if isinstance(level, str):
            level = LogLevel.from_string(level)
        self.python_logger.setLevel(level.to_int())
        
        for backend in self.backends:
            backend.set_level(level.value)


class LoggerManager:
    """Manager for logger instances."""
    
    _instance: Optional["LoggerManager"] = None
    _loggers: dict[str, Logger] = {}
    _default_config: Optional[LoggerConfig] = None
    
    def __new__(cls) -> "LoggerManager":
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def set_default_config(self, config: LoggerConfig) -> None:
        """Set default configuration for new loggers.
        
        Args:
            config: Default logger configuration
        """
        self._default_config = config
    
    async def get_logger(self, name: str) -> Logger:
        """Get or create a logger instance.
        
        Args:
            name: Logger name
            
        Returns:
            Logger instance
        """
        if name not in self._loggers:
            config = self._default_config or self._load_config_from_env()
            logger = Logger(name, config)
            await logger.initialize()
            self._loggers[name] = logger
        
        return self._loggers[name]
    
    def _load_config_from_env(self) -> LoggerConfig:
        """Load configuration from environment variables.
        
        Returns:
            Logger configuration
        """
        config = LoggerConfig()
        
        # Basic configuration
        if log_level := os.getenv("LOG_LEVEL"):
            config.level = LogLevel.from_string(log_level)
        
        if log_format := os.getenv("LOG_FORMAT"):
            config.format = log_format
        
        if service_name := os.getenv("SERVICE_NAME"):
            config.service_name = service_name
        
        if version := os.getenv("TAG_NAME"):
            config.version = version
        
        if environment := os.getenv("ENVIRONMENT"):
            config.environment = environment
        
        # File backend
        if log_file := os.getenv("LOG_FILE"):
            config.file_enabled = True
            config.file_path = log_file
        
        # Aliyun SLS backend
        if os.getenv("SLS_ENABLED", "").lower() == "true":
            config.sls_enabled = True
            config.sls_endpoint = os.getenv("SLS_ENDPOINT", "cn-beijing.log.aliyuncs.com")
            config.sls_access_key_id = os.getenv("SLS_ACCESS_KEY_ID")
            config.sls_access_key_secret = os.getenv("SLS_ACCESS_KEY_SECRET")
            config.sls_project = os.getenv("SLS_PROJECT", "x-scanner")
            config.sls_logstore = os.getenv("SLS_LOGSTORE", "background")
        
        return config
    
    async def close_all(self) -> None:
        """Close all logger instances."""
        for logger in self._loggers.values():
            await logger.close()
        self._loggers.clear()


# Context management functions
def set_request_context(**kwargs: Any) -> None:
    """Set request context for logging.
    
    Args:
        **kwargs: Context fields (request_id, user, etc.)
    """
    current = request_context.get()
    current.update(kwargs)
    request_context.set(current)


def get_request_context() -> dict[str, Any]:
    """Get current request context.
    
    Returns:
        Request context dictionary
    """
    return request_context.get()


def clear_request_context() -> None:
    """Clear request context."""
    request_context.set({})


def set_request_id(request_id: Optional[str] = None) -> str:
    """Set request ID in context.
    
    Args:
        request_id: Request ID (generates new if None)
        
    Returns:
        Request ID that was set
    """
    if request_id is None:
        request_id = str(uuid4())
    set_request_context(request_id=request_id)
    return request_id


def get_request_id() -> Optional[str]:
    """Get current request ID from context.
    
    Returns:
        Request ID or None
    """
    return get_request_context().get("request_id")


# Convenience functions
_manager = LoggerManager()


async def get_logger(name: str) -> Logger:
    """Get a logger instance.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Logger instance
    """
    return await _manager.get_logger(name)


def setup_logging(config: Optional[LoggerConfig] = None) -> None:
    """Setup global logging configuration.
    
    Args:
        config: Logger configuration
    """
    if config:
        _manager.set_default_config(config)
    else:
        # Load from environment
        config = _manager._load_config_from_env()
        _manager.set_default_config(config)