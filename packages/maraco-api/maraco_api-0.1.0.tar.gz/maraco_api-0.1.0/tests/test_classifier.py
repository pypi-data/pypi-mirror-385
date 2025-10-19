"""
Tests for main classifier
"""

import unittest
import numpy as np
import tempfile
import os
from pathlib import Path

from maraco.core.classifier import MarineAcousticClassifier


class TestMarineAcousticClassifier(unittest.TestCase):
    """
    Test cases for MarineAcousticClassifier
    """
    
    def setUp(self):
        """
        Set up test fixtures
        """
        self.temp_dir = tempfile.mkdtemp()
        self.classifier = MarineAcousticClassifier(
            model_dir=self.temp_dir,
            auto_load=False
        )
        
        # Create test audio file
        self.test_audio_file = os.path.join(self.temp_dir, "test_audio.wav")
        self.sample_rate = 16000
        self.duration = 5.0
        
        # Generate test audio
        t = np.linspace(0, self.duration, int(self.sample_rate * self.duration))
        self.test_audio = np.sin(2 * np.pi * 440 * t)
        
        # Save test audio
        import soundfile as sf
        sf.write(self.test_audio_file, self.test_audio, self.sample_rate)
    
    def tearDown(self):
        """
        Clean up test fixtures
        """
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_initialization(self):
        """
        Test classifier initialization
        """
        self.assertIsNotNone(self.classifier.preprocessor)
        self.assertIsNotNone(self.classifier.feature_extractor)
        self.assertIsNotNone(self.classifier.model_manager)
    
    def test_model_loading(self):
        """
        Test model loading
        """
        # Should return False when no models are loaded
        self.assertFalse(self.classifier.is_model_loaded())
    
    def test_supported_classes(self):
        """
        Test getting supported classes
        """
        classes = self.classifier.get_supported_classes()
        
        self.assertIsInstance(classes, list)
        self.assertGreater(len(classes), 0)
        
        # Check for expected marine classes
        expected_classes = ['FIN_WHALE', 'HUMPBACK_WHALE', 'RIGHT_WHALE', 'SONAR', 'VESSEL']
        for expected_class in expected_classes:
            self.assertIn(expected_class, classes)
    
    def test_model_info(self):
        """
        Test getting model information
        """
        info = self.classifier.get_model_info()
        
        self.assertIsInstance(info, dict)
        self.assertIn('classes', info)
        self.assertIn('model_loaded', info)
        self.assertIn('scaler_loaded', info)
        self.assertIn('label_encoder_loaded', info)
    
    def test_predict_without_models(self):
        """
        Test prediction without loaded models
        """
        result = self.classifier.predict(self.test_audio_file)
        
        self.assertIsInstance(result, dict)
        self.assertIn('class', result)
        self.assertIn('processing_time', result)
        self.assertIn('filename', result)
        
        # Should return error when no models are loaded
        self.assertEqual(result['class'], 'ERROR')
        self.assertIn('error', result)
    
    def test_predict_stream(self):
        """
        Test streaming prediction
        """
        result = self.classifier.predict_stream(self.test_audio, self.sample_rate)
        
        self.assertIsInstance(result, dict)
        self.assertIn('class', result)
        self.assertIn('processing_time', result)
        
        # Should return error when no models are loaded
        self.assertEqual(result['class'], 'ERROR')
        self.assertIn('error', result)
    
    def test_predict_batch(self):
        """
        Test batch prediction
        """
        audio_files = [self.test_audio_file, self.test_audio_file]
        results = self.classifier.predict_batch(audio_files)
        
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 2)
        
        for result in results:
            self.assertIsInstance(result, dict)
            self.assertIn('class', result)
            self.assertIn('processing_time', result)
            self.assertIn('filename', result)
    
    def test_validate_model_without_models(self):
        """
        Test model validation without loaded models
        """
        # Create a test data directory structure
        test_data_dir = os.path.join(self.temp_dir, "test_data")
        os.makedirs(test_data_dir, exist_ok=True)
        
        # Create a test class directory
        class_dir = os.path.join(test_data_dir, "FIN_WHALE")
        os.makedirs(class_dir, exist_ok=True)
        
        # Copy test audio file to class directory
        import shutil
        shutil.copy(self.test_audio_file, class_dir)
        
        # Test validation
        results = self.classifier.validate_model(test_data_dir)
        
        self.assertIsInstance(results, dict)
        self.assertIn('error', results)
        self.assertEqual(results['error'], 'No models loaded')
    
    def test_error_handling(self):
        """
        Test error handling for invalid inputs
        """
        # Test with non-existent file
        result = self.classifier.predict("nonexistent_file.wav")
        self.assertEqual(result['class'], 'ERROR')
        self.assertIn('error', result)
        
        # Test with invalid audio data
        invalid_audio = np.array([])
        result = self.classifier.predict_stream(invalid_audio, self.sample_rate)
        self.assertEqual(result['class'], 'ERROR')
        self.assertIn('error', result)
    
    def test_preprocessing_parameters(self):
        """
        Test preprocessing parameters
        """
        # Test with different parameters
        classifier = MarineAcousticClassifier(
            model_dir=self.temp_dir,
            target_sr=8000,
            duration=3.0,
            auto_load=False
        )
        
        self.assertEqual(classifier.preprocessor.target_sr, 8000)
        self.assertEqual(classifier.preprocessor.duration, 3.0)
    
    def test_feature_extraction_parameters(self):
        """
        Test feature extraction parameters
        """
        # Test with different parameters
        classifier = MarineAcousticClassifier(
            model_dir=self.temp_dir,
            auto_load=False
        )
        
        self.assertIsNotNone(classifier.feature_extractor.n_mfcc)
        self.assertIsNotNone(classifier.feature_extractor.n_mels)
        self.assertIsNotNone(classifier.feature_extractor.n_fft)
        self.assertIsNotNone(classifier.feature_extractor.hop_length)


if __name__ == '__main__':
    unittest.main()
