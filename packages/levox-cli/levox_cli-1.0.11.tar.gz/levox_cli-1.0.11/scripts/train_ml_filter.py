#!/usr/bin/env python3
"""
Training script for Levox ML false-positive filter.
"""

import sys
import json
import pickle
import logging
from pathlib import Path
from typing import List, Dict, Any

# Add levox to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import numpy as np
    import pandas as pd
    from sklearn.model_selection import train_test_split, cross_val_score
    from sklearn.metrics import classification_report, accuracy_score, precision_recall_fscore_support
    import xgboost as xgb
    ML_AVAILABLE = True
except ImportError as e:
    print(f"ML dependencies not available: {e}")
    print("Please install: pip install xgboost scikit-learn")
    sys.exit(1)

from levox.core.config import load_default_config
from levox.detection.ml_filter import MLFilter


def create_training_data() -> List[Dict[str, Any]]:
    """Create comprehensive training dataset for ML filter."""
    training_data = []
    
    # True positives - real PII examples
    true_positives = [
        # Email examples
        {
            'pattern_type': 'email',
            'entropy_score': 3.2,
            'code_context': 'user_email = "john.doe@company.com"',
            'line_length': 35,
            'has_quotes': True,
            'has_numbers': False,
            'context_tokens': ['user', 'email', 'contact', 'notification', 'send'],
            'is_true_positive': True,
            'source': 'curated_examples',
            'confidence_score': 0.9
        },
        {
            'pattern_type': 'email',
            'entropy_score': 3.1,
            'code_context': 'send_notification("alice@example.org", message)',
            'line_length': 45,
            'has_quotes': True,
            'has_numbers': False,
            'context_tokens': ['send', 'notification', 'message', 'email'],
            'is_true_positive': True,
            'source': 'curated_examples',
            'confidence_score': 0.85
        },
        
        # Credit card examples
        {
            'pattern_type': 'credit_card',
            'entropy_score': 2.8,
            'code_context': 'card_number = "4532-1234-5678-9012"',
            'line_length': 35,
            'has_quotes': True,
            'has_numbers': True,
            'context_tokens': ['card', 'number', 'payment', 'transaction'],
            'is_true_positive': True,
            'source': 'curated_examples',
            'confidence_score': 0.95
        },
        {
            'pattern_type': 'credit_card',
            'entropy_score': 2.7,
            'code_context': 'process_payment(cc="5555444433332222")',
            'line_length': 40,
            'has_quotes': True,
            'has_numbers': True,
            'context_tokens': ['process', 'payment', 'cc', 'transaction'],
            'is_true_positive': True,
            'source': 'curated_examples',
            'confidence_score': 0.9
        },
        
        # SSN examples
        {
            'pattern_type': 'ssn',
            'entropy_score': 2.5,
            'code_context': 'ssn = "123-45-6789"',
            'line_length': 18,
            'has_quotes': True,
            'has_numbers': True,
            'context_tokens': ['ssn', 'social', 'security', 'personal'],
            'is_true_positive': True,
            'source': 'curated_examples',
            'confidence_score': 0.95
        },
        
        # Phone examples
        {
            'pattern_type': 'phone',
            'entropy_score': 2.3,
            'code_context': 'contact_phone = "555-123-4567"',
            'line_length': 30,
            'has_quotes': True,
            'has_numbers': True,
            'context_tokens': ['contact', 'phone', 'number', 'call'],
            'is_true_positive': True,
            'source': 'curated_examples',
            'confidence_score': 0.8
        },
        
        # API key examples
        {
            'pattern_type': 'api_key',
            'entropy_score': 4.2,
            'code_context': 'api_key = "sk-1234567890abcdef"',
            'line_length': 30,
            'has_quotes': True,
            'has_numbers': True,
            'context_tokens': ['api', 'key', 'secret', 'auth', 'token'],
            'is_true_positive': True,
            'source': 'curated_examples',
            'confidence_score': 0.95
        }
    ]
    
    # False positives - common false alarms
    false_positives = [
        # Version numbers that look like credit cards
        {
            'pattern_type': 'credit_card',
            'entropy_score': 1.2,
            'code_context': 'version = "1.2.3.4"',
            'line_length': 18,
            'has_quotes': True,
            'has_numbers': True,
            'context_tokens': ['version', 'number', 'release', 'build'],
            'is_true_positive': False,
            'source': 'curated_examples',
            'confidence_score': 0.1
        },
        {
            'pattern_type': 'credit_card',
            'entropy_score': 1.1,
            'code_context': 'BUILD_NUMBER = "2024.01.15.001"',
            'line_length': 30,
            'has_quotes': True,
            'has_numbers': True,
            'context_tokens': ['build', 'number', 'version', 'release'],
            'is_true_positive': False,
            'source': 'curated_examples',
            'confidence_score': 0.05
        },
        
        # Example/test emails
        {
            'pattern_type': 'email',
            'entropy_score': 2.1,
            'code_context': 'test_email = "test@example.com"',
            'line_length': 30,
            'has_quotes': True,
            'has_numbers': False,
            'context_tokens': ['test', 'example', 'demo', 'sample'],
            'is_true_positive': False,
            'source': 'curated_examples',
            'confidence_score': 0.2
        },
        {
            'pattern_type': 'email',
            'entropy_score': 1.8,
            'code_context': 'EXAMPLE_EMAIL = "user@localhost"',
            'line_length': 32,
            'has_quotes': True,
            'has_numbers': False,
            'context_tokens': ['example', 'email', 'localhost', 'test'],
            'is_true_positive': False,
            'source': 'curated_examples',
            'confidence_score': 0.1
        },
        
        # Phone extensions that look like SSN
        {
            'pattern_type': 'ssn',
            'entropy_score': 1.5,
            'code_context': 'extension = "123-45-6789"',
            'line_length': 25,
            'has_quotes': True,
            'has_numbers': True,
            'context_tokens': ['extension', 'phone', 'call', 'dial'],
            'is_true_positive': False,
            'source': 'curated_examples',
            'confidence_score': 0.15
        },
        
        # Test phone numbers
        {
            'pattern_type': 'phone',
            'entropy_score': 1.8,
            'code_context': 'TEST_PHONE = "555-000-0000"',
            'line_length': 28,
            'has_quotes': True,
            'has_numbers': True,
            'context_tokens': ['test', 'phone', 'example', 'demo'],
            'is_true_positive': False,
            'source': 'curated_examples',
            'confidence_score': 0.1
        },
        
        # Random strings that look like API keys
        {
            'pattern_type': 'api_key',
            'entropy_score': 2.1,
            'code_context': 'random_id = "abcdef1234567890"',
            'line_length': 30,
            'has_quotes': True,
            'has_numbers': True,
            'context_tokens': ['random', 'id', 'identifier', 'uuid'],
            'is_true_positive': False,
            'source': 'curated_examples',
            'confidence_score': 0.3
        }
    ]
    
    # Add variations and edge cases
    training_data.extend(true_positives)
    training_data.extend(false_positives)
    
    # Add some borderline cases with medium confidence
    borderline_cases = [
        {
            'pattern_type': 'email',
            'entropy_score': 2.5,
            'code_context': 'admin@internal.local',
            'line_length': 20,
            'has_quotes': False,
            'has_numbers': False,
            'context_tokens': ['admin', 'internal', 'local'],
            'is_true_positive': True,
            'source': 'curated_examples',
            'confidence_score': 0.6
        },
        {
            'pattern_type': 'phone',
            'entropy_score': 2.0,
            'code_context': 'emergency = "911-123-4567"',
            'line_length': 25,
            'has_quotes': True,
            'has_numbers': True,
            'context_tokens': ['emergency', 'contact', 'phone'],
            'is_true_positive': False,
            'source': 'curated_examples',
            'confidence_score': 0.4
        }
    ]
    
    training_data.extend(borderline_cases)
    
    return training_data


def extract_features(data_point: Dict[str, Any]) -> List[float]:
    """Extract features from a training data point."""
    features = []
    
    # Basic features
    features.append(data_point.get('confidence_score', 0.5))
    features.append(data_point.get('line_length', 0))
    features.append(len(data_point.get('context_tokens', [])))
    features.append(data_point.get('entropy_score', 0.0))
    features.append(1.0 if data_point.get('has_quotes', False) else 0.0)
    features.append(1.0 if data_point.get('has_numbers', False) else 0.0)
    
    # Pattern type encoding
    pattern_encodings = {
        'email': 1.0,
        'credit_card': 2.0,
        'ssn': 3.0,
        'phone': 4.0,
        'api_key': 5.0
    }
    features.append(pattern_encodings.get(data_point.get('pattern_type', ''), 0.0))
    
    # Context analysis features
    context = data_point.get('code_context', '').lower()
    features.append(1.0 if any(word in context for word in ['test', 'example', 'demo', 'mock']) else 0.0)
    features.append(1.0 if any(word in context for word in ['user', 'customer', 'client']) else 0.0)
    features.append(1.0 if any(word in context for word in ['secret', 'key', 'token', 'password']) else 0.0)
    
    # Statistical features
    features.append(len(context))
    features.append(context.count(' '))
    features.append(context.count('_'))
    features.append(context.count('.'))
    
    # Source reliability
    source_scores = {
        'curated_examples': 1.0,
        'user_feedback': 0.8,
        'automated': 0.6
    }
    features.append(source_scores.get(data_point.get('source', ''), 0.5))
    
    # Pad to fixed length (20 features)
    while len(features) < 20:
        features.append(0.0)
    
    return features[:20]  # Truncate if too long


def train_model(training_data: List[Dict[str, Any]]) -> None:
    """Train the XGBoost model."""
    print(f"Training ML model with {len(training_data)} examples...")
    
    # Extract features and labels
    X = []
    y = []
    
    for data_point in training_data:
        features = extract_features(data_point)
        X.append(features)
        y.append(1 if data_point.get('is_true_positive', False) else 0)
    
    X = np.array(X)
    y = np.array(y)
    
    print(f"Feature matrix shape: {X.shape}")
    print(f"Label distribution: {np.bincount(y)}")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Create and train XGBoost model
    model = xgb.XGBClassifier(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        random_state=42,
        eval_metric='logloss'
    )
    
    print("Training XGBoost model...")
    model.fit(X_train, y_train)
    
    # Evaluate model
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)
    
    accuracy = accuracy_score(y_test, y_pred)
    precision, recall, f1, _ = precision_recall_fscore_support(y_test, y_pred, average='binary')
    
    print("\n=== Model Performance ===")
    print(f"Accuracy: {accuracy:.3f}")
    print(f"Precision: {precision:.3f}")
    print(f"Recall: {recall:.3f}")
    print(f"F1-score: {f1:.3f}")
    
    print("\nDetailed Classification Report:")
    print(classification_report(y_test, y_pred, target_names=['False Positive', 'True Positive']))
    
    # Cross-validation
    cv_scores = cross_val_score(model, X, y, cv=5, scoring='f1')
    print(f"\nCross-validation F1 scores: {cv_scores}")
    print(f"Mean CV F1: {cv_scores.mean():.3f} (+/- {cv_scores.std() * 2:.3f})")
    
    # Feature importance
    feature_importance = model.feature_importances_
    feature_names = [
        'confidence_score', 'line_length', 'context_tokens_count', 'entropy_score',
        'has_quotes', 'has_numbers', 'pattern_type', 'has_test_words',
        'has_user_words', 'has_secret_words', 'context_length', 'space_count',
        'underscore_count', 'dot_count', 'source_reliability', 'feature_15',
        'feature_16', 'feature_17', 'feature_18', 'feature_19'
    ]
    
    print("\n=== Feature Importance ===")
    for name, importance in zip(feature_names, feature_importance):
        if importance > 0.01:  # Only show important features
            print(f"{name}: {importance:.3f}")
    
    # Save model
    model_dir = Path(__file__).parent.parent / "configs" / "ml_models"
    model_dir.mkdir(parents=True, exist_ok=True)
    
    model_data = {
        'model': model,
        'feature_extractor': None,  # We handle features manually
        'scaler': None,  # XGBoost handles scaling internally
        'label_encoder': None,
        'model_info': {
            'training_date': pd.Timestamp.now().isoformat(),
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'training_samples': len(X_train),
            'test_samples': len(X_test),
            'model_type': 'XGBoost',
            'feature_count': X.shape[1],
            'cv_mean_f1': cv_scores.mean(),
            'cv_std_f1': cv_scores.std()
        }
    }
    
    model_path = model_dir / "levox_xgb.bin"
    with open(model_path, 'wb') as f:
        pickle.dump(model_data, f)
    
    print(f"\nModel saved to: {model_path}")
    print(f"Model size: {model_path.stat().st_size / 1024:.1f} KB")


def main():
    """Main training function."""
    print("Levox ML Filter Training Script")
    print("=" * 40)
    
    # Create training data
    training_data = create_training_data()
    print(f"Created {len(training_data)} training examples")
    
    # Train model
    train_model(training_data)
    
    print("\nTraining completed successfully!")
    print("You can now use the trained model with Levox.")


if __name__ == "__main__":
    main()
