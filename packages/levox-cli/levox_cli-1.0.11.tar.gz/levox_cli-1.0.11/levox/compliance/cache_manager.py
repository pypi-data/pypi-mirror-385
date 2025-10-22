import logging
import time
import threading
from typing import Any, Optional, Callable, Dict, List, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import hashlib
import json
import pickle
from collections import OrderedDict

@dataclass
class CacheEntry:
    """Represents a single cache entry."""
    key: str
    value: Any
    created_at: datetime
    last_accessed: datetime
    access_count: int
    ttl_seconds: Optional[int] = None
    
    def is_expired(self) -> bool:
        """Check if the cache entry has expired."""
        if self.ttl_seconds is None:
            return False
        
        age = (datetime.now() - self.created_at).total_seconds()
        return age > self.ttl_seconds
    
    def update_access(self):
        """Update access statistics."""
        self.last_accessed = datetime.now()
        self.access_count += 1

class LRUCache:
    """
    Least Recently Used cache implementation with TTL support.
    """
    
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = threading.RLock()
        self.logger = logging.getLogger(__name__)
    
    def get(self, key: str) -> Optional[Any]:
        """Get a value from the cache."""
        with self._lock:
            if key not in self._cache:
                return None
            
            entry = self._cache[key]
            
            # Check if expired
            if entry.is_expired():
                del self._cache[key]
                return None
            
            # Update access
            entry.update_access()
            
            # Move to end (most recently used)
            self._cache.move_to_end(key)
            
            return entry.value
    
    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        """Set a value in the cache."""
        with self._lock:
            # Remove if already exists
            if key in self._cache:
                del self._cache[key]
            
            # Create new entry
            now = datetime.now()
            entry = CacheEntry(
                key=key,
                value=value,
                created_at=now,
                last_accessed=now,
                access_count=1,
                ttl_seconds=ttl_seconds
            )
            
            self._cache[key] = entry
            
            # Evict if over capacity
            while len(self._cache) > self.max_size:
                # Remove least recently used (first item)
                self._cache.popitem(last=False)
    
    def delete(self, key: str) -> bool:
        """Delete a key from the cache."""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False
    
    def clear(self) -> None:
        """Clear all entries from the cache."""
        with self._lock:
            self._cache.clear()
    
    def cleanup_expired(self) -> int:
        """Remove expired entries and return count of removed entries."""
        with self._lock:
            expired_keys = []
            for key, entry in self._cache.items():
                if entry.is_expired():
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self._cache[key]
            
            return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            if not self._cache:
                return {
                    'size': 0,
                    'max_size': self.max_size,
                    'hit_rate': 0.0,
                    'avg_access_count': 0.0,
                    'oldest_entry': None,
                    'newest_entry': None
                }
            
            total_access_count = sum(entry.access_count for entry in self._cache.values())
            avg_access_count = total_access_count / len(self._cache)
            
            oldest_entry = min(self._cache.values(), key=lambda e: e.created_at)
            newest_entry = max(self._cache.values(), key=lambda e: e.created_at)
            
            return {
                'size': len(self._cache),
                'max_size': self.max_size,
                'avg_access_count': avg_access_count,
                'oldest_entry': oldest_entry.created_at.isoformat(),
                'newest_entry': newest_entry.created_at.isoformat()
            }

class MultiLevelCache:
    """
    Multi-level cache with L1 (memory) and L2 (persistent) storage.
    """
    
    def __init__(self, l1_size: int = 1000, l2_enabled: bool = True, 
                 l2_path: Optional[str] = None):
        self.logger = logging.getLogger(__name__)
        
        # L1 Cache (in-memory)
        self.l1_cache = LRUCache(l1_size)
        
        # L2 Cache (persistent)
        self.l2_enabled = l2_enabled
        self.l2_cache: Optional[Dict[str, Any]] = None
        self.l2_path = l2_path
        self.l2_lock = threading.RLock()
        
        if l2_enabled:
            self._load_l2_cache()
        
        # Statistics
        self.stats = {
            'l1_hits': 0,
            'l2_hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0
        }
        self.stats_lock = threading.Lock()
    
    def _load_l2_cache(self):
        """Load L2 cache from persistent storage."""
        if not self.l2_path:
            return
        
        try:
            with open(self.l2_path, 'rb') as f:
                self.l2_cache = pickle.load(f)
            self.logger.info(f"Loaded L2 cache from {self.l2_path}")
        except FileNotFoundError:
            self.l2_cache = {}
            self.logger.info("L2 cache file not found, starting fresh")
        except Exception as e:
            self.logger.error(f"Failed to load L2 cache: {e}")
            self.l2_cache = {}
    
    def _save_l2_cache(self):
        """Save L2 cache to persistent storage."""
        if not self.l2_enabled or not self.l2_path:
            return
        
        try:
            with self.l2_lock:
                with open(self.l2_path, 'wb') as f:
                    pickle.dump(self.l2_cache, f)
        except Exception as e:
            self.logger.error(f"Failed to save L2 cache: {e}")
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from multi-level cache."""
        # Try L1 cache first
        value = self.l1_cache.get(key)
        if value is not None:
            with self.stats_lock:
                self.stats['l1_hits'] += 1
            return value
        
        # Try L2 cache
        if self.l2_enabled and self.l2_cache:
            with self.l2_lock:
                if key in self.l2_cache:
                    value = self.l2_cache[key]
                    # Promote to L1 cache
                    self.l1_cache.set(key, value)
                    with self.stats_lock:
                        self.stats['l2_hits'] += 1
                    return value
        
        # Cache miss
        with self.stats_lock:
            self.stats['misses'] += 1
        return None
    
    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        """Set value in multi-level cache."""
        # Set in L1 cache
        self.l1_cache.set(key, value, ttl_seconds)
        
        # Set in L2 cache
        if self.l2_enabled:
            with self.l2_lock:
                self.l2_cache[key] = value
                self._save_l2_cache()
        
        with self.stats_lock:
            self.stats['sets'] += 1
    
    def delete(self, key: str) -> bool:
        """Delete key from multi-level cache."""
        l1_deleted = self.l1_cache.delete(key)
        
        l2_deleted = False
        if self.l2_enabled and self.l2_cache:
            with self.l2_lock:
                if key in self.l2_cache:
                    del self.l2_cache[key]
                    l2_deleted = True
                    self._save_l2_cache()
        
        with self.stats_lock:
            self.stats['deletes'] += 1
        
        return l1_deleted or l2_deleted
    
    def clear(self) -> None:
        """Clear all caches."""
        self.l1_cache.clear()
        
        if self.l2_enabled:
            with self.l2_lock:
                self.l2_cache.clear()
                self._save_l2_cache()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics."""
        l1_stats = self.l1_cache.get_stats()
        
        with self.stats_lock:
            total_requests = self.stats['l1_hits'] + self.stats['l2_hits'] + self.stats['misses']
            hit_rate = (self.stats['l1_hits'] + self.stats['l2_hits']) / total_requests if total_requests > 0 else 0
        
        return {
            'l1_cache': l1_stats,
            'l2_enabled': self.l2_enabled,
            'l2_size': len(self.l2_cache) if self.l2_cache else 0,
            'hit_rate': hit_rate,
            'l1_hits': self.stats['l1_hits'],
            'l2_hits': self.stats['l2_hits'],
            'misses': self.stats['misses'],
            'sets': self.stats['sets'],
            'deletes': self.stats['deletes']
        }

class CacheManager:
    """
    High-level cache manager with automatic invalidation and smart caching.
    """
    
    def __init__(self, max_size: int = 1000, ttl_seconds: int = 300, 
                 l2_enabled: bool = True, l2_path: Optional[str] = None):
        self.logger = logging.getLogger(__name__)
        self.cache = MultiLevelCache(max_size, l2_enabled, l2_path)
        self.default_ttl = ttl_seconds
        
        # Invalidation patterns
        self.invalidation_patterns: Dict[str, List[str]] = {}
        
        # Background cleanup thread
        self.cleanup_thread = threading.Thread(target=self._cleanup_expired, daemon=True)
        self.cleanup_thread.start()
    
    def _generate_key(self, prefix: str, *args) -> str:
        """Generate a cache key from prefix and arguments."""
        key_data = f"{prefix}:{':'.join(str(arg) for arg in args)}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get_or_compute(self, key_prefix: str, compute_fn: Callable, 
                      *args, ttl_seconds: Optional[int] = None, **kwargs) -> Any:
        """
        Get value from cache or compute and cache it.
        
        Args:
            key_prefix: Prefix for cache key
            compute_fn: Function to compute value if not in cache
            *args: Arguments for compute function and cache key
            ttl_seconds: TTL for this specific entry
            **kwargs: Additional arguments for compute function
            
        Returns:
            Cached or computed value
        """
        cache_key = self._generate_key(key_prefix, *args)
        
        # Try to get from cache
        value = self.cache.get(cache_key)
        if value is not None:
            return value
        
        # Compute value
        try:
            value = compute_fn(*args, **kwargs)
            
            # Cache the result
            self.cache.set(cache_key, value, ttl_seconds or self.default_ttl)
            
            return value
            
        except Exception as e:
            self.logger.error(f"Failed to compute value for key {cache_key}: {e}")
            raise
    
    def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate all keys matching a pattern."""
        # This is a simplified implementation
        # In a real system, you might use Redis with pattern matching
        invalidated_count = 0
        
        # For now, we'll use a simple approach with stored patterns
        if pattern in self.invalidation_patterns:
            keys_to_invalidate = self.invalidation_patterns[pattern]
            for key in keys_to_invalidate:
                if self.cache.delete(key):
                    invalidated_count += 1
        
        return invalidated_count
    
    def register_invalidation_pattern(self, pattern: str, keys: List[str]):
        """Register keys that should be invalidated for a pattern."""
        self.invalidation_patterns[pattern] = keys
    
    def cache_scan_results(self, company_id: str, scan_id: str, results: Any) -> None:
        """Cache scan results with automatic invalidation."""
        cache_key = self._generate_key('scan_results', company_id, scan_id)
        self.cache.set(cache_key, results, self.default_ttl)
        
        # Register for invalidation when new scans are added
        pattern_key = f"company_scans:{company_id}"
        if pattern_key not in self.invalidation_patterns:
            self.invalidation_patterns[pattern_key] = []
        self.invalidation_patterns[pattern_key].append(cache_key)
    
    def cache_violations(self, company_id: str, scan_id: str, violations: List[Any]) -> None:
        """Cache violations with automatic invalidation."""
        cache_key = self._generate_key('violations', company_id, scan_id)
        self.cache.set(cache_key, violations, self.default_ttl)
        
        # Register for invalidation
        pattern_key = f"company_violations:{company_id}"
        if pattern_key not in self.invalidation_patterns:
            self.invalidation_patterns[pattern_key] = []
        self.invalidation_patterns[pattern_key].append(cache_key)
    
    def cache_compliance_metrics(self, company_id: str, metrics: Any) -> None:
        """Cache compliance metrics."""
        cache_key = self._generate_key('compliance_metrics', company_id)
        self.cache.set(cache_key, metrics, self.default_ttl)
    
    def invalidate_company_cache(self, company_id: str) -> int:
        """Invalidate all cache entries for a company."""
        invalidated_count = 0
        
        # Invalidate scan-related caches
        invalidated_count += self.invalidate_pattern(f"company_scans:{company_id}")
        invalidated_count += self.invalidate_pattern(f"company_violations:{company_id}")
        
        # Invalidate metrics cache
        metrics_key = self._generate_key('compliance_metrics', company_id)
        if self.cache.delete(metrics_key):
            invalidated_count += 1
        
        return invalidated_count
    
    def _cleanup_expired(self):
        """Background thread to cleanup expired entries."""
        while True:
            try:
                time.sleep(60)  # Run every minute
                expired_count = self.cache.l1_cache.cleanup_expired()
                if expired_count > 0:
                    self.logger.debug(f"Cleaned up {expired_count} expired cache entries")
            except Exception as e:
                self.logger.error(f"Error in cache cleanup thread: {e}")
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache performance statistics."""
        return self.cache.get_stats()
    
    def close(self):
        """Close the cache manager and cleanup resources."""
        if hasattr(self, 'cleanup_thread'):
            # In a real implementation, you'd signal the thread to stop
            pass
