"""
Core modules for MarACO API
"""

from .classifier import MarineAcousticClassifier
from .preprocessor import AudioPreprocessor
from .feature_extractor import FeatureExtractor
from .model import ModelManager

__all__ = [
    "MarineAcousticClassifier",
    "AudioPreprocessor",
    "FeatureExtractor", 
    "ModelManager",
]
