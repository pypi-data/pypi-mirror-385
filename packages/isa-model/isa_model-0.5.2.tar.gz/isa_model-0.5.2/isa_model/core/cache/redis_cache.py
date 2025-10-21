"""
Redis-based Caching Strategy for ISA Model

Provides multi-level caching for:
- Model responses and completions
- Model metadata and configurations
- User sessions and authentication
- Rate limiting data
"""

import json
import hashlib
import pickle
import asyncio
import time
import logging
import os
from typing import Any, Dict, Optional, Union, List, Callable
from dataclasses import dataclass
import redis.asyncio as redis
import structlog
from functools import wraps

from ..config.config_manager import ConfigManager

logger = structlog.get_logger(__name__)

@dataclass
class CacheConfig:
    """Configuration for Redis cache"""
    redis_url: str = None
    
    def __post_init__(self):
        if self.redis_url is None:
            config_manager = ConfigManager()
            # Use Consul discovery for Redis URL with fallback
            self.redis_url = config_manager.get_redis_url()
    default_ttl: int = 3600  # 1 hour
    model_cache_ttl: int = 3600  # 1 hour for model responses
    config_cache_ttl: int = 7200  # 2 hours for configurations
    session_cache_ttl: int = 86400  # 24 hours for sessions
    rate_limit_ttl: int = 3600  # 1 hour for rate limiting
    max_key_length: int = 250
    compression_enabled: bool = True
    serialization_method: str = "json"  # "json" or "pickle"

class RedisCache:
    """Redis-based cache with advanced features"""
    
    def __init__(self, config: CacheConfig):
        self.config = config
        self.redis_client = None
        self._connected = False
        self._stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0,
            "errors": 0
        }
        
    async def connect(self):
        """Connect to Redis"""
        try:
            self.redis_client = redis.from_url(
                self.config.redis_url,
                decode_responses=False,  # Handle binary data
                retry_on_timeout=True,
                health_check_interval=30
            )
            
            # Test connection
            await self.redis_client.ping()
            self._connected = True
            
            logger.info("Redis cache connected", url=self.config.redis_url)
            
        except Exception as e:
            logger.error("Failed to connect to Redis", error=str(e))
            self._connected = False
            raise
    
    async def disconnect(self):
        """Disconnect from Redis"""
        if self.redis_client:
            await self.redis_client.close()
            self._connected = False
            logger.info("Redis cache disconnected")
    
    def _generate_key(self, namespace: str, key: str) -> str:
        """Generate a cache key with namespace"""
        full_key = f"isa_model:{namespace}:{key}"
        
        # Hash long keys to avoid Redis key length limits
        if len(full_key) > self.config.max_key_length:
            hash_suffix = hashlib.md5(full_key.encode()).hexdigest()[:8]
            full_key = f"isa_model:{namespace}:hash_{hash_suffix}"
        
        return full_key
    
    def _serialize_value(self, value: Any) -> bytes:
        """Serialize value for storage"""
        try:
            if self.config.serialization_method == "pickle":
                return pickle.dumps(value)
            else:
                # JSON serialization
                json_str = json.dumps(value, default=str, ensure_ascii=False)
                return json_str.encode('utf-8')
        except Exception as e:
            logger.error("Serialization failed", error=str(e))
            raise
    
    def _deserialize_value(self, data: bytes) -> Any:
        """Deserialize value from storage"""
        try:
            if self.config.serialization_method == "pickle":
                return pickle.loads(data)
            else:
                # JSON deserialization
                json_str = data.decode('utf-8')
                return json.loads(json_str)
        except Exception as e:
            logger.error("Deserialization failed", error=str(e))
            raise
    
    async def get(self, namespace: str, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self._connected:
            return None
        
        try:
            cache_key = self._generate_key(namespace, key)
            data = await self.redis_client.get(cache_key)
            
            if data is None:
                self._stats["misses"] += 1
                return None
            
            value = self._deserialize_value(data)
            self._stats["hits"] += 1
            
            logger.debug("Cache hit", namespace=namespace, key=key)
            return value
            
        except Exception as e:
            self._stats["errors"] += 1
            logger.error("Cache get failed", namespace=namespace, key=key, error=str(e))
            return None
    
    async def set(
        self, 
        namespace: str, 
        key: str, 
        value: Any, 
        ttl: Optional[int] = None
    ) -> bool:
        """Set value in cache"""
        if not self._connected:
            return False
        
        try:
            cache_key = self._generate_key(namespace, key)
            serialized_value = self._serialize_value(value)
            
            # Use namespace-specific TTL if not provided
            if ttl is None:
                ttl = self._get_namespace_ttl(namespace)
            
            await self.redis_client.setex(cache_key, ttl, serialized_value)
            self._stats["sets"] += 1
            
            logger.debug("Cache set", namespace=namespace, key=key, ttl=ttl)
            return True
            
        except Exception as e:
            self._stats["errors"] += 1
            logger.error("Cache set failed", namespace=namespace, key=key, error=str(e))
            return False
    
    async def delete(self, namespace: str, key: str) -> bool:
        """Delete value from cache"""
        if not self._connected:
            return False
        
        try:
            cache_key = self._generate_key(namespace, key)
            result = await self.redis_client.delete(cache_key)
            self._stats["deletes"] += 1
            
            logger.debug("Cache delete", namespace=namespace, key=key, existed=bool(result))
            return bool(result)
            
        except Exception as e:
            self._stats["errors"] += 1
            logger.error("Cache delete failed", namespace=namespace, key=key, error=str(e))
            return False
    
    async def exists(self, namespace: str, key: str) -> bool:
        """Check if key exists in cache"""
        if not self._connected:
            return False
        
        try:
            cache_key = self._generate_key(namespace, key)
            return bool(await self.redis_client.exists(cache_key))
        except Exception as e:
            logger.error("Cache exists check failed", error=str(e))
            return False
    
    async def increment(self, namespace: str, key: str, amount: int = 1, ttl: Optional[int] = None) -> Optional[int]:
        """Increment a counter in cache"""
        if not self._connected:
            return None
        
        try:
            cache_key = self._generate_key(namespace, key)
            
            # Use pipeline for atomic operations
            pipe = self.redis_client.pipeline()
            pipe.incrby(cache_key, amount)
            
            if ttl:
                pipe.expire(cache_key, ttl)
            
            results = await pipe.execute()
            return results[0]
            
        except Exception as e:
            logger.error("Cache increment failed", error=str(e))
            return None
    
    async def clear_namespace(self, namespace: str) -> int:
        """Clear all keys in a namespace"""
        if not self._connected:
            return 0
        
        try:
            pattern = f"isa_model:{namespace}:*"
            keys = []
            
            # Use SCAN to avoid blocking Redis
            async for key in self.redis_client.scan_iter(pattern):
                keys.append(key)
            
            if keys:
                deleted = await self.redis_client.delete(*keys)
                logger.info("Namespace cleared", namespace=namespace, deleted_keys=deleted)
                return deleted
            
            return 0
            
        except Exception as e:
            logger.error("Cache namespace clear failed", namespace=namespace, error=str(e))
            return 0
    
    def _get_namespace_ttl(self, namespace: str) -> int:
        """Get TTL for a specific namespace"""
        ttl_mapping = {
            "models": self.config.model_cache_ttl,
            "config": self.config.config_cache_ttl,
            "sessions": self.config.session_cache_ttl,
            "rate_limit": self.config.rate_limit_ttl,
            "responses": self.config.model_cache_ttl,
        }
        return ttl_mapping.get(namespace, self.config.default_ttl)
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        stats = dict(self._stats)
        
        # Calculate hit rate
        total_requests = stats["hits"] + stats["misses"]
        stats["hit_rate"] = stats["hits"] / total_requests if total_requests > 0 else 0
        stats["connected"] = self._connected
        
        # Redis info if connected
        if self._connected:
            try:
                redis_info = await self.redis_client.info()
                stats["redis_info"] = {
                    "used_memory": redis_info.get("used_memory"),
                    "connected_clients": redis_info.get("connected_clients"),
                    "total_commands_processed": redis_info.get("total_commands_processed"),
                    "keyspace_hits": redis_info.get("keyspace_hits"),
                    "keyspace_misses": redis_info.get("keyspace_misses")
                }
            except Exception as e:
                logger.error("Failed to get Redis info", error=str(e))
        
        return stats

# Global cache instance
_cache: Optional[RedisCache] = None

async def get_cache() -> RedisCache:
    """Get the global cache instance"""
    global _cache
    
    if _cache is None:
        config_manager = ConfigManager()
        config = CacheConfig(
            redis_url=os.getenv("REDIS_URL", config_manager.get_redis_url()),
            default_ttl=int(os.getenv("CACHE_DEFAULT_TTL", "3600")),
            model_cache_ttl=int(os.getenv("MODEL_CACHE_TTL", "3600")),
            compression_enabled=os.getenv("CACHE_COMPRESSION", "true").lower() == "true"
        )
        _cache = RedisCache(config)
        await _cache.connect()
    
    return _cache

# Caching decorators
def cached_response(namespace: str = "responses", ttl: Optional[int] = None):
    """Decorator for caching function responses"""
    
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            cache_key = f"{func.__name__}:{hashlib.md5(str(args).encode() + str(kwargs).encode()).hexdigest()}"
            
            cache = await get_cache()
            
            # Try to get from cache first
            cached_result = await cache.get(namespace, cache_key)
            if cached_result is not None:
                logger.debug("Function result served from cache", function=func.__name__)
                return cached_result
            
            # Execute function and cache result
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            # Cache the result
            await cache.set(namespace, cache_key, result, ttl)
            logger.debug("Function result cached", function=func.__name__)
            
            return result
        
        return wrapper
    return decorator

def cached_model_response(ttl: Optional[int] = None):
    """Decorator specifically for model responses"""
    return cached_response(namespace="models", ttl=ttl)

# Specialized cache functions
async def cache_model_response(
    model_id: str,
    input_hash: str,
    response: Any,
    ttl: Optional[int] = None
):
    """Cache a model response"""
    cache = await get_cache()
    cache_key = f"{model_id}:{input_hash}"
    await cache.set("models", cache_key, response, ttl)

async def get_cached_model_response(
    model_id: str,
    input_hash: str
) -> Optional[Any]:
    """Get cached model response"""
    cache = await get_cache()
    cache_key = f"{model_id}:{input_hash}"
    return await cache.get("models", cache_key)

async def cache_user_session(user_id: str, session_data: Dict[str, Any]):
    """Cache user session data"""
    cache = await get_cache()
    await cache.set("sessions", user_id, session_data)

async def get_user_session(user_id: str) -> Optional[Dict[str, Any]]:
    """Get user session data"""
    cache = await get_cache()
    return await cache.get("sessions", user_id)

# Rate limiting cache functions
async def increment_rate_limit(key: str, window_seconds: int = 3600) -> int:
    """Increment rate limit counter"""
    cache = await get_cache()
    return await cache.increment("rate_limit", key, amount=1, ttl=window_seconds) or 0

async def get_rate_limit_count(key: str) -> int:
    """Get current rate limit count"""
    cache = await get_cache()
    count = await cache.get("rate_limit", key)
    return count or 0

# Health check
async def check_cache_health() -> Dict[str, Any]:
    """Check cache health"""
    try:
        cache = await get_cache()
        stats = await cache.get_stats()
        
        return {
            "cache": "redis",
            "status": "healthy" if stats["connected"] else "disconnected",
            "stats": stats
        }
    except Exception as e:
        return {
            "cache": "redis",
            "status": "error",
            "error": str(e)
        }