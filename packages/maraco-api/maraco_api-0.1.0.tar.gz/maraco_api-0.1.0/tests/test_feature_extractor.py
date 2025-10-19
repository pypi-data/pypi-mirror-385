"""
Tests for feature extractor
"""

import unittest
import numpy as np

from maraco.core.feature_extractor import FeatureExtractor


class TestFeatureExtractor(unittest.TestCase):
    """
    Test cases for FeatureExtractor
    """
    
    def setUp(self):
        """
        Set up test fixtures
        """
        self.extractor = FeatureExtractor()
        
        # Generate test audio
        self.sample_rate = 16000
        self.duration = 5.0
        self.test_audio = np.sin(2 * np.pi * 440 * np.linspace(0, self.duration, int(self.sample_rate * self.duration)))
    
    def test_extract_mfcc(self):
        """
        Test MFCC extraction
        """
        mfcc = self.extractor.extract_mfcc(self.test_audio, self.sample_rate)
        
        self.assertIsInstance(mfcc, np.ndarray)
        self.assertEqual(mfcc.shape[0], self.extractor.n_mfcc)
        self.assertGreater(mfcc.shape[1], 0)
    
    def test_extract_mel_spectrogram(self):
        """
        Test mel spectrogram extraction
        """
        mel_spec = self.extractor.extract_mel_spectrogram(self.test_audio, self.sample_rate)
        
        self.assertIsInstance(mel_spec, np.ndarray)
        self.assertEqual(mel_spec.shape[0], self.extractor.n_mels)
        self.assertGreater(mel_spec.shape[1], 0)
    
    def test_extract_spectral_features(self):
        """
        Test spectral feature extraction
        """
        features = self.extractor.extract_spectral_features(self.test_audio, self.sample_rate)
        
        self.assertIsInstance(features, dict)
        
        # Check required keys
        required_keys = [
            'spectral_centroid_mean', 'spectral_centroid_std',
            'spectral_rolloff_mean', 'spectral_rolloff_std',
            'spectral_bandwidth_mean', 'spectral_bandwidth_std',
            'zcr_mean', 'zcr_std',
            'chroma_mean', 'chroma_std'
        ]
        
        for key in required_keys:
            self.assertIn(key, features)
        
        # Check data types
        for key in ['spectral_centroid_mean', 'spectral_centroid_std',
                   'spectral_rolloff_mean', 'spectral_rolloff_std',
                   'spectral_bandwidth_mean', 'spectral_bandwidth_std',
                   'zcr_mean', 'zcr_std']:
            self.assertIsInstance(features[key], (int, float, np.floating))
        
        # Check chroma features
        self.assertIsInstance(features['chroma_mean'], list)
        self.assertIsInstance(features['chroma_std'], list)
        self.assertEqual(len(features['chroma_mean']), 12)
        self.assertEqual(len(features['chroma_std']), 12)
    
    def test_extract_temporal_features(self):
        """
        Test temporal feature extraction
        """
        features = self.extractor.extract_temporal_features(self.test_audio)
        
        self.assertIsInstance(features, dict)
        
        # Check required keys
        required_keys = [
            'rms_mean', 'rms_std', 'audio_mean', 'audio_std',
            'audio_skew', 'audio_kurtosis', 'energy', 'energy_per_sample'
        ]
        
        for key in required_keys:
            self.assertIn(key, features)
            self.assertIsInstance(features[key], (int, float, np.floating))
    
    def test_extract_delta_features(self):
        """
        Test delta feature extraction
        """
        # Create a simple feature matrix
        features = np.random.randn(13, 100)
        
        delta_features = self.extractor.extract_delta_features(features)
        
        self.assertIsInstance(delta_features, np.ndarray)
        self.assertEqual(delta_features.shape[0], features.shape[0] * 3)  # Original + delta + delta2
        self.assertEqual(delta_features.shape[1], features.shape[1])
    
    def test_extract_all_features(self):
        """
        Test extraction of all features
        """
        features = self.extractor.extract_all_features(self.test_audio, self.sample_rate)
        
        self.assertIsInstance(features, dict)
        
        # Check required keys
        required_keys = [
            'mfcc', 'mel_spectrogram', 'spectral_centroid_mean',
            'spectral_centroid_std', 'rms_mean', 'rms_std'
        ]
        
        for key in required_keys:
            self.assertIn(key, features)
    
    def test_extract_features_for_classification(self):
        """
        Test feature extraction for classification
        """
        features = self.extractor.extract_features_for_classification(self.test_audio, self.sample_rate)
        
        self.assertIsInstance(features, np.ndarray)
        self.assertGreater(len(features), 0)
        self.assertTrue(np.all(np.isfinite(features)))
    
    def test_batch_extract_features(self):
        """
        Test batch feature extraction
        """
        # Create multiple audio samples
        audio_list = [self.test_audio, self.test_audio * 0.5, self.test_audio * 2.0]
        sr_list = [self.sample_rate] * 3
        
        features = self.extractor.batch_extract_features(audio_list, sr_list)
        
        self.assertIsInstance(features, list)
        self.assertEqual(len(features), 3)
        
        for feature in features:
            self.assertIsInstance(feature, np.ndarray)
            self.assertGreater(len(feature), 0)
    
    def test_empty_audio(self):
        """
        Test handling of empty audio
        """
        empty_audio = np.array([])
        
        # Should not raise an error
        features = self.extractor.extract_features_for_classification(empty_audio, self.sample_rate)
        self.assertIsInstance(features, np.ndarray)
    
    def test_zero_audio(self):
        """
        Test handling of zero audio
        """
        zero_audio = np.zeros(int(self.sample_rate * self.duration))
        
        features = self.extractor.extract_features_for_classification(zero_audio, self.sample_rate)
        self.assertIsInstance(features, np.ndarray)
        self.assertGreater(len(features), 0)


if __name__ == '__main__':
    unittest.main()
