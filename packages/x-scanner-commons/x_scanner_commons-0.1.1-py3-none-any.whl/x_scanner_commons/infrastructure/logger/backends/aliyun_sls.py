"""Aliyun SLS logger backend implementation."""

import logging
from typing import Any, Optional

from x_scanner_commons.infrastructure.logger.interface import LoggerBackendInterface
from x_scanner_commons.infrastructure.logger.models import LogLevel


class AliyunSLSBackend(LoggerBackendInterface):
    """Aliyun SLS (Simple Log Service) logger backend."""
    
    def __init__(self) -> None:
        """Initialize Aliyun SLS backend."""
        self.handler: Optional[Any] = None  # QueuedLogHandler
        self.min_level = LogLevel.INFO
        self.formatter: Optional[logging.Formatter] = None
        self.initialized = False
    
    async def initialize(self, **kwargs: Any) -> None:
        """Initialize the Aliyun SLS backend.
        
        Args:
            **kwargs: Configuration options
                - endpoint: SLS endpoint
                - access_key_id: Access key ID
                - access_key_secret: Access key secret
                - project: SLS project name
                - logstore: SLS logstore name
                - queue_size: Queue size for batching
                - batch_size: Batch size for sending
                - put_wait: Wait time before sending
                - level: Minimum log level
        """
        try:
            from aliyun.log import QueuedLogHandler
        except ImportError as e:
            raise ImportError(
                "aliyun-log-python-sdk is required for AliyunSLSBackend. "
                "Install with: pip install aliyun-log-python-sdk"
            ) from e
        
        # Get configuration
        endpoint = kwargs.get("endpoint")
        access_key_id = kwargs.get("access_key_id")
        access_key_secret = kwargs.get("access_key_secret")
        project = kwargs.get("project")
        logstore = kwargs.get("logstore")
        
        if not all([endpoint, access_key_id, access_key_secret, project, logstore]):
            raise ValueError(
                "endpoint, access_key_id, access_key_secret, project, and logstore "
                "are required for AliyunSLSBackend"
            )
        
        # Create handler
        self.handler = QueuedLogHandler(
            end_point=endpoint,
            access_key_id=access_key_id,
            access_key=access_key_secret,
            project=project,
            log_store=logstore,
            queue_size=kwargs.get("queue_size", 40000),
            batch_size=kwargs.get("batch_size", 2000),
            put_wait=kwargs.get("put_wait", 1.0),
        )
        
        level = kwargs.get("level", "INFO")
        self.set_level(level)
        
        if self.formatter:
            self.handler.setFormatter(self.formatter)
        
        self.initialized = True
    
    async def log(
        self,
        level: str,
        message: str,
        extra: Optional[dict[str, Any]] = None,
        exc_info: Optional[tuple] = None,
    ) -> None:
        """Log a message to Aliyun SLS.
        
        Args:
            level: Log level
            message: Log message
            extra: Additional fields
            exc_info: Exception information
        """
        if not self.handler:
            raise RuntimeError("AliyunSLSBackend not initialized")
        
        # Create log record
        logger = logging.getLogger("aliyun_sls")
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
        """Flush the Aliyun SLS queue."""
        if self.handler and hasattr(self.handler, "flush"):
            try:
                self.handler.flush()
            except Exception:
                # Ignore flush errors to prevent blocking
                pass
    
    async def close(self) -> None:
        """Close the Aliyun SLS backend."""
        if self.handler:
            try:
                await self.flush()
                if hasattr(self.handler, "close"):
                    self.handler.close()
            except Exception:
                # Ignore close errors
                pass
            finally:
                self.handler = None
                self.initialized = False
    
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