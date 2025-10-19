"""
MarACO - Marine Acoustic Classification API

A Python package for marine acoustic sound classification optimized for CPU usage.
"""

__version__ = "0.1.0"
__author__ = "MarACO Team"
__email__ = "contact@maraco.ai"

from .core.classifier import MarineAcousticClassifier
from .core.preprocessor import AudioPreprocessor
from .core.feature_extractor import FeatureExtractor
from .core.model import ModelManager

__all__ = [
    "MarineAcousticClassifier",
    "AudioPreprocessor", 
    "FeatureExtractor",
    "ModelManager",
]
