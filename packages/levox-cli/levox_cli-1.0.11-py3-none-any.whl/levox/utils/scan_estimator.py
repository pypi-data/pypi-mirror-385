"""
Scan Estimator for Levox CLI

Provides pre-scan estimation of duration, memory usage, and file counts
based on scan parameters and directory analysis.
"""

import os
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class ScanEstimation:
    """Results of scan estimation."""
    file_count: int
    estimated_duration: float  # seconds
    memory_usage_mb: float
    warnings: List[str]
    recommendations: List[str]
    scan_level: str  # basic, standard, advanced, enterprise


class ScanEstimator:
    """Estimates scan duration and resource requirements."""
    
    def __init__(self):
        """Initialize the scan estimator."""
        # Base performance metrics (per file)
        self.base_scan_time_per_file = 0.1  # seconds
        self.memory_per_file_mb = 0.5  # MB
        self.large_file_threshold_mb = 10
        
        # Scan level multipliers
        self.scan_levels = {
            'basic': {'time_multiplier': 1.0, 'memory_multiplier': 1.0},
            'standard': {'time_multiplier': 2.0, 'memory_multiplier': 1.5},
            'advanced': {'time_multiplier': 4.0, 'memory_multiplier': 2.0},
            'enterprise': {'time_multiplier': 6.0, 'memory_multiplier': 3.0}
        }
    
    def estimate_scan(self, scan_path: str, options: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Estimate scan requirements for a given path and options.
        
        Args:
            scan_path: Path to scan
            options: Scan options dictionary
            
        Returns:
            Dictionary with estimation results or None if estimation fails
        """
        try:
            path_obj = Path(scan_path)
            
            # Count files and analyze directory
            file_count, large_files, total_size_mb = self._analyze_directory(path_obj, options)
            
            if file_count == 0:
                return {
                    'file_count': 0,
                    'duration': 0.0,
                    'memory_mb': 0.0,
                    'warnings': ['No files found to scan'],
                    'recommendations': ['Check if path exists and contains scannable files']
                }
            
            # Determine scan level
            scan_level = self._determine_scan_level(options)
            
            # Calculate estimates
            duration = self._estimate_duration(file_count, large_files, scan_level, options)
            memory_mb = self._estimate_memory(file_count, large_files, scan_level, options)
            
            # Generate warnings and recommendations
            warnings = self._generate_warnings(file_count, large_files, total_size_mb, options)
            recommendations = self._generate_recommendations(file_count, large_files, scan_level, options)
            
            return {
                'file_count': file_count,
                'duration': duration,
                'memory_mb': memory_mb,
                'warnings': warnings,
                'recommendations': recommendations,
                'scan_level': scan_level,
                'large_files': large_files,
                'total_size_mb': total_size_mb
            }
            
        except Exception:
            return None
    
    def _analyze_directory(self, path: Path, options: Dict[str, Any]) -> tuple:
        """Analyze directory structure and file characteristics."""
        file_count = 0
        large_files = 0
        total_size_mb = 0.0
        
        # Get include patterns
        include_patterns = options.get('include_patterns', ['*.py', '*.js', '*.ts', '*.java'])
        exclude_patterns = options.get('exclude_patterns', [])
        
        # Get file size limit
        max_file_size_mb = options.get('max_file_size_mb', 100)
        
        try:
            for file_path in path.rglob('*'):
                if not file_path.is_file():
                    continue
                
                # Check if file matches include patterns
                if not self._matches_patterns(file_path, include_patterns):
                    continue
                
                # Check if file matches exclude patterns
                if self._matches_patterns(file_path, exclude_patterns):
                    continue
                
                # Check file size
                try:
                    file_size_mb = file_path.stat().st_size / (1024 * 1024)
                    total_size_mb += file_size_mb
                    
                    if file_size_mb > max_file_size_mb:
                        continue  # Skip files that exceed size limit
                    
                    file_count += 1
                    
                    if file_size_mb > self.large_file_threshold_mb:
                        large_files += 1
                        
                except (OSError, PermissionError):
                    continue
                    
        except (OSError, PermissionError):
            pass
        
        return file_count, large_files, total_size_mb
    
    def _matches_patterns(self, file_path: Path, patterns: List[str]) -> bool:
        """Check if file matches any of the given patterns."""
        if not patterns:
            return True
        
        import fnmatch
        
        for pattern in patterns:
            if fnmatch.fnmatch(str(file_path), pattern):
                return True
            if fnmatch.fnmatch(file_path.name, pattern):
                return True
        
        return False
    
    def _determine_scan_level(self, options: Dict[str, Any]) -> str:
        """Determine the scan level based on options."""
        if options.get('cfg_enabled', False):
            return 'enterprise'
        elif options.get('scan_optional', False):
            return 'advanced'
        else:
            return 'standard'
    
    def _estimate_duration(self, file_count: int, large_files: int, scan_level: str, options: Dict[str, Any]) -> float:
        """Estimate scan duration in seconds."""
        level_config = self.scan_levels[scan_level]
        base_time = file_count * self.base_scan_time_per_file * level_config['time_multiplier']
        
        # Add extra time for large files
        large_file_penalty = large_files * 2.0  # 2 seconds per large file
        
        # Add time for different scan types
        if options.get('cfg_enabled', False):
            base_time *= 1.5  # CFG analysis is slower
        
        if options.get('scan_optional', False):
            base_time *= 1.2  # Optional files add overhead
        
        return base_time + large_file_penalty
    
    def _estimate_memory(self, file_count: int, large_files: int, scan_level: str, options: Dict[str, Any]) -> float:
        """Estimate memory usage in MB."""
        level_config = self.scan_levels[scan_level]
        base_memory = file_count * self.memory_per_file_mb * level_config['memory_multiplier']
        
        # Add extra memory for large files
        large_file_memory = large_files * 5.0  # 5 MB per large file
        
        # Add memory for different scan types
        if options.get('cfg_enabled', False):
            base_memory *= 1.5  # CFG analysis uses more memory
        
        return base_memory + large_file_memory
    
    def _generate_warnings(self, file_count: int, large_files: int, total_size_mb: float, options: Dict[str, Any]) -> List[str]:
        """Generate warnings based on scan characteristics."""
        warnings = []
        
        if file_count > 10000:
            warnings.append(f"Large number of files ({file_count:,}) - consider using --exclude patterns")
        
        if large_files > 100:
            warnings.append(f"Many large files ({large_files}) - scan may be slow")
        
        if total_size_mb > 1000:
            warnings.append(f"Large total size ({total_size_mb:.1f} MB) - consider incremental scanning")
        
        if file_count > 5000 and not options.get('cfg_enabled', False):
            warnings.append("Consider using --cfg for better detection on large codebases")
        
        return warnings
    
    def _generate_recommendations(self, file_count: int, large_files: int, scan_level: str, options: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on scan characteristics."""
        recommendations = []
        
        if file_count > 1000:
            recommendations.append("Use --exclude 'node_modules' 'venv' '__pycache__' to skip dependencies")
        
        if large_files > 50:
            recommendations.append("Consider using --max-file-size-mb 50 to limit large files")
        
        if file_count > 5000:
            recommendations.append("Use --max-workers 2 to reduce memory usage")
        
        if scan_level == 'enterprise' and file_count > 2000:
            recommendations.append("Consider using incremental scanning for large repositories")
        
        if not options.get('exclude_patterns'):
            recommendations.append("Add common exclusions: --exclude '*.log' '*.tmp' '*.cache'")
        
        return recommendations
    
    def get_scan_suggestions(self, scan_path: str) -> Dict[str, Any]:
        """Get scan suggestions for a specific path."""
        try:
            path_obj = Path(scan_path)
            
            # Basic analysis
            file_count, large_files, total_size_mb = self._analyze_directory(path_obj, {})
            
            suggestions = {
                'recommended_workers': min(4, max(1, file_count // 1000)),
                'suggest_incremental': file_count > 5000,
                'suggest_shallow': total_size_mb > 500,
                'recommended_timeout': max(300, file_count * 0.1),
                'memory_warning': total_size_mb > 1000
            }
            
            return suggestions
            
        except Exception:
            return {
                'recommended_workers': 2,
                'suggest_incremental': False,
                'suggest_shallow': False,
                'recommended_timeout': 300,
                'memory_warning': False
            }
