"""
GDPR article mapping for automatic violation categorization.
Maps PII violations to specific GDPR articles with explanations.
"""

import re
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from .models import GDPRArticle, ViolationType, ViolationRecord


@dataclass
class GDPRMapping:
    """GDPR article mapping result."""
    article: GDPRArticle
    confidence: float
    explanation: str
    requirements: List[str]
    remediation_suggestions: List[str]


class GDPRMapper:
    """Maps PII violations to GDPR articles automatically."""
    
    def __init__(self):
        """Initialize GDPR mapper with mapping rules."""
        self.logger = logging.getLogger(__name__)
        self.mapping_rules = self._initialize_mapping_rules()
    
    def _initialize_mapping_rules(self) -> Dict[ViolationType, Dict[str, any]]:
        """Initialize mapping rules for violation types to GDPR articles."""
        return {
            ViolationType.PII_IN_LOGS: {
                'primary_article': GDPRArticle.ARTICLE_32,
                'secondary_articles': [GDPRArticle.ARTICLE_33, GDPRArticle.ARTICLE_34],
                'confidence': 0.95,
                'explanation': "PII in logs violates data security requirements and may constitute a data breach",
                'requirements': [
                    "Implement appropriate technical measures to protect personal data",
                    "Ensure logs do not contain personal data",
                    "Implement data minimization in logging practices"
                ],
                'remediation_suggestions': [
                    "Remove or mask PII from log statements",
                    "Implement log sanitization filters",
                    "Use structured logging with PII redaction",
                    "Review and update logging policies"
                ]
            },
            
            ViolationType.HARDCODED_CREDENTIALS: {
                'primary_article': GDPRArticle.ARTICLE_32,
                'secondary_articles': [GDPRArticle.ARTICLE_5_1_C],
                'confidence': 0.90,
                'explanation': "Hardcoded credentials violate security requirements and data minimization principles",
                'requirements': [
                    "Implement appropriate technical measures for data security",
                    "Use secure credential management systems",
                    "Minimize data collection to what is necessary"
                ],
                'remediation_suggestions': [
                    "Move credentials to secure environment variables",
                    "Use secret management systems (AWS Secrets Manager, HashiCorp Vault)",
                    "Implement proper credential rotation",
                    "Remove hardcoded credentials from codebase"
                ]
            },
            
            ViolationType.UNENCRYPTED_PII: {
                'primary_article': GDPRArticle.ARTICLE_32,
                'secondary_articles': [],
                'confidence': 0.98,
                'explanation': "Unencrypted PII violates security of processing requirements",
                'requirements': [
                    "Implement appropriate technical measures to protect personal data",
                    "Use encryption for personal data at rest and in transit",
                    "Implement access controls for personal data"
                ],
                'remediation_suggestions': [
                    "Encrypt PII data at rest using strong encryption",
                    "Use HTTPS/TLS for data in transit",
                    "Implement field-level encryption for sensitive data",
                    "Review and update encryption policies"
                ]
            },
            
            ViolationType.UNNECESSARY_PII: {
                'primary_article': GDPRArticle.ARTICLE_5_1_C,
                'secondary_articles': [GDPRArticle.ARTICLE_5_1_E],
                'confidence': 0.85,
                'explanation': "Unnecessary PII collection violates data minimization and storage limitation principles",
                'requirements': [
                    "Collect only personal data that is adequate, relevant and limited to what is necessary",
                    "Retain personal data only for as long as necessary",
                    "Implement data minimization practices"
                ],
                'remediation_suggestions': [
                    "Remove unnecessary PII collection",
                    "Implement data retention policies",
                    "Review data collection practices",
                    "Implement data minimization in application design"
                ]
            },
            
            ViolationType.MISSING_CONSENT: {
                'primary_article': GDPRArticle.ARTICLE_6,
                'secondary_articles': [GDPRArticle.ARTICLE_7],
                'confidence': 0.80,
                'explanation': "Missing consent mechanisms violate lawful basis requirements",
                'requirements': [
                    "Ensure lawful basis for processing personal data",
                    "Obtain explicit consent where required",
                    "Implement consent management systems"
                ],
                'remediation_suggestions': [
                    "Implement consent collection mechanisms",
                    "Add consent checkboxes and opt-in forms",
                    "Implement consent withdrawal functionality",
                    "Review lawful basis for data processing"
                ]
            },
            
            ViolationType.NO_DELETION_MECHANISM: {
                'primary_article': GDPRArticle.ARTICLE_17,
                'secondary_articles': [GDPRArticle.ARTICLE_18],
                'confidence': 0.90,
                'explanation': "Missing deletion mechanisms violate the right to erasure",
                'requirements': [
                    "Implement data subject's right to erasure",
                    "Provide mechanisms for data deletion",
                    "Implement data retention policies"
                ],
                'remediation_suggestions': [
                    "Implement user data deletion functionality",
                    "Add 'Delete Account' features",
                    "Implement automated data retention policies",
                    "Create data deletion procedures"
                ]
            },
            
            ViolationType.PII_IN_COMMENTS: {
                'primary_article': GDPRArticle.ARTICLE_32,
                'secondary_articles': [GDPRArticle.ARTICLE_5_1_C],
                'confidence': 0.70,
                'explanation': "PII in comments may violate security and minimization requirements",
                'requirements': [
                    "Protect personal data in all forms",
                    "Minimize data collection and exposure",
                    "Implement secure coding practices"
                ],
                'remediation_suggestions': [
                    "Remove PII from code comments",
                    "Use placeholder data in examples",
                    "Implement code review processes for PII",
                    "Train developers on secure coding practices"
                ]
            },
            
            ViolationType.PII_IN_CONFIG: {
                'primary_article': GDPRArticle.ARTICLE_32,
                'secondary_articles': [GDPRArticle.ARTICLE_5_1_C],
                'confidence': 0.85,
                'explanation': "PII in configuration files violates security requirements",
                'requirements': [
                    "Protect personal data in configuration",
                    "Use secure configuration management",
                    "Implement access controls for sensitive data"
                ],
                'remediation_suggestions': [
                    "Move PII to secure environment variables",
                    "Use encrypted configuration files",
                    "Implement configuration validation",
                    "Use secret management systems"
                ]
            },
            
            ViolationType.PII_IN_TESTS: {
                'primary_article': GDPRArticle.ARTICLE_5_1_C,
                'secondary_articles': [GDPRArticle.ARTICLE_32],
                'confidence': 0.60,
                'explanation': "PII in test data may violate minimization principles",
                'requirements': [
                    "Minimize data collection even in test environments",
                    "Use synthetic data for testing",
                    "Implement secure test data practices"
                ],
                'remediation_suggestions': [
                    "Replace real PII with synthetic test data",
                    "Use data anonymization for test data",
                    "Implement test data generation tools",
                    "Review test data practices"
                ]
            },
            
            ViolationType.PII_IN_DOCUMENTATION: {
                'primary_article': GDPRArticle.ARTICLE_32,
                'secondary_articles': [GDPRArticle.ARTICLE_5_1_C],
                'confidence': 0.75,
                'explanation': "PII in documentation violates security and minimization requirements",
                'requirements': [
                    "Protect personal data in all documentation",
                    "Use placeholder data in examples",
                    "Implement secure documentation practices"
                ],
                'remediation_suggestions': [
                    "Replace real PII with placeholder data",
                    "Use anonymized examples in documentation",
                    "Implement documentation review processes",
                    "Train teams on secure documentation practices"
                ]
            }
        }
    
    def map_violation_to_article(self, violation: ViolationRecord) -> GDPRMapping:
        """Map a violation to GDPR articles with confidence and explanation."""
        try:
            # Get mapping rule for violation type
            rule = self.mapping_rules.get(violation.violation_type)
            if not rule:
                # Default mapping for unknown violation types
                return self._get_default_mapping(violation)
            
            # Create mapping result
            mapping = GDPRMapping(
                article=rule['primary_article'],
                confidence=rule['confidence'],
                explanation=rule['explanation'],
                requirements=rule['requirements'],
                remediation_suggestions=rule['remediation_suggestions']
            )
            
            # Adjust confidence based on violation context
            mapping.confidence = self._adjust_confidence_for_context(violation, mapping.confidence)
            
            return mapping
            
        except Exception as e:
            self.logger.error(f"Failed to map violation to GDPR article: {e}")
            return self._get_default_mapping(violation)
    
    def _get_default_mapping(self, violation: ViolationRecord) -> GDPRMapping:
        """Get default GDPR mapping for unknown violation types."""
        return GDPRMapping(
            article=GDPRArticle.ARTICLE_32,  # Default to security
            confidence=0.50,
            explanation="PII violation requires security review and appropriate technical measures",
            requirements=[
                "Implement appropriate technical measures to protect personal data",
                "Review data processing practices",
                "Ensure compliance with GDPR requirements"
            ],
            remediation_suggestions=[
                "Review and secure the identified PII",
                "Implement appropriate technical measures",
                "Consult with compliance team for specific requirements"
            ]
        )
    
    def _adjust_confidence_for_context(self, violation: ViolationRecord, base_confidence: float) -> float:
        """Adjust confidence based on violation context."""
        confidence = base_confidence
        
        # Adjust based on severity
        severity_adjustments = {
            'critical': 0.1,
            'high': 0.05,
            'medium': 0.0,
            'low': -0.05
        }
        confidence += severity_adjustments.get(violation.severity, 0.0)
        
        # Adjust based on confidence score
        if violation.confidence > 0.8:
            confidence += 0.05
        elif violation.confidence < 0.5:
            confidence -= 0.1
        
        # Adjust based on file path context
        if self._is_production_file(violation.file_path):
            confidence += 0.05
        elif self._is_test_file(violation.file_path):
            confidence -= 0.1
        
        # Ensure confidence is within bounds
        return max(0.0, min(1.0, confidence))
    
    def _is_production_file(self, file_path: str) -> bool:
        """Check if file is in production context."""
        production_indicators = [
            'src/', 'app/', 'lib/', 'main/', 'production/',
            'api/', 'server/', 'backend/', 'frontend/'
        ]
        return any(indicator in file_path.lower() for indicator in production_indicators)
    
    def _is_test_file(self, file_path: str) -> bool:
        """Check if file is in test context."""
        test_indicators = [
            'test/', 'tests/', 'spec/', 'specs/', '__tests__/',
            'test_', '_test.', '.test.', '.spec.'
        ]
        return any(indicator in file_path.lower() for indicator in test_indicators)
    
    def get_article_explanation(self, article: GDPRArticle) -> Dict[str, str]:
        """Get detailed explanation for a GDPR article."""
        return {
            'title': article.title,
            'description': article.description,
            'article_number': article.value,
            'key_requirements': self._get_article_requirements(article)
        }
    
    def _get_article_requirements(self, article: GDPRArticle) -> List[str]:
        """Get key requirements for a GDPR article."""
        requirements_map = {
            GDPRArticle.ARTICLE_5_1_C: [
                "Collect only personal data that is adequate, relevant and limited to what is necessary",
                "Regularly review data collection practices",
                "Implement data minimization by design"
            ],
            GDPRArticle.ARTICLE_5_1_D: [
                "Ensure personal data is accurate and up-to-date",
                "Implement data validation processes",
                "Allow data subjects to correct inaccurate data"
            ],
            GDPRArticle.ARTICLE_5_1_E: [
                "Retain personal data only for as long as necessary",
                "Implement data retention policies",
                "Automatically delete data after retention period"
            ],
            GDPRArticle.ARTICLE_6: [
                "Identify lawful basis for processing personal data",
                "Document lawful basis for each processing activity",
                "Ensure lawful basis is appropriate for the processing"
            ],
            GDPRArticle.ARTICLE_17: [
                "Implement data subject's right to erasure",
                "Provide mechanisms for data deletion",
                "Ensure complete removal of personal data"
            ],
            GDPRArticle.ARTICLE_18: [
                "Implement data subject's right to restriction of processing",
                "Provide mechanisms to restrict processing",
                "Respect data subject's restriction requests"
            ],
            GDPRArticle.ARTICLE_20: [
                "Implement data subject's right to data portability",
                "Provide data in structured, machine-readable format",
                "Enable data transfer to another controller"
            ],
            GDPRArticle.ARTICLE_32: [
                "Implement appropriate technical and organisational measures",
                "Ensure security appropriate to the risk",
                "Regularly test and evaluate security measures"
            ],
            GDPRArticle.ARTICLE_30: [
                "Maintain records of processing activities",
                "Document all processing activities",
                "Keep records up-to-date and accurate"
            ],
            GDPRArticle.ARTICLE_33: [
                "Notify supervisory authority of data breaches within 72 hours",
                "Document all data breaches",
                "Implement breach detection and notification procedures"
            ],
            GDPRArticle.ARTICLE_34: [
                "Communicate data breaches to data subjects when high risk",
                "Provide clear information about the breach",
                "Implement breach communication procedures"
            ]
        }
        
        return requirements_map.get(article, [
            "Review GDPR requirements for this article",
            "Implement appropriate technical and organisational measures",
            "Consult with legal/compliance team for specific requirements"
        ])
    
    def get_compliance_checklist(self, violations: List[ViolationRecord]) -> Dict[str, List[str]]:
        """Generate compliance checklist based on violations."""
        checklist = {}
        
        for violation in violations:
            mapping = self.map_violation_to_article(violation)
            article = mapping.article.value
            
            if article not in checklist:
                checklist[article] = []
            
            # Add specific requirements for this violation
            for requirement in mapping.requirements:
                if requirement not in checklist[article]:
                    checklist[article].append(requirement)
        
        return checklist
    
    def calculate_compliance_score(self, violations: List[ViolationRecord]) -> Dict[str, float]:
        """Calculate compliance score by GDPR article."""
        article_scores = {}
        article_violations = {}
        
        # Group violations by GDPR article
        for violation in violations:
            mapping = self.map_violation_to_article(violation)
            article = mapping.article.value
            
            if article not in article_violations:
                article_violations[article] = []
            article_violations[article].append(violation)
        
        # Calculate score for each article
        for article, article_viols in article_violations.items():
            total_violations = len(article_viols)
            critical_violations = len([v for v in article_viols if v.severity == 'critical'])
            high_violations = len([v for v in article_viols if v.severity == 'high'])
            
            # Calculate score (100 - penalty for violations)
            score = 100.0
            score -= critical_violations * 20  # 20 points per critical violation
            score -= high_violations * 10      # 10 points per high violation
            score -= (total_violations - critical_violations - high_violations) * 5  # 5 points per other violation
            
            article_scores[article] = max(0.0, score)
        
        return article_scores
