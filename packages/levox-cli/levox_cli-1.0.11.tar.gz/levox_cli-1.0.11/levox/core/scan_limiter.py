"""
Local Scan Limiter for Starter Tier
Stores monthly scan usage locally with tamper-evident signatures.
"""

import os
import json
import hmac
import hashlib
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple


@dataclass
class ScanUsage:
    period_start: str  # YYYY-MM-01
    scan_count: int
    signature: str


class LocalScanLimiter:
    def __init__(self, storage_dir: Optional[Path] = None):
        if storage_dir is None:
            storage_dir = Path.home() / ".levox"
        self.storage_dir = storage_dir
        self.usage_file = storage_dir / "scan_usage.json"
        self._ensure_dir()

    def _ensure_dir(self) -> None:
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def _current_period(self) -> str:
        now = datetime.utcnow()
        return f"{now.year:04d}-{now.month:02d}-01"

    def _device_fingerprint(self) -> str:
        try:
            import platform
            sysinfo = f"{platform.node()}-{platform.system()}-{platform.processor()}"
            return hashlib.sha256(sysinfo.encode()).hexdigest()[:16]
        except Exception:
            return "unknown-device"

    def _derive_key(self, jwt_token: Optional[str]) -> bytes:
        # Derive a signing key from the license JWT (server-signed) and device fingerprint
        device_fp = self._device_fingerprint()
        base = (jwt_token or "no-jwt") + ":" + device_fp
        return hashlib.sha256(base.encode()).digest()

    def _sign(self, jwt_token: Optional[str], period_start: str, count: int) -> str:
        key = self._derive_key(jwt_token)
        msg = f"{period_start}:{count}:{self._device_fingerprint()}".encode()
        return hmac.new(key, msg, hashlib.sha256).hexdigest()

    def _load(self) -> Optional[ScanUsage]:
        if not self.usage_file.exists():
            return None
        try:
            with open(self.usage_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return ScanUsage(**data)
        except Exception:
            return None

    def _save(self, usage: ScanUsage) -> None:
        self._ensure_dir()
        with open(self.usage_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(usage), f)

    def get_status(self, jwt_token: Optional[str], tier: str) -> Tuple[int, int, str]:
        period = self._current_period()
        limit = 25 if tier == 'starter' else 999999
        usage = self._load()
        if not usage or usage.period_start != period:
            return 0, limit, period
        # Verify signature
        expected = self._sign(jwt_token, usage.period_start, usage.scan_count)
        if not hmac.compare_digest(expected, usage.signature):
            # Tamper detected: reset to 0
            return 0, limit, period
        return usage.scan_count, limit, usage.period_start

    def can_scan(self, jwt_token: Optional[str], tier: str) -> Tuple[bool, int, int, str]:
        count, limit, period = self.get_status(jwt_token, tier)
        remaining = max(0, limit - count)
        return count < limit, count, limit, period

    def increment(self, jwt_token: Optional[str], tier: str) -> Tuple[int, int, bool]:
        period = self._current_period()
        limit = 25 if tier == 'starter' else 999999
        usage = self._load()
        if not usage or usage.period_start != period:
            new_count = 1
        else:
            # Verify signature; if invalid, reset to 1
            expected = self._sign(jwt_token, usage.period_start, usage.scan_count)
            if not hmac.compare_digest(expected, usage.signature):
                new_count = 1
            else:
                new_count = usage.scan_count + 1
        new_sig = self._sign(jwt_token, period, new_count)
        self._save(ScanUsage(period_start=period, scan_count=new_count, signature=new_sig))
        return new_count, limit, new_count >= limit


_scan_limiter: Optional[LocalScanLimiter] = None


def get_scan_limiter() -> LocalScanLimiter:
    global _scan_limiter
    if _scan_limiter is None:
        _scan_limiter = LocalScanLimiter()
    return _scan_limiter


