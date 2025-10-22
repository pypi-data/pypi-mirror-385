"""
Performance monitoring and metrics collection for Levox.
"""

import time
import psutil
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from collections import defaultdict, deque
import threading


@dataclass
class PerformanceMetric:
    """Individual performance metric."""
    operation: str
    duration: float
    count: int
    timestamp: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PerformanceStats:
    """Aggregated performance statistics."""
    total_operations: int
    total_duration: float
    average_duration: float
    min_duration: float
    max_duration: float
    operations_per_second: float
    last_operation: Optional[float] = None


class PerformanceMonitor:
    """Monitors and tracks performance metrics."""
    
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self.metrics: deque = deque(maxlen=max_history)
        self.stats: Dict[str, PerformanceStats] = defaultdict(
            lambda: PerformanceStats(0, 0.0, 0.0, float('inf'), 0.0, 0.0, None)
        )
        self.lock = threading.Lock()
        
        # System monitoring
        self.start_time = time.time()
        self.memory_samples: List[float] = []
        self.cpu_samples: List[float] = []
        
        # Start background monitoring
        self._start_background_monitoring()
    
    def record_operation(self, operation: str, duration: float, count: int = 1,
                        metadata: Optional[Dict[str, Any]] = None) -> None:
        """Record a performance metric."""
        if metadata is None:
            metadata = {}
        
        metric = PerformanceMetric(
            operation=operation,
            duration=duration,
            count=count,
            timestamp=time.time(),
            metadata=metadata
        )
        
        with self.lock:
            self.metrics.append(metric)
            self._update_stats(operation, duration, count)
    
    def _update_stats(self, operation: str, duration: float, count: int) -> None:
        """Update statistics for an operation."""
        stats = self.stats[operation]
        
        # Update basic stats
        stats.total_operations += count
        stats.total_duration += duration
        stats.last_operation = time.time()
        
        # Update min/max
        if duration < stats.min_duration:
            stats.min_duration = duration
        if duration > stats.max_duration:
            stats.max_duration = duration
        
        # Update averages
        if stats.total_operations > 0:
            stats.average_duration = stats.total_duration / stats.total_operations
        
        # Update operations per second (rolling window)
        if stats.last_operation and stats.last_operation > self.start_time:
            time_window = stats.last_operation - self.start_time
            if time_window > 0:
                stats.operations_per_second = stats.total_operations / time_window
    
    def get_stats(self, operation: Optional[str] = None) -> Dict[str, Any]:
        """Get performance statistics."""
        with self.lock:
            if operation:
                if operation in self.stats:
                    stats = self.stats[operation]
                    return {
                        'operation': operation,
                        'total_operations': stats.total_operations,
                        'total_duration': stats.total_duration,
                        'average_duration': stats.average_duration,
                        'min_duration': stats.min_duration,
                        'max_duration': stats.max_duration,
                        'operations_per_second': stats.operations_per_second,
                        'last_operation': stats.last_operation
                    }
                return {}
            
            # Return all stats
            return {
                op: {
                    'total_operations': stats.total_operations,
                    'total_duration': stats.total_duration,
                    'average_duration': stats.average_duration,
                    'min_duration': stats.min_duration,
                    'max_duration': stats.max_duration,
                    'operations_per_second': stats.operations_per_second,
                    'last_operation': stats.last_operation
                } for op, stats in self.stats.items()
            }
    
    def _stats_to_dict(self, stats: PerformanceStats) -> Dict[str, Any]:
        """Convert PerformanceStats to dictionary."""
        return {
            'total_operations': stats.total_operations,
            'total_duration': stats.total_duration,
            'average_duration': stats.average_duration,
            'min_duration': stats.min_duration,
            'max_duration': stats.max_duration,
            'operations_per_second': stats.operations_per_second,
            'last_operation': stats.last_operation
        }
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get current system resource usage."""
        try:
            process = psutil.Process()
            
            # Memory usage
            memory_info = process.memory_info()
            memory_percent = process.memory_percent()
            
            # CPU usage
            cpu_percent = process.cpu_percent()
            
            # System-wide stats
            system_memory = psutil.virtual_memory()
            system_cpu = psutil.cpu_percent(interval=0.1)
            
            return {
                'process': {
                    'memory_rss_mb': memory_info.rss / 1024 / 1024,
                    'memory_vms_mb': memory_info.vms / 1024 / 1024,
                    'memory_percent': memory_percent,
                    'cpu_percent': cpu_percent,
                    'num_threads': process.num_threads(),
                    'num_fds': getattr(process, 'num_fds', 0),  # Unix only
                },
                'system': {
                    'memory_total_gb': system_memory.total / 1024 / 1024 / 1024,
                    'memory_available_gb': system_memory.available / 1024 / 1024 / 1024,
                    'memory_percent': system_memory.percent,
                    'cpu_percent': system_cpu,
                },
                'uptime': time.time() - self.start_time
            }
        except Exception as e:
            return {'error': str(e)}
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get a comprehensive performance summary."""
        with self.lock:
            # Overall performance
            total_operations = sum(stats.total_operations for stats in self.stats.values())
            total_duration = sum(stats.total_duration for stats in self.stats.values())
            
            # Top operations by duration
            top_operations = sorted(
                self.stats.items(),
                key=lambda x: x[1].total_duration,
                reverse=True
            )[:5]
            
            # Recent metrics
            recent_metrics = list(self.metrics)[-10:] if self.metrics else []
            
            return {
                'summary': {
                    'total_operations': total_operations,
                    'total_duration': total_duration,
                    'average_duration': total_duration / total_operations if total_operations > 0 else 0,
                    'uptime': time.time() - self.start_time
                },
                'top_operations': [
                    {
                        'operation': op,
                        'total_duration': stats.total_duration,
                        'total_operations': stats.total_operations,
                        'average_duration': stats.average_duration
                    }
                    for op, stats in top_operations
                ],
                'recent_metrics': [
                    {
                        'operation': metric.operation,
                        'duration': metric.duration,
                        'timestamp': metric.timestamp,
                        'metadata': metric.metadata
                    }
                    for metric in recent_metrics
                ],
                'system_stats': self.get_system_stats()
            }
    
    def reset_stats(self, operation: Optional[str] = None) -> None:
        """Reset performance statistics."""
        with self.lock:
            if operation:
                if operation in self.stats:
                    del self.stats[operation]
            else:
                self.stats.clear()
                self.metrics.clear()
                self.start_time = time.time()
    
    def export_metrics(self, format: str = 'json') -> str:
        """Export metrics in specified format."""
        if format == 'json':
            import json
            return json.dumps(self.get_performance_summary(), indent=2, default=str)
        elif format == 'csv':
            return self._export_csv()
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _export_csv(self) -> str:
        """Export metrics as CSV."""
        import csv
        from io import StringIO
        
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['Operation', 'Duration', 'Count', 'Timestamp', 'Metadata'])
        
        # Write data
        with self.lock:
            for metric in self.metrics:
                writer.writerow([
                    metric.operation,
                    metric.duration,
                    metric.count,
                    metric.timestamp,
                    str(metric.metadata)
                ])
        
        return output.getvalue()
    
    def _start_background_monitoring(self) -> None:
        """Start background system monitoring."""
        def monitor_system():
            while True:
                try:
                    # Sample system metrics every 5 seconds
                    time.sleep(5)
                    
                    # Memory sample
                    process = psutil.Process()
                    memory_mb = process.memory_info().rss / 1024 / 1024
                    self.memory_samples.append(memory_mb)
                    
                    # Keep only last 100 samples
                    if len(self.memory_samples) > 100:
                        self.memory_samples = self.memory_samples[-100:]
                    
                    # CPU sample
                    cpu_percent = process.cpu_percent()
                    self.cpu_samples.append(cpu_percent)
                    
                    if len(self.cpu_samples) > 100:
                        self.cpu_samples = self.cpu_samples[-100:]
                        
                except Exception:
                    # Continue monitoring even if there are errors
                    pass
        
        # Start monitoring thread
        monitor_thread = threading.Thread(target=monitor_system, daemon=True)
        monitor_thread.start()
    
    def get_memory_trend(self) -> Dict[str, Any]:
        """Get memory usage trend."""
        if not self.memory_samples:
            return {'error': 'No memory samples available'}
        
        return {
            'current_mb': self.memory_samples[-1] if self.memory_samples else 0,
            'peak_mb': max(self.memory_samples) if self.memory_samples else 0,
            'average_mb': sum(self.memory_samples) / len(self.memory_samples) if self.memory_samples else 0,
            'samples': len(self.memory_samples),
            'trend': 'increasing' if len(self.memory_samples) > 1 and 
                     self.memory_samples[-1] > self.memory_samples[-2] else 'stable'
        }
    
    def get_cpu_trend(self) -> Dict[str, Any]:
        """Get CPU usage trend."""
        if not self.cpu_samples:
            return {'error': 'No CPU samples available'}
        
        return {
            'current_percent': self.cpu_samples[-1] if self.cpu_samples else 0,
            'peak_percent': max(self.cpu_samples) if self.cpu_samples else 0,
            'average_percent': sum(self.cpu_samples) / len(self.cpu_samples) if self.cpu_samples else 0,
            'samples': len(self.cpu_samples)
        }
    
    def check_performance_alerts(self) -> List[Dict[str, Any]]:
        """Check for performance alerts."""
        alerts = []
        
        with self.lock:
            # Check for slow operations
            for operation, stats in self.stats.items():
                if stats.average_duration > 1.0:  # More than 1 second
                    alerts.append({
                        'type': 'slow_operation',
                        'operation': operation,
                        'average_duration': stats.average_duration,
                        'severity': 'warning'
                    })
                
                if stats.average_duration > 5.0:  # More than 5 seconds
                    alerts.append({
                        'type': 'very_slow_operation',
                        'operation': operation,
                        'average_duration': stats.average_duration,
                        'severity': 'critical'
                    })
        
        # Check system resources
        system_stats = self.get_system_stats()
        if 'error' not in system_stats:
            process_memory = system_stats['process']['memory_percent']
            if process_memory > 80:
                alerts.append({
                    'type': 'high_memory_usage',
                    'memory_percent': process_memory,
                    'severity': 'warning'
                })
            
            if process_memory > 95:
                alerts.append({
                    'type': 'critical_memory_usage',
                    'memory_percent': process_memory,
                    'severity': 'critical'
                })
        
        return alerts


class HashBasedCache:
    """Hash-based cache for scanned results with TTL support."""
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        """
        Initialize the cache.
        
        Args:
            max_size: Maximum number of cached items
            default_ttl: Default time-to-live in seconds
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.access_times: Dict[str, float] = {}
        self.lock = threading.Lock()
    
    def _generate_hash(self, key_data: str) -> str:
        """Generate SHA-256 hash for cache key."""
        import hashlib
        return hashlib.sha256(key_data.encode('utf-8')).hexdigest()
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get item from cache."""
        with self.lock:
            if key in self.cache:
                item = self.cache[key]
                
                # Check TTL
                if time.time() > item.get('expires_at', 0):
                    # Expired, remove it
                    del self.cache[key]
                    del self.access_times[key]
                    return default
                
                # Update access time
                self.access_times[key] = time.time()
                return item.get('data')
            
            return default
    
    def set(self, key: str, data: Any, ttl: Optional[int] = None) -> None:
        """Set item in cache."""
        if ttl is None:
            ttl = self.default_ttl
        
        with self.lock:
            # Check if we need to evict items
            if len(self.cache) >= self.max_size:
                self._evict_oldest()
            
            # Add new item
            self.cache[key] = {
                'data': data,
                'expires_at': time.time() + ttl,
                'created_at': time.time()
            }
            self.access_times[key] = time.time()
    
    def _evict_oldest(self) -> None:
        """Evict oldest accessed items from cache."""
        if not self.access_times:
            return
        
        # Find oldest accessed item
        oldest_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
        
        # Remove it
        del self.cache[oldest_key]
        del self.access_times[oldest_key]
    
    def clear(self) -> None:
        """Clear all cached items."""
        with self.lock:
            self.cache.clear()
            self.access_times.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self.lock:
            current_time = time.time()
            expired_count = sum(1 for item in self.cache.values() 
                              if current_time > item.get('expires_at', 0))
            
            return {
                'total_items': len(self.cache),
                'expired_items': expired_count,
                'active_items': len(self.cache) - expired_count,
                'max_size': self.max_size,
                'utilization_percent': (len(self.cache) / self.max_size) * 100
            }
    
    def cleanup_expired(self) -> int:
        """Remove expired items and return count of removed items."""
        removed_count = 0
        current_time = time.time()
        
        with self.lock:
            expired_keys = [
                key for key, item in self.cache.items()
                if current_time > item.get('expires_at', 0)
            ]
            
            for key in expired_keys:
                del self.cache[key]
                if key in self.access_times:
                    del self.access_times[key]
                removed_count += 1
        
        return removed_count
