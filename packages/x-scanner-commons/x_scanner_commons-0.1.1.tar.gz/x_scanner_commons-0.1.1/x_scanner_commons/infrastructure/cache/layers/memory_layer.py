"""In-memory cache layer implementation."""

import logging
from typing import Any, Optional
import fnmatch

from aiocache import Cache
from aiocache.backends.memory import SimpleMemoryCache
from aiocache.serializers import PickleSerializer

from ..interface import CacheInterface


logger = logging.getLogger(__name__)


class MemoryLayer(CacheInterface):
    """
    In-memory cache layer implementation using aiocache.
    
    This layer is process-local and not shared between workers.
    Best suited for development, testing, or single-process applications.
    Data is lost when the process restarts.
    """
    
    def __init__(
        self,
        namespace: str = "",
        ttl: int = 300,
        **kwargs
    ):
        """
        Initialize memory layer.
        
        Args:
            namespace: Key namespace/prefix
            ttl: Default time to live in seconds
            **kwargs: Additional arguments for SimpleMemoryCache
        """
        self._cache = Cache(
            SimpleMemoryCache,
            namespace=namespace,
            serializer=PickleSerializer(),
            ttl=ttl,
            **kwargs
        )
        self.namespace = namespace
        self._ttl = ttl
    
    async def get(self, key: str) -> Optional[Any]:
        """Retrieve a value from memory."""
        try:
            return await self._cache.get(key)
        except Exception as e:
            logger.error(f"Memory get error for key {key}: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Store a value in memory."""
        try:
            # Use provided ttl or default
            actual_ttl = ttl if ttl is not None else self._ttl
            await self._cache.set(key, value, ttl=actual_ttl)
            return True
        except Exception as e:
            logger.error(f"Memory set error for key {key}: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if a key exists in memory."""
        try:
            return await self._cache.exists(key)
        except Exception as e:
            logger.error(f"Memory exists error for key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete a key from memory."""
        try:
            return await self._cache.delete(key)
        except Exception as e:
            logger.error(f"Memory delete error for key {key}: {e}")
            return False
    
    async def keys(self, pattern: str = "*") -> list[str]:
        """
        Get all keys matching the given pattern.
        
        Uses fnmatch for pattern matching compatible with Redis patterns.
        """
        try:
            # Access the internal cache storage
            # The _cache._cache is a dict for SimpleMemoryCache
            cache_dict = self._cache._cache
            
            # Build the full pattern with namespace
            if self.namespace:
                full_pattern = f"{self.namespace}:{pattern}"
            else:
                full_pattern = pattern
            
            # Match keys using fnmatch
            result = []
            namespace_prefix = f"{self.namespace}:" if self.namespace else ""
            prefix_len = len(namespace_prefix)
            
            for key in cache_dict.keys():
                if fnmatch.fnmatch(key, full_pattern):
                    # Strip namespace from result
                    if namespace_prefix and key.startswith(namespace_prefix):
                        result.append(key[prefix_len:])
                    elif not namespace_prefix:
                        result.append(key)
            
            return result
        except Exception as e:
            logger.error(f"Memory keys error for pattern {pattern}: {e}")
            return []
    
    async def clear(self) -> int:
        """Clear all keys in the current namespace."""
        try:
            # Get count before clearing (for return value)
            keys = await self.keys("*")
            count = len(keys)
            
            await self._cache.clear()
            return count
        except Exception as e:
            logger.error(f"Memory clear error: {e}")
            return 0
    
    async def close(self):
        """Close the memory backend (no-op for memory cache)."""
        # Memory cache doesn't need explicit cleanup
        pass