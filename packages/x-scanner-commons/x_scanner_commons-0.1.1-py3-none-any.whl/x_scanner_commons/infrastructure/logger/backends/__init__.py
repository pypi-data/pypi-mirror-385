"""Logger backends module."""

from x_scanner_commons.infrastructure.logger.backends.console import ConsoleBackend
from x_scanner_commons.infrastructure.logger.backends.file import FileBackend

__all__ = [
    "ConsoleBackend",
    "FileBackend",
]

# Optional backends
try:
    from x_scanner_commons.infrastructure.logger.backends.aliyun_sls import AliyunSLSBackend
    __all__.append("AliyunSLSBackend")
except ImportError:
    # AliyunSLSBackend requires aliyun-log-python-sdk
    pass