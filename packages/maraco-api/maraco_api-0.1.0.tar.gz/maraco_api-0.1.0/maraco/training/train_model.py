"""
Training script for MarACO models
"""

import argparse
import json
from pathlib import Path
from typing import Dict, Union
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

from ..core.classifier import MarineAcousticClassifier
from ..core.preprocessor import AudioPreprocessor
from ..core.feature_extractor import FeatureExtractor


def load_training_data(data_dir: Union[str, Path]) -> tuple:
    """
    Load training data from directory structure
    
    Args:
        data_dir: Directory containing labeled audio data
        
    Returns:
        Tuple of (audio_files, labels)
    """
    data_dir = Path(data_dir)
    audio_files = []
    labels = []
    
    print(f"Loading data from {data_dir}")
    
    # Load data from directory structure
    for class_dir in data_dir.iterdir():
        if class_dir.is_dir():
            class_name = class_dir.name.upper()
            print(f"Loading {class_name} class...")
            
            # Get all audio files in this class directory
            class_files = []
            for ext in ['*.wav', '*.aiff', '*.mp3', '*.flac']:
                class_files.extend(class_dir.glob(ext))
            
            print(f"  Found {len(class_files)} files")
            
            for audio_file in class_files:
                audio_files.append(audio_file)
                labels.append(class_name)
    
    print(f"Total files loaded: {len(audio_files)}")
    print(f"Classes: {set(labels)}")
    print(f"Class distribution: {dict(zip(*np.unique(labels, return_counts=True)))}")
    
    return audio_files, labels


def preprocess_training_data(audio_files: list, labels: list, 
                           target_sr: int = 16000, duration: float = 5.0) -> tuple:
    """
    Preprocess training data
    
    Args:
        audio_files: List of audio file paths
        labels: List of corresponding labels
        target_sr: Target sample rate
        duration: Target duration
        
    Returns:
        Tuple of (features, labels)
    """
    print("Preprocessing audio files...")
    
    # Initialize preprocessor
    preprocessor = AudioPreprocessor(
        target_sr=target_sr,
        duration=duration
    )
    
    # Preprocess audio files
    audio_data = preprocessor.batch_preprocess(
        audio_files,
        apply_noise_reduction=True,
        n_jobs=-1
    )
    
    print(f"Successfully preprocessed {len(audio_data)} files")
    
    # Extract features
    print("Extracting features...")
    feature_extractor = FeatureExtractor()
    sr_list = [target_sr] * len(audio_data)
    features = feature_extractor.batch_extract_features(
        audio_data, sr_list, n_jobs=-1
    )
    
    print(f"Feature extraction completed. Feature matrix shape: {np.array(features).shape}")
    
    return features, labels


def train_maraco_model(data_dir: Union[str, Path], 
                      model_dir: Union[str, Path] = "models",
                      model_name: str = "maraco_models",
                      test_size: float = 0.2,
                      target_sr: int = 16000,
                      duration: float = 5.0) -> Dict[str, Union[float, str]]:
    """
    Train MarACO model from data directory
    
    Args:
        data_dir: Directory containing labeled audio data
        model_dir: Directory to save trained models
        model_name: Name for the trained model
        test_size: Fraction of data for testing
        target_sr: Target sample rate
        duration: Target duration for audio clips
        
    Returns:
        Dictionary with training results
    """
    print("=" * 60)
    print("MarACO Model Training")
    print("=" * 60)
    
    # Load training data
    audio_files, labels = load_training_data(data_dir)
    
    if len(audio_files) == 0:
        return {'error': 'No audio files found in data directory'}
    
    # Preprocess data
    features, labels = preprocess_training_data(
        audio_files, labels, target_sr, duration
    )
    
    # Convert to numpy arrays
    X = np.array(features)
    y = np.array(labels)
    
    print(f"Final dataset shape: {X.shape}")
    print(f"Number of classes: {len(np.unique(y))}")
    
    # Initialize classifier
    classifier = MarineAcousticClassifier(
        model_dir=model_dir,
        target_sr=target_sr,
        duration=duration,
        auto_load=False
    )
    
    # Train models
    print("\nTraining models...")
    metrics = classifier.train_new_model(
        data_dir, model_name, test_size
    )
    
    # Generate training report
    report = {
        'training_metrics': metrics,
        'dataset_info': {
            'total_samples': len(X),
            'num_classes': len(np.unique(y)),
            'classes': list(np.unique(y)),
            'class_distribution': dict(zip(*np.unique(y, return_counts=True)))
        },
        'model_info': classifier.get_model_info()
    }
    
    # Save training report
    report_path = Path(model_dir) / f"{model_name}_training_report.json"
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\nTraining completed!")
    print(f"Models saved to: {model_dir}")
    print(f"Training report saved to: {report_path}")
    
    return report


def main():
    """
    Main function for command-line training
    """
    parser = argparse.ArgumentParser(description="Train MarACO model")
    parser.add_argument("data_dir", help="Directory containing training data")
    parser.add_argument("--model_dir", default="models", help="Directory to save models")
    parser.add_argument("--model_name", default="maraco_models", help="Model name")
    parser.add_argument("--test_size", type=float, default=0.2, help="Test set size")
    parser.add_argument("--target_sr", type=int, default=16000, help="Target sample rate")
    parser.add_argument("--duration", type=float, default=5.0, help="Target duration")
    
    args = parser.parse_args()
    
    # Train model
    results = train_maraco_model(
        data_dir=args.data_dir,
        model_dir=args.model_dir,
        model_name=args.model_name,
        test_size=args.test_size,
        target_sr=args.target_sr,
        duration=args.duration
    )
    
    if 'error' in results:
        print(f"Training failed: {results['error']}")
        return 1
    
    print("Training completed successfully!")
    return 0


if __name__ == "__main__":
    exit(main())
