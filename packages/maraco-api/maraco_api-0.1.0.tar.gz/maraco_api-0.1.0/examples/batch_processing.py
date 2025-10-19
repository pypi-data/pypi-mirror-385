"""
Batch processing example for MarACO API
"""

from maraco import MarineAcousticClassifier
import os
import time
from pathlib import Path


def process_directory(directory_path: str, output_file: str = "results.csv"):
    """
    Process all audio files in a directory
    
    Args:
        directory_path: Path to directory containing audio files
        output_file: Output CSV file for results
    """
    print("MarACO API - Batch Processing Example")
    print("=" * 40)
    
    # Initialize classifier
    print("Initializing classifier...")
    classifier = MarineAcousticClassifier()
    
    if not classifier.is_model_loaded():
        print("No pre-trained models found. Please train models first.")
        return
    
    # Find all audio files
    directory = Path(directory_path)
    audio_extensions = {'.wav', '.aiff', '.mp3', '.flac', '.m4a'}
    audio_files = []
    
    for ext in audio_extensions:
        audio_files.extend(directory.glob(f"**/*{ext}"))
    
    print(f"Found {len(audio_files)} audio files")
    
    if len(audio_files) == 0:
        print("No audio files found in directory")
        return
    
    # Process files in batches
    batch_size = 10
    results = []
    
    print(f"Processing files in batches of {batch_size}...")
    
    for i in range(0, len(audio_files), batch_size):
        batch_files = audio_files[i:i+batch_size]
        print(f"Processing batch {i//batch_size + 1}/{(len(audio_files)-1)//batch_size + 1}")
        
        start_time = time.time()
        batch_results = classifier.predict_batch(batch_files)
        batch_time = time.time() - start_time
        
        results.extend(batch_results)
        
        print(f"  Batch processed in {batch_time:.2f}s")
        print(f"  Average time per file: {batch_time/len(batch_files):.3f}s")
    
    # Save results to CSV
    import csv
    
    with open(output_file, 'w', newline='') as csvfile:
        fieldnames = ['filename', 'class', 'confidence', 'processing_time']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for result in results:
            writer.writerow({
                'filename': result['filename'],
                'class': result['class'],
                'confidence': result['confidence'],
                'processing_time': result['processing_time']
            })
    
    print(f"\nResults saved to {output_file}")
    
    # Print summary
    total_time = sum(r['processing_time'] for r in results)
    avg_time = total_time / len(results)
    
    print(f"\nSummary:")
    print(f"Total files processed: {len(results)}")
    print(f"Total processing time: {total_time:.2f}s")
    print(f"Average time per file: {avg_time:.3f}s")
    
    # Class distribution
    class_counts = {}
    for result in results:
        class_name = result['class']
        class_counts[class_name] = class_counts.get(class_name, 0) + 1
    
    print(f"\nClass distribution:")
    for class_name, count in sorted(class_counts.items()):
        percentage = (count / len(results)) * 100
        print(f"  {class_name}: {count} ({percentage:.1f}%)")


def main():
    """
    Main function
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Batch process audio files")
    parser.add_argument("directory", help="Directory containing audio files")
    parser.add_argument("--output", default="results.csv", help="Output CSV file")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.directory):
        print(f"Directory {args.directory} does not exist")
        return 1
    
    process_directory(args.directory, args.output)
    return 0


if __name__ == "__main__":
    exit(main())
