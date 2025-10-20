"""Database module for X-Scanner Commons."""

from x_scanner_commons.infrastructure.database.utils import (
    create_async_engine,
    create_async_session,
    get_database_url,
)

__all__ = [
    "create_async_engine",
    "create_async_session",
    "get_database_url",
]

# Conditional imports for optional dependencies
try:
    from x_scanner_commons.infrastructure.database.session import (
        AsyncSessionManager,
        get_async_session,
        init_database,
        close_database,
    )

    __all__.extend([
        "AsyncSessionManager", 
        "get_async_session",
        "init_database",
        "close_database",
    ])
except ImportError:
    # SQLAlchemy dependencies not installed
    pass
