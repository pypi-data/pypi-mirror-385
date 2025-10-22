"""
Simple cache manager for Levox components.

This module provides basic caching functionality for AST parsing and other
computationally expensive operations.
"""

import time
from typing import Any, Dict, Optional
from threading import Lock


class CacheManager:
    """Simple in-memory cache with TTL support."""
    
    def __init__(self, max_size: int = 1000):
        """Initialize cache with maximum size."""
        self.max_size = max_size
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.lock = Lock()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired."""
        with self.lock:
            if key not in self.cache:
                return None
            
            item = self.cache[key]
            if time.time() > item['expires_at']:
                del self.cache[key]
                return None
            
            return item['value']
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        """Set value in cache with TTL in seconds."""
        with self.lock:
            # Remove oldest items if cache is full
            if len(self.cache) >= self.max_size:
                oldest_key = min(self.cache.keys(), 
                               key=lambda k: self.cache[k]['expires_at'])
                del self.cache[oldest_key]
            
            self.cache[key] = {
                'value': value,
                'expires_at': time.time() + ttl
            }
    
    def clear(self) -> None:
        """Clear all cached items."""
        with self.lock:
            self.cache.clear()
    
    def size(self) -> int:
        """Get current cache size."""
        with self.lock:
            return len(self.cache)
    
    def cleanup_expired(self) -> int:
        """Remove expired items and return count removed."""
        current_time = time.time()
        removed_count = 0
        
        with self.lock:
            expired_keys = [
                key for key, item in self.cache.items()
                if current_time > item['expires_at']
            ]
            
            for key in expired_keys:
                del self.cache[key]
                removed_count += 1
        
        return removed_count
