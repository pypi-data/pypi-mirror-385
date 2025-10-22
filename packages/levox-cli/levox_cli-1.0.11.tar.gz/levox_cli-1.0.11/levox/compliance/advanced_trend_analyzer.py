"""
Advanced Trend Analyzer with ML-powered forecasting and anomaly detection.
Enhanced version of the original trend analyzer with machine learning capabilities.
"""

import logging
import numpy as np
import pandas as pd
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import warnings

# ML imports with fallbacks
try:
    from sklearn.ensemble import IsolationForest
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import mean_absolute_error, mean_squared_error
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    warnings.warn("scikit-learn not available. ML features will be disabled.")

try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False
    warnings.warn("Prophet not available. Time series forecasting will use basic methods.")

try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    warnings.warn("XGBoost not available. Advanced ML features will be disabled.")

from .models import ScanHistoryEntry, ViolationRecord, ViolationTrend, ComplianceMetrics
from .trend_analyzer import TrendAnalyzer


class AnomalyType(Enum):
    """Types of anomalies."""
    SPIKE = "spike"
    DROP = "drop"
    PATTERN_CHANGE = "pattern_change"
    OUTLIER = "outlier"


@dataclass
class Anomaly:
    """Represents a detected anomaly."""
    anomaly_id: str
    anomaly_type: AnomalyType
    timestamp: datetime
    severity: float  # 0.0 to 1.0
    description: str
    affected_metrics: List[str]
    confidence: float
    suggested_actions: List[str]


@dataclass
class ViolationPrediction:
    """Represents a violation prediction."""
    prediction_id: str
    predicted_date: date
    predicted_violations: int
    confidence_interval: Tuple[int, int]  # Lower and upper bounds
    prediction_type: str  # 'short_term', 'medium_term', 'long_term'
    factors: Dict[str, float]  # Contributing factors


@dataclass
class TrendInsight:
    """Represents a trend insight."""
    insight_id: str
    insight_type: str
    description: str
    confidence: float
    impact_score: float
    recommendations: List[str]


class MLPredictor:
    """Machine learning predictor for violation forecasting."""
    
    def __init__(self):
        """Initialize ML predictor."""
        self.logger = logging.getLogger(__name__)
        self.models = {}
        self.scalers = {}
        self.is_trained = False
    
    def train_models(self, historical_data: pd.DataFrame):
        """Train ML models on historical data."""
        if not XGBOOST_AVAILABLE:
            self.logger.warning("XGBoost not available. Using basic forecasting.")
            return
        
        try:
            # Prepare features
            features = self._prepare_features(historical_data)
            
            # Train XGBoost model for violation prediction
            self._train_xgboost_model(features)
            
            self.is_trained = True
            self.logger.info("ML models trained successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to train ML models: {e}")
    
    def _prepare_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Prepare features for ML training."""
        # Create time-based features
        data['year'] = data['scan_timestamp'].dt.year
        data['month'] = data['scan_timestamp'].dt.month
        data['day_of_week'] = data['scan_timestamp'].dt.dayofweek
        data['day_of_year'] = data['scan_timestamp'].dt.dayofyear
        
        # Create lag features
        data['violations_lag_1'] = data['total_violations'].shift(1)
        data['violations_lag_7'] = data['total_violations'].shift(7)
        data['violations_lag_30'] = data['total_violations'].shift(30)
        
        # Create rolling statistics
        data['violations_ma_7'] = data['total_violations'].rolling(window=7).mean()
        data['violations_ma_30'] = data['total_violations'].rolling(window=30).mean()
        data['violations_std_7'] = data['total_violations'].rolling(window=7).std()
        
        # Create trend features
        data['violations_trend'] = data['total_violations'].diff()
        data['violations_trend_ma'] = data['violations_trend'].rolling(window=7).mean()
        
        return data.dropna()
    
    def _train_xgboost_model(self, features: pd.DataFrame):
        """Train XGBoost model."""
        # Select feature columns
        feature_cols = [col for col in features.columns if col not in ['scan_timestamp', 'total_violations']]
        X = features[feature_cols]
        y = features['total_violations']
        
        # Scale features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        self.scalers['xgboost'] = scaler
        
        # Train model
        model = xgb.XGBRegressor(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=42
        )
        model.fit(X_scaled, y)
        self.models['xgboost'] = model
        
        # Calculate feature importance
        feature_importance = dict(zip(feature_cols, model.feature_importances_))
        self.logger.info(f"Feature importance: {feature_importance}")
    
    def predict_violations(self, historical_data: pd.DataFrame, periods_ahead: int = 4) -> List[ViolationPrediction]:
        """Predict future violations."""
        if not self.is_trained:
            return self._basic_prediction(historical_data, periods_ahead)
        
        try:
            predictions = []
            current_data = historical_data.copy()
            
            for i in range(periods_ahead):
                # Prepare features for prediction
                features = self._prepare_features(current_data)
                if len(features) == 0:
                    break
                
                # Get latest features
                latest_features = features.iloc[-1:].drop(['scan_timestamp', 'total_violations'], axis=1)
                
                # Scale features
                X_scaled = self.scalers['xgboost'].transform(latest_features)
                
                # Make prediction
                prediction = self.models['xgboost'].predict(X_scaled)[0]
                
                # Calculate confidence interval (simplified)
                confidence_std = np.std(features['total_violations'].tail(30))
                lower_bound = max(0, prediction - 1.96 * confidence_std)
                upper_bound = prediction + 1.96 * confidence_std
                
                # Create prediction
                pred_date = current_data['scan_timestamp'].iloc[-1] + timedelta(days=7)
                prediction_obj = ViolationPrediction(
                    prediction_id=f"pred_{int(datetime.now().timestamp())}_{i}",
                    predicted_date=pred_date.date(),
                    predicted_violations=int(prediction),
                    confidence_interval=(int(lower_bound), int(upper_bound)),
                    prediction_type='short_term' if i < 2 else 'medium_term',
                    factors={}  # Would be populated with feature importance
                )
                predictions.append(prediction_obj)
                
                # Add prediction to data for next iteration
                new_row = current_data.iloc[-1:].copy()
                new_row['scan_timestamp'] = pred_date
                new_row['total_violations'] = prediction
                current_data = pd.concat([current_data, new_row], ignore_index=True)
            
            return predictions
            
        except Exception as e:
            self.logger.error(f"ML prediction failed: {e}")
            return self._basic_prediction(historical_data, periods_ahead)
    
    def _basic_prediction(self, historical_data: pd.DataFrame, periods_ahead: int) -> List[ViolationPrediction]:
        """Basic prediction using simple moving average."""
        predictions = []
        
        if len(historical_data) < 7:
            return predictions
        
        # Calculate moving average
        ma_7 = historical_data['total_violations'].tail(7).mean()
        ma_30 = historical_data['total_violations'].tail(30).mean() if len(historical_data) >= 30 else ma_7
        
        # Use weighted average
        predicted_value = (ma_7 * 0.7 + ma_30 * 0.3)
        
        for i in range(periods_ahead):
            pred_date = historical_data['scan_timestamp'].iloc[-1] + timedelta(days=7 * (i + 1))
            
            prediction = ViolationPrediction(
                prediction_id=f"basic_pred_{int(datetime.now().timestamp())}_{i}",
                predicted_date=pred_date.date(),
                predicted_violations=int(predicted_value),
                confidence_interval=(int(predicted_value * 0.8), int(predicted_value * 1.2)),
                prediction_type='short_term' if i < 2 else 'medium_term',
                factors={'method': 'moving_average'}
            )
            predictions.append(prediction)
        
        return predictions


class AnomalyDetector:
    """Anomaly detection for violation patterns."""
    
    def __init__(self):
        """Initialize anomaly detector."""
        self.logger = logging.getLogger(__name__)
        self.isolation_forest = None
        self.scaler = None
        self.is_trained = False
    
    def train_detector(self, historical_data: pd.DataFrame):
        """Train anomaly detection model."""
        if not SKLEARN_AVAILABLE:
            self.logger.warning("scikit-learn not available. Using basic anomaly detection.")
            return
        
        try:
            # Prepare features for anomaly detection
            features = self._prepare_anomaly_features(historical_data)
            
            if len(features) < 10:
                self.logger.warning("Insufficient data for anomaly detection training")
                return
            
            # Scale features
            self.scaler = StandardScaler()
            features_scaled = self.scaler.fit_transform(features)
            
            # Train Isolation Forest
            self.isolation_forest = IsolationForest(
                contamination=0.1,  # Expect 10% anomalies
                random_state=42
            )
            self.isolation_forest.fit(features_scaled)
            
            self.is_trained = True
            self.logger.info("Anomaly detector trained successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to train anomaly detector: {e}")
    
    def _prepare_anomaly_features(self, data: pd.DataFrame) -> np.ndarray:
        """Prepare features for anomaly detection."""
        features = []
        
        for _, row in data.iterrows():
            feature_vector = [
                row['total_violations'],
                row['critical_violations'],
                row['high_violations'],
                row['medium_violations'],
                row['low_violations'],
                row['scan_duration_seconds'] if 'scan_duration_seconds' in row else 0,
                row['total_files'] if 'total_files' in row else 0
            ]
            features.append(feature_vector)
        
        return np.array(features)
    
    def detect_anomalies(self, historical_data: pd.DataFrame) -> List[Anomaly]:
        """Detect anomalies in violation patterns."""
        anomalies = []
        
        if not self.is_trained:
            return self._basic_anomaly_detection(historical_data)
        
        try:
            # Prepare features
            features = self._prepare_anomaly_features(historical_data)
            features_scaled = self.scaler.transform(features)
            
            # Detect anomalies
            anomaly_scores = self.isolation_forest.decision_function(features_scaled)
            anomaly_predictions = self.isolation_forest.predict(features_scaled)
            
            # Process results
            for i, (score, prediction) in enumerate(zip(anomaly_scores, anomaly_predictions)):
                if prediction == -1:  # Anomaly detected
                    row = historical_data.iloc[i]
                    
                    # Determine anomaly type
                    anomaly_type = self._classify_anomaly_type(row, historical_data, i)
                    
                    # Calculate severity
                    severity = min(1.0, abs(score) / 2.0)
                    
                    anomaly = Anomaly(
                        anomaly_id=f"anomaly_{int(datetime.now().timestamp())}_{i}",
                        anomaly_type=anomaly_type,
                        timestamp=row['scan_timestamp'],
                        severity=severity,
                        description=self._generate_anomaly_description(row, anomaly_type),
                        affected_metrics=['total_violations', 'critical_violations'],
                        confidence=min(1.0, abs(score)),
                        suggested_actions=self._generate_suggested_actions(anomaly_type, row)
                    )
                    anomalies.append(anomaly)
            
            return anomalies
            
        except Exception as e:
            self.logger.error(f"Anomaly detection failed: {e}")
            return self._basic_anomaly_detection(historical_data)
    
    def _classify_anomaly_type(self, row: pd.Series, data: pd.DataFrame, index: int) -> AnomalyType:
        """Classify the type of anomaly."""
        if index < 7:
            return AnomalyType.OUTLIER
        
        # Compare with recent average
        recent_data = data.iloc[max(0, index-7):index]
        avg_violations = recent_data['total_violations'].mean()
        
        if row['total_violations'] > avg_violations * 1.5:
            return AnomalyType.SPIKE
        elif row['total_violations'] < avg_violations * 0.5:
            return AnomalyType.DROP
        else:
            return AnomalyType.PATTERN_CHANGE
    
    def _generate_anomaly_description(self, row: pd.Series, anomaly_type: AnomalyType) -> str:
        """Generate description for anomaly."""
        descriptions = {
            AnomalyType.SPIKE: f"Unusual spike in violations detected: {row['total_violations']} violations",
            AnomalyType.DROP: f"Significant drop in violations detected: {row['total_violations']} violations",
            AnomalyType.PATTERN_CHANGE: "Change in violation pattern detected",
            AnomalyType.OUTLIER: f"Outlier detected with {row['total_violations']} violations"
        }
        return descriptions.get(anomaly_type, "Anomaly detected")
    
    def _generate_suggested_actions(self, anomaly_type: AnomalyType, row: pd.Series) -> List[str]:
        """Generate suggested actions for anomaly."""
        actions = {
            AnomalyType.SPIKE: [
                "Review recent code changes",
                "Check for new PII patterns",
                "Verify scan configuration",
                "Investigate critical violations"
            ],
            AnomalyType.DROP: [
                "Verify scan completeness",
                "Check for configuration changes",
                "Review remediation efforts"
            ],
            AnomalyType.PATTERN_CHANGE: [
                "Analyze violation type distribution",
                "Review scanning patterns",
                "Check for process changes"
            ],
            AnomalyType.OUTLIER: [
                "Investigate specific scan",
                "Review scan parameters",
                "Check for data quality issues"
            ]
        }
        return actions.get(anomaly_type, ["Investigate anomaly"])
    
    def _basic_anomaly_detection(self, historical_data: pd.DataFrame) -> List[Anomaly]:
        """Basic anomaly detection using statistical methods."""
        anomalies = []
        
        if len(historical_data) < 7:
            return anomalies
        
        # Calculate rolling statistics
        data = historical_data.copy()
        data['violations_ma'] = data['total_violations'].rolling(window=7).mean()
        data['violations_std'] = data['total_violations'].rolling(window=7).std()
        
        # Detect anomalies using z-score
        data['z_score'] = (data['total_violations'] - data['violations_ma']) / data['violations_std']
        
        for i, row in data.iterrows():
            if abs(row['z_score']) > 2.0:  # Z-score threshold
                anomaly_type = AnomalyType.SPIKE if row['z_score'] > 0 else AnomalyType.DROP
                
                anomaly = Anomaly(
                    anomaly_id=f"basic_anomaly_{int(datetime.now().timestamp())}_{i}",
                    anomaly_type=anomaly_type,
                    timestamp=row['scan_timestamp'],
                    severity=min(1.0, abs(row['z_score']) / 3.0),
                    description=f"Statistical anomaly detected (z-score: {row['z_score']:.2f})",
                    affected_metrics=['total_violations'],
                    confidence=min(1.0, abs(row['z_score']) / 3.0),
                    suggested_actions=self._generate_suggested_actions(anomaly_type, row)
                )
                anomalies.append(anomaly)
        
        return anomalies


class AdvancedTrendAnalyzer(TrendAnalyzer):
    """
    Advanced trend analyzer with ML-powered forecasting and anomaly detection.
    Enhanced version of the original TrendAnalyzer.
    """
    
    def __init__(self):
        """Initialize advanced trend analyzer."""
        super().__init__()
        self.ml_predictor = MLPredictor()
        self.anomaly_detector = AnomalyDetector()
        self.is_trained = False
    
    def train_models(self, scans: List[ScanHistoryEntry]):
        """Train ML models on historical scan data."""
        if len(scans) < 30:
            self.logger.warning("Insufficient data for ML training. Need at least 30 scans.")
            return
        
        try:
            # Convert to DataFrame
            data = self._scans_to_dataframe(scans)
            
            # Train ML predictor
            self.ml_predictor.train_models(data)
            
            # Train anomaly detector
            self.anomaly_detector.train_detector(data)
            
            self.is_trained = True
            self.logger.info("Advanced trend analyzer models trained successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to train advanced trend analyzer: {e}")
    
    def _scans_to_dataframe(self, scans: List[ScanHistoryEntry]) -> pd.DataFrame:
        """Convert scan history to DataFrame."""
        data = []
        for scan in scans:
            data.append({
                'scan_timestamp': scan.scan_timestamp,
                'total_violations': scan.total_violations,
                'critical_violations': scan.critical_violations,
                'high_violations': scan.high_violations,
                'medium_violations': scan.medium_violations,
                'low_violations': scan.low_violations,
                'total_files': scan.total_files,
                'scan_duration_seconds': scan.scan_duration_seconds
            })
        
        df = pd.DataFrame(data)
        df = df.sort_values('scan_timestamp').reset_index(drop=True)
        return df
    
    def calculate_violation_trends(self, scans: List[ScanHistoryEntry], 
                                  period_days: int = 30) -> List[ViolationTrend]:
        """Calculate violation trends with enhanced analysis."""
        # Use original implementation as base
        base_trends = super().calculate_violation_trends(scans, period_days)
        
        # Enhance with ML insights if trained
        if self.is_trained and len(scans) > 0:
            try:
                data = self._scans_to_dataframe(scans)
                
                # Add ML-based insights to trends
                for trend in base_trends:
                    trend.ml_insights = self._generate_trend_insights(trend, data)
                    
            except Exception as e:
                self.logger.error(f"Failed to enhance trends with ML: {e}")
        
        return base_trends
    
    def predict_future_violations(self, scans: List[ScanHistoryEntry], 
                                 periods_ahead: int = 4) -> List[ViolationPrediction]:
        """Predict future violations using ML."""
        if len(scans) < 7:
            self.logger.warning("Insufficient data for prediction")
            return []
        
        try:
            data = self._scans_to_dataframe(scans)
            return self.ml_predictor.predict_violations(data, periods_ahead)
            
        except Exception as e:
            self.logger.error(f"Prediction failed: {e}")
            return []
    
    def detect_anomalies(self, scans: List[ScanHistoryEntry]) -> List[Anomaly]:
        """Detect anomalies in violation patterns."""
        if len(scans) < 7:
            self.logger.warning("Insufficient data for anomaly detection")
            return []
        
        try:
            data = self._scans_to_dataframe(scans)
            return self.anomaly_detector.detect_anomalies(data)
            
        except Exception as e:
            self.logger.error(f"Anomaly detection failed: {e}")
            return []
    
    def calculate_compliance_metrics(self, company_id: str, scans: List[ScanHistoryEntry], 
                                   violations: List[ViolationRecord]) -> ComplianceMetrics:
        """Calculate enhanced compliance metrics."""
        # Use original implementation as base
        base_metrics = super().calculate_compliance_metrics(company_id, scans, violations)
        
        # Enhance with ML insights
        if self.is_trained and len(scans) > 0:
            try:
                data = self._scans_to_dataframe(scans)
                
                # Add ML-based risk assessment
                base_metrics.risk_assessment = self._calculate_risk_assessment(data, violations)
                
                # Add trend predictions
                predictions = self.predict_future_violations(scans, 4)
                base_metrics.forecasted_violations = predictions
                
                # Add anomaly detection
                anomalies = self.detect_anomalies(scans)
                base_metrics.anomalies = anomalies
                
            except Exception as e:
                self.logger.error(f"Failed to enhance compliance metrics: {e}")
        
        return base_metrics
    
    def _generate_trend_insights(self, trend: ViolationTrend, data: pd.DataFrame) -> List[TrendInsight]:
        """Generate ML-based insights for trends."""
        insights = []
        
        # Analyze trend direction
        if trend.improvement_percentage > 10:
            insights.append(TrendInsight(
                insight_id=f"improvement_{int(datetime.now().timestamp())}",
                insight_type="positive_trend",
                description=f"Strong improvement trend: {trend.improvement_percentage:.1f}% reduction",
                confidence=0.8,
                impact_score=0.7,
                recommendations=["Continue current remediation efforts", "Document successful practices"]
            ))
        elif trend.improvement_percentage < -10:
            insights.append(TrendInsight(
                insight_id=f"deterioration_{int(datetime.now().timestamp())}",
                insight_type="negative_trend",
                description=f"Concerning deterioration: {abs(trend.improvement_percentage):.1f}% increase",
                confidence=0.8,
                impact_score=0.9,
                recommendations=["Investigate root causes", "Implement additional controls", "Review processes"]
            ))
        
        return insights
    
    def _calculate_risk_assessment(self, data: pd.DataFrame, violations: List[ViolationRecord]) -> Dict[str, Any]:
        """Calculate ML-based risk assessment."""
        if len(data) < 7:
            return {"risk_level": "unknown", "confidence": 0.0}
        
        # Calculate trend-based risk
        recent_violations = data['total_violations'].tail(7).mean()
        historical_violations = data['total_violations'].mean()
        
        trend_risk = (recent_violations - historical_violations) / historical_violations
        
        # Calculate volatility risk
        volatility = data['total_violations'].std() / data['total_violations'].mean()
        
        # Calculate critical violation risk
        critical_violations = sum(1 for v in violations if v.severity == 'critical')
        critical_risk = critical_violations / len(violations) if violations else 0
        
        # Combine risk factors
        overall_risk = (abs(trend_risk) * 0.4 + volatility * 0.3 + critical_risk * 0.3)
        
        if overall_risk < 0.2:
            risk_level = "low"
        elif overall_risk < 0.5:
            risk_level = "medium"
        else:
            risk_level = "high"
        
        return {
            "risk_level": risk_level,
            "risk_score": overall_risk,
            "trend_risk": abs(trend_risk),
            "volatility_risk": volatility,
            "critical_risk": critical_risk,
            "confidence": min(1.0, len(data) / 30.0)
        }
    
    def get_model_status(self) -> Dict[str, Any]:
        """Get status of ML models."""
        return {
            "is_trained": self.is_trained,
            "ml_predictor_available": XGBOOST_AVAILABLE,
            "anomaly_detector_available": SKLEARN_AVAILABLE,
            "prophet_available": PROPHET_AVAILABLE,
            "training_data_requirements": {
                "minimum_scans": 30,
                "recommended_scans": 100
            }
        }
