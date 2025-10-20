"""Logger models and data structures."""

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field, field_serializer


class LogLevel(str, Enum):
    """Log level enumeration."""
    
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
    
    @classmethod
    def from_string(cls, level: str) -> "LogLevel":
        """Convert string to LogLevel."""
        return cls[level.upper()]
    
    def to_int(self) -> int:
        """Convert to logging level integer."""
        levels = {
            "DEBUG": 10,
            "INFO": 20,
            "WARNING": 30,
            "ERROR": 40,
            "CRITICAL": 50,
        }
        return levels[self.value]


class LogEntry(BaseModel):
    """Structured log entry model."""
    
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    level: LogLevel
    logger_name: str
    message: str
    service_name: Optional[str] = None
    version: Optional[str] = None
    environment: Optional[str] = None
    request_id: Optional[str] = None
    user: Optional[str] = None
    source: Optional[dict[str, Any]] = None
    extra: Optional[dict[str, Any]] = None
    exception: Optional[dict[str, Any]] = None
    
    @field_serializer('timestamp', mode='plain')
    def serialize_timestamp(self, value: datetime) -> str:
        """Serialize timestamp to ISO format."""
        return value.isoformat() if value else None
    
    model_config = {
        "use_enum_values": True,
    }


class LoggerConfig(BaseModel):
    """Logger configuration model."""
    
    level: LogLevel = LogLevel.INFO
    format: str = "json"  # json or text
    service_name: str = "x-scanner"
    version: Optional[str] = None
    environment: Optional[str] = None
    
    # Backend configurations
    console_enabled: bool = True
    file_enabled: bool = False
    file_path: Optional[str] = None
    
    # Aliyun SLS configuration
    sls_enabled: bool = False
    sls_endpoint: Optional[str] = None
    sls_access_key_id: Optional[str] = None
    sls_access_key_secret: Optional[str] = None
    sls_project: Optional[str] = None
    sls_logstore: Optional[str] = None
    sls_queue_size: int = 40000
    sls_batch_size: int = 2000
    sls_put_wait: float = 1.0
    
    # Third-party logger levels
    third_party_level: LogLevel = LogLevel.WARNING
    third_party_loggers: list[str] = Field(
        default_factory=lambda: [
            "httpx",
            "httpcore",
            "urllib3",
            "asyncio",
            "aiohttp",
            "kr8s",
            "kubernetes",
        ]
    )
    
    model_config = {
        "use_enum_values": True,
    }