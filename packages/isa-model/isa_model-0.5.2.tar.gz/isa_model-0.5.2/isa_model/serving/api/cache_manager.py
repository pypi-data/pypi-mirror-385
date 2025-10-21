#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Simple Cache Manager for ISA Model API
Provides in-memory caching to improve API performance
"""

import time
import logging
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass
from threading import RLock
import asyncio
import hashlib
import json

logger = logging.getLogger(__name__)

@dataclass
class CacheEntry:
    """Cache entry with data and metadata"""
    data: Any
    created_at: float
    ttl: float
    access_count: int = 0
    last_accessed: float = None
    
    def is_expired(self) -> bool:
        """Check if cache entry is expired"""
        return time.time() - self.created_at > self.ttl
    
    def access(self) -> Any:
        """Mark as accessed and return data"""
        self.access_count += 1
        self.last_accessed = time.time()
        return self.data

class APICache:
    """
    Simple in-memory cache for API responses
    Thread-safe with automatic expiration
    """
    
    def __init__(self, default_ttl: float = 300.0, max_size: int = 1000):
        self.default_ttl = default_ttl  # 5 minutes default
        self.max_size = max_size
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = RLock()
        self._stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "total_requests": 0
        }
    
    def _generate_key(self, *args, **kwargs) -> str:
        """Generate cache key from arguments"""
        # Create a stable key from arguments
        key_data = {
            "args": args,
            "kwargs": sorted(kwargs.items()) if kwargs else {}
        }
        key_string = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _cleanup_expired(self):
        """Remove expired entries"""
        with self._lock:
            current_time = time.time()
            expired_keys = [
                key for key, entry in self._cache.items()
                if entry.is_expired()
            ]
            
            for key in expired_keys:
                del self._cache[key]
            
            if expired_keys:
                logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
    
    def _evict_lru(self):
        """Evict least recently used entries when cache is full"""
        with self._lock:
            if len(self._cache) >= self.max_size:
                # Sort by last_accessed time (LRU)
                sorted_entries = sorted(
                    self._cache.items(),
                    key=lambda x: x[1].last_accessed or x[1].created_at
                )
                
                # Remove oldest 20% of entries
                num_to_remove = max(1, len(sorted_entries) // 5)
                for key, _ in sorted_entries[:num_to_remove]:
                    del self._cache[key]
                    self._stats["evictions"] += 1
                
                logger.debug(f"Evicted {num_to_remove} LRU cache entries")
    
    def get(self, key: str) -> Optional[Any]:
        """Get cached value by key"""
        with self._lock:
            self._stats["total_requests"] += 1
            
            if key in self._cache:
                entry = self._cache[key]
                if not entry.is_expired():
                    self._stats["hits"] += 1
                    return entry.access()
                else:
                    # Remove expired entry
                    del self._cache[key]
            
            self._stats["misses"] += 1
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[float] = None) -> None:
        """Set cached value with optional TTL"""
        with self._lock:
            # Cleanup and eviction
            self._cleanup_expired()
            self._evict_lru()
            
            entry = CacheEntry(
                data=value,
                created_at=time.time(),
                ttl=ttl or self.default_ttl,
                last_accessed=time.time()
            )
            
            self._cache[key] = entry
    
    def delete(self, key: str) -> bool:
        """Delete cached value"""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False
    
    def clear(self) -> None:
        """Clear all cached values"""
        with self._lock:
            self._cache.clear()
            logger.info("Cache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self._lock:
            hit_rate = (
                self._stats["hits"] / self._stats["total_requests"]
                if self._stats["total_requests"] > 0 else 0
            )
            
            return {
                "cache_size": len(self._cache),
                "max_size": self.max_size,
                "default_ttl": self.default_ttl,
                "hit_rate": round(hit_rate * 100, 2),
                **self._stats
            }

# Decorator for caching function results
def cached(ttl: float = 300.0, cache_key_func: Optional[Callable] = None):
    """
    Decorator to cache function results
    
    Args:
        ttl: Time to live in seconds
        cache_key_func: Custom function to generate cache key
    """
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            # Generate cache key
            if cache_key_func:
                cache_key = cache_key_func(*args, **kwargs)
            else:
                cache_key = api_cache._generate_key(func.__name__, *args, **kwargs)
            
            # Try to get from cache
            cached_result = api_cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return cached_result
            
            # Execute function and cache result
            try:
                result = await func(*args, **kwargs)
                api_cache.set(cache_key, result, ttl)
                logger.debug(f"Cached result for {func.__name__}")
                return result
            except Exception as e:
                logger.error(f"Function {func.__name__} failed: {e}")
                raise
        
        def sync_wrapper(*args, **kwargs):
            # Generate cache key
            if cache_key_func:
                cache_key = cache_key_func(*args, **kwargs)
            else:
                cache_key = api_cache._generate_key(func.__name__, *args, **kwargs)
            
            # Try to get from cache
            cached_result = api_cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return cached_result
            
            # Execute function and cache result
            try:
                result = func(*args, **kwargs)
                api_cache.set(cache_key, result, ttl)
                logger.debug(f"Cached result for {func.__name__}")
                return result
            except Exception as e:
                logger.error(f"Function {func.__name__} failed: {e}")
                raise
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

# Global cache instance
api_cache = APICache(default_ttl=300.0, max_size=1000)

def get_api_cache() -> APICache:
    """Get the global API cache instance"""
    return api_cache

# Cache key generators for common patterns
def model_list_cache_key(service_type=None):
    """Generate cache key for model list API"""
    return f"models_list_{service_type or 'all'}"

def provider_list_cache_key():
    """Generate cache key for provider list API"""
    return "providers_list"

def custom_models_cache_key(model_type=None, provider=None):
    """Generate cache key for custom models API"""
    return f"custom_models_{model_type or 'all'}_{provider or 'all'}"