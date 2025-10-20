"""Database utility functions."""

from typing import Any


def get_database_url(
    driver: str = "postgresql+asyncpg",
    username: str = "postgres",
    password: str = "postgres",
    host: str = "localhost",
    port: int = 5432,
    database: str = "postgres",
    **kwargs: Any,
) -> str:
    """Build database URL.

    Args:
        driver: Database driver
        username: Database username
        password: Database password
        host: Database host
        port: Database port
        database: Database name
        **kwargs: Additional query parameters

    Returns:
        Database URL string
    """
    url = f"{driver}://{username}:{password}@{host}:{port}/{database}"

    if kwargs:
        params = "&".join(f"{k}={v}" for k, v in kwargs.items())
        url = f"{url}?{params}"

    return url


def create_async_engine(
    database_url: str,
    pool_size: int = 10,
    max_overflow: int = 20,
    pool_pre_ping: bool = True,
    echo: bool = False,
    **kwargs: Any,
) -> Any:
    """Create async SQLAlchemy engine.

    Args:
        database_url: Database URL
        pool_size: Connection pool size
        max_overflow: Maximum overflow connections
        pool_pre_ping: Check connections before using
        echo: Echo SQL statements
        **kwargs: Additional engine arguments

    Returns:
        AsyncEngine instance
    """
    try:
        from sqlalchemy.ext.asyncio import create_async_engine as _create_async_engine
    except ImportError:
        raise ImportError(
            "Database dependencies not installed. Install with: pip install 'x-scanner-commons[database]'"
        )

    return _create_async_engine(
        database_url,
        pool_size=pool_size,
        max_overflow=max_overflow,
        pool_pre_ping=pool_pre_ping,
        echo=echo,
        **kwargs,
    )


def create_async_session(
    engine: Any,
    expire_on_commit: bool = False,
    **kwargs: Any,
) -> Any:
    """Create async session factory.

    Args:
        engine: AsyncEngine instance
        expire_on_commit: Expire objects on commit
        **kwargs: Additional session arguments

    Returns:
        AsyncSession factory
    """
    try:
        from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
    except ImportError:
        raise ImportError(
            "Database dependencies not installed. Install with: pip install 'x-scanner-commons[database]'"
        )

    return async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=expire_on_commit,
        **kwargs,
    )
