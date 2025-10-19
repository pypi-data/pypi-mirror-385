"""
Main classifier module for MarACO API
Provides the main interface for marine acoustic classification
"""

import numpy as np
import time
from pathlib import Path
from typing import Union, List, Dict, Optional, Tuple
import warnings

from .preprocessor import AudioPreprocessor
from .feature_extractor import FeatureExtractor
from .model import ModelManager


class MarineAcousticClassifier:
    """
    Main classifier class for marine acoustic sound classification
    """
    
    def __init__(self, 
                 model_dir: Optional[Union[str, Path]] = None,
                 target_sr: int = 16000,
                 duration: float = 5.0,
                 auto_load: bool = True,
                 model_name: str = "maraco_models"):
        """
        Initialize marine acoustic classifier
        
        Args:
            model_dir: Directory containing trained models
            target_sr: Target sample rate for audio processing
            duration: Target duration for audio clips
            auto_load: Whether to automatically load models on initialization
            model_name: Name of the model files to load
        """
        self.model_dir = Path(model_dir) if model_dir else Path("models")
        self.model_name = model_name
        
        # Initialize components
        self.preprocessor = AudioPreprocessor(
            target_sr=target_sr,
            duration=duration
        )
        self.feature_extractor = FeatureExtractor()
        self.model_manager = ModelManager(model_dir=self.model_dir, model_name=self.model_name)
        
        # Load models if available
        if auto_load:
            self._load_models()
    
    def _load_models(self) -> bool:
        """
        Load pre-trained models
        
        Returns:
            True if models loaded successfully
        """
        return self.model_manager.load_models()
    
    def predict(self, audio_path: Union[str, Path], 
                return_confidence: bool = True,
                apply_noise_reduction: bool = True) -> Dict[str, Union[str, float, int]]:
        """
        Predict marine acoustic class for a single audio file
        
        Args:
            audio_path: Path to audio file
            return_confidence: Whether to return confidence score
            apply_noise_reduction: Whether to apply noise reduction
            
        Returns:
            Dictionary with prediction results
        """
        start_time = time.time()
        
        try:
            # Preprocess audio
            audio = self.preprocessor.preprocess_audio(
                audio_path, 
                apply_noise_reduction=apply_noise_reduction
            )
            
            # Extract features
            features = self.feature_extractor.extract_features_for_classification(
                audio, self.preprocessor.target_sr
            )
            
            # Make prediction
            features_array = features.reshape(1, -1)
            predictions, confidence_scores = self.model_manager.predict(features_array)
            
            processing_time = time.time() - start_time
            
            result = {
                'class': predictions[0],
                'processing_time': processing_time,
                'filename': str(Path(audio_path).name)
            }
            
            if return_confidence:
                result['confidence'] = float(confidence_scores[0])
            
            return result
            
        except Exception as e:
            return {
                'class': 'ERROR',
                'confidence': 0.0,
                'processing_time': time.time() - start_time,
                'filename': str(Path(audio_path).name),
                'error': str(e)
            }
    
    def predict_batch(self, audio_paths: List[Union[str, Path]], 
                     return_confidence: bool = True,
                     apply_noise_reduction: bool = True,
                     n_jobs: int = -1) -> List[Dict[str, Union[str, float, int]]]:
        """
        Predict marine acoustic classes for multiple audio files
        
        Args:
            audio_paths: List of audio file paths
            return_confidence: Whether to return confidence scores
            apply_noise_reduction: Whether to apply noise reduction
            n_jobs: Number of parallel jobs for processing
            
        Returns:
            List of prediction results
        """
        from joblib import Parallel, delayed
        
        def process_single(path):
            return self.predict(path, return_confidence, apply_noise_reduction)
        
        results = Parallel(n_jobs=n_jobs)(
            delayed(process_single)(path) for path in audio_paths
        )
        
        return results
    
    def predict_stream(self, audio_chunk: np.ndarray, 
                      sr: int,
                      return_confidence: bool = True) -> Dict[str, Union[str, float, int]]:
        """
        Predict marine acoustic class for streaming audio
        
        Args:
            audio_chunk: Audio data array
            sr: Sample rate
            return_confidence: Whether to return confidence score
            
        Returns:
            Dictionary with prediction results
        """
        start_time = time.time()
        
        try:
            # Resample if needed
            if sr != self.preprocessor.target_sr:
                audio_chunk = self.preprocessor.resample_audio(audio_chunk, sr)
            
            # Segment audio
            audio_chunk = self.preprocessor.segment_audio(
                audio_chunk, self.preprocessor.target_sr
            )
            
            # Normalize
            audio_chunk = self.preprocessor.normalize_audio(audio_chunk)
            
            # Extract features
            features = self.feature_extractor.extract_features_for_classification(
                audio_chunk, self.preprocessor.target_sr
            )
            
            # Make prediction
            features_array = features.reshape(1, -1)
            predictions, confidence_scores = self.model_manager.predict(features_array)
            
            processing_time = time.time() - start_time
            
            result = {
                'class': predictions[0],
                'processing_time': processing_time
            }
            
            if return_confidence:
                result['confidence'] = float(confidence_scores[0])
            
            return result
            
        except Exception as e:
            return {
                'class': 'ERROR',
                'confidence': 0.0,
                'processing_time': time.time() - start_time,
                'error': str(e)
            }
    
    def get_supported_classes(self) -> List[str]:
        """
        Get list of supported classification classes
        
        Returns:
            List of class names
        """
        return self.model_manager.classes.copy()
    
    def get_model_info(self) -> Dict[str, Union[str, int, List[str], bool]]:
        """
        Get information about loaded models
        
        Returns:
            Dictionary with model information
        """
        return self.model_manager.get_model_info()
    
    def is_model_loaded(self) -> bool:
        """
        Check if models are loaded and ready for prediction
        
        Returns:
            True if models are loaded
        """
        return (self.model_manager.pre_classifier is not None and 
                self.model_manager.detailed_classifier is not None and
                self.model_manager.scaler is not None and
                self.model_manager.label_encoder is not None)
    
    def train_new_model(self, data_dir: Union[str, Path], 
                       model_name: str = "maraco_models",
                       test_size: float = 0.2) -> Dict[str, float]:
        """
        Train a new model from data directory
        
        Args:
            data_dir: Directory containing labeled audio data
            model_name: Name for the trained model
            test_size: Fraction of data for testing
            
        Returns:
            Dictionary with training metrics
        """
        print("Loading training data...")
        
        # Load and preprocess training data
        data_dir = Path(data_dir)
        audio_files = []
        labels = []
        
        # Load data from directory structure
        for class_dir in data_dir.iterdir():
            if class_dir.is_dir():
                class_name = class_dir.name.upper()
                for audio_file in class_dir.glob("*.wav"):
                    audio_files.append(audio_file)
                    labels.append(class_name)
        
        print(f"Found {len(audio_files)} audio files")
        
        # Preprocess audio files
        print("Preprocessing audio files...")
        audio_data = self.preprocessor.batch_preprocess(
            audio_files, 
            apply_noise_reduction=True,
            n_jobs=-1
        )
        
        # Extract features
        print("Extracting features...")
        sr_list = [self.preprocessor.target_sr] * len(audio_data)
        features = self.feature_extractor.batch_extract_features(
            audio_data, sr_list, n_jobs=-1
        )
        
        # Convert to numpy arrays
        X = np.array(features)
        y = np.array(labels)
        
        print(f"Feature matrix shape: {X.shape}")
        print(f"Labels shape: {y.shape}")
        
        # Train models
        print("Training models...")
        metrics = self.model_manager.train_models(X, y, test_size=test_size)
        
        # Save models
        print("Saving models...")
        self.model_manager.save_models(model_name)
        
        return metrics
    
    def validate_model(self, test_data_dir: Union[str, Path]) -> Dict[str, Union[float, str]]:
        """
        Validate model performance on test data
        
        Args:
            test_data_dir: Directory containing test audio data
            
        Returns:
            Dictionary with validation metrics
        """
        if not self.is_model_loaded():
            return {'error': 'No models loaded'}
        
        # Load test data
        test_data_dir = Path(test_data_dir)
        audio_files = []
        true_labels = []
        
        for class_dir in test_data_dir.iterdir():
            if class_dir.is_dir():
                class_name = class_dir.name.upper()
                for audio_file in class_dir.glob("*.wav"):
                    audio_files.append(audio_file)
                    true_labels.append(class_name)
        
        # Make predictions
        predictions = self.predict_batch(audio_files)
        
        # Calculate metrics
        predicted_labels = [pred['class'] for pred in predictions]
        
        # Calculate accuracy
        correct = sum(1 for pred, true in zip(predicted_labels, true_labels) if pred == true)
        accuracy = correct / len(true_labels)
        
        # Calculate average confidence
        confidences = [pred.get('confidence', 0.0) for pred in predictions if 'confidence' in pred]
        avg_confidence = np.mean(confidences) if confidences else 0.0
        
        # Calculate average processing time
        processing_times = [pred.get('processing_time', 0.0) for pred in predictions]
        avg_processing_time = np.mean(processing_times)
        
        return {
            'accuracy': accuracy,
            'avg_confidence': avg_confidence,
            'avg_processing_time': avg_processing_time,
            'total_samples': len(true_labels),
            'correct_predictions': correct
        }
