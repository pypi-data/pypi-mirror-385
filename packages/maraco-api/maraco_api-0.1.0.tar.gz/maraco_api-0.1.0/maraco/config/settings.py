"""
Configuration settings for MarACO API
"""

import os
from pathlib import Path

# Default model directory
DEFAULT_MODEL_DIR = Path("models")

# Audio processing settings
DEFAULT_TARGET_SR = 16000
DEFAULT_DURATION = 5.0
DEFAULT_MIN_DURATION = 1.0
DEFAULT_MAX_DURATION = 30.0

# Feature extraction settings
DEFAULT_N_MFCC = 13
DEFAULT_N_MELS = 128
DEFAULT_N_FFT = 2048
DEFAULT_HOP_LENGTH = 512
DEFAULT_INCLUDE_DELTAS = True

# Model settings
DEFAULT_PRE_CLASSIFIER_CONFIG = {
    'type': 'RandomForest',
    'n_estimators': 100,
    'max_depth': 10,
    'random_state': 42
}

DEFAULT_DETAILED_CLASSIFIER_CONFIG = {
    'type': 'XGBoost',
    'n_estimators': 200,
    'max_depth': 6,
    'learning_rate': 0.1,
    'random_state': 42
}

# Supported audio formats
SUPPORTED_AUDIO_FORMATS = {'.wav', '.aiff', '.mp3', '.flac', '.m4a'}

# Class labels
DEFAULT_CLASSES = [
    'FIN_WHALE',
    'HUMPBACK_WHALE',
    'RIGHT_WHALE',
    'SONAR',
    'VESSEL',
    'EXPLOSION',
    'PHYSICAL_NOISE',
    'OTHER'
]

# Performance settings
DEFAULT_N_JOBS = -1  # Use all available CPUs
DEFAULT_BATCH_SIZE = 10

# Logging settings
LOG_LEVEL = os.getenv('MARACO_LOG_LEVEL', 'INFO')
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Model file names
MODEL_FILES = {
    'pre_classifier': 'maraco_models_pre_classifier.joblib',
    'detailed_classifier': 'maraco_models_detailed_classifier.joblib',
    'scaler': 'maraco_models_scaler.joblib',
    'label_encoder': 'maraco_models_label_encoder.joblib',
    'config': 'maraco_models_config.json'
}
