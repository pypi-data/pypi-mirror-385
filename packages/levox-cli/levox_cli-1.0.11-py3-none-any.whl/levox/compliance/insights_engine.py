"""
ML-Powered Insights Engine for Evidence Engine.
Machine learning for compliance insights, pattern recognition, and risk prediction.
"""

import logging
import numpy as np
import pandas as pd
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import warnings
from collections import defaultdict, Counter

# ML imports with fallbacks
try:
    from sklearn.cluster import KMeans, DBSCAN
    from sklearn.preprocessing import StandardScaler, LabelEncoder
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics import silhouette_score
    from sklearn.decomposition import PCA
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    warnings.warn("scikit-learn not available. ML insights will be disabled.")

try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    warnings.warn("XGBoost not available. Advanced ML features will be disabled.")

try:
    import nltk
    from nltk.sentiment import SentimentIntensityAnalyzer
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False
    warnings.warn("NLTK not available. Text analysis features will be disabled.")

from .models import ScanHistoryEntry, ViolationRecord, RemediationEvidence, CompanyProfile


class InsightType(Enum):
    """Types of insights."""
    PATTERN_RECOGNITION = "pattern_recognition"
    ROOT_CAUSE_ANALYSIS = "root_cause_analysis"
    RISK_PREDICTION = "risk_prediction"
    REMEDIATION_EFFECTIVENESS = "remediation_effectiveness"
    COMPLIANCE_TREND = "compliance_trend"
    ANOMALY_EXPLANATION = "anomaly_explanation"


class RiskLevel(Enum):
    """Risk levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ComplianceInsight:
    """Represents a compliance insight."""
    insight_id: str
    insight_type: InsightType
    title: str
    description: str
    confidence: float  # 0.0 to 1.0
    impact_score: float  # 0.0 to 1.0
    risk_level: RiskLevel
    affected_areas: List[str]
    recommendations: List[str]
    supporting_evidence: Dict[str, Any]
    generated_at: datetime


@dataclass
class PatternCluster:
    """Represents a pattern cluster."""
    cluster_id: str
    cluster_type: str
    description: str
    violation_count: int
    common_characteristics: Dict[str, Any]
    representative_violations: List[str]
    risk_score: float


@dataclass
class RootCauseAnalysis:
    """Represents root cause analysis results."""
    analysis_id: str
    primary_causes: List[str]
    contributing_factors: List[str]
    confidence: float
    evidence: Dict[str, Any]
    recommendations: List[str]


@dataclass
class RemediationEffectiveness:
    """Represents remediation effectiveness analysis."""
    effectiveness_id: str
    remediation_type: str
    success_rate: float
    average_time_to_resolution: float
    factors_affecting_success: List[str]
    recommendations: List[str]


class PatternRecognizer:
    """Recognizes patterns in violation data using ML clustering."""
    
    def __init__(self):
        """Initialize pattern recognizer."""
        self.logger = logging.getLogger(__name__)
        self.scaler = None
        self.clustering_model = None
        self.is_trained = False
    
    def train_patterns(self, violations: List[ViolationRecord]):
        """Train pattern recognition model."""
        if not SKLEARN_AVAILABLE or len(violations) < 20:
            self.logger.warning("Insufficient data or sklearn not available for pattern training")
            return
        
        try:
            # Prepare features for clustering
            features = self._prepare_clustering_features(violations)
            
            # Scale features
            self.scaler = StandardScaler()
            features_scaled = self.scaler.fit_transform(features)
            
            # Determine optimal number of clusters
            optimal_clusters = self._find_optimal_clusters(features_scaled)
            
            # Train clustering model
            self.clustering_model = KMeans(
                n_clusters=optimal_clusters,
                random_state=42,
                n_init=10
            )
            self.clustering_model.fit(features_scaled)
            
            self.is_trained = True
            self.logger.info(f"Pattern recognizer trained with {optimal_clusters} clusters")
            
        except Exception as e:
            self.logger.error(f"Failed to train pattern recognizer: {e}")
    
    def _prepare_clustering_features(self, violations: List[ViolationRecord]) -> np.ndarray:
        """Prepare features for clustering."""
        features = []
        
        for violation in violations:
            # Extract features
            feature_vector = [
                len(violation.file_path.split('/')),  # Directory depth
                1 if 'test' in violation.file_path.lower() else 0,  # Test file
                1 if 'config' in violation.file_path.lower() else 0,  # Config file
                1 if 'log' in violation.file_path.lower() else 0,  # Log file
                violation.line_number,  # Line number
                len(violation.matched_text) if violation.matched_text else 0,  # Text length
                violation.confidence,  # Confidence score
                self._encode_severity(violation.severity),  # Severity encoding
                self._encode_violation_type(violation.violation_type),  # Type encoding
            ]
            features.append(feature_vector)
        
        return np.array(features)
    
    def _encode_severity(self, severity: str) -> int:
        """Encode severity to numeric value."""
        severity_map = {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}
        return severity_map.get(severity, 0)
    
    def _encode_violation_type(self, violation_type: str) -> int:
        """Encode violation type to numeric value."""
        # Simple hash-based encoding
        return hash(str(violation_type)) % 100
    
    def _find_optimal_clusters(self, features: np.ndarray) -> int:
        """Find optimal number of clusters using silhouette score."""
        if len(features) < 10:
            return min(3, len(features) // 2)
        
        best_score = -1
        best_k = 2
        
        for k in range(2, min(10, len(features) // 2)):
            try:
                kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
                cluster_labels = kmeans.fit_predict(features)
                score = silhouette_score(features, cluster_labels)
                
                if score > best_score:
                    best_score = score
                    best_k = k
            except Exception:
                continue
        
        return best_k
    
    def identify_patterns(self, violations: List[ViolationRecord]) -> List[PatternCluster]:
        """Identify patterns in violations."""
        if not self.is_trained:
            return self._basic_pattern_analysis(violations)
        
        try:
            # Prepare features
            features = self._prepare_clustering_features(violations)
            features_scaled = self.scaler.transform(features)
            
            # Get cluster assignments
            cluster_labels = self.clustering_model.predict(features_scaled)
            
            # Analyze each cluster
            clusters = []
            for cluster_id in range(self.clustering_model.n_clusters):
                cluster_violations = [
                    violations[i] for i in range(len(violations))
                    if cluster_labels[i] == cluster_id
                ]
                
                if cluster_violations:
                    cluster = self._analyze_cluster(cluster_id, cluster_violations)
                    clusters.append(cluster)
            
            return clusters
            
        except Exception as e:
            self.logger.error(f"Pattern identification failed: {e}")
            return self._basic_pattern_analysis(violations)
    
    def _analyze_cluster(self, cluster_id: int, violations: List[ViolationRecord]) -> PatternCluster:
        """Analyze a specific cluster."""
        # Analyze common characteristics
        file_paths = [v.file_path for v in violations]
        severities = [v.severity for v in violations]
        violation_types = [str(v.violation_type) for v in violations]
        
        # Find common patterns
        common_files = Counter(file_paths).most_common(5)
        common_severities = Counter(severities).most_common()
        common_types = Counter(violation_types).most_common()
        
        # Calculate risk score
        risk_score = self._calculate_cluster_risk(violations)
        
        return PatternCluster(
            cluster_id=f"cluster_{cluster_id}",
            cluster_type=self._classify_cluster_type(violations),
            description=f"Pattern cluster with {len(violations)} violations",
            violation_count=len(violations),
            common_characteristics={
                'common_files': common_files,
                'common_severities': common_severities,
                'common_types': common_types
            },
            representative_violations=[v.id for v in violations[:5]],
            risk_score=risk_score
        )
    
    def _classify_cluster_type(self, violations: List[ViolationRecord]) -> str:
        """Classify the type of cluster."""
        if len(violations) < 2:
            return "single_violation"
        
        # Analyze file patterns
        file_paths = [v.file_path for v in violations]
        unique_files = len(set(file_paths))
        
        if unique_files == 1:
            return "file_hotspot"
        elif unique_files < len(violations) * 0.5:
            return "directory_hotspot"
        else:
            return "pattern_cluster"
    
    def _calculate_cluster_risk(self, violations: List[ViolationRecord]) -> float:
        """Calculate risk score for cluster."""
        if not violations:
            return 0.0
        
        # Base risk from severity
        severity_scores = {'critical': 1.0, 'high': 0.8, 'medium': 0.6, 'low': 0.4}
        avg_severity = np.mean([severity_scores.get(v.severity, 0.5) for v in violations])
        
        # Risk from cluster size
        size_risk = min(1.0, len(violations) / 20.0)
        
        # Risk from concentration
        file_paths = [v.file_path for v in violations]
        concentration_risk = 1.0 - (len(set(file_paths)) / len(file_paths))
        
        return (avg_severity * 0.5 + size_risk * 0.3 + concentration_risk * 0.2)
    
    def _basic_pattern_analysis(self, violations: List[ViolationRecord]) -> List[PatternCluster]:
        """Basic pattern analysis without ML."""
        clusters = []
        
        # Group by file path
        file_groups = defaultdict(list)
        for violation in violations:
            file_groups[violation.file_path].append(violation)
        
        # Create clusters for files with multiple violations
        for file_path, file_violations in file_groups.items():
            if len(file_violations) > 1:
                cluster = PatternCluster(
                    cluster_id=f"file_{hash(file_path) % 1000}",
                    cluster_type="file_hotspot",
                    description=f"Multiple violations in {file_path}",
                    violation_count=len(file_violations),
                    common_characteristics={'file_path': file_path},
                    representative_violations=[v.id for v in file_violations[:3]],
                    risk_score=self._calculate_cluster_risk(file_violations)
                )
                clusters.append(cluster)
        
        return clusters


class RiskPredictor:
    """Predicts compliance risk using ML models."""
    
    def __init__(self):
        """Initialize risk predictor."""
        self.logger = logging.getLogger(__name__)
        self.risk_model = None
        self.scaler = None
        self.is_trained = False
    
    def train_risk_model(self, historical_data: List[Dict[str, Any]]):
        """Train risk prediction model."""
        if not XGBOOST_AVAILABLE or len(historical_data) < 50:
            self.logger.warning("Insufficient data or XGBoost not available for risk training")
            return
        
        try:
            # Prepare training data
            df = pd.DataFrame(historical_data)
            features, labels = self._prepare_risk_features(df)
            
            # Scale features
            self.scaler = StandardScaler()
            features_scaled = self.scaler.fit_transform(features)
            
            # Train XGBoost model
            self.risk_model = xgb.XGBClassifier(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                random_state=42
            )
            self.risk_model.fit(features_scaled, labels)
            
            self.is_trained = True
            self.logger.info("Risk predictor trained successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to train risk predictor: {e}")
    
    def _prepare_risk_features(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare features for risk prediction."""
        # Create features
        features = []
        labels = []
        
        for _, row in df.iterrows():
            feature_vector = [
                row.get('total_violations', 0),
                row.get('critical_violations', 0),
                row.get('high_violations', 0),
                row.get('medium_violations', 0),
                row.get('low_violations', 0),
                row.get('days_since_last_scan', 0),
                row.get('scan_frequency', 0),
                row.get('remediation_rate', 0),
                row.get('violation_trend', 0),
                row.get('compliance_score', 0)
            ]
            features.append(feature_vector)
            
            # Risk label (simplified)
            risk_label = 1 if row.get('risk_level') in ['high', 'critical'] else 0
            labels.append(risk_label)
        
        return np.array(features), np.array(labels)
    
    def predict_risk(self, current_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predict compliance risk."""
        if not self.is_trained:
            return self._basic_risk_assessment(current_data)
        
        try:
            # Prepare features
            features = np.array([[
                current_data.get('total_violations', 0),
                current_data.get('critical_violations', 0),
                current_data.get('high_violations', 0),
                current_data.get('medium_violations', 0),
                current_data.get('low_violations', 0),
                current_data.get('days_since_last_scan', 0),
                current_data.get('scan_frequency', 0),
                current_data.get('remediation_rate', 0),
                current_data.get('violation_trend', 0),
                current_data.get('compliance_score', 0)
            ]])
            
            # Scale features
            features_scaled = self.scaler.transform(features)
            
            # Make prediction
            risk_probability = self.risk_model.predict_proba(features_scaled)[0][1]
            
            # Determine risk level
            if risk_probability > 0.8:
                risk_level = RiskLevel.CRITICAL
            elif risk_probability > 0.6:
                risk_level = RiskLevel.HIGH
            elif risk_probability > 0.4:
                risk_level = RiskLevel.MEDIUM
            else:
                risk_level = RiskLevel.LOW
            
            return {
                'risk_level': risk_level.value,
                'risk_probability': risk_probability,
                'confidence': min(1.0, len(self.risk_model.feature_importances_) / 10.0),
                'factors': self._get_risk_factors(current_data, risk_probability)
            }
            
        except Exception as e:
            self.logger.error(f"Risk prediction failed: {e}")
            return self._basic_risk_assessment(current_data)
    
    def _basic_risk_assessment(self, current_data: Dict[str, Any]) -> Dict[str, Any]:
        """Basic risk assessment without ML."""
        risk_score = 0.0
        factors = []
        
        # Critical violations
        critical_violations = current_data.get('critical_violations', 0)
        if critical_violations > 0:
            risk_score += critical_violations * 0.3
            factors.append(f"{critical_violations} critical violations")
        
        # High violations
        high_violations = current_data.get('high_violations', 0)
        if high_violations > 5:
            risk_score += high_violations * 0.1
            factors.append(f"{high_violations} high-severity violations")
        
        # Days since last scan
        days_since_scan = current_data.get('days_since_last_scan', 0)
        if days_since_scan > 30:
            risk_score += 0.2
            factors.append(f"{days_since_scan} days since last scan")
        
        # Determine risk level
        if risk_score > 0.8:
            risk_level = RiskLevel.CRITICAL
        elif risk_score > 0.6:
            risk_level = RiskLevel.HIGH
        elif risk_score > 0.4:
            risk_level = RiskLevel.MEDIUM
        else:
            risk_level = RiskLevel.LOW
        
        return {
            'risk_level': risk_level.value,
            'risk_probability': min(1.0, risk_score),
            'confidence': 0.5,
            'factors': factors
        }
    
    def _get_risk_factors(self, current_data: Dict[str, Any], risk_probability: float) -> List[str]:
        """Get risk factors based on current data."""
        factors = []
        
        if current_data.get('critical_violations', 0) > 0:
            factors.append("Critical violations present")
        
        if current_data.get('days_since_last_scan', 0) > 30:
            factors.append("Stale scan data")
        
        if current_data.get('violation_trend', 0) > 0:
            factors.append("Increasing violation trend")
        
        if current_data.get('remediation_rate', 0) < 0.5:
            factors.append("Low remediation rate")
        
        return factors


class RecommendationEngine:
    """Generates intelligent recommendations based on ML analysis."""
    
    def __init__(self):
        """Initialize recommendation engine."""
        self.logger = logging.getLogger(__name__)
        self.recommendation_templates = self._load_recommendation_templates()
    
    def _load_recommendation_templates(self) -> Dict[str, List[str]]:
        """Load recommendation templates."""
        return {
            'critical_violations': [
                "Immediately address all critical violations",
                "Implement emergency remediation procedures",
                "Escalate to compliance officer",
                "Consider external audit"
            ],
            'high_violations': [
                "Prioritize high-severity violations",
                "Implement additional monitoring",
                "Review compliance processes",
                "Schedule remediation sprint"
            ],
            'pattern_cluster': [
                "Investigate root cause of pattern",
                "Implement preventive measures",
                "Review development processes",
                "Consider automated detection"
            ],
            'stale_data': [
                "Schedule regular compliance scans",
                "Implement automated scanning",
                "Set up monitoring alerts",
                "Review scan configuration"
            ],
            'low_remediation': [
                "Improve remediation processes",
                "Provide training on compliance",
                "Implement tracking system",
                "Set remediation targets"
            ],
            'trend_deterioration': [
                "Analyze trend causes",
                "Strengthen compliance controls",
                "Review recent changes",
                "Implement additional safeguards"
            ]
        }
    
    def generate_recommendations(self, insights: List[ComplianceInsight], 
                               current_state: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on insights and current state."""
        recommendations = []
        
        # Process insights
        for insight in insights:
            if insight.insight_type == InsightType.PATTERN_RECOGNITION:
                recommendations.extend(self._get_pattern_recommendations(insight))
            elif insight.insight_type == InsightType.RISK_PREDICTION:
                recommendations.extend(self._get_risk_recommendations(insight))
            elif insight.insight_type == InsightType.ROOT_CAUSE_ANALYSIS:
                recommendations.extend(self._get_root_cause_recommendations(insight))
        
        # Process current state
        recommendations.extend(self._get_state_based_recommendations(current_state))
        
        # Remove duplicates and prioritize
        unique_recommendations = list(set(recommendations))
        return self._prioritize_recommendations(unique_recommendations, current_state)
    
    def _get_pattern_recommendations(self, insight: ComplianceInsight) -> List[str]:
        """Get recommendations for pattern insights."""
        return self.recommendation_templates.get('pattern_cluster', [])
    
    def _get_risk_recommendations(self, insight: ComplianceInsight) -> List[str]:
        """Get recommendations for risk insights."""
        risk_level = insight.risk_level.value
        
        if risk_level == 'critical':
            return self.recommendation_templates.get('critical_violations', [])
        elif risk_level == 'high':
            return self.recommendation_templates.get('high_violations', [])
        else:
            return ["Continue monitoring compliance status"]
    
    def _get_root_cause_recommendations(self, insight: ComplianceInsight) -> List[str]:
        """Get recommendations for root cause insights."""
        return insight.recommendations
    
    def _get_state_based_recommendations(self, current_state: Dict[str, Any]) -> List[str]:
        """Get recommendations based on current state."""
        recommendations = []
        
        # Check for critical violations
        if current_state.get('critical_violations', 0) > 0:
            recommendations.extend(self.recommendation_templates.get('critical_violations', []))
        
        # Check for stale data
        if current_state.get('days_since_last_scan', 0) > 30:
            recommendations.extend(self.recommendation_templates.get('stale_data', []))
        
        # Check for low remediation rate
        if current_state.get('remediation_rate', 0) < 0.5:
            recommendations.extend(self.recommendation_templates.get('low_remediation', []))
        
        # Check for deteriorating trend
        if current_state.get('violation_trend', 0) > 0.1:
            recommendations.extend(self.recommendation_templates.get('trend_deterioration', []))
        
        return recommendations
    
    def _prioritize_recommendations(self, recommendations: List[str], 
                                  current_state: Dict[str, Any]) -> List[str]:
        """Prioritize recommendations based on urgency and impact."""
        # Simple prioritization based on keywords
        priority_keywords = {
            'immediately': 10,
            'emergency': 9,
            'critical': 8,
            'escalate': 7,
            'urgent': 6,
            'priority': 5,
            'schedule': 3,
            'consider': 2,
            'review': 1
        }
        
        def get_priority(rec: str) -> int:
            for keyword, priority in priority_keywords.items():
                if keyword.lower() in rec.lower():
                    return priority
            return 0
        
        # Sort by priority
        sorted_recs = sorted(recommendations, key=get_priority, reverse=True)
        
        # Return top 10 recommendations
        return sorted_recs[:10]


class InsightsEngine:
    """
    Main insights engine that orchestrates ML-powered analysis.
    Combines pattern recognition, risk prediction, and recommendation generation.
    """
    
    def __init__(self):
        """Initialize insights engine."""
        self.logger = logging.getLogger(__name__)
        self.pattern_recognizer = PatternRecognizer()
        self.risk_predictor = RiskPredictor()
        self.recommendation_engine = RecommendationEngine()
        self.is_trained = False
    
    def train_models(self, historical_data: Dict[str, Any]):
        """Train all ML models."""
        try:
            # Train pattern recognizer
            violations = historical_data.get('violations', [])
            if violations:
                self.pattern_recognizer.train_patterns(violations)
            
            # Train risk predictor
            risk_data = historical_data.get('risk_training_data', [])
            if risk_data:
                self.risk_predictor.train_risk_model(risk_data)
            
            self.is_trained = True
            self.logger.info("Insights engine models trained successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to train insights engine: {e}")
    
    def analyze_compliance_patterns(self, company_id: str, 
                                   violations: List[ViolationRecord],
                                   scans: List[ScanHistoryEntry],
                                   remediations: List[RemediationEvidence]) -> List[ComplianceInsight]:
        """Analyze compliance patterns and generate insights."""
        insights = []
        
        try:
            # Pattern recognition
            patterns = self.pattern_recognizer.identify_patterns(violations)
            for pattern in patterns:
                insight = ComplianceInsight(
                    insight_id=f"pattern_{pattern.cluster_id}",
                    insight_type=InsightType.PATTERN_RECOGNITION,
                    title=f"Pattern Detected: {pattern.cluster_type}",
                    description=pattern.description,
                    confidence=0.8,
                    impact_score=pattern.risk_score,
                    risk_level=self._map_risk_level(pattern.risk_score),
                    affected_areas=[pattern.cluster_type],
                    recommendations=self.recommendation_engine._get_pattern_recommendations(
                        ComplianceInsight(
                            insight_id="temp",
                            insight_type=InsightType.PATTERN_RECOGNITION,
                            title="",
                            description="",
                            confidence=0.0,
                            impact_score=0.0,
                            risk_level=self._map_risk_level(pattern.risk_score),
                            affected_areas=[],
                            recommendations=[],
                            supporting_evidence={},
                            generated_at=datetime.now()
                        )
                    ),
                    supporting_evidence={
                        'pattern_cluster': pattern,
                        'violation_count': pattern.violation_count
                    },
                    generated_at=datetime.now()
                )
                insights.append(insight)
            
            # Risk prediction
            current_state = self._prepare_current_state(violations, scans, remediations)
            risk_prediction = self.risk_predictor.predict_risk(current_state)
            
            if risk_prediction['risk_probability'] > 0.6:
                insight = ComplianceInsight(
                    insight_id=f"risk_{int(datetime.now().timestamp())}",
                    insight_type=InsightType.RISK_PREDICTION,
                    title=f"High Risk Detected: {risk_prediction['risk_level']}",
                    description=f"Risk probability: {risk_prediction['risk_probability']:.2f}",
                    confidence=risk_prediction['confidence'],
                    impact_score=risk_prediction['risk_probability'],
                    risk_level=RiskLevel(risk_prediction['risk_level']),
                    affected_areas=['compliance'],
                    recommendations=self.recommendation_engine._get_risk_recommendations(
                        ComplianceInsight(
                            insight_id="temp",
                            insight_type=InsightType.RISK_PREDICTION,
                            title="",
                            description="",
                            confidence=0.0,
                            impact_score=0.0,
                            risk_level=RiskLevel(risk_prediction['risk_level']),
                            affected_areas=[],
                            recommendations=[],
                            supporting_evidence={},
                            generated_at=datetime.now()
                        )
                    ),
                    supporting_evidence=risk_prediction,
                    generated_at=datetime.now()
                )
                insights.append(insight)
            
            # Root cause analysis
            root_causes = self._analyze_root_causes(violations, remediations)
            if root_causes:
                insight = ComplianceInsight(
                    insight_id=f"root_cause_{int(datetime.now().timestamp())}",
                    insight_type=InsightType.ROOT_CAUSE_ANALYSIS,
                    title="Root Cause Analysis",
                    description=f"Primary causes: {', '.join(root_causes.primary_causes)}",
                    confidence=root_causes.confidence,
                    impact_score=0.7,
                    risk_level=RiskLevel.MEDIUM,
                    affected_areas=['development_process'],
                    recommendations=root_causes.recommendations,
                    supporting_evidence={'root_cause_analysis': root_causes},
                    generated_at=datetime.now()
                )
                insights.append(insight)
            
            return insights
            
        except Exception as e:
            self.logger.error(f"Failed to analyze compliance patterns: {e}")
            return []
    
    def _prepare_current_state(self, violations: List[ViolationRecord],
                             scans: List[ScanHistoryEntry],
                             remediations: List[RemediationEvidence]) -> Dict[str, Any]:
        """Prepare current state for analysis."""
        current_state = {
            'total_violations': len(violations),
            'critical_violations': len([v for v in violations if v.severity == 'critical']),
            'high_violations': len([v for v in violations if v.severity == 'high']),
            'medium_violations': len([v for v in violations if v.severity == 'medium']),
            'low_violations': len([v for v in violations if v.severity == 'low']),
            'total_scans': len(scans),
            'total_remediations': len(remediations),
            'remediation_rate': len(remediations) / len(violations) if violations else 0,
            'days_since_last_scan': self._calculate_days_since_last_scan(scans),
            'scan_frequency': self._calculate_scan_frequency(scans),
            'violation_trend': self._calculate_violation_trend(scans),
            'compliance_score': self._calculate_compliance_score(violations)
        }
        
        return current_state
    
    def _calculate_days_since_last_scan(self, scans: List[ScanHistoryEntry]) -> int:
        """Calculate days since last scan."""
        if not scans:
            return 999  # Large number for no scans
        
        last_scan = max(scans, key=lambda x: x.scan_timestamp)
        return (datetime.now() - last_scan.scan_timestamp).days
    
    def _calculate_scan_frequency(self, scans: List[ScanHistoryEntry]) -> float:
        """Calculate scan frequency (scans per week)."""
        if len(scans) < 2:
            return 0.0
        
        # Calculate time span
        first_scan = min(scans, key=lambda x: x.scan_timestamp)
        last_scan = max(scans, key=lambda x: x.scan_timestamp)
        days_span = (last_scan.scan_timestamp - first_scan.scan_timestamp).days
        
        if days_span == 0:
            return 0.0
        
        # Calculate frequency
        weeks_span = days_span / 7.0
        return len(scans) / weeks_span
    
    def _calculate_violation_trend(self, scans: List[ScanHistoryEntry]) -> float:
        """Calculate violation trend (positive = increasing)."""
        if len(scans) < 2:
            return 0.0
        
        # Sort by timestamp
        sorted_scans = sorted(scans, key=lambda x: x.scan_timestamp)
        
        # Calculate trend
        first_half = sorted_scans[:len(sorted_scans)//2]
        second_half = sorted_scans[len(sorted_scans)//2:]
        
        first_avg = sum(scan.total_violations for scan in first_half) / len(first_half)
        second_avg = sum(scan.total_violations for scan in second_half) / len(second_half)
        
        if first_avg == 0:
            return 0.0
        
        return (second_avg - first_avg) / first_avg
    
    def _calculate_compliance_score(self, violations: List[ViolationRecord]) -> float:
        """Calculate compliance score."""
        if not violations:
            return 100.0
        
        score = 100.0
        for violation in violations:
            if violation.severity == 'critical':
                score -= 20
            elif violation.severity == 'high':
                score -= 10
            elif violation.severity == 'medium':
                score -= 5
            else:
                score -= 2
        
        return max(0.0, score)
    
    def _analyze_root_causes(self, violations: List[ViolationRecord],
                           remediations: List[RemediationEvidence]) -> Optional[RootCauseAnalysis]:
        """Analyze root causes of violations."""
        if not violations:
            return None
        
        # Analyze common patterns
        file_patterns = Counter(violation.file_path for violation in violations)
        type_patterns = Counter(str(violation.violation_type) for violation in violations)
        
        primary_causes = []
        contributing_factors = []
        
        # File-based causes
        if len(file_patterns) < len(violations) * 0.5:
            primary_causes.append("Concentrated violations in specific files")
            contributing_factors.append("Potential code quality issues")
        
        # Type-based causes
        most_common_type = type_patterns.most_common(1)[0]
        if most_common_type[1] > len(violations) * 0.3:
            primary_causes.append(f"Frequent {most_common_type[0]} violations")
            contributing_factors.append("Insufficient detection/prevention")
        
        # Remediation analysis
        if remediations:
            remediation_types = Counter(str(r.remediation_type) for r in remediations)
            contributing_factors.append(f"Common remediation: {remediation_types.most_common(1)[0][0]}")
        
        recommendations = [
            "Implement preventive measures for identified patterns",
            "Review development processes",
            "Consider automated detection",
            "Provide team training on compliance"
        ]
        
        return RootCauseAnalysis(
            analysis_id=f"root_cause_{int(datetime.now().timestamp())}",
            primary_causes=primary_causes,
            contributing_factors=contributing_factors,
            confidence=0.7,
            evidence={
                'file_patterns': dict(file_patterns.most_common(5)),
                'type_patterns': dict(type_patterns.most_common(5))
            },
            recommendations=recommendations
        )
    
    def _map_risk_level(self, risk_score: float) -> RiskLevel:
        """Map risk score to risk level."""
        if risk_score > 0.8:
            return RiskLevel.CRITICAL
        elif risk_score > 0.6:
            return RiskLevel.HIGH
        elif risk_score > 0.4:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def get_model_status(self) -> Dict[str, Any]:
        """Get status of ML models."""
        return {
            "is_trained": self.is_trained,
            "pattern_recognizer_available": SKLEARN_AVAILABLE,
            "risk_predictor_available": XGBOOST_AVAILABLE,
            "text_analysis_available": NLTK_AVAILABLE,
            "training_data_requirements": {
                "minimum_violations": 20,
                "minimum_risk_data": 50,
                "recommended_violations": 100
            }
        }
