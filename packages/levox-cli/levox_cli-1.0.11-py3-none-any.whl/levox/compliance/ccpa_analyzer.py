"""
CCPA Compliance Analyzer - California Consumer Privacy Act compliance detection.

Provides comprehensive CCPA compliance analysis with article mapping (§1798.100-1798.199),
pattern detection, and violation identification for California Consumer Privacy Act.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import re

from ..core.config import Config, LicenseTier
from ..core.exceptions import DetectionError
from ..models.detection_result import DetectionResult, DetectionMatch
from .models import ComplianceIssue, ComplianceLevel
from .gdpr_analyzer import GDPRAnalyzer


logger = logging.getLogger(__name__)


class CCPAArticle(str, Enum):
    """CCPA articles with descriptions and requirements."""
    
    # Consumer Rights
    SECTION_1798_100 = "§1798.100"  # Right to Know
    SECTION_1798_105 = "§1798.105"  # Right to Delete
    SECTION_1798_110 = "§1798.110"  # Right to Opt-Out
    SECTION_1798_115 = "§1798.115"  # Right to Non-Discrimination
    SECTION_1798_120 = "§1798.120"  # Right to Opt-Out of Sale
    SECTION_1798_125 = "§1798.125"  # Non-Discrimination Rights
    
    # Business Obligations
    SECTION_1798_130 = "§1798.130"  # Notice Requirements
    SECTION_1798_135 = "§1798.135"  # Opt-Out Mechanisms
    SECTION_1798_140 = "§1798.140"  # Definitions
    SECTION_1798_145 = "§1798.145"  # Exceptions
    SECTION_1798_150 = "§1798.150"  # Data Security Requirements
    SECTION_1798_155 = "§1798.155"  # Enforcement
    
    @property
    def title(self) -> str:
        """Get article title."""
        titles = {
            self.SECTION_1798_100: "Right to Know",
            self.SECTION_1798_105: "Right to Delete",
            self.SECTION_1798_110: "Right to Opt-Out",
            self.SECTION_1798_115: "Right to Non-Discrimination",
            self.SECTION_1798_120: "Right to Opt-Out of Sale",
            self.SECTION_1798_125: "Non-Discrimination Rights",
            self.SECTION_1798_130: "Notice Requirements",
            self.SECTION_1798_135: "Opt-Out Mechanisms",
            self.SECTION_1798_140: "Definitions",
            self.SECTION_1798_145: "Exceptions",
            self.SECTION_1798_150: "Data Security Requirements",
            self.SECTION_1798_155: "Enforcement"
        }
        return titles.get(self, f"CCPA {self}")
    
    @property
    def description(self) -> str:
        """Get article description."""
        descriptions = {
            self.SECTION_1798_100: "Consumers have the right to know what personal information is collected, used, shared, or sold.",
            self.SECTION_1798_105: "Consumers have the right to request deletion of their personal information.",
            self.SECTION_1798_110: "Consumers have the right to opt-out of the sale of their personal information.",
            self.SECTION_1798_115: "Consumers have the right to non-discrimination for exercising their privacy rights.",
            self.SECTION_1798_120: "Consumers have the right to opt-out of the sale of personal information.",
            self.SECTION_1798_125: "Businesses cannot discriminate against consumers who exercise their privacy rights.",
            self.SECTION_1798_130: "Businesses must provide clear notices about data collection and use.",
            self.SECTION_1798_135: "Businesses must provide easy-to-use opt-out mechanisms.",
            self.SECTION_1798_140: "Definitions of key terms under CCPA.",
            self.SECTION_1798_145: "Exceptions to CCPA requirements.",
            self.SECTION_1798_150: "Businesses must implement reasonable security measures.",
            self.SECTION_1798_155: "Enforcement mechanisms and penalties."
        }
        return descriptions.get(self, f"CCPA {self} requirements")


@dataclass
class CCPAPattern:
    """CCPA-specific detection pattern."""
    name: str
    pattern: str
    article: CCPAArticle
    severity: ComplianceLevel
    description: str
    remediation: str
    confidence_threshold: float = 0.7


class CCPAAnalyzer:
    """
    CCPA compliance analyzer with article mapping and pattern detection.
    
    Provides comprehensive CCPA compliance analysis including consumer rights,
    business obligations, and data security requirements.
    """
    
    def __init__(self, config: Config):
        """Initialize the CCPA analyzer."""
        self.config = config
        self.license_tier = config.license.tier
        
        # Initialize CCPA patterns
        self.ccpa_patterns = self._initialize_ccpa_patterns()
        
        # Initialize GDPR analyzer for shared patterns
        self.gdpr_analyzer = GDPRAnalyzer(config)
        
        logger.info("CCPA Analyzer initialized successfully")
    
    def _initialize_ccpa_patterns(self) -> List[CCPAPattern]:
        """Initialize CCPA-specific detection patterns."""
        return [
            # Section 1798.100 - Right to Know
            CCPAPattern(
                name="ccpa_data_access_endpoint",
                pattern=r'\b(?:ccpa_access|data_access|personal_info_request|consumer_data_request)\b',
                article=CCPAArticle.SECTION_1798_100,
                severity=ComplianceLevel.HIGH,
                description="CCPA data access request endpoint detected",
                remediation="Implement comprehensive data access functionality for consumers"
            ),
            CCPAPattern(
                name="ccpa_data_collection_notice",
                pattern=r'\b(?:privacy_notice|data_collection_notice|ccpa_notice)\b',
                article=CCPAArticle.SECTION_1798_100,
                severity=ComplianceLevel.MEDIUM,
                description="Data collection notice for CCPA compliance",
                remediation="Ensure privacy notices clearly explain data collection practices"
            ),
            
            # Section 1798.105 - Right to Delete
            CCPAPattern(
                name="ccpa_data_deletion_endpoint",
                pattern=r'\b(?:ccpa_delete|data_deletion|personal_info_deletion|consumer_deletion)\b',
                article=CCPAArticle.SECTION_1798_105,
                severity=ComplianceLevel.HIGH,
                description="CCPA data deletion request endpoint detected",
                remediation="Implement comprehensive data deletion functionality"
            ),
            CCPAPattern(
                name="ccpa_deletion_confirmation",
                pattern=r'\b(?:deletion_confirmed|data_deleted|personal_info_removed)\b',
                article=CCPAArticle.SECTION_1798_105,
                severity=ComplianceLevel.MEDIUM,
                description="Data deletion confirmation mechanism",
                remediation="Provide clear confirmation when data is deleted"
            ),
            
            # Section 1798.120 - Right to Opt-Out of Sale
            CCPAPattern(
                name="ccpa_opt_out_endpoint",
                pattern=r'\b(?:ccpa_opt_out|do_not_sell|opt_out_sale|consumer_opt_out)\b',
                article=CCPAArticle.SECTION_1798_120,
                severity=ComplianceLevel.HIGH,
                description="CCPA opt-out of sale endpoint detected",
                remediation="Implement opt-out mechanisms for data sales"
            ),
            CCPAPattern(
                name="ccpa_sale_indicator",
                pattern=r'\b(?:sells?|sale|selling)\s+(?:personal|consumer)\s+(?:data|information)\b',
                article=CCPAArticle.SECTION_1798_120,
                severity=ComplianceLevel.MEDIUM,
                description="Indication of personal data sales",
                remediation="Ensure opt-out mechanisms are available for data sales"
            ),
            
            # Section 1798.125 - Non-Discrimination
            CCPAPattern(
                name="ccpa_discrimination_check",
                pattern=r'\b(?:non_discrimination|equal_service|privacy_choice_discrimination)\b',
                article=CCPAArticle.SECTION_1798_125,
                severity=ComplianceLevel.HIGH,
                description="Non-discrimination policy for privacy choices",
                remediation="Ensure equal service regardless of privacy choices"
            ),
            CCPAPattern(
                name="ccpa_differential_treatment",
                pattern=r'\b(?:different_service|reduced_service|privacy_penalty)\b',
                article=CCPAArticle.SECTION_1798_125,
                severity=ComplianceLevel.CRITICAL,
                description="Potential discrimination based on privacy choices",
                remediation="Remove any differential treatment based on privacy choices"
            ),
            
            # Section 1798.130 - Notice Requirements
            CCPAPattern(
                name="ccpa_privacy_policy",
                pattern=r'\b(?:privacy_policy|ccpa_policy|consumer_privacy_policy)\b',
                article=CCPAArticle.SECTION_1798_130,
                severity=ComplianceLevel.MEDIUM,
                description="CCPA-compliant privacy policy",
                remediation="Ensure privacy policy includes all required CCPA disclosures"
            ),
            CCPAPattern(
                name="ccpa_data_categories",
                pattern=r'\b(?:data_categories|personal_info_categories|collected_data_types)\b',
                article=CCPAArticle.SECTION_1798_130,
                severity=ComplianceLevel.MEDIUM,
                description="Data categories disclosure",
                remediation="Clearly disclose all categories of personal information collected"
            ),
            
            # Section 1798.135 - Opt-Out Mechanisms
            CCPAPattern(
                name="ccpa_opt_out_link",
                pattern=r'\b(?:do_not_sell_link|opt_out_link|privacy_choices_link)\b',
                article=CCPAArticle.SECTION_1798_135,
                severity=ComplianceLevel.HIGH,
                description="Opt-out mechanism link",
                remediation="Provide easily accessible opt-out mechanisms"
            ),
            CCPAPattern(
                name="ccpa_opt_out_button",
                pattern=r'\b(?:do_not_sell_button|opt_out_button|privacy_button)\b',
                article=CCPAArticle.SECTION_1798_135,
                severity=ComplianceLevel.HIGH,
                description="Opt-out mechanism button",
                remediation="Implement prominent opt-out buttons"
            ),
            
            # Section 1798.150 - Data Security
            CCPAPattern(
                name="ccpa_data_security",
                pattern=r'\b(?:ccpa_security|consumer_data_security|personal_info_protection)\b',
                article=CCPAArticle.SECTION_1798_150,
                severity=ComplianceLevel.HIGH,
                description="CCPA data security measures",
                remediation="Implement reasonable security measures for consumer data"
            ),
            CCPAPattern(
                name="ccpa_breach_notification",
                pattern=r'\b(?:ccpa_breach|consumer_breach_notification|data_breach_ccpa)\b',
                article=CCPAArticle.SECTION_1798_150,
                severity=ComplianceLevel.HIGH,
                description="CCPA breach notification",
                remediation="Implement breach notification procedures"
            ),
            
            # Negative patterns (violations)
            CCPAPattern(
                name="ccpa_missing_access",
                pattern=r'(?<!ccpa_|consumer_|personal_info_)(?:access|request)\s+(?:data|information)(?!.*ccpa)',
                article=CCPAArticle.SECTION_1798_100,
                severity=ComplianceLevel.MEDIUM,
                description="Potential missing CCPA data access functionality",
                remediation="Implement CCPA-compliant data access requests"
            ),
            CCPAPattern(
                name="ccpa_missing_deletion",
                pattern=r'(?<!ccpa_|consumer_|personal_info_)(?:delete|remove)\s+(?:data|information)(?!.*ccpa)',
                article=CCPAArticle.SECTION_1798_105,
                severity=ComplianceLevel.MEDIUM,
                description="Potential missing CCPA data deletion functionality",
                remediation="Implement CCPA-compliant data deletion requests"
            ),
            CCPAPattern(
                name="ccpa_missing_opt_out",
                pattern=r'(?<!ccpa_|consumer_|do_not_sell_)(?:opt_out|optout)(?!.*ccpa)',
                article=CCPAArticle.SECTION_1798_120,
                severity=ComplianceLevel.MEDIUM,
                description="Potential missing CCPA opt-out functionality",
                remediation="Implement CCPA-compliant opt-out mechanisms"
            )
        ]
    
    def analyze_compliance(self, results: DetectionResult) -> List[ComplianceIssue]:
        """
        Analyze CCPA compliance from detection results.
        
        Args:
            results: Detection results from scan
            
        Returns:
            List of CCPA compliance issues
        """
        try:
            compliance_issues = []
            
            # Analyze each file result
            for file_result in results.file_results:
                file_issues = self._analyze_file_compliance(file_result)
                compliance_issues.extend(file_issues)
            
            # Filter patterns based on license tier
            filtered_issues = self._filter_by_license_tier(compliance_issues)
            
            logger.info(f"CCPA compliance analysis completed: {len(filtered_issues)} issues found")
            return filtered_issues
            
        except Exception as e:
            logger.error(f"Failed to analyze CCPA compliance: {e}")
            raise DetectionError(f"CCPA compliance analysis failed: {e}")
    
    def _analyze_file_compliance(self, file_result) -> List[ComplianceIssue]:
        """Analyze CCPA compliance for a single file."""
        issues = []
        
        # Get file content for context analysis
        try:
            with open(file_result.file_path, 'r', encoding='utf-8', errors='ignore') as f:
                file_content = f.read()
        except Exception:
            file_content = ""
        
        # Check for CCPA patterns
        for pattern in self.ccpa_patterns:
            matches = re.finditer(pattern.pattern, file_content, re.IGNORECASE | re.MULTILINE)
            
            for match in matches:
                # Calculate confidence based on context
                confidence = self._calculate_pattern_confidence(match, file_content, pattern)
                
                if confidence >= pattern.confidence_threshold:
                    issue = ComplianceIssue(
                        article_ref=pattern.article,
                        severity=pattern.severity,
                        description=pattern.description,
                        file_path=str(file_result.file_path),
                        line_number=self._get_line_number(file_content, match.start()),
                        evidence=match.group(0),
                        remediation=pattern.remediation,
                        confidence=confidence,
                        category="CCPA Compliance",
                        check_type="pattern_detection",
                        created_at=datetime.now()
                    )
                    issues.append(issue)
        
        # Check for missing CCPA requirements
        missing_issues = self._check_missing_ccpa_requirements(file_content, file_result.file_path)
        issues.extend(missing_issues)
        
        return issues
    
    def _calculate_pattern_confidence(self, match, file_content: str, pattern: CCPAPattern) -> float:
        """Calculate confidence score for a pattern match."""
        base_confidence = 0.8
        
        # Context analysis
        context_start = max(0, match.start() - 100)
        context_end = min(len(file_content), match.end() + 100)
        context = file_content[context_start:context_end].lower()
        
        # Boost confidence for specific CCPA keywords
        ccpa_keywords = ['ccpa', 'california', 'consumer', 'privacy', 'personal information']
        keyword_boost = sum(0.1 for keyword in ccpa_keywords if keyword in context)
        
        # Boost confidence for API endpoint patterns
        if any(endpoint in context for endpoint in ['/api/', 'endpoint', 'route', 'controller']):
            keyword_boost += 0.1
        
        # Reduce confidence for test files
        if any(test_indicator in context for test_indicator in ['test', 'mock', 'example', 'sample']):
            keyword_boost -= 0.2
        
        final_confidence = min(1.0, base_confidence + keyword_boost)
        return max(0.0, final_confidence)
    
    def _get_line_number(self, content: str, position: int) -> int:
        """Get line number for a position in content."""
        return content[:position].count('\n') + 1
    
    def _check_missing_ccpa_requirements(self, file_content: str, file_path: str) -> List[ComplianceIssue]:
        """Check for missing CCPA requirements."""
        issues = []
        
        # Check for missing data access functionality
        if not re.search(r'\b(?:ccpa_access|data_access|personal_info_request)\b', file_content, re.IGNORECASE):
            if self._is_api_file(file_path):
                issues.append(ComplianceIssue(
                    article_ref=CCPAArticle.SECTION_1798_100,
                    severity=ComplianceLevel.MEDIUM,
                    description="Missing CCPA data access request functionality",
                    file_path=file_path,
                    line_number=1,
                    evidence="No CCPA data access endpoints detected",
                    remediation="Implement CCPA-compliant data access request endpoints",
                    confidence=0.6,
                    category="CCPA Compliance",
                    check_type="missing_requirement",
                    created_at=datetime.now()
                ))
        
        # Check for missing data deletion functionality
        if not re.search(r'\b(?:ccpa_delete|data_deletion|personal_info_deletion)\b', file_content, re.IGNORECASE):
            if self._is_api_file(file_path):
                issues.append(ComplianceIssue(
                    article_ref=CCPAArticle.SECTION_1798_105,
                    severity=ComplianceLevel.MEDIUM,
                    description="Missing CCPA data deletion request functionality",
                    file_path=file_path,
                    line_number=1,
                    evidence="No CCPA data deletion endpoints detected",
                    remediation="Implement CCPA-compliant data deletion request endpoints",
                    confidence=0.6,
                    category="CCPA Compliance",
                    check_type="missing_requirement",
                    created_at=datetime.now()
                ))
        
        # Check for missing opt-out functionality
        if not re.search(r'\b(?:ccpa_opt_out|do_not_sell|opt_out_sale)\b', file_content, re.IGNORECASE):
            if self._is_api_file(file_path):
                issues.append(ComplianceIssue(
                    article_ref=CCPAArticle.SECTION_1798_120,
                    severity=ComplianceLevel.MEDIUM,
                    description="Missing CCPA opt-out of sale functionality",
                    file_path=file_path,
                    line_number=1,
                    evidence="No CCPA opt-out endpoints detected",
                    remediation="Implement CCPA-compliant opt-out of sale mechanisms",
                    confidence=0.6,
                    category="CCPA Compliance",
                    check_type="missing_requirement",
                    created_at=datetime.now()
                ))
        
        return issues
    
    def _is_api_file(self, file_path: str) -> bool:
        """Check if file is likely an API file."""
        api_indicators = ['api', 'controller', 'route', 'endpoint', 'service']
        file_name = Path(file_path).name.lower()
        return any(indicator in file_name for indicator in api_indicators)
    
    def _filter_by_license_tier(self, issues: List[ComplianceIssue]) -> List[ComplianceIssue]:
        """Filter issues based on license tier."""
        if self.license_tier == LicenseTier.STARTER:
            # Starter tier: Only critical and high issues
            return [issue for issue in issues if issue.severity in [ComplianceLevel.CRITICAL, ComplianceLevel.HIGH]]
        elif self.license_tier == LicenseTier.PRO:
            # Pro tier: Critical, high, and medium issues
            return [issue for issue in issues if issue.severity in [ComplianceLevel.CRITICAL, ComplianceLevel.HIGH, ComplianceLevel.MEDIUM]]
        else:
            # Business and Enterprise: All issues
            return issues
    
    def get_ccpa_article_info(self, article: CCPAArticle) -> Dict[str, Any]:
        """Get detailed information about a CCPA article."""
        return {
            'article': article.value,
            'title': article.title,
            'description': article.description,
            'requirements': self._get_article_requirements(article),
            'violations': self._get_article_violations(article),
            'remediation': self._get_article_remediation(article)
        }
    
    def _get_article_requirements(self, article: CCPAArticle) -> List[str]:
        """Get requirements for a CCPA article."""
        requirements = {
            CCPAArticle.SECTION_1798_100: [
                "Provide clear notice of data collection",
                "Disclose categories of personal information collected",
                "Explain purposes for data collection",
                "Provide data access mechanisms"
            ],
            CCPAArticle.SECTION_1798_105: [
                "Implement data deletion requests",
                "Verify consumer identity",
                "Provide deletion confirmation",
                "Handle deletion exceptions"
            ],
            CCPAArticle.SECTION_1798_120: [
                "Provide opt-out mechanisms",
                "Honor opt-out requests",
                "Maintain opt-out status",
                "Provide clear opt-out instructions"
            ],
            CCPAArticle.SECTION_1798_125: [
                "Provide equal service regardless of privacy choices",
                "Avoid discrimination based on privacy rights",
                "Maintain service quality",
                "Respect consumer choices"
            ],
            CCPAArticle.SECTION_1798_150: [
                "Implement reasonable security measures",
                "Protect consumer data",
                "Prevent unauthorized access",
                "Implement breach notification"
            ]
        }
        return requirements.get(article, [])
    
    def _get_article_violations(self, article: CCPAArticle) -> List[str]:
        """Get common violations for a CCPA article."""
        violations = {
            CCPAArticle.SECTION_1798_100: [
                "Unclear data collection notices",
                "Missing data categories disclosure",
                "Inaccessible data access mechanisms",
                "Incomplete privacy policies"
            ],
            CCPAArticle.SECTION_1798_105: [
                "Missing data deletion functionality",
                "Incomplete deletion processes",
                "No deletion confirmation",
                "Ignoring deletion requests"
            ],
            CCPAArticle.SECTION_1798_120: [
                "Missing opt-out mechanisms",
                "Hidden opt-out options",
                "Ignoring opt-out requests",
                "No opt-out confirmation"
            ],
            CCPAArticle.SECTION_1798_125: [
                "Differential service based on privacy choices",
                "Penalties for exercising privacy rights",
                "Reduced functionality for opt-outs",
                "Discrimination against privacy-conscious users"
            ],
            CCPAArticle.SECTION_1798_150: [
                "Inadequate security measures",
                "Unencrypted data transmission",
                "Weak access controls",
                "No breach notification procedures"
            ]
        }
        return violations.get(article, [])
    
    def _get_article_remediation(self, article: CCPAArticle) -> List[str]:
        """Get remediation steps for a CCPA article."""
        remediation = {
            CCPAArticle.SECTION_1798_100: [
                "Update privacy notices with clear disclosures",
                "Implement comprehensive data access APIs",
                "Create consumer-friendly data request forms",
                "Provide detailed data collection explanations"
            ],
            CCPAArticle.SECTION_1798_105: [
                "Implement data deletion endpoints",
                "Create deletion request verification",
                "Establish deletion confirmation processes",
                "Handle deletion exceptions properly"
            ],
            CCPAArticle.SECTION_1798_120: [
                "Add prominent opt-out mechanisms",
                "Implement opt-out request processing",
                "Create opt-out status tracking",
                "Provide clear opt-out instructions"
            ],
            CCPAArticle.SECTION_1798_125: [
                "Remove differential treatment",
                "Ensure equal service quality",
                "Eliminate privacy choice penalties",
                "Implement non-discrimination policies"
            ],
            CCPAArticle.SECTION_1798_150: [
                "Implement strong encryption",
                "Enhance access controls",
                "Create breach notification procedures",
                "Regular security assessments"
            ]
        }
        return remediation.get(article, [])
    
    def validate_ccpa_compliance(self, issues: List[ComplianceIssue]) -> Dict[str, Any]:
        """Validate CCPA compliance based on issues found."""
        validation_results = {
            "total_issues": len(issues),
            "critical_issues": len([i for i in issues if i.severity == ComplianceLevel.CRITICAL]),
            "high_issues": len([i for i in issues if i.severity == ComplianceLevel.HIGH]),
            "medium_issues": len([i for i in issues if i.severity == ComplianceLevel.MEDIUM]),
            "low_issues": len([i for i in issues if i.severity == ComplianceLevel.LOW]),
            "article_coverage": {},
            "compliance_score": 0.0,
            "recommendations": []
        }
        
        # Calculate article coverage
        for issue in issues:
            article = issue.article_ref.value
            if article not in validation_results["article_coverage"]:
                validation_results["article_coverage"][article] = 0
            validation_results["article_coverage"][article] += 1
        
        # Calculate compliance score
        total_possible_issues = 50  # Estimated maximum issues
        actual_issues = len(issues)
        validation_results["compliance_score"] = max(0.0, 100.0 - (actual_issues / total_possible_issues) * 100.0)
        
        # Generate recommendations
        if validation_results["critical_issues"] > 0:
            validation_results["recommendations"].append("Address critical CCPA violations immediately")
        if validation_results["high_issues"] > 0:
            validation_results["recommendations"].append("Resolve high-priority CCPA issues")
        if validation_results["compliance_score"] < 70:
            validation_results["recommendations"].append("Implement comprehensive CCPA compliance program")
        
        return validation_results
