"""
Model management module for MarACO API
Handles model loading, saving, and inference
"""

import numpy as np
import joblib
import json
from pathlib import Path
from typing import Dict, List, Union, Optional, Tuple
import warnings
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import xgboost as xgb


class ModelManager:
    """
    Model management class for marine acoustic classification
    """
    
    def __init__(self, model_dir: Optional[Union[str, Path]] = None, model_name: str = "maraco_models"):
        """
        Initialize model manager
        
        Args:
            model_dir: Directory to store/load models
            model_name: Name of the model files
        """
        self.model_dir = Path(model_dir) if model_dir else Path("models")
        self.model_name = model_name
        self.model_dir.mkdir(exist_ok=True)
        
        # Model components
        self.pre_classifier = None  # Fast binary classifier
        self.detailed_classifier = None  # Multi-class classifier
        self.scaler = None
        self.label_encoder = None
        
        # Class labels
        self.classes = [
            'FIN_WHALE',
            'HUMPBACK_WHALE', 
            'RIGHT_WHALE',
            'SONAR',
            'VESSEL',
            'EXPLOSION',
            'PHYSICAL_NOISE',
            'OTHER'
        ]
        
        # Model configuration
        self.model_config = {
            'pre_classifier': {
                'type': 'RandomForest',
                'n_estimators': 100,
                'max_depth': 10,
                'random_state': 42
            },
            'detailed_classifier': {
                'type': 'XGBoost',
                'n_estimators': 200,
                'max_depth': 6,
                'learning_rate': 0.1,
                'random_state': 42
            }
        }
    
    def create_pre_classifier(self) -> RandomForestClassifier:
        """
        Create fast pre-classifier for binary classification
        
        Returns:
            RandomForest classifier
        """
        config = self.model_config['pre_classifier']
        return RandomForestClassifier(
            n_estimators=config['n_estimators'],
            max_depth=config['max_depth'],
            random_state=config['random_state'],
            n_jobs=-1
        )
    
    def create_detailed_classifier(self) -> xgb.XGBClassifier:
        """
        Create detailed classifier for multi-class classification
        
        Returns:
            XGBoost classifier
        """
        config = self.model_config['detailed_classifier']
        return xgb.XGBClassifier(
            n_estimators=config['n_estimators'],
            max_depth=config['max_depth'],
            learning_rate=config['learning_rate'],
            random_state=config['random_state'],
            n_jobs=-1
        )
    
    def train_models(self, X: np.ndarray, y: np.ndarray, 
                    test_size: float = 0.2) -> Dict[str, float]:
        """
        Train both pre-classifier and detailed classifier
        
        Args:
            X: Feature matrix
            y: Target labels
            test_size: Fraction of data for testing
            
        Returns:
            Dictionary with training metrics
        """
        # Ensure X and y have the same number of samples
        if len(X) != len(y):
            min_samples = min(len(X), len(y))
            X = X[:min_samples]
            y = y[:min_samples]
            print(f"Warning: Adjusted to {min_samples} samples due to preprocessing mismatches")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )
        
        # Create and fit scaler
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Create label encoder
        self.label_encoder = LabelEncoder()
        y_train_encoded = self.label_encoder.fit_transform(y_train)
        y_test_encoded = self.label_encoder.transform(y_test)
        
        # Create binary labels for pre-classifier (marine vs non-marine)
        marine_classes = ['FIN_WHALE', 'HUMPBACK_WHALE', 'RIGHT_WHALE', 'SONAR']
        y_binary_train = np.isin(y_train, marine_classes).astype(int)
        y_binary_test = np.isin(y_test, marine_classes).astype(int)
        
        # Train pre-classifier
        print("Training pre-classifier...")
        self.pre_classifier = self.create_pre_classifier()
        self.pre_classifier.fit(X_train_scaled, y_binary_train)
        
        # Train detailed classifier
        print("Training detailed classifier...")
        self.detailed_classifier = self.create_detailed_classifier()
        self.detailed_classifier.fit(X_train_scaled, y_train_encoded)
        
        # Evaluate models
        metrics = {}
        
        # Pre-classifier metrics
        pre_pred = self.pre_classifier.predict(X_test_scaled)
        pre_accuracy = np.mean(pre_pred == y_binary_test)
        metrics['pre_classifier_accuracy'] = pre_accuracy
        
        # Detailed classifier metrics
        detailed_pred = self.detailed_classifier.predict(X_test_scaled)
        detailed_accuracy = np.mean(detailed_pred == y_test_encoded)
        metrics['detailed_classifier_accuracy'] = detailed_accuracy
        
        # Combined accuracy
        combined_pred = self._combine_predictions(X_test_scaled)
        combined_accuracy = np.mean(combined_pred == y_test)
        metrics['combined_accuracy'] = combined_accuracy
        
        print(f"Pre-classifier accuracy: {pre_accuracy:.3f}")
        print(f"Detailed classifier accuracy: {detailed_accuracy:.3f}")
        print(f"Combined accuracy: {combined_accuracy:.3f}")
        
        return metrics
    
    def _combine_predictions(self, X: np.ndarray) -> np.ndarray:
        """
        Combine pre-classifier and detailed classifier predictions
        
        Args:
            X: Feature matrix
            
        Returns:
            Combined predictions
        """
        # Get pre-classifier prediction
        pre_pred = self.pre_classifier.predict(X)
        
        # Get detailed classifier prediction
        detailed_pred = self.detailed_classifier.predict(X)
        detailed_pred_labels = self.label_encoder.inverse_transform(detailed_pred)
        
        # Combine: if pre-classifier says non-marine, return OTHER
        # Otherwise, return detailed classifier prediction
        combined = np.where(
            pre_pred == 0,  # Non-marine
            'OTHER',
            detailed_pred_labels
        )
        
        return combined
    
    def predict(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Make predictions using the combined model
        
        Args:
            X: Feature matrix
            
        Returns:
            Tuple of (predictions, confidence_scores)
        """
        if self.scaler is None or self.pre_classifier is None or self.detailed_classifier is None:
            raise ValueError("Models not trained. Call train_models() first.")
        
        # Scale features
        X_scaled = self.scaler.transform(X)
        
        # Get predictions
        predictions = self._combine_predictions(X_scaled)
        
        # Get confidence scores
        pre_proba = self.pre_classifier.predict_proba(X_scaled)
        detailed_proba = self.detailed_classifier.predict_proba(X_scaled)
        
        # Calculate confidence scores
        confidence_scores = []
        for i, pred in enumerate(predictions):
            if pred == 'OTHER':
                # Confidence for non-marine classification
                conf = pre_proba[i, 0]  # Probability of non-marine
            else:
                # Confidence for marine classification
                marine_conf = pre_proba[i, 1]  # Probability of marine
                class_idx = self.label_encoder.transform([pred])[0]
                class_conf = detailed_proba[i, class_idx]  # Probability of specific class
                conf = marine_conf * class_conf
            confidence_scores.append(conf)
        
        return predictions, np.array(confidence_scores)
    
    def save_models(self, model_name: str = "maraco_models") -> Dict[str, str]:
        """
        Save all model components
        
        Args:
            model_name: Base name for model files
            
        Returns:
            Dictionary with saved file paths
        """
        saved_files = {}
        
        # Save pre-classifier
        pre_classifier_path = self.model_dir / f"{model_name}_pre_classifier.joblib"
        joblib.dump(self.pre_classifier, pre_classifier_path)
        saved_files['pre_classifier'] = str(pre_classifier_path)
        
        # Save detailed classifier
        detailed_classifier_path = self.model_dir / f"{model_name}_detailed_classifier.joblib"
        joblib.dump(self.detailed_classifier, detailed_classifier_path)
        saved_files['detailed_classifier'] = str(detailed_classifier_path)
        
        # Save scaler
        scaler_path = self.model_dir / f"{model_name}_scaler.joblib"
        joblib.dump(self.scaler, scaler_path)
        saved_files['scaler'] = str(scaler_path)
        
        # Save label encoder
        label_encoder_path = self.model_dir / f"{model_name}_label_encoder.joblib"
        joblib.dump(self.label_encoder, label_encoder_path)
        saved_files['label_encoder'] = str(label_encoder_path)
        
        # Save model configuration
        config_path = self.model_dir / f"{model_name}_config.json"
        with open(config_path, 'w') as f:
            json.dump(self.model_config, f, indent=2)
        saved_files['config'] = str(config_path)
        
        print(f"Models saved to {self.model_dir}")
        return saved_files
    
    def load_models(self, model_name: Optional[str] = None) -> bool:
        """
        Load all model components
        
        Args:
            model_name: Base name for model files (uses instance model_name if None)
            
        Returns:
            True if successful, False otherwise
        """
        if model_name is None:
            model_name = self.model_name
            
        try:
            # Load pre-classifier
            pre_classifier_path = self.model_dir / f"{model_name}_pre_classifier.joblib"
            if pre_classifier_path.exists():
                self.pre_classifier = joblib.load(pre_classifier_path)
            else:
                warnings.warn(f"Pre-classifier not found: {pre_classifier_path}")
                return False
            
            # Load detailed classifier
            detailed_classifier_path = self.model_dir / f"{model_name}_detailed_classifier.joblib"
            if detailed_classifier_path.exists():
                self.detailed_classifier = joblib.load(detailed_classifier_path)
            else:
                warnings.warn(f"Detailed classifier not found: {detailed_classifier_path}")
                return False
            
            # Load scaler
            scaler_path = self.model_dir / f"{model_name}_scaler.joblib"
            if scaler_path.exists():
                self.scaler = joblib.load(scaler_path)
            else:
                warnings.warn(f"Scaler not found: {scaler_path}")
                return False
            
            # Load label encoder
            label_encoder_path = self.model_dir / f"{model_name}_label_encoder.joblib"
            if label_encoder_path.exists():
                self.label_encoder = joblib.load(label_encoder_path)
            else:
                warnings.warn(f"Label encoder not found: {label_encoder_path}")
                return False
            
            # Load configuration
            config_path = self.model_dir / f"{model_name}_config.json"
            if config_path.exists():
                with open(config_path, 'r') as f:
                    self.model_config = json.load(f)
            
            print(f"Models loaded from {self.model_dir}")
            return True
            
        except Exception as e:
            warnings.warn(f"Failed to load models: {str(e)}")
            return False
    
    def get_model_info(self) -> Dict[str, Union[str, int, List[str]]]:
        """
        Get information about loaded models
        
        Returns:
            Dictionary with model information
        """
        info = {
            'classes': self.classes,
            'model_loaded': self.pre_classifier is not None and self.detailed_classifier is not None,
            'scaler_loaded': self.scaler is not None,
            'label_encoder_loaded': self.label_encoder is not None
        }
        
        if self.pre_classifier is not None:
            info['pre_classifier_type'] = type(self.pre_classifier).__name__
            info['pre_classifier_n_features'] = self.pre_classifier.n_features_in_
        
        if self.detailed_classifier is not None:
            info['detailed_classifier_type'] = type(self.detailed_classifier).__name__
            info['detailed_classifier_n_features'] = self.detailed_classifier.n_features_in_
        
        return info
