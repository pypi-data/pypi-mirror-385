"""
Levox CI/CD Performance Optimizer

Provides performance optimization for CI/CD environments including
incremental scanning, intelligent caching, and memory optimization.
"""

import os
import json
import hashlib
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import logging

from ..core.config import Config, LicenseTier
from ..core.exceptions import LevoxException

logger = logging.getLogger(__name__)


class OptimizationLevel(str, Enum):
    """Optimization levels for CI/CD."""
    MINIMAL = "minimal"      # Basic optimizations
    BALANCED = "balanced"    # Standard optimizations
    AGGRESSIVE = "aggressive"  # Maximum optimizations


@dataclass
class OptimizationConfig:
    """Configuration for CI/CD optimizations."""
    level: OptimizationLevel = OptimizationLevel.BALANCED
    enable_incremental: bool = True
    enable_caching: bool = True
    enable_parallel: bool = True
    enable_memory_optimization: bool = True
    cache_ttl_hours: int = 24
    max_cache_size_mb: int = 500
    parallel_jobs: int = 4
    memory_limit_mb: int = 2048
    skip_unchanged_files: bool = True
    use_file_hashes: bool = True
    optimize_for_containers: bool = True


@dataclass
class ScanContext:
    """Context information for scan optimization."""
    repository_path: str
    branch_name: str
    commit_hash: str
    changed_files: List[str] = field(default_factory=list)
    last_scan_hash: Optional[str] = None
    cache_directory: Optional[str] = None
    is_ci_environment: bool = True


class CIOptimizer:
    """Optimizes Levox scanning for CI/CD environments."""
    
    def __init__(self, config: Config):
        self.config = config
        self.cache_dir = Path.home() / ".levox" / "cache"
        self._ensure_cache_dir()
    
    def _ensure_cache_dir(self):
        """Ensure cache directory exists."""
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def optimize_scan_command(self, base_command: List[str], optimization_config: OptimizationConfig, 
                            scan_context: ScanContext) -> List[str]:
        """
        Optimize scan command for CI/CD environment.
        
        Args:
            base_command: Base Levox scan command
            optimization_config: Optimization configuration
            scan_context: Scan context information
            
        Returns:
            Optimized scan command
        """
        try:
            optimized_command = base_command.copy()
            
            # Apply optimizations based on level
            if optimization_config.level == OptimizationLevel.MINIMAL:
                optimized_command = self._apply_minimal_optimizations(optimized_command, optimization_config)
            elif optimization_config.level == OptimizationLevel.BALANCED:
                optimized_command = self._apply_balanced_optimizations(optimized_command, optimization_config, scan_context)
            elif optimization_config.level == OptimizationLevel.AGGRESSIVE:
                optimized_command = self._apply_aggressive_optimizations(optimized_command, optimization_config, scan_context)
            
            # Apply common optimizations
            optimized_command = self._apply_common_optimizations(optimized_command, optimization_config, scan_context)
            
            return optimized_command
            
        except Exception as e:
            logger.error(f"Failed to optimize scan command: {e}")
            return base_command
    
    def get_incremental_scan_files(self, scan_context: ScanContext, 
                                 optimization_config: OptimizationConfig) -> List[str]:
        """
        Get list of files for incremental scanning.
        
        Args:
            scan_context: Scan context information
            optimization_config: Optimization configuration
            
        Returns:
            List of files to scan
        """
        try:
            if not optimization_config.enable_incremental:
                return []
            
            # Get changed files from git
            changed_files = self._get_git_changed_files(scan_context.repository_path)
            
            # Filter files based on optimization settings
            if optimization_config.skip_unchanged_files:
                changed_files = self._filter_changed_files(changed_files, scan_context)
            
            # Apply file size limits
            changed_files = self._apply_file_size_limits(changed_files, optimization_config)
            
            return changed_files
            
        except Exception as e:
            logger.error(f"Failed to get incremental scan files: {e}")
            return []
    
    def setup_caching(self, optimization_config: OptimizationConfig, 
                     scan_context: ScanContext) -> bool:
        """
        Setup caching for CI/CD environment.
        
        Args:
            optimization_config: Optimization configuration
            scan_context: Scan context information
            
        Returns:
            True if caching setup successful
        """
        try:
            if not optimization_config.enable_caching:
                return True
            
            # Create cache directory for this scan
            cache_path = self._get_cache_path(scan_context)
            cache_path.mkdir(parents=True, exist_ok=True)
            
            # Setup cache configuration
            cache_config = {
                "repository_path": scan_context.repository_path,
                "branch_name": scan_context.branch_name,
                "commit_hash": scan_context.commit_hash,
                "created_at": time.time(),
                "ttl_hours": optimization_config.cache_ttl_hours,
                "max_size_mb": optimization_config.max_cache_size_mb
            }
            
            config_file = cache_path / "cache_config.json"
            with open(config_file, 'w') as f:
                json.dump(cache_config, f, indent=2)
            
            # Clean old cache entries
            self._cleanup_old_cache()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup caching: {e}")
            return False
    
    def optimize_memory_usage(self, optimization_config: OptimizationConfig) -> Dict[str, Any]:
        """
        Get memory optimization settings.
        
        Args:
            optimization_config: Optimization configuration
            
        Returns:
            Memory optimization settings
        """
        try:
            memory_settings = {}
            
            if optimization_config.enable_memory_optimization:
                # Set memory limits
                memory_settings["max_memory_mb"] = optimization_config.memory_limit_mb
                
                # Optimize for containers
                if optimization_config.optimize_for_containers:
                    memory_settings["use_mmap"] = True
                    memory_settings["stream_processing"] = True
                    memory_settings["chunk_size_mb"] = min(64, optimization_config.memory_limit_mb // 4)
                
                # Parallel processing settings
                if optimization_config.enable_parallel:
                    memory_settings["parallel_jobs"] = min(
                        optimization_config.parallel_jobs,
                        optimization_config.memory_limit_mb // 512  # 512MB per job
                    )
                
                # File processing optimization
                memory_settings["max_file_size_mb"] = min(50, optimization_config.memory_limit_mb // 20)
                memory_settings["buffer_size_mb"] = min(16, optimization_config.memory_limit_mb // 32)
            
            return memory_settings
            
        except Exception as e:
            logger.error(f"Failed to optimize memory usage: {e}")
            return {}
    
    def get_scan_performance_metrics(self, scan_context: ScanContext) -> Dict[str, Any]:
        """
        Get performance metrics for scan optimization.
        
        Args:
            scan_context: Scan context information
            
        Returns:
            Performance metrics
        """
        try:
            metrics = {
                "repository_size_mb": self._get_repository_size(scan_context.repository_path),
                "file_count": self._get_file_count(scan_context.repository_path),
                "changed_files_count": len(scan_context.changed_files),
                "cache_hit_rate": self._get_cache_hit_rate(scan_context),
                "estimated_scan_time": self._estimate_scan_time(scan_context),
                "memory_usage_mb": self._get_current_memory_usage(),
                "cpu_cores": os.cpu_count() or 1
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to get performance metrics: {e}")
            return {}
    
    def _apply_minimal_optimizations(self, command: List[str], 
                                   optimization_config: OptimizationConfig) -> List[str]:
        """Apply minimal optimizations."""
        optimized = command.copy()
        
        # Add basic performance flags
        optimized.extend([
            "--max-file-size-mb", str(min(10, optimization_config.memory_limit_mb // 100)),
            "--verbosity", "summary"
        ])
        
        return optimized
    
    def _apply_balanced_optimizations(self, command: List[str], 
                                    optimization_config: OptimizationConfig,
                                    scan_context: ScanContext) -> List[str]:
        """Apply balanced optimizations."""
        optimized = command.copy()
        
        # Add performance flags
        optimized.extend([
            "--max-file-size-mb", str(min(25, optimization_config.memory_limit_mb // 50)),
            "--verbosity", "summary"
        ])
        
        # Add caching if enabled
        if optimization_config.enable_caching:
            cache_path = self._get_cache_path(scan_context)
            optimized.extend(["--cache-dir", str(cache_path)])
        
        # Add parallel processing
        if optimization_config.enable_parallel:
            optimized.extend(["--parallel-jobs", str(optimization_config.parallel_jobs)])
        
        return optimized
    
    def _apply_aggressive_optimizations(self, command: List[str], 
                                      optimization_config: OptimizationConfig,
                                      scan_context: ScanContext) -> List[str]:
        """Apply aggressive optimizations."""
        optimized = command.copy()
        
        # Add all performance flags
        optimized.extend([
            "--max-file-size-mb", str(min(50, optimization_config.memory_limit_mb // 20)),
            "--verbosity", "summary",
            "--stream-processing",
            "--memory-optimized"
        ])
        
        # Add caching
        if optimization_config.enable_caching:
            cache_path = self._get_cache_path(scan_context)
            optimized.extend(["--cache-dir", str(cache_path)])
        
        # Add parallel processing
        if optimization_config.enable_parallel:
            optimized.extend(["--parallel-jobs", str(optimization_config.parallel_jobs)])
        
        # Add incremental scanning
        if optimization_config.enable_incremental and scan_context.changed_files:
            file_list_path = self._create_file_list(scan_context.changed_files)
            optimized.extend(["--file-list", str(file_list_path)])
        
        return optimized
    
    def _apply_common_optimizations(self, command: List[str], 
                                  optimization_config: OptimizationConfig,
                                  scan_context: ScanContext) -> List[str]:
        """Apply common optimizations."""
        optimized = command.copy()
        
        # Add CI-specific flags
        if scan_context.is_ci_environment:
            optimized.extend([
                "--ci-mode",
                "--fail-fast"
            ])
        
        # Add memory optimization flags
        if optimization_config.enable_memory_optimization:
            optimized.extend([
                "--memory-limit-mb", str(optimization_config.memory_limit_mb)
            ])
        
        return optimized
    
    def _get_git_changed_files(self, repository_path: str) -> List[str]:
        """Get list of changed files from git."""
        try:
            import subprocess
            
            # Get changed files from last commit
            result = subprocess.run(
                ["git", "diff", "--name-only", "HEAD~1", "HEAD"],
                cwd=repository_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return [f.strip() for f in result.stdout.split('\n') if f.strip()]
            
            return []
            
        except Exception as e:
            logger.error(f"Failed to get git changed files: {e}")
            return []
    
    def _filter_changed_files(self, changed_files: List[str], 
                            scan_context: ScanContext) -> List[str]:
        """Filter changed files based on context."""
        try:
            # Filter out non-source files
            source_extensions = {'.py', '.js', '.ts', '.java', '.go', '.rs', '.cpp', '.c', '.h', 
                               '.php', '.rb', '.swift', '.kt', '.scala', '.clj', '.hs', '.ml', 
                               '.fs', '.vb', '.cs', '.dart', '.r', '.m', '.pl', '.sh', '.bash'}
            
            filtered_files = []
            for file_path in changed_files:
                if Path(file_path).suffix.lower() in source_extensions:
                    filtered_files.append(file_path)
            
            return filtered_files
            
        except Exception as e:
            logger.error(f"Failed to filter changed files: {e}")
            return changed_files
    
    def _apply_file_size_limits(self, files: List[str], 
                              optimization_config: OptimizationConfig) -> List[str]:
        """Apply file size limits to file list."""
        try:
            max_size_bytes = optimization_config.memory_limit_mb * 1024 * 1024
            filtered_files = []
            
            for file_path in files:
                try:
                    file_size = Path(file_path).stat().st_size
                    if file_size <= max_size_bytes:
                        filtered_files.append(file_path)
                except (OSError, FileNotFoundError):
                    continue
            
            return filtered_files
            
        except Exception as e:
            logger.error(f"Failed to apply file size limits: {e}")
            return files
    
    def _get_cache_path(self, scan_context: ScanContext) -> Path:
        """Get cache path for scan context."""
        # Create unique cache path based on repository and commit
        cache_key = hashlib.md5(
            f"{scan_context.repository_path}:{scan_context.commit_hash}".encode()
        ).hexdigest()[:8]
        
        return self.cache_dir / f"scan_{cache_key}"
    
    def _create_file_list(self, files: List[str]) -> Path:
        """Create temporary file list for incremental scanning."""
        temp_file = self.cache_dir / f"file_list_{int(time.time())}.txt"
        temp_file.write_text('\n'.join(files))
        return temp_file
    
    def _cleanup_old_cache(self):
        """Clean up old cache entries."""
        try:
            current_time = time.time()
            max_age_seconds = 7 * 24 * 3600  # 7 days
            
            for cache_dir in self.cache_dir.iterdir():
                if cache_dir.is_dir() and cache_dir.name.startswith("scan_"):
                    config_file = cache_dir / "cache_config.json"
                    if config_file.exists():
                        try:
                            with open(config_file, 'r') as f:
                                config = json.load(f)
                            
                            created_at = config.get("created_at", 0)
                            if current_time - created_at > max_age_seconds:
                                import shutil
                                shutil.rmtree(cache_dir)
                                logger.info(f"Cleaned up old cache: {cache_dir}")
                        except Exception:
                            # If config is corrupted, remove the cache
                            import shutil
                            shutil.rmtree(cache_dir)
                            
        except Exception as e:
            logger.error(f"Failed to cleanup old cache: {e}")
    
    def _get_repository_size(self, repository_path: str) -> float:
        """Get repository size in MB."""
        try:
            total_size = 0
            for file_path in Path(repository_path).rglob('*'):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
            
            return total_size / (1024 * 1024)  # Convert to MB
            
        except Exception as e:
            logger.error(f"Failed to get repository size: {e}")
            return 0.0
    
    def _get_file_count(self, repository_path: str) -> int:
        """Get total file count in repository."""
        try:
            count = 0
            for file_path in Path(repository_path).rglob('*'):
                if file_path.is_file():
                    count += 1
            
            return count
            
        except Exception as e:
            logger.error(f"Failed to get file count: {e}")
            return 0
    
    def _get_cache_hit_rate(self, scan_context: ScanContext) -> float:
        """Get cache hit rate for scan context."""
        try:
            cache_path = self._get_cache_path(scan_context)
            if cache_path.exists():
                return 1.0  # Cache exists
            return 0.0
            
        except Exception as e:
            logger.error(f"Failed to get cache hit rate: {e}")
            return 0.0
    
    def _estimate_scan_time(self, scan_context: ScanContext) -> float:
        """Estimate scan time in seconds."""
        try:
            # Simple estimation based on file count and repository size
            file_count = self._get_file_count(scan_context.repository_path)
            repo_size_mb = self._get_repository_size(scan_context.repository_path)
            
            # Rough estimation: 0.1 seconds per file + 0.01 seconds per MB
            estimated_time = (file_count * 0.1) + (repo_size_mb * 0.01)
            
            return min(estimated_time, 3600)  # Cap at 1 hour
            
        except Exception as e:
            logger.error(f"Failed to estimate scan time: {e}")
            return 300.0  # Default 5 minutes
    
    def _get_current_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss / (1024 * 1024)  # Convert to MB
            
        except ImportError:
            return 0.0
        except Exception as e:
            logger.error(f"Failed to get memory usage: {e}")
            return 0.0
    
    def get_optimization_recommendations(self, scan_context: ScanContext, 
                                       current_config: OptimizationConfig) -> List[str]:
        """Get optimization recommendations based on scan context."""
        recommendations = []
        
        try:
            metrics = self.get_scan_performance_metrics(scan_context)
            
            # Memory recommendations
            if metrics.get("memory_usage_mb", 0) > current_config.memory_limit_mb * 0.8:
                recommendations.append("Consider increasing memory limit or reducing parallel jobs")
            
            # File count recommendations
            if metrics.get("file_count", 0) > 10000:
                recommendations.append("Large repository detected - consider enabling incremental scanning")
            
            # Cache recommendations
            if metrics.get("cache_hit_rate", 0) < 0.5:
                recommendations.append("Low cache hit rate - consider adjusting cache TTL")
            
            # Time recommendations
            if metrics.get("estimated_scan_time", 0) > 600:
                recommendations.append("Long scan time expected - consider using quick scan profile")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Failed to get optimization recommendations: {e}")
            return []
