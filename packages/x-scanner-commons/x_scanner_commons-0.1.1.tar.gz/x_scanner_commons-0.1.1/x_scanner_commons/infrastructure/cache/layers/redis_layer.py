"""Redis cache backend implementation."""

import logging
from typing import Any, Optional
from urllib.parse import urlparse

from aiocache import Cache
from aiocache.backends.redis import RedisCache
from aiocache.serializers import PickleSerializer

from ..interface import CacheInterface


logger = logging.getLogger(__name__)


class RedisLayer(CacheInterface):
    """
    Redis cache layer implementation using aiocache.
    
    This layer wraps aiocache's RedisCache to provide a consistent
    interface while leveraging aiocache's mature Redis implementation.
    """
    
    def __init__(
        self,
        endpoint: str = "localhost",
        port: int = 6379,
        password: Optional[str] = None,
        db: int = 0,
        namespace: str = "",
        timeout: int = 10,
        pool_max_size: int = 300,
        **kwargs
    ):
        """
        Initialize Redis backend.
        
        Args:
            endpoint: Redis server hostname
            port: Redis server port
            password: Redis password if required
            db: Redis database number
            namespace: Key namespace/prefix
            timeout: Operation timeout in seconds
            pool_max_size: Maximum connection pool size
            **kwargs: Additional arguments for RedisCache
        """
        self._cache = Cache(
            RedisCache,
            endpoint=endpoint,
            port=port,
            password=password,
            db=db,
            namespace=namespace,
            serializer=PickleSerializer(),
            timeout=timeout,
            pool_max_size=pool_max_size,
            **kwargs
        )
        self.namespace = namespace
        
    @classmethod
    async def from_url(cls, url: str, namespace: str = "", **kwargs) -> "RedisLayer":
        """
        Create RedisLayer from a Redis URL.
        
        Args:
            url: Redis URL (e.g., redis://password@localhost:6379/0)
            namespace: Key namespace/prefix
            **kwargs: Additional arguments for initialization
            
        Returns:
            Configured RedisLayer instance
        """
        parsed = urlparse(url)
        
        endpoint = parsed.hostname or "localhost"
        port = parsed.port or 6379
        password = parsed.password
        
        # Extract database number from path
        db = 0
        if parsed.path and len(parsed.path) > 1:
            try:
                db = int(parsed.path[1:])
            except ValueError:
                pass
        
        return cls(
            endpoint=endpoint,
            port=port,
            password=password,
            db=db,
            namespace=namespace,
            **kwargs
        )
    
    async def get(self, key: str) -> Optional[Any]:
        """Retrieve a value from Redis."""
        try:
            return await self._cache.get(key)
        except Exception as e:
            logger.error(f"Redis get error for key {key}: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Store a value in Redis."""
        try:
            await self._cache.set(key, value, ttl=ttl)
            return True
        except Exception as e:
            logger.error(f"Redis set error for key {key}: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if a key exists in Redis."""
        try:
            return await self._cache.exists(key)
        except Exception as e:
            logger.error(f"Redis exists error for key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete a key from Redis."""
        try:
            return await self._cache.delete(key)
        except Exception as e:
            logger.error(f"Redis delete error for key {key}: {e}")
            return False
    
    async def keys(self, pattern: str = "*") -> list[str]:
        """
        Get all keys matching the given pattern.
        
        Note: This uses the underlying Redis KEYS command which can be slow
        on large databases. Use with caution in production.
        """
        try:
            # Access the underlying Redis client
            client = self._cache._cache.client  # aiocache internal structure
            
            # Build the full pattern with namespace
            if self.namespace:
                full_pattern = f"{self.namespace}:{pattern}"
            else:
                full_pattern = pattern
            
            # Get matching keys
            keys = await client.keys(full_pattern)
            
            # Decode and strip namespace
            result = []
            namespace_prefix = f"{self.namespace}:" if self.namespace else ""
            prefix_len = len(namespace_prefix)
            
            for key in keys:
                key_str = key.decode("utf-8") if isinstance(key, bytes) else key
                if namespace_prefix and key_str.startswith(namespace_prefix):
                    result.append(key_str[prefix_len:])
                elif not namespace_prefix:
                    result.append(key_str)
            
            return result
        except Exception as e:
            logger.error(f"Redis keys error for pattern {pattern}: {e}")
            return []
    
    async def clear(self) -> int:
        """Clear all keys in the current namespace."""
        try:
            await self._cache.clear()
            return 0  # aiocache doesn't return count
        except Exception as e:
            logger.error(f"Redis clear error: {e}")
            return 0
    
    async def mget(self, keys: list[str]) -> dict[str, Any]:
        """Get multiple values at once using Redis MGET."""
        try:
            # aiocache doesn't have native mget, use base implementation
            return await super().mget(keys)
        except Exception as e:
            logger.error(f"Redis mget error: {e}")
            return {}
    
    async def close(self):
        """Close the Redis connection pool."""
        try:
            await self._cache.close()
        except Exception as e:
            logger.error(f"Error closing Redis connection: {e}")