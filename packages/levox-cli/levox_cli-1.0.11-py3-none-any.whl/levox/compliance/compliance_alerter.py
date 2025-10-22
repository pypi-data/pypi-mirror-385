"""
Compliance Alerter - Real-time GDPR/CCPA violation notification system.

Provides immediate, actionable compliance alerts during scans with specific article
references and remediation guidance. Designed for engineer-focused feedback.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import uuid

from ..core.config import Config, LicenseTier
from ..core.exceptions import DetectionError
from ..models.detection_result import DetectionResult, DetectionMatch
from .models import ComplianceIssue, ComplianceLevel, GDPRArticle
from .gdpr_mapper import GDPRMapper


logger = logging.getLogger(__name__)


class AlertSeverity(str, Enum):
    """Alert severity levels for compliance violations."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class AlertVerbosity(str, Enum):
    """Alert verbosity levels for different user needs."""
    SILENT = "silent"      # No alerts shown
    SUMMARY = "summary"     # Only critical/high alerts
    DETAILED = "detailed"   # All alerts with context
    VERBOSE = "verbose"     # All alerts with full details


@dataclass
class ComplianceAlert:
    """Individual compliance alert with rich context."""
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    severity: AlertSeverity = AlertSeverity.MEDIUM
    framework: str = "GDPR"  # GDPR, CCPA, etc.
    article_ref: str = ""    # Article 32, §1798.100, etc.
    title: str = ""
    description: str = ""
    file_path: str = ""
    line_number: int = 0
    context: str = ""
    remediation: str = ""
    confidence: float = 0.0
    category: str = ""
    matched_text: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'severity': self.severity.value,
            'framework': self.framework,
            'article_ref': self.article_ref,
            'title': self.title,
            'description': self.description,
            'file_path': self.file_path,
            'line_number': self.line_number,
            'context': self.context,
            'remediation': self.remediation,
            'confidence': self.confidence,
            'category': self.category,
            'matched_text': self.matched_text,
            'metadata': self.metadata
        }


class ComplianceAlerter:
    """
    Real-time compliance alert system for GDPR/CCPA violations.
    
    Provides immediate, actionable feedback to engineers during scans with
    specific article references and remediation guidance.
    """
    
    def __init__(self, config: Config):
        """Initialize the compliance alerter."""
        self.config = config
        self.license_tier = config.license.tier
        
        # Initialize GDPR mapper for article mapping
        self.gdpr_mapper = GDPRMapper()
        
        # Alert templates for different violation types
        self.alert_templates = self._initialize_alert_templates()
        
        # Alert aggregation to prevent spam
        self.alert_groups: Dict[str, List[ComplianceAlert]] = {}
        
        # Performance tracking
        self.alerts_generated = 0
        self.alerts_filtered = 0
        
        logger.info("Compliance Alerter initialized successfully")
    
    def _initialize_alert_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialize alert templates for different violation types."""
        return {
            # Article 32 - Security violations
            "hardcoded_secrets": {
                "title": "Hardcoded Credentials Detected",
                "article_ref": "GDPR Article 32",
                "severity": AlertSeverity.CRITICAL,
                "description": "Hardcoded credentials violate data security requirements",
                "remediation": "Move credentials to secure environment variables or secret management systems",
                "category": "Security"
            },
            "weak_crypto": {
                "title": "Weak Cryptographic Algorithm",
                "article_ref": "GDPR Article 32",
                "severity": AlertSeverity.CRITICAL,
                "description": "Weak cryptographic algorithm violates security requirements",
                "remediation": "Use strong encryption algorithms (AES-256, RSA-2048+)",
                "category": "Security"
            },
            "unencrypted_protocols": {
                "title": "Unencrypted Data Transmission",
                "article_ref": "GDPR Article 32",
                "severity": AlertSeverity.HIGH,
                "description": "PII transmitted over unencrypted protocols",
                "remediation": "Enable HTTPS/TLS for all data transmission",
                "category": "Security"
            },
            "sql_injection_risk": {
                "title": "SQL Injection Vulnerability",
                "article_ref": "GDPR Article 32",
                "severity": AlertSeverity.CRITICAL,
                "description": "SQL injection vulnerability detected in data processing",
                "remediation": "Use parameterized queries and input validation",
                "category": "Security"
            },
            
            # Article 15 - DSAR violations
            "missing_dsar": {
                "title": "Missing Data Access Endpoint",
                "article_ref": "GDPR Article 15",
                "severity": AlertSeverity.HIGH,
                "description": "No data subject access request functionality detected",
                "remediation": "Implement DSAR endpoints for user data export",
                "category": "Data Subject Rights"
            },
            "incomplete_dsar": {
                "title": "Incomplete DSAR Implementation",
                "article_ref": "GDPR Article 15",
                "severity": AlertSeverity.MEDIUM,
                "description": "DSAR endpoint may not export all required data",
                "remediation": "Ensure DSAR exports all personal data categories",
                "category": "Data Subject Rights"
            },
            
            # Article 17 - Right to erasure
            "missing_deletion": {
                "title": "Missing Data Deletion Mechanism",
                "article_ref": "GDPR Article 17",
                "severity": AlertSeverity.HIGH,
                "description": "No data deletion functionality detected",
                "remediation": "Implement user data deletion endpoints",
                "category": "Data Subject Rights"
            },
            "soft_delete_only": {
                "title": "Soft Delete May Not Comply",
                "article_ref": "GDPR Article 17",
                "severity": AlertSeverity.MEDIUM,
                "description": "Only soft deletion detected - may not meet erasure requirements",
                "remediation": "Implement hard deletion for complete data erasure",
                "category": "Data Subject Rights"
            },
            
            # Article 25 - Data minimization
            "excessive_collection": {
                "title": "Excessive Data Collection",
                "article_ref": "GDPR Article 25",
                "severity": AlertSeverity.MEDIUM,
                "description": "Potential excessive data collection detected",
                "remediation": "Review data collection practices for minimization",
                "category": "Data Minimization"
            },
            "unnecessary_pii": {
                "title": "Unnecessary PII Collection",
                "article_ref": "GDPR Article 5(1)(c)",
                "severity": AlertSeverity.MEDIUM,
                "description": "PII collection may exceed necessary requirements",
                "remediation": "Remove unnecessary PII collection",
                "category": "Data Minimization"
            },
            
            # Article 44-49 - Cross-border transfers
            "international_transfer": {
                "title": "International Data Transfer",
                "article_ref": "GDPR Articles 44-49",
                "severity": AlertSeverity.HIGH,
                "description": "International data transfer detected",
                "remediation": "Verify adequate safeguards for cross-border transfers",
                "category": "Data Transfer"
            },
            "third_party_service": {
                "title": "Third-Party Service Integration",
                "article_ref": "GDPR Articles 44-49",
                "severity": AlertSeverity.MEDIUM,
                "description": "Third-party service may involve data transfer",
                "remediation": "Review data processing agreements and safeguards",
                "category": "Data Transfer"
            },
            
            # Article 6 - Lawful basis
            "missing_consent": {
                "title": "Missing Consent Mechanism",
                "article_ref": "GDPR Article 6",
                "severity": AlertSeverity.HIGH,
                "description": "No consent collection mechanism detected",
                "remediation": "Implement consent collection and management",
                "category": "Lawful Basis"
            },
            "unclear_basis": {
                "title": "Unclear Lawful Basis",
                "article_ref": "GDPR Article 6",
                "severity": AlertSeverity.MEDIUM,
                "description": "Lawful basis for processing unclear",
                "remediation": "Document lawful basis for all data processing",
                "category": "Lawful Basis"
            }
        }
    
    def generate_alert_from_match(self, match: DetectionMatch, file_path: str, 
                                verbosity: AlertVerbosity = AlertVerbosity.DETAILED) -> Optional[ComplianceAlert]:
        """
        Generate a compliance alert from a detection match.
        
        Args:
            match: Detection match from scan
            file_path: Path to the file containing the match
            verbosity: Alert verbosity level
            
        Returns:
            ComplianceAlert if alert should be shown, None otherwise
        """
        try:
            # Map detection pattern to compliance violation type
            violation_type = self._map_pattern_to_violation(match.pattern_name)
            if not violation_type:
                return None
            
            # Get alert template
            template = self.alert_templates.get(violation_type)
            if not template:
                return None
            
            # Create compliance alert
            alert = ComplianceAlert(
                severity=template["severity"],
                framework="GDPR",
                article_ref=template["article_ref"],
                title=template["title"],
                description=template["description"],
                file_path=file_path,
                line_number=match.line_number,
                context=self._generate_context(match, file_path),
                remediation=template["remediation"],
                confidence=match.confidence,
                category=template["category"],
                matched_text=match.matched_text,
                metadata={
                    "pattern_name": match.pattern_name,
                    "risk_level": str(match.risk_level),
                    "detection_level": match.metadata.get('detection_level', 'unknown')
                }
            )
            
            # Apply verbosity filtering
            if not self._should_show_alert(alert, verbosity):
                self.alerts_filtered += 1
                return None
            
            self.alerts_generated += 1
            return alert
            
        except Exception as e:
            logger.error(f"Failed to generate alert from match: {e}")
            return None
    
    def generate_alert_from_compliance_issue(self, issue: ComplianceIssue, 
                                            verbosity: AlertVerbosity = AlertVerbosity.DETAILED) -> Optional[ComplianceAlert]:
        """
        Generate a compliance alert from a compliance issue.
        
        Args:
            issue: Compliance issue from analysis
            verbosity: Alert verbosity level
            
        Returns:
            ComplianceAlert if alert should be shown, None otherwise
        """
        try:
            # Map compliance level to alert severity
            severity_mapping = {
                ComplianceLevel.CRITICAL: AlertSeverity.CRITICAL,
                ComplianceLevel.HIGH: AlertSeverity.HIGH,
                ComplianceLevel.MEDIUM: AlertSeverity.MEDIUM,
                ComplianceLevel.LOW: AlertSeverity.LOW
            }
            
            alert = ComplianceAlert(
                severity=severity_mapping.get(issue.severity, AlertSeverity.MEDIUM),
                framework="GDPR",
                article_ref=issue.article_ref.value,
                title=f"{issue.article_ref.value} Violation",
                description=issue.description,
                file_path=issue.file_path,
                line_number=issue.line_number,
                context=issue.evidence,
                remediation=issue.remediation,
                confidence=issue.confidence,
                category=issue.category,
                metadata={
                    "check_type": issue.check_type,
                    "created_at": issue.created_at.isoformat()
                }
            )
            
            # Apply verbosity filtering
            if not self._should_show_alert(alert, verbosity):
                self.alerts_filtered += 1
                return None
            
            self.alerts_generated += 1
            return alert
            
        except Exception as e:
            logger.error(f"Failed to generate alert from compliance issue: {e}")
            return None
    
    def _map_pattern_to_violation(self, pattern_name: str) -> Optional[str]:
        """Map detection pattern name to violation type."""
        pattern_mapping = {
            "hardcoded_secrets": "hardcoded_secrets",
            "weak_crypto": "weak_crypto",
            "unencrypted_protocols": "unencrypted_protocols",
            "sql_injection_risk": "sql_injection_risk",
            "dsar_endpoint": "missing_dsar",
            "dsar_api_route": "incomplete_dsar",
            "user_deletion_endpoint": "missing_deletion",
            "soft_delete_pattern": "soft_delete_only",
            "excessive_data_collection": "excessive_collection",
            "missing_data_minimization": "unnecessary_pii",
            "third_party_service": "third_party_service",
            "international_api_call": "international_transfer",
            "missing_consent": "missing_consent",
            "unclear_consent": "unclear_basis"
        }
        
        return pattern_mapping.get(pattern_name)
    
    def _generate_context(self, match: DetectionMatch, file_path: str) -> str:
        """Generate contextual information for the alert."""
        context_parts = []
        
        # Add file context
        context_parts.append(f"File: {Path(file_path).name}")
        
        # Add line context
        context_parts.append(f"Line {match.line_number}")
        
        # Add matched text context
        if match.matched_text:
            # Truncate long matches
            text = match.matched_text
            if len(text) > 100:
                text = text[:97] + "..."
            context_parts.append(f"Code: {text}")
        
        # Add detection level context
        detection_level = match.metadata.get('detection_level', 'unknown')
        if detection_level != 'unknown':
            context_parts.append(f"Detection: {detection_level}")
        
        return " | ".join(context_parts)
    
    def _should_show_alert(self, alert: ComplianceAlert, verbosity: AlertVerbosity) -> bool:
        """Determine if alert should be shown based on verbosity level."""
        if verbosity == AlertVerbosity.SILENT:
            return False
        
        if verbosity == AlertVerbosity.SUMMARY:
            return alert.severity in [AlertSeverity.CRITICAL, AlertSeverity.HIGH]
        
        if verbosity == AlertVerbosity.DETAILED:
            return alert.severity in [AlertSeverity.CRITICAL, AlertSeverity.HIGH, AlertSeverity.MEDIUM]
        
        # VERBOSE shows all alerts
        return True
    
    def aggregate_alerts(self, alerts: List[ComplianceAlert]) -> List[ComplianceAlert]:
        """
        Aggregate similar alerts to prevent spam.
        
        Groups alerts by file, pattern, and severity to reduce noise.
        """
        if not alerts:
            return []
        
        # Group alerts by aggregation key
        groups: Dict[str, List[ComplianceAlert]] = {}
        
        for alert in alerts:
            # Create aggregation key
            key = f"{alert.file_path}:{alert.category}:{alert.severity.value}"
            
            if key not in groups:
                groups[key] = []
            groups[key].append(alert)
        
        # Process each group
        aggregated_alerts = []
        
        for group_alerts in groups.values():
            if len(group_alerts) == 1:
                # Single alert, no aggregation needed
                aggregated_alerts.append(group_alerts[0])
            else:
                # Multiple alerts, create aggregated alert
                aggregated_alert = self._create_aggregated_alert(group_alerts)
                aggregated_alerts.append(aggregated_alert)
        
        return aggregated_alerts
    
    def _create_aggregated_alert(self, alerts: List[ComplianceAlert]) -> ComplianceAlert:
        """Create an aggregated alert from multiple similar alerts."""
        if not alerts:
            raise ValueError("Cannot aggregate empty alert list")
        
        # Use the first alert as base
        base_alert = alerts[0]
        
        # Update title to indicate aggregation
        aggregated_title = f"{base_alert.title} ({len(alerts)} instances)"
        
        # Update description to include count
        aggregated_description = f"{base_alert.description} Found {len(alerts)} instances in this file."
        
        # Update context to include line numbers
        line_numbers = sorted([alert.line_number for alert in alerts])
        if len(line_numbers) == 1:
            context = f"Line {line_numbers[0]}"
        elif len(line_numbers) <= 5:
            context = f"Lines: {', '.join(map(str, line_numbers))}"
        else:
            context = f"Lines: {line_numbers[0]}-{line_numbers[-1]} ({len(line_numbers)} total)"
        
        # Create aggregated alert
        aggregated_alert = ComplianceAlert(
            severity=base_alert.severity,
            framework=base_alert.framework,
            article_ref=base_alert.article_ref,
            title=aggregated_title,
            description=aggregated_description,
            file_path=base_alert.file_path,
            line_number=line_numbers[0],  # Use first line number
            context=context,
            remediation=base_alert.remediation,
            confidence=max(alert.confidence for alert in alerts),  # Use highest confidence
            category=base_alert.category,
            matched_text="",  # Clear matched text for aggregated alerts
            metadata={
                "aggregated": True,
                "instance_count": len(alerts),
                "line_numbers": line_numbers,
                "original_alerts": [alert.id for alert in alerts]
            }
        )
        
        return aggregated_alert
    
    def get_alert_statistics(self) -> Dict[str, Any]:
        """Get statistics about alerts generated."""
        return {
            "alerts_generated": self.alerts_generated,
            "alerts_filtered": self.alerts_filtered,
            "alert_groups": len(self.alert_groups),
            "license_tier": self.license_tier.value,
            "templates_loaded": len(self.alert_templates)
        }
    
    def reset_statistics(self) -> None:
        """Reset alert statistics."""
        self.alerts_generated = 0
        self.alerts_filtered = 0
        self.alert_groups.clear()
    
    def validate_alert_templates(self) -> Dict[str, Any]:
        """Validate alert templates for completeness."""
        validation_results = {
            "total_templates": len(self.alert_templates),
            "missing_fields": [],
            "invalid_severities": [],
            "invalid_articles": []
        }
        
        required_fields = ["title", "article_ref", "severity", "description", "remediation", "category"]
        valid_severities = [s.value for s in AlertSeverity]
        
        for template_name, template in self.alert_templates.items():
            # Check required fields
            for field in required_fields:
                if field not in template:
                    validation_results["missing_fields"].append(f"{template_name}.{field}")
            
            # Check severity validity
            if "severity" in template and template["severity"] not in valid_severities:
                validation_results["invalid_severities"].append(f"{template_name}.severity")
        
        validation_results["is_valid"] = (
            len(validation_results["missing_fields"]) == 0 and
            len(validation_results["invalid_severities"]) == 0
        )
        
        return validation_results
