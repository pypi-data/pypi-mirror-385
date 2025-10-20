# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: MIT

# Copyright (c) 2025 KR-Labs Foundation. All rights reserved.
# Licensed under MIT License (see LICENSE file for details)
#
# This file is part of the KRL platform.
# For more information, visit: https://krlabs.dev
#
# KRL™ is a trademark of KR-Labs Foundation.

"""Redis-based cache implementation."""

import json
from typing import Any, Optional

from .base import Cache

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


class RedisCache(Cache):
    """
    Redis-based cache with TTL support.
    
    Stores cached values in Redis with automatic expiration.
    Values are JSON-serialized for compatibility.
    
    Requires redis package to be installed (optional dependency).
    
    Args:
        host: Redis host (default: localhost)
        port: Redis port (default: 6379)
        db: Redis database number (default: 0)
        password: Redis password (default: None)
        default_ttl: Default time-to-live in seconds (None = no expiration)
        namespace: Optional namespace to prefix cache keys
        decode_responses: Whether to decode responses as strings (default: True)
    
    Raises:
        ImportError: If redis package is not installed
        redis.ConnectionError: If cannot connect to Redis
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        default_ttl: Optional[int] = None,
        namespace: Optional[str] = None,
        decode_responses: bool = True,
    ):
        if not REDIS_AVAILABLE:
            raise ImportError(
                "Redis support requires the 'redis' package. "
                "Install it with: pip install krl-core[redis]"
            )
        
        self.default_ttl = default_ttl
        self.namespace = namespace or ""
        
        # Connect to Redis
        self.client = redis.Redis(
            host=host,
            port=port,
            db=db,
            password=password,
            decode_responses=decode_responses,
        )
        
        # Test connection
        try:
            self.client.ping()
        except redis.ConnectionError as e:
            raise redis.ConnectionError(
                f"Cannot connect to Redis at {host}:{port}: {e}"
            )
        
        # Statistics tracking (using Redis itself)
        self._stats_key = self._make_key("__stats__")

    def _make_key(self, key: str) -> str:
        """
        Create a namespaced cache key.
        
        Args:
            key: Original cache key
            
        Returns:
            Namespaced key
        """
        if self.namespace:
            return f"{self.namespace}:{key}"
        return key

    def _increment_stat(self, stat: str) -> None:
        """
        Increment a statistic counter.
        
        Args:
            stat: Statistic name ('hits' or 'misses')
        """
        self.client.hincrby(self._stats_key, stat, 1)

    def get(self, key: str, default: Optional[Any] = None) -> Optional[Any]:
        """
        Get a value from the cache.
        
        Args:
            key: Cache key
            default: Default value to return if key not found
            
        Returns:
            Cached value or default if not found/expired
        """
        namespaced_key = self._make_key(key)
        
        try:
            value = self.client.get(namespaced_key)
            
            if value is None:
                self._increment_stat("misses")
                return default
            
            self._increment_stat("hits")
            
            # Deserialize JSON
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                # Return raw value if not JSON
                return value
                
        except redis.RedisError:
            # Redis error, return default
            return default

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Set a value in the cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (None = use default_ttl)
        """
        namespaced_key = self._make_key(key)
        
        # Use default TTL if not specified
        if ttl is None:
            ttl = self.default_ttl
        
        try:
            # Serialize to JSON
            try:
                serialized = json.dumps(value)
            except (TypeError, ValueError):
                # Fallback to string representation
                serialized = str(value)
            
            # Set with TTL
            if ttl is not None:
                self.client.setex(namespaced_key, ttl, serialized)
            else:
                self.client.set(namespaced_key, serialized)
                
        except redis.RedisError:
            # Redis error, fail silently (caching should be non-fatal)
            pass

    def delete(self, key: str) -> None:
        """
        Delete a key from the cache.
        
        Args:
            key: Cache key to delete
        """
        namespaced_key = self._make_key(key)
        
        try:
            self.client.delete(namespaced_key)
        except redis.RedisError:
            pass

    def clear(self) -> None:
        """
        Clear all cache entries in the namespace.
        
        Note: This uses SCAN to find all keys with the namespace prefix,
        which is safe for production but may be slow for large datasets.
        """
        try:
            # Get all keys with namespace prefix
            pattern = f"{self.namespace}:*" if self.namespace else "*"
            
            # Use SCAN for safe iteration (doesn't block Redis)
            cursor = 0
            while True:
                cursor, keys = self.client.scan(cursor, match=pattern, count=100)
                
                if keys:
                    # Exclude stats key
                    keys_to_delete = [k for k in keys if k != self._stats_key]
                    if keys_to_delete:
                        self.client.delete(*keys_to_delete)
                
                if cursor == 0:
                    break
            
            # Reset statistics
            self.client.delete(self._stats_key)
            
        except redis.RedisError:
            pass

    def has(self, key: str) -> bool:
        """
        Check if a key exists in the cache.
        
        Args:
            key: Cache key to check
            
        Returns:
            True if key exists, False otherwise
        """
        namespaced_key = self._make_key(key)
        
        try:
            return bool(self.client.exists(namespaced_key))
        except redis.RedisError:
            return False

    def get_stats(self) -> dict:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        try:
            stats = self.client.hgetall(self._stats_key)
            
            hits = int(stats.get("hits", 0))
            misses = int(stats.get("misses", 0))
            total_requests = hits + misses
            hit_rate = (hits / total_requests * 100) if total_requests > 0 else 0
            
            # Get cache size (approximate)
            pattern = f"{self.namespace}:*" if self.namespace else "*"
            cache_size = 0
            cursor = 0
            while True:
                cursor, keys = self.client.scan(cursor, match=pattern, count=100)
                cache_size += len([k for k in keys if k != self._stats_key])
                if cursor == 0:
                    break
            
            return {
                "hits": hits,
                "misses": misses,
                "total_requests": total_requests,
                "hit_rate": hit_rate,
                "cache_size": cache_size,
                "backend": "redis",
            }
            
        except redis.RedisError:
            return {
                "hits": 0,
                "misses": 0,
                "total_requests": 0,
                "hit_rate": 0.0,
                "cache_size": 0,
                "backend": "redis",
                "error": "Cannot retrieve statistics",
            }

    def cleanup_expired(self) -> int:
        """
        Remove expired entries from the cache.
        
        Note: Redis automatically removes expired keys, so this is a no-op.
        
        Returns:
            0 (Redis handles expiration automatically)
        """
        # Redis handles expiration automatically via TTL
        return 0

    def __repr__(self) -> str:
        """String representation."""
        stats = self.get_stats()
        return (
            f"RedisCache(namespace='{self.namespace}', "
            f"size={stats['cache_size']}, "
            f"hit_rate={stats['hit_rate']:.1f}%)"
        )
