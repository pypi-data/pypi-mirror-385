"""
Tests for audio preprocessor
"""

import unittest
import numpy as np
import tempfile
import os
from pathlib import Path

from maraco.core.preprocessor import AudioPreprocessor


class TestAudioPreprocessor(unittest.TestCase):
    """
    Test cases for AudioPreprocessor
    """
    
    def setUp(self):
        """
        Set up test fixtures
        """
        self.preprocessor = AudioPreprocessor(
            target_sr=16000,
            duration=5.0
        )
        
        # Create temporary audio file
        self.temp_dir = tempfile.mkdtemp()
        self.temp_audio = os.path.join(self.temp_dir, "test_audio.wav")
        
        # Generate test audio
        self.sample_rate = 16000
        self.duration = 3.0
        self.test_audio = np.sin(2 * np.pi * 440 * np.linspace(0, self.duration, int(self.sample_rate * self.duration)))
        
        # Save test audio
        import soundfile as sf
        sf.write(self.temp_audio, self.test_audio, self.sample_rate)
    
    def tearDown(self):
        """
        Clean up test fixtures
        """
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_load_audio(self):
        """
        Test audio loading
        """
        audio, sr = self.preprocessor.load_audio(self.temp_audio)
        
        self.assertIsInstance(audio, np.ndarray)
        self.assertEqual(sr, self.sample_rate)
        self.assertGreater(len(audio), 0)
    
    def test_resample_audio(self):
        """
        Test audio resampling
        """
        # Test with same sample rate
        resampled = self.preprocessor.resample_audio(self.test_audio, self.sample_rate)
        np.testing.assert_array_equal(resampled, self.test_audio)
        
        # Test with different sample rate - just check that it returns a valid array
        resampled = self.preprocessor.resample_audio(self.test_audio, 8000)
        self.assertIsInstance(resampled, np.ndarray)
        self.assertGreater(len(resampled), 0)
    
    def test_normalize_audio(self):
        """
        Test audio normalization
        """
        # Test with normal audio
        normalized = self.preprocessor.normalize_audio(self.test_audio)
        self.assertLessEqual(np.max(np.abs(normalized)), 1.0)
        
        # Test with zero audio
        zero_audio = np.zeros(1000)
        normalized_zero = self.preprocessor.normalize_audio(zero_audio)
        np.testing.assert_array_equal(normalized_zero, zero_audio)
    
    def test_segment_audio(self):
        """
        Test audio segmentation
        """
        # Test with short audio (should be padded)
        short_audio = np.random.randn(int(2 * self.sample_rate))  # 2 seconds of audio
        segmented = self.preprocessor.segment_audio(short_audio, self.sample_rate)
        self.assertEqual(len(segmented), int(self.preprocessor.duration * self.sample_rate))
        
        # Test with long audio (should be truncated)
        long_audio = np.random.randn(int(10 * self.sample_rate))
        segmented = self.preprocessor.segment_audio(long_audio, self.sample_rate)
        self.assertEqual(len(segmented), int(self.preprocessor.duration * self.sample_rate))
    
    def test_preprocess_audio(self):
        """
        Test complete preprocessing pipeline
        """
        preprocessed = self.preprocessor.preprocess_audio(self.temp_audio)
        
        self.assertIsInstance(preprocessed, np.ndarray)
        self.assertEqual(len(preprocessed), int(self.preprocessor.duration * self.preprocessor.target_sr))
        self.assertLessEqual(np.max(np.abs(preprocessed)), 1.0)
    
    def test_batch_preprocess(self):
        """
        Test batch preprocessing
        """
        # Create multiple test files
        audio_files = []
        for i in range(3):
            audio_file = os.path.join(self.temp_dir, f"test_audio_{i}.wav")
            import soundfile as sf
            sf.write(audio_file, self.test_audio, self.sample_rate)
            audio_files.append(audio_file)
        
        # Test batch preprocessing
        results = self.preprocessor.batch_preprocess(audio_files)
        
        self.assertEqual(len(results), 3)
        for result in results:
            self.assertIsInstance(result, np.ndarray)
            self.assertEqual(len(result), int(self.preprocessor.duration * self.preprocessor.target_sr))
    
    def test_unsupported_format(self):
        """
        Test handling of unsupported audio formats
        """
        unsupported_file = os.path.join(self.temp_dir, "test.txt")
        with open(unsupported_file, 'w') as f:
            f.write("This is not an audio file")
        
        with self.assertRaises(ValueError):
            self.preprocessor.load_audio(unsupported_file)
    
    def test_nonexistent_file(self):
        """
        Test handling of non-existent files
        """
        nonexistent_file = os.path.join(self.temp_dir, "nonexistent.wav")
        
        with self.assertRaises(FileNotFoundError):
            self.preprocessor.load_audio(nonexistent_file)


if __name__ == '__main__':
    unittest.main()
