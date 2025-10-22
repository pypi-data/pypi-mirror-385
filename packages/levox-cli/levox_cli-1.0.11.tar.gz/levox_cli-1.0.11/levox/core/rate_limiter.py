"""
Rate Limiter for Levox CLI Freemium Features
Tracks usage of enterprise features and enforces monthly limits.
"""

import os
import json
import logging
from pathlib import Path
from datetime import datetime, date
from typing import Dict, Optional, Tuple
from dataclasses import dataclass, asdict
import threading

from .exceptions import RateLimitExceededError


@dataclass
class FeatureUsage:
    """Track usage of a specific feature."""
    feature_name: str
    usage_count: int = 0
    monthly_limit: int = 0
    reset_date: date = None
    last_used: Optional[datetime] = None
    
    def __post_init__(self):
        if self.reset_date is None:
            # Set reset date to first day of next month
            today = date.today()
            if today.month == 12:
                self.reset_date = date(today.year + 1, 1, 1)
            else:
                self.reset_date = date(today.year, today.month + 1, 1)
    
    def can_use(self) -> bool:
        """Check if the feature can still be used."""
        return self.usage_count < self.monthly_limit
    
    def use(self) -> None:
        """Increment usage count."""
        self.usage_count += 1
        self.last_used = datetime.now()
    
    def get_remaining_uses(self) -> int:
        """Get remaining uses for this month."""
        return max(0, self.monthly_limit - self.usage_count)
    
    def needs_reset(self) -> bool:
        """Check if usage should be reset for new month."""
        return date.today() >= self.reset_date
    
    def reset_monthly_usage(self) -> None:
        """Reset usage for new month."""
        self.usage_count = 0
        today = date.today()
        if today.month == 12:
            self.reset_date = date(today.year + 1, 1, 1)
        else:
            self.reset_date = date(today.year, today.month + 1, 1)


class RateLimiter:
    """Rate limiter for freemium features with persistent storage."""
    
    def __init__(self, config_dir: Optional[Path] = None, license_tier=None):
        if config_dir is None:
            config_dir = Path.home() / ".levox"
        
        self.config_dir = config_dir
        self.usage_file = config_dir / "feature_usage.json"
        self.logger = logging.getLogger(__name__)
        self._lock = threading.Lock()
        self.license_tier = license_tier
        
        # Default freemium limits (matching server-side limits)
        self.default_limits = {
            "ast_analysis": 50,
            "cfg_analysis": 50,
            "gdpr_compliance": 50,
            "dataflow_analysis": 25,
            "ml_filtering": 25,
            "advanced_reporting": 50,
            "context_analysis": 50
        }
        
        # Load existing usage data
        self.feature_usage = self._load_usage_data()
        
        # Ensure all features have usage tracking
        self._initialize_missing_features()
    
    def _load_usage_data(self) -> Dict[str, FeatureUsage]:
        """Load usage data from persistent storage."""
        if not self.usage_file.exists():
            return {}
        
        try:
            with open(self.usage_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            usage_data = {}
            for feature_name, usage_dict in data.items():
                if 'reset_date' in usage_dict:
                    # Parse date string back to date object
                    reset_date_str = usage_dict['reset_date']
                    if isinstance(reset_date_str, str):
                        usage_dict['reset_date'] = datetime.strptime(reset_date_str, '%Y-%m-%d').date()
                
                usage_data[feature_name] = FeatureUsage(**usage_dict)
            
            return usage_data
            
        except Exception as e:
            self.logger.warning(f"Failed to load usage data: {e}")
            return {}
    
    def _save_usage_data(self) -> None:
        """Save usage data to persistent storage."""
        try:
            # Ensure directory exists
            self.usage_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Convert to serializable format
            data = {}
            for feature_name, usage in self.feature_usage.items():
                usage_dict = asdict(usage)
                # Convert date to string for JSON serialization
                if usage_dict['reset_date']:
                    usage_dict['reset_date'] = usage_dict['reset_date'].isoformat()
                data[feature_name] = usage_dict
            
            with open(self.usage_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)
                
        except Exception as e:
            self.logger.error(f"Failed to save usage data: {e}")
    
    def _initialize_missing_features(self) -> None:
        """Initialize usage tracking for features that don't have it yet."""
        for feature_name, limit in self.default_limits.items():
            if feature_name not in self.feature_usage:
                self.feature_usage[feature_name] = FeatureUsage(
                    feature_name=feature_name,
                    monthly_limit=limit
                )
        
        # Save after initialization
        self._save_usage_data()
    
    def _check_and_reset_monthly_usage(self) -> None:
        """Check if any features need monthly usage reset."""
        needs_save = False
        
        for usage in self.feature_usage.values():
            if usage.needs_reset():
                usage.reset_monthly_usage()
                needs_save = True
                self.logger.info(f"Reset monthly usage for {usage.feature_name}")
        
        if needs_save:
            self._save_usage_data()
    
    def can_use_feature(self, feature_name: str) -> Tuple[bool, int]:
        """
        Check if a feature can be used.
        
        Returns:
            Tuple of (can_use, remaining_uses)
        """
        with self._lock:
            self._check_and_reset_monthly_usage()
            
            if feature_name not in self.feature_usage:
                # Unknown feature - allow by default
                return True, -1
            
            usage = self.feature_usage[feature_name]
            can_use = usage.can_use()
            remaining = usage.get_remaining_uses()
            
            return can_use, remaining
    
    def use_feature(self, feature_name: str) -> None:
        """
        Mark a feature as used.
        
        Raises:
            RateLimitExceededError: If the feature usage limit is exceeded
        """
        with self._lock:
            self._check_and_reset_monthly_usage()
            
            if feature_name not in self.feature_usage:
                # Unknown feature - allow without tracking
                return
            
            usage = self.feature_usage[feature_name]
            
            if not usage.can_use():
                raise RateLimitExceededError(
                    f"Feature '{feature_name}' usage limit exceeded. "
                    f"Monthly limit: {usage.monthly_limit}, "
                    f"Reset date: {usage.reset_date}"
                )
            
            usage.use()
            self._save_usage_data()
            
            self.logger.debug(f"Used feature '{feature_name}'. "
                            f"Remaining: {usage.get_remaining_uses()}")
    
    def get_feature_status(self, feature_name: str) -> Optional[Dict[str, any]]:
        """Get detailed status of a feature's usage."""
        with self._lock:
            self._check_and_reset_monthly_usage()
            
            if feature_name not in self.feature_usage:
                return None
            
            usage = self.feature_usage[feature_name]
            return {
                'feature_name': feature_name,
                'usage_count': usage.usage_count,
                'monthly_limit': usage.monthly_limit,
                'remaining_uses': usage.get_remaining_uses(),
                'reset_date': usage.reset_date,
                'last_used': usage.last_used,
                'can_use': usage.can_use()
            }
    
    def get_all_feature_status(self) -> Dict[str, Dict[str, any]]:
        """Get status of all tracked features."""
        with self._lock:
            self._check_and_reset_monthly_usage()
            
            status = {}
            for feature_name, usage in self.feature_usage.items():
                status[feature_name] = {
                    'usage_count': usage.usage_count,
                    'monthly_limit': usage.monthly_limit,
                    'remaining_uses': usage.get_remaining_uses(),
                    'reset_date': usage.reset_date,
                    'last_used': usage.last_used,
                    'can_use': usage.can_use()
                }
            
            return status
    
    def reset_feature_usage(self, feature_name: str) -> None:
        """Reset usage for a specific feature (admin function)."""
        with self._lock:
            if feature_name in self.feature_usage:
                self.feature_usage[feature_name].reset_monthly_usage()
                self._save_usage_data()
                self.logger.info(f"Reset usage for feature: {feature_name}")
    
    def reset_all_usage(self) -> None:
        """Reset usage for all features."""
        with self._lock:
            for feature_name in self.feature_usage:
                self.feature_usage[feature_name].reset_monthly_usage()
            self._save_usage_data()
            self.logger.info("Reset usage for all features")
    
    def update_feature_limit(self, feature_name: str, new_limit: int) -> None:
        """Update the monthly limit for a feature."""
        with self._lock:
            if feature_name in self.feature_usage:
                self.feature_usage[feature_name].monthly_limit = new_limit
                self._save_usage_data()
                self.logger.info(f"Updated limit for {feature_name}: {new_limit}")
            else:
                # Create new feature tracking
                self.feature_usage[feature_name] = FeatureUsage(
                    feature_name=feature_name,
                    monthly_limit=new_limit
                )
                self._save_usage_data()
    
    def get_usage_summary(self) -> Dict[str, any]:
        """Get a summary of all feature usage."""
        with self._lock:
            self._check_and_reset_monthly_usage()
            
            total_features = len(self.feature_usage)
            features_at_limit = sum(1 for u in self.feature_usage.values() if not u.can_use())
            features_available = total_features - features_at_limit
            
            return {
                'total_features': total_features,
                'features_at_limit': features_at_limit,
                'features_available': features_available,
                'features': self.get_all_feature_status()
            }


# Global rate limiter instance
_rate_limiter: Optional[RateLimiter] = None


def get_rate_limiter(config_dir: Optional[Path] = None) -> RateLimiter:
    """Get the global rate limiter instance."""
    global _rate_limiter
    
    if _rate_limiter is None:
        _rate_limiter = RateLimiter(config_dir)
    
    return _rate_limiter


def check_feature_usage(feature_name: str) -> Tuple[bool, int]:
    """Convenience function to check if a feature can be used."""
    limiter = get_rate_limiter()
    return limiter.can_use_feature(feature_name)


def use_feature(feature_name: str) -> None:
    """Convenience function to mark a feature as used."""
    limiter = get_rate_limiter()
    limiter.use_feature(feature_name)
