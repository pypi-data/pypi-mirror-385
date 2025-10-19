"""
Basic usage example for MarACO API
"""

from maraco import MarineAcousticClassifier
import os


def main():
    """
    Basic usage example
    """
    print("MarACO API - Basic Usage Example")
    print("=" * 40)
    
    # Initialize classifier
    print("Initializing classifier...")
    classifier = MarineAcousticClassifier()
    
    # Check if models are loaded
    if not classifier.is_model_loaded():
        print("No pre-trained models found. Please train models first.")
        print("Use: python -m maraco.training.train_model <data_directory>")
        return
    
    print("Models loaded successfully!")
    print(f"Supported classes: {classifier.get_supported_classes()}")
    
    # Example with a single audio file
    audio_file = "example_audio.wav"  # Replace with your audio file
    
    if os.path.exists(audio_file):
        print(f"\nClassifying {audio_file}...")
        result = classifier.predict(audio_file)
        
        print(f"Predicted class: {result['class']}")
        print(f"Confidence: {result['confidence']:.3f}")
        print(f"Processing time: {result['processing_time']:.3f}s")
    else:
        print(f"Audio file {audio_file} not found. Please provide a valid audio file.")
    
    # Example with multiple files
    audio_files = ["file1.wav", "file2.wav", "file3.wav"]  # Replace with your files
    
    existing_files = [f for f in audio_files if os.path.exists(f)]
    
    if existing_files:
        print(f"\nClassifying {len(existing_files)} files...")
        results = classifier.predict_batch(existing_files)
        
        for i, result in enumerate(results):
            print(f"File {i+1}: {result['filename']}")
            print(f"  Class: {result['class']}")
            print(f"  Confidence: {result['confidence']:.3f}")
            print(f"  Processing time: {result['processing_time']:.3f}s")
            print()
    
    # Example with streaming audio
    print("Streaming audio example:")
    print("For real-time processing, use classifier.predict_stream(audio_chunk, sample_rate)")


if __name__ == "__main__":
    main()
