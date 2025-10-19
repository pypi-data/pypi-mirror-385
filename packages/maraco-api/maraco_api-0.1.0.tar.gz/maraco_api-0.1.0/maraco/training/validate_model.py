"""
Validation script for MarACO models
"""

import argparse
import json
from pathlib import Path
from typing import Dict, Union
import numpy as np
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

from ..core.classifier import MarineAcousticClassifier


def validate_maraco_model(test_data_dir: Union[str, Path],
                         model_dir: Union[str, Path] = "models",
                         model_name: str = "maraco_models",
                         save_plots: bool = True) -> Dict[str, Union[float, str]]:
    """
    Validate MarACO model on test data
    
    Args:
        test_data_dir: Directory containing test audio data
        model_dir: Directory containing trained models
        model_name: Name of the trained model
        save_plots: Whether to save validation plots
        
    Returns:
        Dictionary with validation results
    """
    print("=" * 60)
    print("MarACO Model Validation")
    print("=" * 60)
    
    # Initialize classifier
    classifier = MarineAcousticClassifier(
        model_dir=model_dir,
        auto_load=True
    )
    
    if not classifier.is_model_loaded():
        return {'error': 'No models loaded. Please train models first.'}
    
    # Load test data
    test_data_dir = Path(test_data_dir)
    audio_files = []
    true_labels = []
    
    print(f"Loading test data from {test_data_dir}")
    
    for class_dir in test_data_dir.iterdir():
        if class_dir.is_dir():
            class_name = class_dir.name.upper()
            print(f"Loading {class_name} test files...")
            
            # Get all audio files in this class directory
            class_files = []
            for ext in ['*.wav', '*.aiff', '*.mp3', '*.flac']:
                class_files.extend(class_dir.glob(ext))
            
            print(f"  Found {len(class_files)} files")
            
            for audio_file in class_files:
                audio_files.append(audio_file)
                true_labels.append(class_name)
    
    if len(audio_files) == 0:
        return {'error': 'No test audio files found'}
    
    print(f"Total test files: {len(audio_files)}")
    print(f"Test classes: {set(true_labels)}")
    print(f"Test class distribution: {dict(zip(*np.unique(true_labels, return_counts=True)))}")
    
    # Make predictions
    print("\nMaking predictions...")
    predictions = classifier.predict_batch(audio_files)
    
    # Extract results
    predicted_labels = [pred['class'] for pred in predictions]
    confidences = [pred.get('confidence', 0.0) for pred in predictions if 'confidence' in pred]
    processing_times = [pred.get('processing_time', 0.0) for pred in predictions]
    
    # Calculate metrics
    accuracy = np.mean([pred == true for pred, true in zip(predicted_labels, true_labels)])
    avg_confidence = np.mean(confidences) if confidences else 0.0
    avg_processing_time = np.mean(processing_times)
    
    # Generate classification report
    class_report = classification_report(
        true_labels, predicted_labels, 
        output_dict=True, zero_division=0
    )
    
    # Generate confusion matrix
    cm = confusion_matrix(true_labels, predicted_labels)
    
    # Create validation report
    validation_results = {
        'overall_accuracy': accuracy,
        'avg_confidence': avg_confidence,
        'avg_processing_time': avg_processing_time,
        'total_samples': len(true_labels),
        'correct_predictions': sum(1 for pred, true in zip(predicted_labels, true_labels) if pred == true),
        'classification_report': class_report,
        'confusion_matrix': cm.tolist(),
        'class_labels': list(set(true_labels + predicted_labels))
    }
    
    # Save validation report
    report_path = Path(model_dir) / f"{model_name}_validation_report.json"
    with open(report_path, 'w') as f:
        json.dump(validation_results, f, indent=2)
    
    print(f"\nValidation completed!")
    print(f"Overall accuracy: {accuracy:.3f}")
    print(f"Average confidence: {avg_confidence:.3f}")
    print(f"Average processing time: {avg_processing_time:.3f}s")
    print(f"Validation report saved to: {report_path}")
    
    # Generate and save plots if requested
    if save_plots:
        save_validation_plots(validation_results, model_dir, model_name)
    
    return validation_results


def save_validation_plots(validation_results: Dict, model_dir: Union[str, Path], model_name: str):
    """
    Save validation plots
    
    Args:
        validation_results: Validation results dictionary
        model_dir: Directory to save plots
        model_name: Model name for file naming
    """
    model_dir = Path(model_dir)
    
    # Confusion matrix plot
    plt.figure(figsize=(10, 8))
    cm = np.array(validation_results['confusion_matrix'])
    class_labels = validation_results['class_labels']
    
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=class_labels, yticklabels=class_labels)
    plt.title('Confusion Matrix')
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    plt.xticks(rotation=45)
    plt.yticks(rotation=0)
    plt.tight_layout()
    
    confusion_plot_path = model_dir / f"{model_name}_confusion_matrix.png"
    plt.savefig(confusion_plot_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    # Per-class accuracy plot
    class_report = validation_results['classification_report']
    classes = [cls for cls in class_report.keys() if cls not in ['accuracy', 'macro avg', 'weighted avg']]
    precisions = [class_report[cls]['precision'] for cls in classes]
    recalls = [class_report[cls]['recall'] for cls in classes]
    f1_scores = [class_report[cls]['f1-score'] for cls in classes]
    
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(15, 5))
    
    ax1.bar(classes, precisions)
    ax1.set_title('Precision by Class')
    ax1.set_ylabel('Precision')
    ax1.tick_params(axis='x', rotation=45)
    
    ax2.bar(classes, recalls)
    ax2.set_title('Recall by Class')
    ax2.set_ylabel('Recall')
    ax2.tick_params(axis='x', rotation=45)
    
    ax3.bar(classes, f1_scores)
    ax3.set_title('F1-Score by Class')
    ax3.set_ylabel('F1-Score')
    ax3.tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    
    metrics_plot_path = model_dir / f"{model_name}_class_metrics.png"
    plt.savefig(metrics_plot_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Validation plots saved to: {model_dir}")


def main():
    """
    Main function for command-line validation
    """
    parser = argparse.ArgumentParser(description="Validate MarACO model")
    parser.add_argument("test_data_dir", help="Directory containing test data")
    parser.add_argument("--model_dir", default="models", help="Directory containing models")
    parser.add_argument("--model_name", default="maraco_models", help="Model name")
    parser.add_argument("--no_plots", action="store_true", help="Skip generating plots")
    
    args = parser.parse_args()
    
    # Validate model
    results = validate_maraco_model(
        test_data_dir=args.test_data_dir,
        model_dir=args.model_dir,
        model_name=args.model_name,
        save_plots=not args.no_plots
    )
    
    if 'error' in results:
        print(f"Validation failed: {results['error']}")
        return 1
    
    print("Validation completed successfully!")
    return 0


if __name__ == "__main__":
    exit(main())
