"""
GDPR Compliance Engine for Levox - Production-grade compliance auditing.

This module provides comprehensive GDPR compliance analysis integrated with the existing
Levox detection pipeline. It includes Article 32 security checks, DSAR automation,
right to be forgotten analysis, and cross-border data transfer detection.
"""

import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime

from ..core.config import Config, LicenseTier, ThreadSafeConfig
from ..core.exceptions import DetectionError, LicenseError
from ..models.detection_result import DetectionResult, FileResult
from .gdpr_analyzer import GDPRAnalyzer
from .audit_logger import ComplianceAuditLogger
from .reporting import ComplianceReporter
from .models import ComplianceIssue, ComplianceResult, GDPRArticle, ComplianceLevel


logger = logging.getLogger(__name__)


@dataclass
class ComplianceAuditOptions:
    """Configuration options for compliance audits."""
    gdpr_check_level: str = "standard"  # basic, standard, strict
    include_security_checks: bool = True
    include_dsar_checks: bool = True
    include_deletion_checks: bool = True
    include_transfer_checks: bool = True
    audit_log_retention_days: int = 90
    enable_crypto_verification: bool = True
    compliance_score_threshold: float = 70.0


class GDPRComplianceEngine:
    """
    Production-grade GDPR compliance engine that integrates seamlessly with Levox.
    
    This engine runs GDPR compliance checks in sequence with AST, regex, and ML detectors,
    providing comprehensive compliance analysis with full license tier integration.
    """
    
    def __init__(self, config: Optional[Config] = None, config_path: Optional[str] = None):
        """Initialize the GDPR compliance engine."""
        # Store config for lazy initialization of detection engine
        self._config = config
        self._config_path = config_path
        self._detection_engine = None  # Lazy-loaded
        
        # Get configuration wrapper
        if config_path:
            self.config_wrapper = ThreadSafeConfig(Config.from_file(config_path), Path(config_path))
        elif config:
            self.config_wrapper = ThreadSafeConfig(config)
        else:
            self.config_wrapper = ThreadSafeConfig(Config())
        
        # Initialize compliance components
        self.gdpr_analyzer = GDPRAnalyzer(self.config_wrapper.get_config())
        self.audit_logger = ComplianceAuditLogger(self.config_wrapper.get_config())
        self.reporter = ComplianceReporter(self.config_wrapper.get_config())
        
        # Validate license tier for compliance features
        self._validate_license_tier()
        
        logger.info("GDPR Compliance Engine initialized successfully")
    
    @property
    def detection_engine(self):
        """Lazy-loaded detection engine to avoid circular imports."""
        if self._detection_engine is None:
            # Import here to avoid circular dependency
            from ..core.engine import DetectionEngine
            self._detection_engine = DetectionEngine(self._config, self._config_path)
        return self._detection_engine
    
    def _validate_license_tier(self) -> None:
        """Validate that the current license tier supports compliance features."""
        config = self.config_wrapper.get_config()
        license_tier = config.license.tier
        
        if license_tier == LicenseTier.STANDARD:
            logger.warning("Standard license tier detected. Some compliance features may be limited.")
        elif license_tier in [LicenseTier.PREMIUM, LicenseTier.ENTERPRISE]:
            logger.info(f"Premium license tier detected: {license_tier}. Full compliance features available.")
        else:
            logger.warning(f"Unknown license tier: {license_tier}. Defaulting to standard features.")
    
    def run_compliance_audit(self, project_path: str, options: Optional[ComplianceAuditOptions] = None) -> ComplianceResult:
        """
        Run a comprehensive GDPR compliance audit on the specified project.
        
        Args:
            project_path: Path to the project directory to audit
            options: Optional compliance audit configuration
            
        Returns:
            ComplianceResult containing comprehensive audit findings
            
        Raises:
            DetectionError: If the audit process fails
            LicenseError: If license tier doesn't support requested features
        """
        start_time = datetime.now()
        project_path = Path(project_path)
        
        if not project_path.exists():
            raise DetectionError(f"Project path does not exist: {project_path}")
        
        logger.info(f"Starting GDPR compliance audit for project: {project_path}")
        
        # Use default options if none provided
        if options is None:
            options = ComplianceAuditOptions()
        
        # Validate license tier for requested features
        self._validate_compliance_features(options)
        
        try:
            # Step 1: Run standard PII detection
            logger.info("Running standard PII detection...")
            detection_result = self.detection_engine.scan_project(str(project_path))
            
            # Step 2: Run GDPR-specific compliance analysis
            logger.info("Running GDPR compliance analysis...")
            compliance_issues = self.gdpr_analyzer.analyze_project(
                project_path, 
                detection_result,
                options
            )
            
            # Step 3: Generate compliance score
            compliance_score = self._calculate_compliance_score(compliance_issues)
            
            # Step 4: Create comprehensive result
            compliance_result = ComplianceResult(
                project_path=str(project_path),
                audit_timestamp=start_time,
                completion_timestamp=datetime.now(),
                compliance_score=compliance_score,
                total_issues=len(compliance_issues),
                issues_by_severity=self._group_issues_by_severity(compliance_issues),
                issues_by_article=self._group_issues_by_article(compliance_issues),
                detection_result=detection_result,
                compliance_issues=compliance_issues,
                audit_options=options
            )
            
            # Step 5: Log audit results
            self.audit_logger.log_compliance_audit(compliance_result)
            
            # Step 6: Generate detailed report
            report = self.reporter.generate_compliance_report(compliance_result)
            compliance_result.report = report
            
            logger.info(f"GDPR compliance audit completed successfully. Score: {compliance_score:.1f}/100")
            
            return compliance_result
            
        except Exception as e:
            logger.error(f"GDPR compliance audit failed: {e}")
            self.audit_logger.log_audit_error(str(project_path), str(e))
            raise DetectionError(f"Compliance audit failed: {e}")
    
    def _validate_compliance_features(self, options: ComplianceAuditOptions) -> None:
        """Validate that the current license tier supports requested compliance features."""
        config = self.config_wrapper.get_config()
        license_tier = config.license.tier
        
        # Check for enterprise-only features
        if options.enable_crypto_verification and license_tier != LicenseTier.ENTERPRISE:
            logger.warning("Cryptographic verification requires Enterprise license tier")
            options.enable_crypto_verification = False
        
        if options.gdpr_check_level == "strict" and license_tier == LicenseTier.STANDARD:
            logger.warning("Strict GDPR checks require Premium or Enterprise license tier")
            options.gdpr_check_level = "standard"
    
    def _calculate_compliance_score(self, issues: List[ComplianceIssue]) -> float:
        """Calculate GDPR compliance score (0-100) based on issue severity and coverage."""
        if not issues:
            return 100.0
        
        # Weight factors for different severity levels
        severity_weights = {
            ComplianceLevel.CRITICAL: 10.0,
            ComplianceLevel.HIGH: 7.0,
            ComplianceLevel.MEDIUM: 4.0,
            ComplianceLevel.LOW: 1.0
        }
        
        total_weight = 0.0
        weighted_penalty = 0.0
        
        for issue in issues:
            weight = severity_weights.get(issue.severity, 1.0)
            total_weight += weight
            weighted_penalty += weight * 2.0  # Each issue reduces score by 2 points per weight
        
        # Calculate base score (100 - penalties)
        base_score = max(0.0, 100.0 - weighted_penalty)
        
        # Apply coverage bonus (bonus for comprehensive checking)
        coverage_bonus = min(10.0, total_weight * 0.5)
        
        final_score = min(100.0, base_score + coverage_bonus)
        
        return round(final_score, 1)
    
    def _group_issues_by_severity(self, issues: List[ComplianceIssue]) -> Dict[ComplianceLevel, int]:
        """Group compliance issues by severity level."""
        grouped = {}
        for issue in issues:
            severity = issue.severity
            grouped[severity] = grouped.get(severity, 0) + 1
        return grouped
    
    def _group_issues_by_article(self, issues: List[ComplianceIssue]) -> Dict[GDPRArticle, int]:
        """Group compliance issues by GDPR article."""
        grouped = {}
        for issue in issues:
            article = issue.article_ref
            grouped[article] = grouped.get(article, 0) + 1
        return grouped
    
    def get_compliance_summary(self, project_path: str) -> Dict[str, Any]:
        """Get a quick compliance summary without full audit."""
        try:
            # Run a lightweight compliance check
            options = ComplianceAuditOptions()
            options.gdpr_check_level = "basic"
            options.include_security_checks = True
            options.include_dsar_checks = False
            options.include_deletion_checks = False
            options.include_transfer_checks = False
            
            result = self.run_compliance_audit(project_path, options)
            
            return {
                "compliance_score": result.compliance_score,
                "total_issues": result.total_issues,
                "critical_issues": result.issues_by_severity.get(ComplianceLevel.CRITICAL, 0),
                "high_issues": result.issues_by_severity.get(ComplianceLevel.HIGH, 0),
                "audit_timestamp": result.audit_timestamp.isoformat(),
                "status": "compliant" if result.compliance_score >= 80 else "needs_attention"
            }
            
        except Exception as e:
            logger.error(f"Failed to generate compliance summary: {e}")
            return {
                "error": str(e),
                "status": "failed"
            }


# Export main classes and types
__all__ = [
    'GDPRComplianceEngine',
    'ComplianceAuditOptions',
    'ComplianceResult',
    'ComplianceIssue',
    'GDPRArticle',
    'ComplianceLevel'
]
