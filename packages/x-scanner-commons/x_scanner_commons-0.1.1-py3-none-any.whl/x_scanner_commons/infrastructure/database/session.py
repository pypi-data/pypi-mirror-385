"""Database session management with zero-config Vault integration."""

import os
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from typing import Any
from fastapi import Depends, Request
from x_scanner_commons.infrastructure.vault import VaultClient

try:
    from sqlalchemy.ext.asyncio import (
        AsyncSession,
        async_sessionmaker,
        create_async_engine,
    )
except ImportError:
    raise ImportError(
        "Database dependencies not installed. Install with: pip install 'x-scanner-commons[database]'"
    )


class AsyncSessionManager:
    """Async database session manager with lazy initialization.

    - If ``database_url`` is provided, it will be used to create the engine on first use
    - Otherwise, credentials are fetched from Vault lazily using ``vault_path``
    """

    def __init__(
        self,
        vault_path: str,
        *,
        database_url: str | None = None,
        pool_size: int = 10,
        max_overflow: int = 20,
        pool_pre_ping: bool = True,
        echo: bool = False,
        **engine_kwargs: Any,
    ) -> None:
        """Initialize session manager with configuration only (no IO).

        Engine and session factory are created lazily on first use.
        """
        self._vault_path = vault_path
        self._database_url = database_url
        self._pool_size = pool_size
        self._max_overflow = max_overflow
        self._pool_pre_ping = pool_pre_ping
        self._echo = echo
        self._engine_kwargs = engine_kwargs

        self._engine = None
        self._session_factory = None

    async def ensure_ready(self) -> None:
        """Ensure engine and session factory are initialized."""
        if self._engine is not None and self._session_factory is not None:
            return

        database_url = self._database_url
        if database_url is None:
            # Fetch DSN from Vault asynchronously
            vault_addr = os.environ.get("VAULT_ADDR")
            vault_token = os.environ.get("VAULT_TOKEN")

            if not (vault_addr and vault_token):
                raise RuntimeError(
                    "Vault not configured. Set VAULT_ADDR and VAULT_TOKEN environment variables."
                )

            

            client = VaultClient(url=vault_addr, token=vault_token)
            secret = await client.get_secret(self._vault_path)
            database_url = secret.data.get("url")
            if not database_url:
                raise RuntimeError(
                    f"Database URL not found in Vault at {self._vault_path}"
                )

        # Create engine and session factory
        self._engine = create_async_engine(
            database_url,
            pool_size=self._pool_size,
            max_overflow=self._max_overflow,
            pool_pre_ping=self._pool_pre_ping,
            echo=self._echo,
            **self._engine_kwargs,
        )

        self._session_factory = async_sessionmaker(
            self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    @classmethod
    async def from_vault(
        cls,
        vault_path: str,
        *,
        pool_size: int = 10,
        max_overflow: int = 20,
        pool_pre_ping: bool = True,
        echo: bool = False,
        **engine_kwargs: Any,
    ) -> "AsyncSessionManager":
        """Create an ``AsyncSessionManager`` by fetching DSN from Vault asynchronously.

        Args:
            vault_path: Vault KV path that stores a key named ``url``
            pool_size: Connection pool size
            max_overflow: Maximum overflow connections
            pool_pre_ping: Check connections before using
            echo: Echo SQL statements
            **engine_kwargs: Additional engine arguments passed to SQLAlchemy engine

        Returns:
            AsyncSessionManager instance
        """
        # Explicit factory: still supported for clarity
        vault_addr = os.environ.get("VAULT_ADDR")
        vault_token = os.environ.get("VAULT_TOKEN")

        if not (vault_addr and vault_token):
            raise RuntimeError(
                "Vault not configured. Set VAULT_ADDR and VAULT_TOKEN environment variables."
            )

        

        client = VaultClient(url=vault_addr, token=vault_token)
        secret = await client.get_secret(vault_path)

        url = secret.data.get("url")
        if not url:
            raise RuntimeError(f"Database URL not found in Vault at {vault_path}")

        return cls(
            vault_path=vault_path,
            database_url=url,
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_pre_ping=pool_pre_ping,
            echo=echo,
            **engine_kwargs,
        )
    
    async def get_session(self) -> AsyncIterator[AsyncSession]:
        """Get database session for dependency injection.

        Yields:
            AsyncSession instance
        """
        await self.ensure_ready()
        async with self._session_factory() as session:
            try:
                yield session
            except Exception:
                transaction = session.get_transaction()
                if transaction is not None:
                    try:
                        await session.rollback()
                    except Exception:
                        pass
                raise
            else:
                transaction = session.get_transaction()
                if transaction is None:
                    return
                if not transaction.is_active:
                    try:
                        await session.rollback()
                    except Exception:
                        pass
                    return
                try:
                    await session.commit()
                except Exception:
                    try:
                        await session.rollback()
                    except Exception:
                        pass
                    raise

    async def close(self) -> None:
        """Close all connections."""
        if self._engine is not None:
            await self._engine.dispose()

def create_db_lifespan(
    vault_path: str,
    *,
    database_url: str | None = None,
    pool_size: int = 20,
    max_overflow: int = 20,
    pool_pre_ping: bool = True,
    echo: bool = False,
    eager_init: bool = False,
    **engine_kwargs: Any,
):
    """Create a FastAPI lifespan context manager that manages DB resources.

    Usage (FastAPI):
        app = FastAPI(lifespan=create_db_lifespan(...))
    """

    @asynccontextmanager
    async def lifespan(app):
        manager = AsyncSessionManager(
            vault_path=vault_path,
            database_url=database_url,
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_pre_ping=pool_pre_ping,
            echo=echo,
            **engine_kwargs,
        )

        app.state.db_manager = manager
        try:
            if eager_init:
                await manager.ensure_ready()
            yield
        finally:
            await manager.close()

    return lifespan


def get_db_manager(request: Request) -> "AsyncSessionManager":
    """Retrieve ``AsyncSessionManager`` from ``app.state``.

    Raises RuntimeError if the application is not initialized with ``create_db_lifespan``.
    """
    manager = getattr(request.app.state, "db_manager", None)
    if manager is None:
        raise RuntimeError("Database not initialized. Did you set app.lifespan?")
    return manager


async def get_async_session(
    manager: "AsyncSessionManager" = Depends(get_db_manager),
) -> AsyncIterator[AsyncSession]:
    """Dependency that yields an ``AsyncSession``.

    Typical usage in FastAPI:
        from fastapi import Depends

        @router.get("/items")
        async def list_items(db: AsyncSession = Depends(get_async_session)):
            ...
    """
    async for session in manager.get_session():
        yield session
