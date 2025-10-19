"""
Validation utilities for MarACO API
"""

import numpy as np
from pathlib import Path
from typing import Union, List, Dict, Any, Optional
import warnings


def validate_input(input_data: Any, expected_type: type, 
                  allow_none: bool = False) -> bool:
    """
    Validate input data type
    
    Args:
        input_data: Input data to validate
        expected_type: Expected data type
        allow_none: Whether to allow None values
        
    Returns:
        True if valid, False otherwise
    """
    if input_data is None:
        return allow_none
    
    return isinstance(input_data, expected_type)


def validate_audio_data(audio: np.ndarray, 
                       min_length: int = 100,
                       max_length: int = 1000000,
                       allow_empty: bool = False) -> bool:
    """
    Validate audio data array
    
    Args:
        audio: Audio data array
        min_length: Minimum length in samples
        max_length: Maximum length in samples
        allow_empty: Whether to allow empty arrays
        
    Returns:
        True if valid, False otherwise
    """
    if not isinstance(audio, np.ndarray):
        return False
    
    if len(audio) == 0:
        return allow_empty
    
    if len(audio) < min_length:
        return False
    
    if len(audio) > max_length:
        return False
    
    # Check for NaN or infinite values
    if not np.all(np.isfinite(audio)):
        return False
    
    return True


def validate_sample_rate(sr: Union[int, float], 
                        min_sr: int = 1000,
                        max_sr: int = 48000) -> bool:
    """
    Validate sample rate
    
    Args:
        sr: Sample rate
        min_sr: Minimum sample rate
        max_sr: Maximum sample rate
        
    Returns:
        True if valid, False otherwise
    """
    if not isinstance(sr, (int, float)):
        return False
    
    if sr <= 0:
        return False
    
    if sr < min_sr or sr > max_sr:
        return False
    
    return True


def validate_file_path(file_path: Union[str, Path], 
                      must_exist: bool = True,
                      allowed_extensions: Optional[List[str]] = None) -> bool:
    """
    Validate file path
    
    Args:
        file_path: File path to validate
        must_exist: Whether file must exist
        allowed_extensions: List of allowed file extensions
        
    Returns:
        True if valid, False otherwise
    """
    try:
        file_path = Path(file_path)
        
        if must_exist and not file_path.exists():
            return False
        
        if allowed_extensions:
            if file_path.suffix.lower() not in allowed_extensions:
                return False
        
        return True
        
    except Exception:
        return False


def validate_model_path(model_path: Union[str, Path]) -> bool:
    """
    Validate model file path
    
    Args:
        model_path: Model file path
        
    Returns:
        True if valid, False otherwise
    """
    return validate_file_path(
        model_path,
        must_exist=True,
        allowed_extensions=['.pkl', '.joblib', '.json']
    )


def validate_classification_result(result: Dict[str, Any]) -> bool:
    """
    Validate classification result
    
    Args:
        result: Classification result dictionary
        
    Returns:
        True if valid, False otherwise
    """
    required_keys = ['class', 'processing_time']
    
    for key in required_keys:
        if key not in result:
            return False
    
    # Check class is string
    if not isinstance(result['class'], str):
        return False
    
    # Check processing time is numeric
    if not isinstance(result['processing_time'], (int, float)):
        return False
    
    if result['processing_time'] < 0:
        return False
    
    # Check confidence if present
    if 'confidence' in result:
        if not isinstance(result['confidence'], (int, float)):
            return False
        
        if not (0 <= result['confidence'] <= 1):
            return False
    
    return True


def validate_feature_vector(features: np.ndarray, 
                        expected_length: Optional[int] = None,
                        allow_empty: bool = False) -> bool:
    """
    Validate feature vector
    
    Args:
        features: Feature vector
        expected_length: Expected length of feature vector
        allow_empty: Whether to allow empty vectors
        
    Returns:
        True if valid, False otherwise
    """
    if not isinstance(features, np.ndarray):
        return False
    
    if len(features) == 0:
        return allow_empty
    
    if expected_length is not None and len(features) != expected_length:
        return False
    
    # Check for NaN or infinite values
    if not np.all(np.isfinite(features)):
        return False
    
    return True


def validate_batch_input(input_list: List[Any], 
                        min_size: int = 1,
                        max_size: int = 1000) -> bool:
    """
    Validate batch input
    
    Args:
        input_list: List of inputs
        min_size: Minimum batch size
        max_size: Maximum batch size
        
    Returns:
        True if valid, False otherwise
    """
    if not isinstance(input_list, list):
        return False
    
    if len(input_list) < min_size:
        return False
    
    if len(input_list) > max_size:
        return False
    
    return True


def validate_model_config(config: Dict[str, Any]) -> bool:
    """
    Validate model configuration
    
    Args:
        config: Model configuration dictionary
        
    Returns:
        True if valid, False otherwise
    """
    if not isinstance(config, dict):
        return False
    
    # Check for required keys
    required_keys = ['pre_classifier', 'detailed_classifier']
    
    for key in required_keys:
        if key not in config:
            return False
        
        if not isinstance(config[key], dict):
            return False
    
    # Check pre-classifier config
    pre_config = config['pre_classifier']
    pre_required = ['type', 'n_estimators', 'max_depth', 'random_state']
    
    for key in pre_required:
        if key not in pre_config:
            return False
    
    # Check detailed classifier config
    detailed_config = config['detailed_classifier']
    detailed_required = ['type', 'n_estimators', 'max_depth', 'learning_rate', 'random_state']
    
    for key in detailed_required:
        if key not in detailed_config:
            return False
    
    return True


def validate_audio_parameters(target_sr: int, duration: float, 
                             min_duration: float = 0.1,
                             max_duration: float = 60.0) -> bool:
    """
    Validate audio processing parameters
    
    Args:
        target_sr: Target sample rate
        duration: Target duration
        min_duration: Minimum duration
        max_duration: Maximum duration
        
    Returns:
        True if valid, False otherwise
    """
    if not validate_sample_rate(target_sr):
        return False
    
    if not isinstance(duration, (int, float)):
        return False
    
    if duration < min_duration or duration > max_duration:
        return False
    
    return True


def validate_classification_classes(classes: List[str]) -> bool:
    """
    Validate classification classes
    
    Args:
        classes: List of class names
        
    Returns:
        True if valid, False otherwise
    """
    if not isinstance(classes, list):
        return False
    
    if len(classes) == 0:
        return False
    
    for class_name in classes:
        if not isinstance(class_name, str):
            return False
        
        if len(class_name) == 0:
            return False
    
    # Check for duplicates
    if len(classes) != len(set(classes)):
        return False
    
    return True


def validate_performance_metrics(metrics: Dict[str, Any]) -> bool:
    """
    Validate performance metrics
    
    Args:
        metrics: Performance metrics dictionary
        
    Returns:
        True if valid, False otherwise
    """
    if not isinstance(metrics, dict):
        return False
    
    # Check for required keys
    required_keys = ['accuracy', 'processing_time']
    
    for key in required_keys:
        if key not in metrics:
            return False
        
        if not isinstance(metrics[key], (int, float)):
            return False
    
    # Check accuracy is between 0 and 1
    if not (0 <= metrics['accuracy'] <= 1):
        return False
    
    # Check processing time is positive
    if metrics['processing_time'] < 0:
        return False
    
    return True
