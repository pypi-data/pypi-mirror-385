"""
Framework Mapper - GDPR-CCPA cross-framework mapping system.

Provides intelligent mapping between GDPR and CCPA violations, identifying
shared requirements and framework-specific obligations for unified compliance.
"""

import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum

from ..core.config import Config, LicenseTier
from ..core.exceptions import DetectionError
from .models import ComplianceIssue, ComplianceLevel, GDPRArticle, CCPAArticle, ComplianceFramework, FrameworkMapping


logger = logging.getLogger(__name__)


class ViolationType(str, Enum):
    """Types of violations for cross-framework mapping."""
    DATA_ACCESS_RIGHT = "data_access_right"
    DATA_DELETION_RIGHT = "data_deletion_right"
    OPT_OUT_RIGHT = "opt_out_right"
    DATA_SECURITY = "data_security"
    BREACH_NOTIFICATION = "breach_notification"
    NON_DISCRIMINATION = "non_discrimination"
    CONSENT_MANAGEMENT = "consent_management"
    DATA_MINIMIZATION = "data_minimization"
    CROSS_BORDER_TRANSFER = "cross_border_transfer"
    AUDIT_LOGGING = "audit_logging"


@dataclass
class CrossFrameworkMapping:
    """Detailed cross-framework mapping."""
    violation_type: ViolationType
    gdpr_articles: List[GDPRArticle]
    ccpa_articles: List[CCPAArticle]
    shared_requirements: List[str]
    gdpr_specific_requirements: List[str]
    ccpa_specific_requirements: List[str]
    mapping_confidence: float
    description: str


@dataclass
class MappingResult:
    """Result of cross-framework mapping."""
    primary_framework: ComplianceFramework
    primary_article: str
    mapped_frameworks: Dict[ComplianceFramework, str]
    violation_type: ViolationType
    shared_requirements: List[str]
    framework_specific_requirements: Dict[ComplianceFramework, List[str]]
    mapping_confidence: float


class FrameworkMapper:
    """
    GDPR-CCPA cross-framework mapping system.
    
    Provides intelligent mapping between GDPR and CCPA violations, identifying
    shared requirements and framework-specific obligations for unified compliance.
    """
    
    def __init__(self, config: Config):
        """Initialize the framework mapper."""
        self.config = config
        self.license_tier = config.license.tier
        
        # Initialize mapping rules
        self.mapping_rules = self._initialize_mapping_rules()
        
        # Initialize cross-framework mappings
        self.cross_framework_mappings = self._initialize_cross_framework_mappings()
        
        logger.info("Framework Mapper initialized successfully")
    
    def _initialize_mapping_rules(self) -> Dict[str, Dict[ComplianceFramework, str]]:
        """Initialize basic mapping rules between frameworks."""
        return {
            "data_access_right": {
                ComplianceFramework.GDPR: "Article 15",
                ComplianceFramework.CCPA: "§1798.100"
            },
            "data_deletion_right": {
                ComplianceFramework.GDPR: "Article 17",
                ComplianceFramework.CCPA: "§1798.105"
            },
            "opt_out_right": {
                ComplianceFramework.GDPR: "Article 21",
                ComplianceFramework.CCPA: "§1798.120"
            },
            "data_security": {
                ComplianceFramework.GDPR: "Article 32",
                ComplianceFramework.CCPA: "§1798.150"
            },
            "breach_notification": {
                ComplianceFramework.GDPR: "Article 33",
                ComplianceFramework.CCPA: "§1798.150"
            },
            "non_discrimination": {
                ComplianceFramework.GDPR: "Article 22",
                ComplianceFramework.CCPA: "§1798.125"
            },
            "consent_management": {
                ComplianceFramework.GDPR: "Article 7",
                ComplianceFramework.CCPA: "§1798.130"
            },
            "data_minimization": {
                ComplianceFramework.GDPR: "Article 5(1)(c)",
                ComplianceFramework.CCPA: "§1798.100"
            },
            "cross_border_transfer": {
                ComplianceFramework.GDPR: "Articles 44-49",
                ComplianceFramework.CCPA: "§1798.150"
            },
            "audit_logging": {
                ComplianceFramework.GDPR: "Article 30",
                ComplianceFramework.CCPA: "§1798.150"
            }
        }
    
    def _initialize_cross_framework_mappings(self) -> Dict[ViolationType, CrossFrameworkMapping]:
        """Initialize detailed cross-framework mappings."""
        return {
            ViolationType.DATA_ACCESS_RIGHT: CrossFrameworkMapping(
                violation_type=ViolationType.DATA_ACCESS_RIGHT,
                gdpr_articles=[GDPRArticle.ARTICLE_15],
                ccpa_articles=[CCPAArticle.SECTION_1798_100],
                shared_requirements=[
                    "Provide clear information about data collection",
                    "Allow individuals to access their personal data",
                    "Respond to data access requests within specified timeframes",
                    "Verify identity before providing data access"
                ],
                gdpr_specific_requirements=[
                    "Provide data in structured, machine-readable format",
                    "Include information about data processing purposes",
                    "Specify data retention periods",
                    "Inform about data subject rights"
                ],
                ccpa_specific_requirements=[
                    "Disclose categories of personal information collected",
                    "Explain purposes for data collection",
                    "Provide information about data sales",
                    "Include opt-out mechanisms"
                ],
                mapping_confidence=0.95,
                description="Right to access personal data - fundamental privacy right"
            ),
            
            ViolationType.DATA_DELETION_RIGHT: CrossFrameworkMapping(
                violation_type=ViolationType.DATA_DELETION_RIGHT,
                gdpr_articles=[GDPRArticle.ARTICLE_17],
                ccpa_articles=[CCPAArticle.SECTION_1798_105],
                shared_requirements=[
                    "Allow individuals to request data deletion",
                    "Verify identity before processing deletion requests",
                    "Respond to deletion requests within specified timeframes",
                    "Confirm deletion completion"
                ],
                gdpr_specific_requirements=[
                    "Handle deletion exceptions (legal obligations, public interest)",
                    "Inform third parties about deletion requests",
                    "Provide detailed deletion procedures",
                    "Maintain deletion logs"
                ],
                ccpa_specific_requirements=[
                    "Handle deletion exceptions (business purposes, legal obligations)",
                    "Provide clear deletion procedures",
                    "Maintain deletion records",
                    "Ensure service providers comply with deletion"
                ],
                mapping_confidence=0.90,
                description="Right to delete personal data - core privacy protection"
            ),
            
            ViolationType.OPT_OUT_RIGHT: CrossFrameworkMapping(
                violation_type=ViolationType.OPT_OUT_RIGHT,
                gdpr_articles=[GDPRArticle.ARTICLE_21],
                ccpa_articles=[CCPAArticle.SECTION_1798_120],
                shared_requirements=[
                    "Provide opt-out mechanisms",
                    "Honor opt-out requests promptly",
                    "Maintain opt-out status",
                    "Provide clear opt-out instructions"
                ],
                gdpr_specific_requirements=[
                    "Allow objection to processing for legitimate interests",
                    "Provide opt-out for direct marketing",
                    "Handle opt-out for automated decision-making",
                    "Inform about opt-out consequences"
                ],
                ccpa_specific_requirements=[
                    "Provide opt-out for data sales",
                    "Implement "Do Not Sell" mechanisms",
                    "Maintain opt-out status for 12 months",
                    "Provide clear opt-out instructions"
                ],
                mapping_confidence=0.85,
                description="Right to opt-out of data processing/sales"
            ),
            
            ViolationType.DATA_SECURITY: CrossFrameworkMapping(
                violation_type=ViolationType.DATA_SECURITY,
                gdpr_articles=[GDPRArticle.ARTICLE_32],
                ccpa_articles=[CCPAArticle.SECTION_1798_150],
                shared_requirements=[
                    "Implement appropriate technical measures",
                    "Protect against unauthorized access",
                    "Ensure data confidentiality and integrity",
                    "Regular security assessments"
                ],
                gdpr_specific_requirements=[
                    "Implement data protection by design",
                    "Conduct Data Protection Impact Assessments",
                    "Appoint Data Protection Officer if required",
                    "Implement breach notification procedures"
                ],
                ccpa_specific_requirements=[
                    "Implement reasonable security measures",
                    "Protect consumer data from unauthorized access",
                    "Implement breach notification procedures",
                    "Maintain security incident logs"
                ],
                mapping_confidence=0.95,
                description="Data security requirements - fundamental protection"
            ),
            
            ViolationType.BREACH_NOTIFICATION: CrossFrameworkMapping(
                violation_type=ViolationType.BREACH_NOTIFICATION,
                gdpr_articles=[GDPRArticle.ARTICLE_33, GDPRArticle.ARTICLE_34],
                ccpa_articles=[CCPAArticle.SECTION_1798_150],
                shared_requirements=[
                    "Notify authorities of data breaches",
                    "Notify affected individuals",
                    "Document breach incidents",
                    "Implement breach response procedures"
                ],
                gdpr_specific_requirements=[
                    "Notify supervisory authority within 72 hours",
                    "Notify data subjects without undue delay",
                    "Provide detailed breach information",
                    "Maintain breach notification records"
                ],
                ccpa_specific_requirements=[
                    "Notify affected consumers",
                    "Provide breach information",
                    "Implement breach response procedures",
                    "Maintain breach records"
                ],
                mapping_confidence=0.90,
                description="Breach notification requirements"
            ),
            
            ViolationType.NON_DISCRIMINATION: CrossFrameworkMapping(
                violation_type=ViolationType.NON_DISCRIMINATION,
                gdpr_articles=[GDPRArticle.ARTICLE_22],
                ccpa_articles=[CCPAArticle.SECTION_1798_125],
                shared_requirements=[
                    "Provide equal service regardless of privacy choices",
                    "Avoid discrimination based on privacy rights",
                    "Maintain service quality",
                    "Respect individual choices"
                ],
                gdpr_specific_requirements=[
                    "Avoid automated decision-making discrimination",
                    "Provide human intervention options",
                    "Explain automated decision logic",
                    "Ensure fairness in processing"
                ],
                ccpa_specific_requirements=[
                    "Avoid discrimination for exercising privacy rights",
                    "Maintain equal service quality",
                    "Avoid differential pricing",
                    "Respect consumer choices"
                ],
                mapping_confidence=0.85,
                description="Non-discrimination requirements"
            )
        }
    
    def map_violation(self, issue: ComplianceIssue) -> MappingResult:
        """
        Map a compliance issue to other frameworks.
        
        Args:
            issue: Compliance issue to map
            
        Returns:
            Mapping result with cross-framework information
        """
        try:
            # Determine violation type
            violation_type = self._classify_violation_type(issue)
            
            # Get mapping rules
            if violation_type not in self.mapping_rules:
                return self._create_no_mapping_result(issue)
            
            mapping_rules = self.mapping_rules[violation_type]
            
            # Find mapped frameworks
            mapped_frameworks = {}
            for framework, article_ref in mapping_rules.items():
                if framework != issue.framework:
                    mapped_frameworks[framework] = article_ref
            
            # Get detailed mapping information
            cross_mapping = self.cross_framework_mappings.get(violation_type)
            
            if cross_mapping:
                shared_requirements = cross_mapping.shared_requirements
                framework_specific_requirements = {
                    ComplianceFramework.GDPR: cross_mapping.gdpr_specific_requirements,
                    ComplianceFramework.CCPA: cross_mapping.ccpa_specific_requirements
                }
                mapping_confidence = cross_mapping.mapping_confidence
            else:
                shared_requirements = []
                framework_specific_requirements = {}
                mapping_confidence = 0.5
            
            return MappingResult(
                primary_framework=issue.framework,
                primary_article=issue.article_ref.value,
                mapped_frameworks=mapped_frameworks,
                violation_type=violation_type,
                shared_requirements=shared_requirements,
                framework_specific_requirements=framework_specific_requirements,
                mapping_confidence=mapping_confidence
            )
            
        except Exception as e:
            logger.error(f"Failed to map violation: {e}")
            return self._create_no_mapping_result(issue)
    
    def _classify_violation_type(self, issue: ComplianceIssue) -> ViolationType:
        """Classify violation type for cross-framework mapping."""
        article = issue.article_ref.value.lower()
        
        # GDPR to violation type mapping
        if "article 15" in article or "right of access" in article:
            return ViolationType.DATA_ACCESS_RIGHT
        elif "article 17" in article or "right to erasure" in article:
            return ViolationType.DATA_DELETION_RIGHT
        elif "article 21" in article or "right to object" in article:
            return ViolationType.OPT_OUT_RIGHT
        elif "article 32" in article or "security" in article:
            return ViolationType.DATA_SECURITY
        elif "article 33" in article or "article 34" in article or "breach" in article:
            return ViolationType.BREACH_NOTIFICATION
        elif "article 22" in article or "discrimination" in article:
            return ViolationType.NON_DISCRIMINATION
        elif "article 7" in article or "consent" in article:
            return ViolationType.CONSENT_MANAGEMENT
        elif "article 5" in article or "minimization" in article:
            return ViolationType.DATA_MINIMIZATION
        elif "article 44" in article or "transfer" in article:
            return ViolationType.CROSS_BORDER_TRANSFER
        elif "article 30" in article or "logging" in article:
            return ViolationType.AUDIT_LOGGING
        
        # CCPA to violation type mapping
        elif "§1798.100" in article or "right to know" in article:
            return ViolationType.DATA_ACCESS_RIGHT
        elif "§1798.105" in article or "right to delete" in article:
            return ViolationType.DATA_DELETION_RIGHT
        elif "§1798.120" in article or "opt-out" in article:
            return ViolationType.OPT_OUT_RIGHT
        elif "§1798.150" in article or "security" in article:
            return ViolationType.DATA_SECURITY
        elif "§1798.125" in article or "discrimination" in article:
            return ViolationType.NON_DISCRIMINATION
        elif "§1798.130" in article or "notice" in article:
            return ViolationType.CONSENT_MANAGEMENT
        
        return ViolationType.DATA_SECURITY  # Default fallback
    
    def _create_no_mapping_result(self, issue: ComplianceIssue) -> MappingResult:
        """Create a result when no mapping is available."""
        return MappingResult(
            primary_framework=issue.framework,
            primary_article=issue.article_ref.value,
            mapped_frameworks={},
            violation_type=ViolationType.DATA_SECURITY,
            shared_requirements=[],
            framework_specific_requirements={},
            mapping_confidence=0.0
        )
    
    def get_shared_violations(self, issues: List[ComplianceIssue]) -> Dict[ViolationType, List[ComplianceIssue]]:
        """
        Group violations by type to identify shared requirements.
        
        Args:
            issues: List of compliance issues
            
        Returns:
            Dictionary mapping violation types to issues
        """
        shared_violations = {}
        
        for issue in issues:
            violation_type = self._classify_violation_type(issue)
            
            if violation_type not in shared_violations:
                shared_violations[violation_type] = []
            
            shared_violations[violation_type].append(issue)
        
        return shared_violations
    
    def generate_cross_framework_insights(self, issues: List[ComplianceIssue]) -> Dict[str, Any]:
        """
        Generate insights about cross-framework compliance.
        
        Args:
            issues: List of compliance issues
            
        Returns:
            Cross-framework insights
        """
        insights = {
            "total_issues": len(issues),
            "framework_distribution": {},
            "shared_violations": {},
            "mapping_opportunities": [],
            "compliance_gaps": [],
            "recommendations": []
        }
        
        # Count issues by framework
        for issue in issues:
            framework = issue.framework.value
            insights["framework_distribution"][framework] = insights["framework_distribution"].get(framework, 0) + 1
        
        # Identify shared violations
        shared_violations = self.get_shared_violations(issues)
        for violation_type, violation_issues in shared_violations.items():
            if len(violation_issues) > 1:
                insights["shared_violations"][violation_type.value] = {
                    "count": len(violation_issues),
                    "frameworks": list(set(issue.framework.value for issue in violation_issues)),
                    "issues": [issue.id for issue in violation_issues]
                }
        
        # Identify mapping opportunities
        for issue in issues:
            mapping_result = self.map_violation(issue)
            if mapping_result.mapped_frameworks:
                insights["mapping_opportunities"].append({
                    "issue_id": issue.id,
                    "primary_framework": issue.framework.value,
                    "mapped_frameworks": list(mapping_result.mapped_frameworks.keys()),
                    "violation_type": mapping_result.violation_type.value,
                    "confidence": mapping_result.mapping_confidence
                })
        
        # Generate recommendations
        if insights["shared_violations"]:
            insights["recommendations"].append("Address shared violations across frameworks simultaneously")
        
        if insights["mapping_opportunities"]:
            insights["recommendations"].append("Leverage cross-framework mappings for unified compliance")
        
        # Check for compliance gaps
        available_frameworks = set(issue.framework for issue in issues)
        if len(available_frameworks) < 2:
            insights["compliance_gaps"].append("Limited cross-framework coverage")
        
        return insights
    
    def validate_framework_coverage(self, issues: List[ComplianceIssue]) -> Dict[str, Any]:
        """
        Validate framework coverage and identify gaps.
        
        Args:
            issues: List of compliance issues
            
        Returns:
            Coverage validation results
        """
        validation_result = {
            "gdpr_coverage": False,
            "ccpa_coverage": False,
            "coverage_gaps": [],
            "recommendations": []
        }
        
        # Check framework coverage
        frameworks_covered = set(issue.framework for issue in issues)
        
        if ComplianceFramework.GDPR in frameworks_covered:
            validation_result["gdpr_coverage"] = True
        else:
            validation_result["coverage_gaps"].append("GDPR compliance not analyzed")
        
        if ComplianceFramework.CCPA in frameworks_covered:
            validation_result["ccpa_coverage"] = True
        else:
            validation_result["coverage_gaps"].append("CCPA compliance not analyzed")
        
        # Generate recommendations
        if not validation_result["gdpr_coverage"]:
            validation_result["recommendations"].append("Enable GDPR compliance analysis")
        
        if not validation_result["ccpa_coverage"]:
            validation_result["recommendations"].append("Enable CCPA compliance analysis")
        
        if validation_result["coverage_gaps"]:
            validation_result["recommendations"].append("Implement comprehensive multi-framework compliance")
        
        return validation_result
    
    def get_framework_mapping_summary(self) -> Dict[str, Any]:
        """Get summary of framework mapping capabilities."""
        return {
            "supported_frameworks": [f.value for f in ComplianceFramework if f != ComplianceFramework.ALL],
            "violation_types_mapped": len(self.mapping_rules),
            "cross_framework_mappings": len(self.cross_framework_mappings),
            "mapping_confidence_average": sum(m.mapping_confidence for m in self.cross_framework_mappings.values()) / len(self.cross_framework_mappings),
            "license_tier": self.license_tier.value,
            "capabilities": {
                "violation_classification": True,
                "cross_framework_mapping": True,
                "shared_requirement_identification": True,
                "compliance_gap_analysis": True,
                "unified_recommendations": True
            }
        }
