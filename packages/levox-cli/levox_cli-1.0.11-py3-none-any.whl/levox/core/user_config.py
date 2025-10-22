"""
User Configuration Management

Handles user preferences, settings, and configuration persistence
for the Levox CLI application.
"""

import os
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class UserPreferences:
    """User preferences and settings."""
    # Workspace settings
    default_scan_directory: str = ""
    smart_exclusions: bool = True
    auto_detect_project: bool = True
    
    # Output preferences
    preferred_formats: List[str] = None
    verbosity_level: str = "normal"  # quiet, normal, verbose
    report_directory: str = ""
    
    # Git integration
    github_token: Optional[str] = None
    gitlab_token: Optional[str] = None
    bitbucket_token: Optional[str] = None
    
    # ML preferences
    auto_download_models: bool = True
    model_cache_directory: str = ""
    preferred_ml_model: str = "default"
    
    # UI preferences
    progress_theme: str = "smooth"  # smooth, classic, ascii, dots, spinner
    show_tips: bool = True
    auto_cleanup_repos: bool = True
    
    # Advanced settings
    max_concurrent_workers: int = 0  # 0 = auto-detect
    memory_limit_mb: int = 0  # 0 = no limit
    cache_enabled: bool = True
    cache_ttl_hours: int = 24
    
    # Compliance settings
    default_company_id: Optional[str] = None
    compliance_mode: bool = False
    audit_logging: bool = True
    
    def __post_init__(self):
        """Initialize default values after dataclass creation."""
        if self.preferred_formats is None:
            self.preferred_formats = ["json", "html"]
        
        if not self.default_scan_directory:
            self.default_scan_directory = str(Path.cwd())
        
        if not self.report_directory:
            self.report_directory = str(Path.home() / "levox_reports")
        
        if not self.model_cache_directory:
            self.model_cache_directory = str(Path.home() / ".levox" / "models")


@dataclass
class ScanHistory:
    """Represents a scan in the user's history."""
    scan_id: str
    timestamp: datetime
    scan_path: str
    files_scanned: int
    matches_found: int
    duration: float
    scan_type: str  # "directory", "repository", "file"
    license_tier: str
    success: bool
    error_message: Optional[str] = None


@dataclass
class UserStats:
    """User statistics and usage metrics."""
    total_scans: int = 0
    total_files_scanned: int = 0
    total_matches_found: int = 0
    total_scan_time: float = 0.0
    first_scan_date: Optional[datetime] = None
    last_scan_date: Optional[datetime] = None
    favorite_scan_paths: List[str] = None
    most_common_languages: Dict[str, int] = None
    
    def __post_init__(self):
        """Initialize default values."""
        if self.favorite_scan_paths is None:
            self.favorite_scan_paths = []
        if self.most_common_languages is None:
            self.most_common_languages = {}


class UserConfig:
    """Manages user configuration and preferences."""
    
    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize user configuration manager.
        
        Args:
            config_dir: Custom configuration directory (defaults to ~/.levox)
        """
        if config_dir is None:
            config_dir = Path.home() / ".levox"
        
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        
        # Configuration files
        self.preferences_file = self.config_dir / "user_preferences.json"
        self.history_file = self.config_dir / "scan_history.json"
        self.stats_file = self.config_dir / "user_stats.json"
        self.first_run_file = self.config_dir / "first_run"
        
        # Load existing configuration
        self.preferences = self._load_preferences()
        self.history = self._load_history()
        self.stats = self._load_stats()
    
    def _load_preferences(self) -> UserPreferences:
        """Load user preferences from file."""
        try:
            if self.preferences_file.exists():
                with open(self.preferences_file, 'r') as f:
                    data = json.load(f)
                    return UserPreferences(**data)
        except Exception:
            pass
        
        return UserPreferences()
    
    def _load_history(self) -> List[ScanHistory]:
        """Load scan history from file."""
        try:
            if self.history_file.exists():
                with open(self.history_file, 'r') as f:
                    data = json.load(f)
                    return [ScanHistory(**item) for item in data]
        except Exception:
            pass
        
        return []
    
    def _load_stats(self) -> UserStats:
        """Load user statistics from file."""
        try:
            if self.stats_file.exists():
                with open(self.stats_file, 'r') as f:
                    data = json.load(f)
                    # Convert datetime strings back to datetime objects
                    if 'first_scan_date' in data and data['first_scan_date']:
                        data['first_scan_date'] = datetime.fromisoformat(data['first_scan_date'])
                    if 'last_scan_date' in data and data['last_scan_date']:
                        data['last_scan_date'] = datetime.fromisoformat(data['last_scan_date'])
                    return UserStats(**data)
        except Exception:
            pass
        
        return UserStats()
    
    def save_preferences(self, preferences: UserPreferences) -> bool:
        """
        Save user preferences to file.
        
        Args:
            preferences: User preferences to save
            
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            with open(self.preferences_file, 'w') as f:
                json.dump(asdict(preferences), f, indent=2)
            
            self.preferences = preferences
            return True
        except Exception:
            return False
    
    def save_history(self, history: List[ScanHistory]) -> bool:
        """
        Save scan history to file.
        
        Args:
            history: Scan history to save
            
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            # Convert datetime objects to strings for JSON serialization
            history_data = []
            for item in history:
                item_dict = asdict(item)
                if item_dict['timestamp']:
                    item_dict['timestamp'] = item_dict['timestamp'].isoformat()
                history_data.append(item_dict)
            
            with open(self.history_file, 'w') as f:
                json.dump(history_data, f, indent=2)
            
            self.history = history
            return True
        except Exception:
            return False
    
    def save_stats(self, stats: UserStats) -> bool:
        """
        Save user statistics to file.
        
        Args:
            stats: User statistics to save
            
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            # Convert datetime objects to strings for JSON serialization
            stats_data = asdict(stats)
            if stats_data['first_scan_date']:
                stats_data['first_scan_date'] = stats_data['first_scan_date'].isoformat()
            if stats_data['last_scan_date']:
                stats_data['last_scan_date'] = stats_data['last_scan_date'].isoformat()
            
            with open(self.stats_file, 'w') as f:
                json.dump(stats_data, f, indent=2)
            
            self.stats = stats
            return True
        except Exception:
            return False
    
    def add_scan_to_history(self, scan_result) -> bool:
        """
        Add a scan result to the history.
        
        Args:
            scan_result: DetectionResult object from a scan
            
        Returns:
            True if added successfully, False otherwise
        """
        try:
            scan_history = ScanHistory(
                scan_id=scan_result.scan_id,
                timestamp=datetime.now(),
                scan_path=scan_result.scan_path,
                files_scanned=scan_result.files_scanned,
                matches_found=scan_result.total_matches,
                duration=scan_result.scan_duration,
                scan_type="directory",  # Could be determined from scan_result
                license_tier=scan_result.license_tier,
                success=len(scan_result.scan_errors) == 0,
                error_message=scan_result.scan_errors[0] if scan_result.scan_errors else None
            )
            
            # Add to history (keep last 100 scans)
            self.history.insert(0, scan_history)
            if len(self.history) > 100:
                self.history = self.history[:100]
            
            # Update statistics
            self._update_stats_from_scan(scan_result)
            
            # Save both history and stats
            self.save_history(self.history)
            self.save_stats(self.stats)
            
            return True
        except Exception:
            return False
    
    def _update_stats_from_scan(self, scan_result):
        """Update user statistics from a scan result."""
        self.stats.total_scans += 1
        self.stats.total_files_scanned += scan_result.files_scanned
        self.stats.total_matches_found += scan_result.total_matches
        self.stats.total_scan_time += scan_result.scan_duration
        
        # Update dates
        now = datetime.now()
        if not self.stats.first_scan_date:
            self.stats.first_scan_date = now
        self.stats.last_scan_date = now
        
        # Update favorite paths
        scan_path = scan_result.scan_path
        if scan_path not in self.stats.favorite_scan_paths:
            self.stats.favorite_scan_paths.append(scan_path)
        
        # Keep only top 10 favorite paths
        if len(self.stats.favorite_scan_paths) > 10:
            self.stats.favorite_scan_paths = self.stats.favorite_scan_paths[:10]
    
    def get_recent_scans(self, limit: int = 10) -> List[ScanHistory]:
        """Get recent scan history."""
        return self.history[:limit]
    
    def get_scan_by_id(self, scan_id: str) -> Optional[ScanHistory]:
        """Get a specific scan by ID."""
        for scan in self.history:
            if scan.scan_id == scan_id:
                return scan
        return None
    
    def clear_history(self) -> bool:
        """Clear all scan history."""
        try:
            self.history = []
            self.save_history(self.history)
            return True
        except Exception:
            return False
    
    def is_first_run(self) -> bool:
        """Check if this is the first time running Levox."""
        return not self.first_run_file.exists()
    
    def mark_first_run_complete(self):
        """Mark that the first run has been completed."""
        try:
            self.first_run_file.touch()
        except Exception:
            pass
    
    def get_smart_exclusions(self) -> List[str]:
        """Get smart exclusion patterns based on user preferences."""
        if not self.preferences.smart_exclusions:
            return []
        
        return [
            # Common dependency directories
            "node_modules/",
            "venv/",
            "env/",
            ".venv/",
            "__pycache__/",
            ".pytest_cache/",
            "dist/",
            "build/",
            ".git/",
            ".svn/",
            ".hg/",
            
            # Common build/cache directories
            "target/",  # Rust
            ".gradle/",  # Gradle
            ".m2/",  # Maven
            ".npm/",  # npm cache
            "vendor/",  # Composer (PHP)
            
            # Common file patterns
            "*.log",
            "*.tmp",
            "*.temp",
            "*.cache",
            "*.pyc",
            "*.pyo",
            "*.class",
            "*.jar",
            "*.war",
            "*.ear",
            
            # Image and media files
            "*.jpg",
            "*.jpeg",
            "*.png",
            "*.gif",
            "*.bmp",
            "*.tiff",
            "*.svg",
            "*.ico",
            "*.mp4",
            "*.avi",
            "*.mov",
            "*.wmv",
            "*.mp3",
            "*.wav",
            "*.flac",
            
            # Archive files
            "*.zip",
            "*.tar",
            "*.gz",
            "*.bz2",
            "*.7z",
            "*.rar",
            
            # Database files
            "*.db",
            "*.sqlite",
            "*.sqlite3",
            
            # IDE and editor files
            ".vscode/",
            ".idea/",
            "*.swp",
            "*.swo",
            "*~",
            
            # OS files
            ".DS_Store",
            "Thumbs.db",
            "desktop.ini"
        ]
    
    def get_project_type_hints(self, directory: Path) -> List[str]:
        """Get project type hints for a directory."""
        hints = []
        
        # Check for common project files
        if (directory / "package.json").exists():
            hints.append("javascript")
        if (directory / "requirements.txt").exists() or (directory / "pyproject.toml").exists():
            hints.append("python")
        if (directory / "pom.xml").exists() or (directory / "build.gradle").exists():
            hints.append("java")
        if (directory / "Cargo.toml").exists():
            hints.append("rust")
        if (directory / "go.mod").exists():
            hints.append("go")
        if (directory / "composer.json").exists():
            hints.append("php")
        if (directory / "Gemfile").exists():
            hints.append("ruby")
        
        return hints
    
    def get_recommended_scan_options(self, directory: Path) -> Dict[str, Any]:
        """Get recommended scan options for a directory."""
        options = {
            "exclusions": self.get_smart_exclusions(),
            "formats": self.preferences.preferred_formats,
            "verbosity": self.preferences.verbosity_level
        }
        
        # Add project-specific recommendations
        project_hints = self.get_project_type_hints(directory)
        if project_hints:
            options["project_types"] = project_hints
        
        # Add size-based recommendations
        try:
            file_count = sum(1 for _ in directory.rglob("*") if _.is_file())
            if file_count > 1000:
                options["suggest_shallow_scan"] = True
                options["suggest_incremental"] = True
        except Exception:
            pass
        
        return options
    
    def get_default_company_id(self) -> Optional[str]:
        """Get the default company ID."""
        return self.preferences.default_company_id
    
    def set_default_company_id(self, company_id: str) -> None:
        """Set the default company ID."""
        self.preferences.default_company_id = company_id
        self.save()
    
    def save(self) -> bool:
        """Save all configuration data to files."""
        try:
            # Save preferences
            preferences_saved = self.save_preferences(self.preferences)
            
            # Save history
            history_saved = self.save_history(self.history)
            
            # Save stats
            stats_saved = self.save_stats(self.stats)
            
            return preferences_saved and history_saved and stats_saved
        except Exception:
            return False
    
    def export_configuration(self, file_path: Path) -> bool:
        """
        Export current configuration to a file.
        
        Args:
            file_path: Path to export configuration to
            
        Returns:
            True if exported successfully, False otherwise
        """
        try:
            config_data = {
                "preferences": asdict(self.preferences),
                "stats": asdict(self.stats),
                "export_timestamp": datetime.now().isoformat(),
                "version": "1.0"
            }
            
            with open(file_path, 'w') as f:
                json.dump(config_data, f, indent=2)
            
            return True
        except Exception:
            return False
    
    def import_configuration(self, file_path: Path) -> bool:
        """
        Import configuration from a file.
        
        Args:
            file_path: Path to import configuration from
            
        Returns:
            True if imported successfully, False otherwise
        """
        try:
            with open(file_path, 'r') as f:
                config_data = json.load(f)
            
            if "preferences" in config_data:
                self.preferences = UserPreferences(**config_data["preferences"])
                self.save_preferences(self.preferences)
            
            if "stats" in config_data:
                stats_data = config_data["stats"]
                # Convert datetime strings back to datetime objects
                if 'first_scan_date' in stats_data and stats_data['first_scan_date']:
                    stats_data['first_scan_date'] = datetime.fromisoformat(stats_data['first_scan_date'])
                if 'last_scan_date' in stats_data and stats_data['last_scan_date']:
                    stats_data['last_scan_date'] = datetime.fromisoformat(stats_data['last_scan_date'])
                
                self.stats = UserStats(**stats_data)
                self.save_stats(self.stats)
            
            return True
        except Exception:
            return False


# Global user config instance
_global_user_config: Optional[UserConfig] = None


def get_user_config() -> UserConfig:
    """Get the global user configuration instance."""
    global _global_user_config
    if _global_user_config is None:
        _global_user_config = UserConfig()
    return _global_user_config


def reset_user_config():
    """Reset the global user configuration."""
    global _global_user_config
    _global_user_config = None
