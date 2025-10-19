# MarACO - Marine Acoustic Classification API

A Python package for marine acoustic sound classification optimized for CPU usage with balanced speed and accuracy.

## Features

- **Fast Classification**: <200ms per 5-second audio clip on CPU
- **High Accuracy**: >90% accuracy on marine acoustic sounds
- **Noise Reduction**: Built-in noise reduction and audio preprocessing
- **Multiple Classes**: Fin Whale, Humpback Whale, Right Whale, Sonar, Vessels, Explosions, Physical Noise
- **Easy Integration**: Simple API for quick integration into your projects
- **CPU Optimized**: Designed specifically for CPU-only environments

## Installation

```bash
pip install maraco-api
```

## Quick Start

```python
from maraco import MarineAcousticClassifier

# Initialize classifier
classifier = MarineAcousticClassifier()

# Classify a single audio file
result = classifier.predict("audio_file.wav")
print(f"Class: {result['class']}, Confidence: {result['confidence']:.2f}")

# Batch processing
results = classifier.predict_batch(["file1.wav", "file2.wav"])
for result in results:
    print(f"File: {result['filename']}, Class: {result['class']}")
```

## Supported Audio Formats

- WAV, AIFF, MP3, FLAC
- Sample rates: 600Hz - 48kHz (automatically resampled)
- Duration: 1-30 seconds (optimal: 2-5 seconds)

## Performance

- **Processing Speed**: <200ms per clip
- **Memory Usage**: <500MB RAM
- **Model Size**: <50MB
- **Accuracy**: >90% on test data

## License

MIT License
