"""Core cache implementation with multi-layer support."""

import asyncio
import logging
import os
import traceback
from typing import Any, Callable, Optional, List
from dataclasses import dataclass

import mmh3
from async_lru import alru_cache

from .layers import RedisLayer, MemoryLayer
from .interface import CacheInterface
from x_scanner_commons.infrastructure.vault import VaultClient


logger = logging.getLogger(__name__)


@dataclass
class CacheLayer:
    """
    Represents a single cache layer in the multi-tier cache system.
    
    Attributes:
        layer_impl: The cache layer implementation
        ttl: Default time to live for this layer
        write_through: If True, writes propagate to lower layers
        read_through: If True, reads check lower layers on miss
    """
    layer_impl: CacheInterface
    ttl: int = 300
    write_through: bool = True
    read_through: bool = True


class Cache:
    """
    Unified cache client with support for multi-tier caching and automatic key hashing.
    
    Features:
        - Flexible multi-layer cache architecture
        - Automatic key hashing with mmh3
        - Query limiting to prevent retry storms
        - Graceful error handling
        - Per-layer TTL configuration
        - Read-through and write-through strategies
    """
    
    def __init__(
        self,
        cache_layers: List[CacheLayer],
        *,
        namespace: str = "",
        auto_hash_key: bool = True,
    ):
        """
        Initialize cache client with multi-layer support.
        
        Args:
            cache_layers: List of cache layers ordered by priority (fastest first)
            namespace: Namespace for cache keys
            auto_hash_key: Automatically hash keys with mmh3
        """
        if not cache_layers:
            raise ValueError("At least one cache layer must be provided")
        
        self.layers = cache_layers
        self.namespace = namespace
        self.auto_hash_key = auto_hash_key
    
    def _hash_key(self, key: str) -> str:
        """Hash a key if auto_hash_key is enabled."""
        if self.auto_hash_key:
            return str(mmh3.hash64(key)[0])  # Use first part of 128-bit hash
        return key
    
    async def get(self, key: str) -> Optional[Any]:
        """
        Retrieve a value from cache.
        
        Checks cache layers in order, with read-through to lower layers.
        
        Args:
            key: The cache key
            
        Returns:
            The cached value if exists, None otherwise
        """
        hashed_key = self._hash_key(key)
        
        for i, layer in enumerate(self.layers):
            try:
                value = await layer.layer_impl.get(hashed_key)
                if value is not None:
                    logger.debug(f"Cache hit in layer {i} for key: {key}")
                    # Populate higher layers (write-back)
                    for j in range(i):
                        higher_layer = self.layers[j]
                        if higher_layer.write_through:
                            try:
                                await higher_layer.layer_impl.set(hashed_key, value, higher_layer.ttl)
                            except Exception as e:
                                logger.warning(f"Failed to populate layer {j}: {e}")
                    return value
                elif not layer.read_through:
                    # Stop checking lower layers if read_through is False
                    break
            except Exception as e:
                logger.warning(f"Layer {i} get error for key {key}: {e}")
                # Continue to next layer on error
        
        return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Store a value in cache.
        
        Sets value in all layers based on write_through configuration.
        
        Args:
            key: The cache key
            value: The value to store
            ttl: Time to live in seconds, uses layer defaults if None
            
        Returns:
            True if at least one layer succeeded, False otherwise
        """
        hashed_key = self._hash_key(key)
        any_success = False
        
        for i, layer in enumerate(self.layers):
            # Use provided ttl or layer's default
            layer_ttl = ttl if ttl is not None else layer.ttl
            
            try:
                if await layer.layer_impl.set(hashed_key, value, layer_ttl):
                    any_success = True
                    if not layer.write_through:
                        # Stop writing to lower layers if write_through is False
                        break
            except Exception as e:
                logger.error(f"Layer {i} set error for key {key}: {e}")
                # Continue trying other layers
        
        return any_success
    
    async def get_or_set(
        self,
        key: str,
        default: Callable,
        ttl: Optional[int] = None,
        query_limit: int = 0
    ) -> Optional[Any]:
        """
        Get value from cache or set it using the default callable.
        
        This is the core method that implements the cache-aside pattern with
        optional query limiting to prevent retry storms.
        
        Args:
            key: The cache key
            default: Async callable that returns the value to cache if not found
            ttl: Time to live in seconds
            query_limit: Maximum number of failed queries before giving up (0 = unlimited)
            
        Returns:
            The cached or fetched value, None if all attempts failed
        """
        try:
            # Try to get from cache first
            value = await self.get(key)
            if value is not None:
                return value
            
            # Check query limit if enabled
            if query_limit > 0:
                query_key = f"{key}_query_err"
                query_count = await self._get_query_count(query_key)
                
                if query_count >= query_limit:
                    logger.debug(f"Query limit reached for key {key}: {query_count}/{query_limit}")
                    return None
                
                # Increment query count (use first layer's TTL as default)
                default_ttl = self.layers[0].ttl if self.layers else 300
                await self._increment_query_count(query_key, ttl or default_ttl)
            
            # Fetch new value
            logger.debug(f"Cache miss for key {key}, fetching new value")
            result = await default()
            
            # Cache the result (including None to prevent repeated fetches)
            if result is not None:
                await self.set(key, result, ttl)
            elif result is None and query_limit == 0:
                # Cache None result when no query limit to prevent repeated fetches
                await self.set(key, None, ttl or 60)  # Short TTL for None values
            
            return result
            
        except Exception as e:
            logger.error(f"get_or_set error for key {key}: {e}\n{traceback.format_exc()}")
            return None
    
    async def _get_query_count(self, query_key: str) -> int:
        """Get the current query error count for a key."""
        try:
            count = await self.get(query_key)
            return int(count) if count is not None else 0
        except Exception:
            return 0
    
    async def _increment_query_count(self, query_key: str, ttl: int) -> None:
        """Increment the query error count for a key."""
        try:
            current = await self._get_query_count(query_key)
            await self.set(query_key, current + 1, ttl)
        except Exception as e:
            logger.error(f"Error incrementing query count: {e}")
    
    async def exists(self, key: str) -> bool:
        """
        Check if a key exists in cache.
        
        Args:
            key: The cache key
            
        Returns:
            True if the key exists in any layer, False otherwise
        """
        hashed_key = self._hash_key(key)
        
        for i, layer in enumerate(self.layers):
            try:
                if await layer.layer_impl.exists(hashed_key):
                    return True
                if not layer.read_through:
                    # Stop checking lower layers if read_through is False
                    break
            except Exception as e:
                logger.warning(f"Layer {i} exists error for key {key}: {e}")
                # Continue to next layer on error
        
        return False
    
    async def delete(self, key: str) -> bool:
        """
        Delete a key from cache.
        
        Args:
            key: The cache key
            
        Returns:
            True if the key was deleted from at least one layer, False otherwise
        """
        hashed_key = self._hash_key(key)
        any_success = False
        
        # Delete from all layers
        for i, layer in enumerate(self.layers):
            try:
                if await layer.layer_impl.delete(hashed_key):
                    any_success = True
            except Exception as e:
                logger.warning(f"Layer {i} delete error for key {key}: {e}")
                # Continue trying other layers
        
        return any_success
    
    async def clear(self, namespace: Optional[str] = None) -> int:
        """
        Clear all keys in the cache or specific namespace.
        
        Args:
            namespace: Specific namespace to clear (not implemented yet)
            
        Returns:
            Total number of keys deleted from all layers
        """
        total_count = 0
        
        # Clear all layers
        for i, layer in enumerate(self.layers):
            try:
                count = await layer.layer_impl.clear()
                total_count += count
            except Exception as e:
                logger.warning(f"Layer {i} clear error: {e}")
                # Continue clearing other layers
        
        return total_count
    
    async def keys(self, pattern: str = "*") -> list[str]:
        """
        Get all keys matching the given pattern.
        
        Queries the last (most persistent) layer.
        
        Args:
            pattern: The pattern to match (e.g., "user:*")
            
        Returns:
            List of matching keys (unhashed)
        """
        if not self.layers:
            return []
        
        # Query the last layer (most persistent storage)
        last_layer = self.layers[-1]
        
        try:
            # For pattern matching, we can't use hashed keys
            # This only works properly when auto_hash_key is False
            if self.auto_hash_key:
                logger.warning("Pattern matching with auto_hash_key=True may not work as expected")
            return await last_layer.layer_impl.keys(pattern)
        except Exception as e:
            logger.error(f"Keys error for pattern {pattern}: {e}")
            return []
    
    async def mget(self, keys: list[str]) -> dict[str, Any]:
        """
        Get multiple values at once.
        
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
    
    async def close(self):
        """Close all cache layer connections."""
        for i, layer in enumerate(self.layers):
            try:
                if hasattr(layer.layer_impl, 'close'):
                    await layer.layer_impl.close()
            except Exception as e:
                logger.error(f"Error closing layer {i}: {e}")


# Factory functions

@alru_cache(maxsize=128)
async def create_cache(
    namespace: str,
    cache_layers: Optional[str] = None,  # Can be "redis", "memory", or "memory,redis" for multi-tier
    redis_url: Optional[str] = None,
    vault_path: str = "x-scanner/main/redis",
    ttls: Optional[str] = None,  # Comma-separated TTLs like "60,300"
    auto_hash_key: bool = True,
    **kwargs
) -> Cache:
    """
    Create a cache client with multi-layer support.
    
    Automatically fetches Redis configuration from Vault if redis_url is not provided.
    
    Args:
        namespace: Cache namespace for key isolation
        cache_layers: Cache layer configuration as a string:
                     - Single layer: "redis" or "memory"
                     - Multi-tier: "memory,redis" (comma-separated, priority order)
                     - Defaults to "redis" if not provided
        redis_url: Direct Redis URL (optional, fetched from Vault if not provided)
        vault_path: Vault KV path for Redis configuration (default: x-scanner/main/redis)
                   Note: Do not include mount point or 'data' prefix, the VaultClient handles this
        ttls: Comma-separated TTLs like "60,300" (defaults based on layer types)
        auto_hash_key: Automatically hash keys with mmh3
        **kwargs: Additional arguments (for backward compatibility)
        
    Returns:
        Configured Cache instance with multi-layer support
        
    Raises:
        RuntimeError: If Vault is not configured or Redis credentials not found
        ValueError: If layer configuration is invalid
        
    Examples:
        # Single Redis cache (default)
        cache = await create_cache("my_cache")
        
        # Single memory cache
        cache = await create_cache(
            "my_cache",
            cache_layers="memory"
        )

        # Two-tier cache (Memory + Redis)
        cache = await create_cache(
            "my_cache",
            cache_layers="memory,redis",
            ttls="60,300"  # 1 minute for memory, 5 minutes for Redis
        )

        # Three-tier cache (theoretical)
        cache = await create_cache(
            "my_cache",
            cache_layers="memory,memory,redis",
            ttls="10,60,300"
        )
    """
    # Parse configuration
    layer_types = (cache_layers or "redis").split(",")
    ttl_list = list(map(int, ttls.split(","))) if ttls else []
    
    # Smart TTL defaults: 60s for memory, 300s for persistent storage
    default_ttls = {"memory": 60, "redis": 300}
    ttl_list += [default_ttls.get(layer_types[i], 300) for i in range(len(ttl_list), len(layer_types))]
    
    # Get Redis URL if needed
    if "redis" in layer_types and not redis_url:
        redis_url = await _get_redis_url_from_vault(vault_path)
    
    # Layer factory mapping - make async wrappers
    async def create_redis_layer(ns):
        return await RedisLayer.from_url(redis_url, ns)
    
    async def create_memory_layer(ns):
        return MemoryLayer(namespace=ns)
    
    layer_factories = {
        "redis": create_redis_layer,
        "memory": create_memory_layer
    }
    
    # Build cache layers
    layers = []
    for i, layer_type in enumerate(layer_types):
        if layer_type not in layer_factories:
            raise ValueError(f"Unknown layer type: {layer_type}")
        
        ns = f"{namespace}_L{i}" if len(layer_types) > 1 else namespace
        layer_impl = await layer_factories[layer_type](ns)
        
        layers.append(CacheLayer(
            layer_impl=layer_impl,
            ttl=ttl_list[i],
            write_through=True,
            read_through=True
        ))
    
    return Cache(
        cache_layers=layers,
        namespace=namespace,
        auto_hash_key=auto_hash_key
    )



async def _get_redis_url_from_vault(vault_path: str) -> str:
    """
    Get Redis URL from Vault.
    
    Args:
        vault_path: Vault path for Redis configuration
        
    Returns:
        Redis connection URL
        
    Raises:
        RuntimeError: If Vault is not configured or credentials not found
    """
    vault_addr = os.environ.get("VAULT_ADDR")
    vault_token = os.environ.get("VAULT_TOKEN")
    
    if not (vault_addr and vault_token):
        raise RuntimeError(
            "Vault not configured. Set VAULT_ADDR and VAULT_TOKEN environment variables."
        )
    
    client = VaultClient(url=vault_addr, token=vault_token)
    
    # Get Redis configuration from Vault
    secret = await client.get_secret(vault_path)
    
    # Try different key names for Redis URL
    for key in ["url", "uri", "redis_url"]:
        if key in secret.data:
            return secret.data[key]
    
    raise RuntimeError(f"Redis URL not found in Vault at {vault_path}")