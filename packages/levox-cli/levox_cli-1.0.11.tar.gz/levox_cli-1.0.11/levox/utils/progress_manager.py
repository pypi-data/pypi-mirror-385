"""
Progress Manager for Levox CLI

Provides a unified interface for progress tracking using alive-progress.
Supports multiple progress types: repository cloning, file scanning, multi-stage detection.
"""

import time
import threading
from typing import Optional, Dict, Any, Callable, Union
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

try:
    from alive_progress import alive_bar, showtime, showspinner
    ALIVE_PROGRESS_AVAILABLE = True
except ImportError:
    ALIVE_PROGRESS_AVAILABLE = False
    # Optional Rich fallback
    try:
        from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
        RICH_AVAILABLE = True
    except Exception:
        RICH_AVAILABLE = False

from ..core.exceptions import LevoxException


class ProgressError(LevoxException):
    """Exception raised for progress-related errors."""
    pass


@dataclass
class ProgressInfo:
    """Information about current progress."""
    current: int = 0
    total: int = 0
    percentage: float = 0.0
    message: str = ""
    stage: str = ""
    findings_count: int = 0
    speed: Optional[float] = None  # items per second
    eta: Optional[float] = None  # estimated time remaining in seconds


class ProgressManager:
    """Manages progress bars for different Levox operations."""
    
    def __init__(self, quiet: bool = False, theme: str = 'smooth'):
        """
        Initialize the progress manager.
        
        Args:
            quiet: If True, suppress all progress output
            theme: Progress bar theme ('smooth', 'classic', 'ascii', 'dots', 'spinner')
        """
        self.quiet = quiet
        self.theme = theme
        self._current_bar = None
        self._bar_thread = None
        self._stop_event = threading.Event()
        
        if not ALIVE_PROGRESS_AVAILABLE and not quiet:
            if RICH_AVAILABLE:
                print("alive-progress not available. Using Rich progress fallback.")
            else:
                print("Warning: alive-progress not available. Progress bars disabled.")
    
    def _get_theme_config(self) -> Dict[str, Any]:
        """Get theme configuration for alive-progress."""
        themes = {
            'smooth': {'bar': 'smooth', 'spinner': 'dots_waves'},
            'classic': {'bar': 'classic', 'spinner': 'dots'},
            'ascii': {'bar': 'ascii', 'spinner': 'dots'},
            'dots': {'bar': 'dots', 'spinner': 'dots'},
            'spinner': {'bar': 'spinner', 'spinner': 'dots'}
        }
        return themes.get(self.theme, themes['smooth'])
    
    @contextmanager
    def repository_clone(self, repo_name: str, total_size: int = 0):
        """
        Context manager for repository cloning progress.
        
        Args:
            repo_name: Name of the repository being cloned
            total_size: Total size in bytes (0 if unknown)
        """
        if self.quiet:
            yield self._dummy_callback
            return
        if not ALIVE_PROGRESS_AVAILABLE and RICH_AVAILABLE:
            with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), BarColumn(), TimeElapsedColumn()) as progress:
                task = progress.add_task(f"Cloning {repo_name}", total=total_size if total_size > 0 else None)
                def progress_callback(progress_info: ProgressInfo):
                    if total_size > 0 and progress_info.current:
                        progress.update(task, completed=progress_info.current)
                    else:
                        progress.advance(task)
                yield progress_callback
            return
        
        theme_config = self._get_theme_config()
        
        with alive_bar(
            total=total_size if total_size > 0 else None,
            title=f'Cloning {repo_name}',
            bar=theme_config['bar'],
            spinner=theme_config['spinner'],
            dual_line=True,
            force_tty=True
        ) as bar:
            self._current_bar = bar
            
            def progress_callback(progress_info: ProgressInfo):
                if total_size > 0:
                    bar(progress_info.current)
                else:
                    bar()
                
                # Update sub-info with current status
                if progress_info.message:
                    bar.text = progress_info.message
                
                # Show speed and ETA if available
                if progress_info.speed:
                    speed_mb = progress_info.speed / (1024 * 1024)
                    bar.text = f"{progress_info.message} ({speed_mb:.1f} MB/s)"
                
                if progress_info.eta:
                    eta_str = self._format_eta(progress_info.eta)
                    bar.text = f"{progress_info.message} - ETA: {eta_str}"
            
            yield progress_callback
    
    @contextmanager
    def file_scanning(self, total_files: int, scan_type: str = "Scanning"):
        """
        Context manager for file scanning progress.
        
        Args:
            total_files: Total number of files to scan
            scan_type: Type of scan (e.g., "Scanning", "Analyzing")
        """
        if self.quiet:
            yield self._dummy_callback
            return
        if not ALIVE_PROGRESS_AVAILABLE and RICH_AVAILABLE:
            with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), BarColumn(), TimeElapsedColumn()) as progress:
                task = progress.add_task(f"{scan_type} files", total=total_files)
                def progress_callback(progress_info: ProgressInfo):
                    progress.update(task, completed=progress_info.current, description=f"{scan_type} files {progress_info.current}/{progress_info.total}")
                yield progress_callback
            return
        
        theme_config = self._get_theme_config()
        
        with alive_bar(
            total=total_files,
            title=f'{scan_type} files',
            bar=theme_config['bar'],
            spinner=theme_config['spinner'],
            dual_line=True,
            force_tty=True
        ) as bar:
            self._current_bar = bar
            
            def progress_callback(progress_info: ProgressInfo):
                bar(progress_info.current)
                
                # Show current file and stage
                file_info = f"File {progress_info.current}/{progress_info.total}"
                if progress_info.stage:
                    file_info += f" | {progress_info.stage}"
                
                bar.text = file_info
                
                # Show findings count if available
                if progress_info.findings_count > 0:
                    bar.text += f" | Found {progress_info.findings_count} potential matches"
            
            yield progress_callback
    
    @contextmanager
    def multi_stage_detection(self, stages: list):
        """
        Context manager for multi-stage detection progress.
        
        Args:
            stages: List of stage names (e.g., ['Regex', 'AST', 'Context', 'Dataflow', 'CFG', 'ML', 'GDPR'])
        """
        if self.quiet:
            yield self._dummy_callback
            return
        if not ALIVE_PROGRESS_AVAILABLE and RICH_AVAILABLE:
            with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), BarColumn(), TimeElapsedColumn()) as progress:
                task = progress.add_task("Detection Pipeline", total=len(stages))
                def progress_callback(progress_info: ProgressInfo):
                    progress.update(task, completed=progress_info.current, description=f"Stage {progress_info.current + 1}/{len(stages)}: {progress_info.stage}")
                yield progress_callback
            return
        
        theme_config = self._get_theme_config()
        
        with alive_bar(
            total=len(stages),
            title='Detection Pipeline',
            bar=theme_config['bar'],
            spinner=theme_config['spinner'],
            dual_line=True,
            force_tty=True
        ) as bar:
            self._current_bar = bar
            
            def progress_callback(progress_info: ProgressInfo):
                if progress_info.current > 0:
                    bar(progress_info.current)
                
                # Show current stage
                if progress_info.stage:
                    bar.text = f"Stage {progress_info.current + 1}/{len(stages)}: {progress_info.stage}"
                
                # Show findings from this stage
                if progress_info.findings_count > 0:
                    bar.text += f" | Found {progress_info.findings_count} matches"
                
                # Show message if provided
                if progress_info.message:
                    bar.text = f"{progress_info.stage}: {progress_info.message}"
            
            yield progress_callback
    
    @contextmanager
    def license_verification(self):
        """Context manager for license verification progress."""
        if self.quiet or not ALIVE_PROGRESS_AVAILABLE:
            yield self._dummy_callback
            return
        
        theme_config = self._get_theme_config()
        
        with alive_bar(
            title='Verifying license',
            bar=theme_config['bar'],
            spinner=theme_config['spinner'],
            force_tty=True
        ) as bar:
            self._current_bar = bar
            
            def progress_callback(progress_info: ProgressInfo):
                bar()
                if progress_info.message:
                    bar.text = progress_info.message
            
            yield progress_callback
    
    @contextmanager
    def ml_model_loading(self, model_name: str = "ML Model"):
        """Context manager for ML model loading progress."""
        if self.quiet or not ALIVE_PROGRESS_AVAILABLE:
            yield self._dummy_callback
            return
        
        theme_config = self._get_theme_config()
        
        with alive_bar(
            title=f'Loading {model_name}',
            bar=theme_config['bar'],
            spinner=theme_config['spinner'],
            force_tty=True
        ) as bar:
            self._current_bar = bar
            
            def progress_callback(progress_info: ProgressInfo):
                bar()
                if progress_info.message:
                    bar.text = progress_info.message
            
            yield progress_callback
    
    @contextmanager
    def report_generation(self, report_type: str = "Report"):
        """Context manager for report generation progress."""
        if self.quiet or not ALIVE_PROGRESS_AVAILABLE:
            yield self._dummy_callback
            return
        
        theme_config = self._get_theme_config()
        
        with alive_bar(
            title=f'Generating {report_type}',
            bar=theme_config['bar'],
            spinner=theme_config['spinner'],
            force_tty=True
        ) as bar:
            self._current_bar = bar
            
            def progress_callback(progress_info: ProgressInfo):
                bar()
                if progress_info.message:
                    bar.text = progress_info.message
            
            yield progress_callback
    
    def _dummy_callback(self, progress_info: ProgressInfo):
        """Dummy callback for when progress is disabled."""
        pass
    
    def _format_eta(self, eta_seconds: float) -> str:
        """Format ETA in a human-readable format."""
        if eta_seconds < 60:
            return f"{eta_seconds:.0f}s"
        elif eta_seconds < 3600:
            minutes = eta_seconds / 60
            return f"{minutes:.1f}m"
        else:
            hours = eta_seconds / 3600
            return f"{hours:.1f}h"
    
    def stop(self):
        """Stop the current progress bar."""
        if self._current_bar:
            self._stop_event.set()
    
    def is_active(self) -> bool:
        """Check if a progress bar is currently active."""
        return self._current_bar is not None


# Global progress manager instance
_global_progress_manager: Optional[ProgressManager] = None


def get_progress_manager(quiet: bool = False, theme: str = 'smooth') -> ProgressManager:
    """Get the global progress manager instance."""
    global _global_progress_manager
    if _global_progress_manager is None:
        _global_progress_manager = ProgressManager(quiet=quiet, theme=theme)
    return _global_progress_manager


def set_progress_manager(manager: ProgressManager):
    """Set the global progress manager instance."""
    global _global_progress_manager
    _global_progress_manager = manager


def reset_progress_manager():
    """Reset the global progress manager."""
    global _global_progress_manager
    _global_progress_manager = None
