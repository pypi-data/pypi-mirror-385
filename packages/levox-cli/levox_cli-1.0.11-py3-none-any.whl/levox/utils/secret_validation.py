"""
Secret validation and enrichment utilities.

This module validates detected secrets with provider APIs when explicitly enabled.
Currently supports AWS Access Key ID + Secret Access Key validation via STS GetCallerIdentity.

Safety principles:
- Network validation only runs when allow_network is True and feature enabled.
- Secrets are never logged; values are redacted in all output.
- Timeouts are short; failures degrade gracefully without raising.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple


AWS_ACCESS_KEY_ID_RE = re.compile(r"\b(AKIA|ASIA|ABIA|ACCA|AGPA|AIDA)[A-Z0-9]{16}\b")


@dataclass
class SecretVerificationResult:
    provider: str
    status: str  # confirmed_active | invalid | incomplete | skipped
    confidence: float
    details: Dict[str, Any]


def _redact(value: str, keep: int = 4) -> str:
    if not value:
        return "[redacted]"
    if len(value) <= keep * 2:
        return value[0:1] + "***"
    return f"{value[:keep]}***{value[-keep:]}"


def detect_aws_access_key_id(text: str) -> Optional[str]:
    m = AWS_ACCESS_KEY_ID_RE.search(text)
    return m.group(0) if m else None


def verify_aws_credentials(access_key_id: str, secret_access_key: str, timeout_seconds: int) -> SecretVerificationResult:
    try:
        import boto3  # type: ignore
        from botocore.config import Config as BotoConfig  # type: ignore
        from botocore.exceptions import ClientError, BotoCoreError  # type: ignore

        session = boto3.session.Session()
        cfg = BotoConfig(retries={"max_attempts": 1}, read_timeout=timeout_seconds, connect_timeout=timeout_seconds)
        sts = session.client(
            "sts",
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
            config=cfg,
        )
        identity = sts.get_caller_identity()
        return SecretVerificationResult(
            provider="aws",
            status="confirmed_active",
            confidence=0.99,
            details={
                "account": identity.get("Account"),
                "arn": identity.get("Arn"),
                "access_key_id": _redact(access_key_id),
            },
        )
    except Exception:
        # Treat as invalid/unauthorized without surfacing details
        return SecretVerificationResult(
            provider="aws",
            status="invalid",
            confidence=0.6,
            details={"access_key_id": _redact(access_key_id)},
        )


def enrich_detection_with_secret_validation(
    match: Any,
    allow_network: bool,
    aws_enabled: bool,
    timeout_seconds: int,
) -> Optional[SecretVerificationResult]:
    """
    Attempt to validate a detected secret and return enrichment info.
    - Only runs when allow_network is True.
    - For AWS: requires Access Key ID pattern and nearby Secret Key presence in matched_text/context.
    """
    try:
        if not allow_network:
            return SecretVerificationResult("generic", "skipped", 0.0, {})

        text_blob = " ".join(
            [
                str(getattr(match, "matched_text", "")),
                str(getattr(match, "context_before", "")),
                str(getattr(match, "context_after", "")),
            ]
        )

        if aws_enabled:
            access_key = detect_aws_access_key_id(text_blob)
            if access_key:
                # Try to find secret access key in proximity (common 40-char base64-ish)
                secret_match = re.search(r"(?i)aws[_-]?secret[_-]?access[_-]?key\s*[:=]\s*['\"]?([A-Za-z0-9/+=]{30,50})", text_blob)
                if secret_match:
                    secret = secret_match.group(1)
                    return verify_aws_credentials(access_key, secret, timeout_seconds)
                else:
                    return SecretVerificationResult(
                        provider="aws",
                        status="incomplete",
                        confidence=0.7,
                        details={"access_key_id": _redact(access_key)},
                    )
        return None
    except Exception:
        return None


