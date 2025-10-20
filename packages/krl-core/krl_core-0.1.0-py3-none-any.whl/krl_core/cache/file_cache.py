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

"""File-based cache implementation."""

import hashlib
import os
import pickle
import time
from pathlib import Path
from threading import Lock
from typing import Any, Optional

from .base import Cache


class FileCache(Cache):
    """
    File-based cache with TTL support.
    
    Stores cached values as pickle files in a directory. Each cache entry
    includes metadata (creation time, TTL) for expiration handling.
    
    Thread-safe for concurrent access.
    
    Args:
        cache_dir: Directory to store cache files (default: ~/.krl_cache)
        default_ttl: Default time-to-live in seconds (None = no expiration)
        namespace: Optional namespace to prefix cache keys
    """

    def __init__(
        self,
        cache_dir: Optional[str] = None,
        default_ttl: Optional[int] = None,
        namespace: Optional[str] = None,
    ):
        self.cache_dir = Path(cache_dir or os.path.expanduser("~/.krl_cache"))
        self.default_ttl = default_ttl
        self.namespace = namespace or ""
        
        # Thread safety
        self._lock = Lock()
        
        # Statistics
        self._hits = 0
        self._misses = 0
        
        # Create cache directory
        self.cache_dir.mkdir(parents=True, exist_ok=True)

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

    def _key_to_filename(self, key: str) -> Path:
        """
        Convert cache key to filename.
        
        Uses SHA256 hash to handle special characters and long keys.
        
        Args:
            key: Cache key
            
        Returns:
            Path to cache file
        """
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        return self.cache_dir / f"{key_hash}.cache"

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
        cache_file = self._key_to_filename(namespaced_key)
        
        with self._lock:
            if not cache_file.exists():
                self._misses += 1
                return default
            
            try:
                with open(cache_file, "rb") as f:
                    data = pickle.load(f)
                
                # Check expiration
                if data["ttl"] is not None:
                    age = time.time() - data["timestamp"]
                    if age > data["ttl"]:
                        # Expired, delete file
                        cache_file.unlink()
                        self._misses += 1
                        return default
                
                self._hits += 1
                return data["value"]
                
            except Exception:
                # Corrupted cache file, delete it
                cache_file.unlink(missing_ok=True)
                self._misses += 1
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
        cache_file = self._key_to_filename(namespaced_key)
        
        # Use default TTL if not specified
        if ttl is None:
            ttl = self.default_ttl
        
        data = {
            "value": value,
            "timestamp": time.time(),
            "ttl": ttl,
            "key": namespaced_key,
        }
        
        with self._lock:
            try:
                with open(cache_file, "wb") as f:
                    pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
            except Exception as e:
                # Log error but don't raise (caching should be non-fatal)
                pass

    def delete(self, key: str) -> None:
        """
        Delete a key from the cache.
        
        Args:
            key: Cache key to delete
        """
        namespaced_key = self._make_key(key)
        cache_file = self._key_to_filename(namespaced_key)
        
        with self._lock:
            cache_file.unlink(missing_ok=True)

    def clear(self) -> None:
        """Clear all cache entries."""
        with self._lock:
            for cache_file in self.cache_dir.glob("*.cache"):
                cache_file.unlink(missing_ok=True)
            
            # Reset statistics
            self._hits = 0
            self._misses = 0

    def has(self, key: str) -> bool:
        """
        Check if a key exists in the cache (and is not expired).
        
        Args:
            key: Cache key to check
            
        Returns:
            True if key exists and is not expired, False otherwise
        """
        # Use get() and check if result is not the sentinel
        # This properly handles expiration checking
        sentinel = object()
        result = self.get(key, default=sentinel)
        return result is not sentinel

    def get_stats(self) -> dict:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = (self._hits / total_requests * 100) if total_requests > 0 else 0
            
            # Count cache files
            cache_files = list(self.cache_dir.glob("*.cache"))
            
            return {
                "hits": self._hits,
                "misses": self._misses,
                "total_requests": total_requests,
                "hit_rate": hit_rate,
                "cache_size": len(cache_files),
                "cache_dir": str(self.cache_dir),
            }

    def cleanup_expired(self) -> int:
        """
        Remove expired entries from the cache.
        
        Returns:
            Number of entries removed
        """
        removed = 0
        current_time = time.time()
        
        with self._lock:
            for cache_file in self.cache_dir.glob("*.cache"):
                try:
                    with open(cache_file, "rb") as f:
                        data = pickle.load(f)
                    
                    # Check if expired
                    if data["ttl"] is not None:
                        age = current_time - data["timestamp"]
                        if age > data["ttl"]:
                            cache_file.unlink()
                            removed += 1
                            
                except Exception:
                    # Corrupted file, remove it
                    cache_file.unlink(missing_ok=True)
                    removed += 1
        
        return removed

    def __repr__(self) -> str:
        """String representation."""
        stats = self.get_stats()
        return (
            f"FileCache(cache_dir='{self.cache_dir}', "
            f"size={stats['cache_size']}, "
            f"hit_rate={stats['hit_rate']:.1f}%)"
        )
