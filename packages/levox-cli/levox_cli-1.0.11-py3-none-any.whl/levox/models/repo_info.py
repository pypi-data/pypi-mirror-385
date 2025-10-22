"""
Repository information models for Git repository scanning.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict, Any, List
from pathlib import Path
import tempfile


class GitPlatform(Enum):
    """Supported Git platforms."""
    GITHUB = "github"
    GITLAB = "gitlab"
    BITBUCKET = "bitbucket"
    UNKNOWN = "unknown"


class CloneStrategy(Enum):
    """Repository cloning strategies."""
    FULL = "full"           # Complete clone with full history
    SHALLOW = "shallow"      # Clone with depth=1 (latest commit only)
    SPARSE = "sparse"        # Sparse checkout of scannable files only
    STREAMING = "streaming"  # Stream files without full clone (for very large repos)


class RepoVisibility(Enum):
    """Repository visibility levels."""
    PUBLIC = "public"
    PRIVATE = "private"
    UNKNOWN = "unknown"


@dataclass
class RepoCredentials:
    """Repository authentication credentials."""
    platform: GitPlatform
    token: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    
    def is_valid(self) -> bool:
        """Check if credentials are valid."""
        return bool(self.token or (self.username and self.password))


@dataclass
class RepoMetadata:
    """Repository metadata information."""
    platform: GitPlatform
    owner: str
    repo_name: str
    full_name: str
    url: str
    visibility: RepoVisibility
    size_bytes: int
    default_branch: str
    file_count: int
    language: Optional[str] = None
    description: Optional[str] = None
    
    @property
    def size_mb(self) -> float:
        """Get repository size in MB."""
        return self.size_bytes / (1024 * 1024)
    
    @property
    def size_gb(self) -> float:
        """Get repository size in GB."""
        return self.size_bytes / (1024 * 1024 * 1024)


@dataclass
class ClonedRepo:
    """Information about a cloned repository."""
    metadata: RepoMetadata
    local_path: Path
    clone_strategy: CloneStrategy
    clone_time: float
    temp_directory: bool = True
    
    def cleanup(self) -> bool:
        """Clean up the cloned repository."""
        try:
            import shutil
            import logging
            import time
            import os
            import stat
            
            if not self.local_path.exists():
                # Directory doesn't exist, consider it already cleaned up
                return True
                
            # On Windows, Git files might be locked, so we need to handle this specially
            if os.name == 'nt':  # Windows
                # Try to make files writable first
                for root, dirs, files in os.walk(self.local_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        try:
                            os.chmod(file_path, stat.S_IWRITE)
                        except (OSError, PermissionError):
                            pass
                
                # Give a small delay for file handles to be released
                time.sleep(0.1)
                
                # Try multiple times with increasing delays for Windows file locking issues
                max_attempts = 3
                for attempt in range(max_attempts):
                    try:
                        shutil.rmtree(self.local_path)
                        break
                    except (PermissionError, OSError) as e:
                        if attempt < max_attempts - 1:
                            logging.warning(f"Cleanup attempt {attempt + 1} failed, retrying: {e}")
                            time.sleep(0.5 * (attempt + 1))  # Increasing delay
                        else:
                            raise e
            else:
                # Non-Windows systems
                shutil.rmtree(self.local_path)
            
            # Verify it was actually removed
            if self.local_path.exists():
                logging.warning(f"Directory still exists after cleanup attempt: {self.local_path}")
                return False
                
            return True
            
        except PermissionError as e:
            logging.error(f"Permission denied when cleaning up repository: {self.local_path} - {e}")
            return False
        except OSError as e:
            logging.error(f"OS error when cleaning up repository: {self.local_path} - {e}")
            return False
        except Exception as e:
            logging.error(f"Unexpected error when cleaning up repository: {self.local_path} - {e}")
            return False


@dataclass
class CloneProgress:
    """Progress information for repository cloning."""
    stage: str  # "fetching", "checking_out", "scanning"
    progress_percent: float
    message: str
    bytes_downloaded: int = 0
    total_bytes: int = 0
    
    @property
    def download_progress_percent(self) -> float:
        """Get download progress as percentage."""
        if self.total_bytes == 0:
            return 0.0
        return (self.bytes_downloaded / self.total_bytes) * 100


@dataclass
class RepoScanResult:
    """Result of scanning a repository."""
    cloned_repo: ClonedRepo
    scan_results: Any  # DetectionResult from the engine
    scan_time: float
    files_scanned: int
    violations_found: int
    cleanup_prompted: bool = False
    cleanup_choice: Optional[str] = None  # "keep", "delete", "always", "never"


class RepoConfig:
    """Configuration for repository scanning."""
    
    def __init__(self):
        self.auto_cleanup: bool = False
        self.clone_timeout_seconds: int = 300
        self.max_repo_size_mb: int = 5000  # 5GB limit
        self.prefer_shallow_clone: bool = True
        self.temp_clone_directory: Optional[str] = None
        self.repo_cache_enabled: bool = False
        self.repo_cache_ttl_hours: int = 24
        
        # Clone strategy thresholds
        self.small_repo_threshold_mb: int = 100
        self.medium_repo_threshold_mb: int = 1000
        self.large_repo_threshold_mb: int = 5000
    
    def get_clone_strategy(self, repo_size_mb: float) -> CloneStrategy:
        """Determine the best clone strategy based on repository size."""
        if repo_size_mb <= self.small_repo_threshold_mb:
            return CloneStrategy.FULL
        elif repo_size_mb <= self.medium_repo_threshold_mb:
            return CloneStrategy.SHALLOW
        elif repo_size_mb <= self.large_repo_threshold_mb:
            return CloneStrategy.SPARSE
        else:
            return CloneStrategy.STREAMING
    
    def get_temp_directory(self) -> Path:
        """Get the temporary directory for cloning."""
        if self.temp_clone_directory:
            temp_dir = Path(self.temp_clone_directory)
            temp_dir.mkdir(parents=True, exist_ok=True)
            return temp_dir
        else:
            return Path(tempfile.gettempdir()) / "levox_repos"
