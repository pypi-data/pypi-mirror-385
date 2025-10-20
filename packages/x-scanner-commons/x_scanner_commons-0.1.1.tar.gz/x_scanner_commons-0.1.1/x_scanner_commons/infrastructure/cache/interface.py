"""Cache interface definition for unified cache operations."""

from abc import ABC, abstractmethod
from typing import Any, Optional


class CacheInterface(ABC):
    """
    Abstract base class defining the cache backend interface.
    
    All cache backends must implement these methods to ensure
    consistent behavior across different storage mechanisms.
    """
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """
        Retrieve a value from the cache.
        
        Args:
            key: The cache key to retrieve
            
        Returns:
            The cached value if exists, None otherwise
        """
        pass
    
    @abstractmethod
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Store a value in the cache.
        
        Args:
            key: The cache key
            value: The value to store
            ttl: Time to live in seconds, None for default
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def exists(self, key: str) -> bool:
        """
        Check if a key exists in the cache.
        
        Args:
            key: The cache key to check
            
        Returns:
            True if the key exists, False otherwise
        """
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """
        Delete a key from the cache.
        
        Args:
            key: The cache key to delete
            
        Returns:
            True if the key was deleted, False otherwise
        """
        pass
    
    @abstractmethod
    async def keys(self, pattern: str = "*") -> list[str]:
        """
        Get all keys matching the given pattern.
        
        Args:
            pattern: The pattern to match (e.g., "user:*")
            
        Returns:
            List of matching keys
        """
        pass
    
    @abstractmethod
    async def clear(self) -> int:
        """
        Clear all keys in the current namespace.
        
        Returns:
            Number of keys deleted
        """
        pass
    
    async def mget(self, keys: list[str]) -> dict[str, Any]:
        """
        Get multiple values at once.
        
        Default implementation uses individual gets.
        Backends can override for better performance.
        
        Args:
            keys: List of keys to retrieve
            
        Returns:
            Dictionary mapping keys to values
        """
        result = {}
        for key in keys:
            value = await self.get(key)
            if value is not None:
                result[key] = value
        return result
    
    async def mset(self, mapping: dict[str, Any], ttl: Optional[int] = None) -> bool:
        """
        Set multiple key-value pairs at once.
        
        Default implementation uses individual sets.
        Backends can override for better performance.
        
        Args:
            mapping: Dictionary of key-value pairs
            ttl: Time to live for all keys
            
        Returns:
            True if all operations succeeded
        """
        success = True
        for key, value in mapping.items():
            if not await self.set(key, value, ttl):
                success = False
        return success