"""
Git repository scanner with smart cloning strategies for GitHub, GitLab, and Bitbucket.
"""

import os
import re
import time
import logging
import tempfile
import subprocess
from pathlib import Path
from typing import Optional, Tuple, Dict, Any, Iterator, List
from urllib.parse import urlparse
import shutil

try:
    import git
    GIT_PYTHON_AVAILABLE = True
except ImportError:
    GIT_PYTHON_AVAILABLE = False

try:
    from github import Github
    GITHUB_API_AVAILABLE = True
except ImportError:
    GITHUB_API_AVAILABLE = False

try:
    import gitlab
    GITLAB_API_AVAILABLE = True
except ImportError:
    GITLAB_API_AVAILABLE = False

from ..models.repo_info import (
    GitPlatform, CloneStrategy, RepoVisibility, RepoCredentials,
    RepoMetadata, ClonedRepo, CloneProgress, RepoConfig
)
from ..utils.progress_manager import ProgressManager, ProgressInfo


class RepoScannerError(Exception):
    """Exception raised for repository scanning errors."""
    pass


class GitRepoScanner:
    """Smart Git repository scanner with support for multiple platforms."""
    
    def __init__(self, config: Optional[RepoConfig] = None):
        """Initialize the repository scanner."""
        self.logger = logging.getLogger(__name__)
        self.config = config or RepoConfig()
        
        # Initialize API clients
        self.github_client = None
        self.gitlab_client = None
        
        self._init_api_clients()
    
    def _init_api_clients(self):
        """Initialize API clients for repository metadata."""
        # GitHub client
        if GITHUB_API_AVAILABLE:
            github_token = os.getenv('GITHUB_TOKEN')
            if github_token:
                self.github_client = Github(github_token)
        
        # GitLab client
        if GITLAB_API_AVAILABLE:
            gitlab_token = os.getenv('GITLAB_TOKEN')
            if gitlab_token:
                self.gitlab_client = gitlab.Gitlab(token=gitlab_token)
    
    def validate_repo_url(self, url: str) -> Tuple[GitPlatform, str, str]:
        """
        Validate and parse a Git repository URL.
        
        Returns:
            Tuple of (platform, owner, repo_name)
        """
        # Clean up the URL
        url = url.strip()
        if url.endswith('.git'):
            url = url[:-4]
        
        # Parse the URL
        parsed = urlparse(url)
        
        if not parsed.scheme or not parsed.netloc:
            raise RepoScannerError(f"Invalid URL format: {url}")
        
        # Extract platform, owner, and repo from path
        path_parts = parsed.path.strip('/').split('/')
        if len(path_parts) < 2:
            raise RepoScannerError(f"Invalid repository path: {parsed.path}")
        
        owner = path_parts[0]
        repo_name = path_parts[1]
        
        # Determine platform
        hostname = parsed.netloc.lower()
        if 'github.com' in hostname:
            platform = GitPlatform.GITHUB
        elif 'gitlab.com' in hostname or 'gitlab.' in hostname:
            platform = GitPlatform.GITLAB
        elif 'bitbucket.org' in hostname:
            platform = GitPlatform.BITBUCKET
        else:
            raise RepoScannerError(f"Unsupported Git platform: {hostname}")
        
        return platform, owner, repo_name
    
    def estimate_repo_size(self, url: str) -> int:
        """
        Estimate repository size using platform APIs.
        
        Returns:
            Repository size in bytes
        """
        try:
            platform, owner, repo_name = self.validate_repo_url(url)
            
            if platform == GitPlatform.GITHUB and self.github_client:
                return self._get_github_repo_size(owner, repo_name)
            elif platform == GitPlatform.GITLAB and self.gitlab_client:
                return self._get_gitlab_repo_size(owner, repo_name)
            elif platform == GitPlatform.BITBUCKET:
                return self._get_bitbucket_repo_size(owner, repo_name)
            else:
                # Fallback: assume medium size
                return 100 * 1024 * 1024  # 100MB
                
        except Exception as e:
            self.logger.warning(f"Could not estimate repo size: {e}")
            return 100 * 1024 * 1024  # Default to 100MB
    
    def _get_github_repo_size(self, owner: str, repo_name: str) -> int:
        """Get GitHub repository size."""
        try:
            repo = self.github_client.get_repo(f"{owner}/{repo_name}")
            # GitHub API doesn't provide exact size, estimate from clone size
            return repo.size * 1024  # Convert KB to bytes
        except Exception as e:
            self.logger.warning(f"GitHub API error: {e}")
            return 100 * 1024 * 1024
    
    def _get_gitlab_repo_size(self, owner: str, repo_name: str) -> int:
        """Get GitLab repository size."""
        try:
            projects = self.gitlab_client.projects.list(search=repo_name, owned=True)
            for project in projects:
                if project.name == repo_name and project.namespace['name'] == owner:
                    return project.statistics.get('repository_size', 0)
            return 100 * 1024 * 1024
        except Exception as e:
            self.logger.warning(f"GitLab API error: {e}")
            return 100 * 1024 * 1024
    
    def _get_bitbucket_repo_size(self, owner: str, repo_name: str) -> int:
        """Get Bitbucket repository size (API not easily accessible)."""
        # Bitbucket API requires authentication and is more complex
        # For now, return a default estimate
        return 100 * 1024 * 1024
    
    def get_repo_metadata(self, url: str) -> RepoMetadata:
        """Get comprehensive repository metadata."""
        platform, owner, repo_name = self.validate_repo_url(url)
        full_name = f"{owner}/{repo_name}"
        size_bytes = self.estimate_repo_size(url)
        
        # Determine visibility (simplified - assume public if no auth errors)
        visibility = RepoVisibility.PUBLIC
        
        return RepoMetadata(
            platform=platform,
            owner=owner,
            repo_name=repo_name,
            full_name=full_name,
            url=url,
            visibility=visibility,
            size_bytes=size_bytes,
            default_branch="main",  # Most repos use main now
            file_count=0,  # Would need API call to get exact count
            language=None,
            description=None
        )
    
    def get_credentials(self, platform: GitPlatform) -> Optional[RepoCredentials]:
        """Get credentials for the specified platform."""
        if platform == GitPlatform.GITHUB:
            token = os.getenv('GITHUB_TOKEN')
            if token:
                return RepoCredentials(platform=platform, token=token)
        elif platform == GitPlatform.GITLAB:
            token = os.getenv('GITLAB_TOKEN')
            if token:
                return RepoCredentials(platform=platform, token=token)
        elif platform == GitPlatform.BITBUCKET:
            token = os.getenv('BITBUCKET_TOKEN')
            if token:
                return RepoCredentials(platform=platform, token=token)
        
        return None
    
    def select_clone_strategy(self, repo_size_mb: float) -> CloneStrategy:
        """Select the best clone strategy based on repository size."""
        return self.config.get_clone_strategy(repo_size_mb)
    
    def clone_with_strategy(self, url: str, strategy: CloneStrategy, 
                          progress_callback: Optional[callable] = None) -> ClonedRepo:
        """
        Clone repository using the specified strategy.
        
        Args:
            url: Repository URL
            strategy: Clone strategy to use
            progress_callback: Optional callback for progress updates
            
        Returns:
            ClonedRepo object with metadata
        """
        metadata = self.get_repo_metadata(url)
        
        # Create temporary directory
        temp_dir = self.config.get_temp_directory()
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        repo_dir = temp_dir / f"levox_repo_{int(time.time())}_{metadata.repo_name}"
        
        start_time = time.time()
        
        try:
            # Use progress manager for better visual feedback
            progress_manager = ProgressManager(quiet=False, theme='smooth')
            
            with progress_manager.repository_clone(metadata.repo_name, metadata.size_bytes) as progress_cb:
                if strategy == CloneStrategy.FULL:
                    self._clone_full(url, repo_dir, progress_cb)
                elif strategy == CloneStrategy.SHALLOW:
                    self._clone_shallow(url, repo_dir, progress_cb)
                elif strategy == CloneStrategy.SPARSE:
                    self._clone_sparse(url, repo_dir, progress_cb)
                elif strategy == CloneStrategy.STREAMING:
                    self._clone_streaming(url, repo_dir, progress_cb)
                else:
                    raise RepoScannerError(f"Unknown clone strategy: {strategy}")
            
            clone_time = time.time() - start_time
            
            return ClonedRepo(
                metadata=metadata,
                local_path=repo_dir,
                clone_strategy=strategy,
                clone_time=clone_time,
                temp_directory=True
            )
            
        except Exception as e:
            # Cleanup on failure
            if repo_dir.exists():
                shutil.rmtree(repo_dir, ignore_errors=True)
            raise RepoScannerError(f"Failed to clone repository: {e}")
    
    def _clone_full(self, url: str, target_dir: Path, progress_callback: Optional[callable]):
        """Perform a full clone."""
        if not GIT_PYTHON_AVAILABLE:
            raise RepoScannerError("GitPython not available for full clone")
        
        if progress_callback:
            progress_info = ProgressInfo(
                current=0,
                total=100,
                percentage=0.0,
                message="Cloning repository...",
                stage="fetching"
            )
            progress_callback(progress_info)
        
        repo = git.Repo.clone_from(url, target_dir)
        
        if progress_callback:
            progress_info = ProgressInfo(
                current=100,
                total=100,
                percentage=100.0,
                message="Clone complete",
                stage="checking_out"
            )
            progress_callback(progress_info)
    
    def _clone_shallow(self, url: str, target_dir: Path, progress_callback: Optional[callable]):
        """Perform a shallow clone (depth=1)."""
        if not GIT_PYTHON_AVAILABLE:
            raise RepoScannerError("GitPython not available for shallow clone")
        
        if progress_callback:
            progress_info = ProgressInfo(
                current=0,
                total=100,
                percentage=0.0,
                message="Shallow cloning repository...",
                stage="fetching"
            )
            progress_callback(progress_info)
        
        repo = git.Repo.clone_from(url, target_dir, depth=1)
        
        if progress_callback:
            progress_info = ProgressInfo(
                current=100,
                total=100,
                percentage=100.0,
                message="Shallow clone complete",
                stage="checking_out"
            )
            progress_callback(progress_info)
    
    def _clone_sparse(self, url: str, target_dir: Path, progress_callback: Optional[callable]):
        """Perform a sparse checkout clone."""
        if not GIT_PYTHON_AVAILABLE:
            raise RepoScannerError("GitPython not available for sparse clone")
        
        if progress_callback:
            progress_info = ProgressInfo(
                current=0,
                total=100,
                percentage=0.0,
                message="Sparse cloning repository...",
                stage="fetching"
            )
            progress_callback(progress_info)
        
        # Clone with sparse checkout
        repo = git.Repo.clone_from(url, target_dir, depth=1, filter='blob:none')
        
        # Configure sparse checkout for scannable files
        repo.git.config('core.sparseCheckout', 'true')
        
        # Create sparse-checkout file with scannable patterns
        sparse_file = target_dir / '.git' / 'info' / 'sparse-checkout'
        scannable_patterns = [
            '*.py', '*.js', '*.ts', '*.java', '*.cpp', '*.c', '*.h',
            '*.json', '*.yaml', '*.yml', '*.xml', '*.properties',
            '.env*', '*.env', '*.log', '*.txt', '*.md',
            'Dockerfile*', 'docker-compose*', '*.sh', '*.bat'
        ]
        
        with open(sparse_file, 'w') as f:
            for pattern in scannable_patterns:
                f.write(f"{pattern}\n")
        
        # Apply sparse checkout
        repo.git.read_tree('-m', '-u', 'HEAD')
        
        if progress_callback:
            progress_info = ProgressInfo(
                current=100,
                total=100,
                percentage=100.0,
                message="Sparse clone complete",
                stage="checking_out"
            )
            progress_callback(progress_info)
    
    def _clone_streaming(self, url: str, target_dir: Path, progress_callback: Optional[callable]):
        """Perform a streaming clone for very large repositories."""
        if not GIT_PYTHON_AVAILABLE:
            raise RepoScannerError("GitPython not available for streaming clone")
        
        if progress_callback:
            progress_info = ProgressInfo(
                current=0,
                total=100,
                percentage=0.0,
                message="Streaming clone (no full download)...",
                stage="fetching"
            )
            progress_callback(progress_info)
        
        # For streaming, we'll do a minimal clone and fetch files on demand
        # This is a simplified implementation - in practice, you'd want more sophisticated
        # file-by-file fetching based on the repository structure
        
        repo = git.Repo.clone_from(url, target_dir, depth=1, filter='blob:none')
        
        if progress_callback:
            progress_info = ProgressInfo(
                current=100,
                total=100,
                percentage=100.0,
                message="Streaming clone ready",
                stage="checking_out"
            )
            progress_callback(progress_info)
    
    def stream_scannable_files(self, url: str) -> Iterator[Tuple[str, bytes]]:
        """
        Stream scannable files from repository without full clone.
        This is for extremely large repositories.
        """
        # This would be implemented with platform-specific APIs
        # For now, raise not implemented
        raise NotImplementedError("Streaming file download not yet implemented")
    
    def cleanup_repo(self, cloned_repo: ClonedRepo) -> bool:
        """Clean up a cloned repository."""
        return cloned_repo.cleanup()
    
    def is_git_url(self, text: str) -> bool:
        """Check if text looks like a Git repository URL."""
        try:
            self.validate_repo_url(text)
            return True
        except RepoScannerError:
            return False
