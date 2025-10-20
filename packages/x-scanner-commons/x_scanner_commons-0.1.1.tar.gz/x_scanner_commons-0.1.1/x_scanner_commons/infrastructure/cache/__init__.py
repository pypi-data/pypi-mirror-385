"""Cache module with unified interface and multi-tier support."""

from .cache import Cache, CacheLayer, create_cache
from .interface import CacheInterface
from .layers import MemoryLayer, RedisLayer

__all__ = [
    "Cache",
    "CacheLayer",
    "CacheInterface", 
    "MemoryLayer",
    "RedisLayer",
    "create_cache",
]