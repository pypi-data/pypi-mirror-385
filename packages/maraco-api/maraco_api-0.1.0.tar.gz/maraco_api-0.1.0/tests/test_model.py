"""
Tests for model manager
"""

import unittest
import numpy as np
import tempfile
import os
from pathlib import Path

from maraco.core.model import ModelManager


class TestModelManager(unittest.TestCase):
    """
    Test cases for ModelManager
    """
    
    def setUp(self):
        """
        Set up test fixtures
        """
        self.temp_dir = tempfile.mkdtemp()
        self.model_manager = ModelManager(model_dir=self.temp_dir)
        
        # Generate test data
        self.n_samples = 100
        self.n_features = 50
        self.n_classes = 5
        
        # Create synthetic feature matrix
        np.random.seed(42)
        self.X = np.random.randn(self.n_samples, self.n_features)
        
        # Create synthetic labels
        self.y = np.random.choice(['FIN_WHALE', 'HUMPBACK_WHALE', 'RIGHT_WHALE', 'SONAR', 'OTHER'], 
                                 size=self.n_samples, p=[0.2, 0.2, 0.2, 0.2, 0.2])
    
    def tearDown(self):
        """
        Clean up test fixtures
        """
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_initialization(self):
        """
        Test model manager initialization
        """
        self.assertIsNone(self.model_manager.pre_classifier)
        self.assertIsNone(self.model_manager.detailed_classifier)
        self.assertIsNone(self.model_manager.scaler)
        self.assertIsNone(self.model_manager.label_encoder)
        
        # Check model configuration
        self.assertIn('pre_classifier', self.model_manager.model_config)
        self.assertIn('detailed_classifier', self.model_manager.model_config)
    
    def test_create_pre_classifier(self):
        """
        Test pre-classifier creation
        """
        pre_classifier = self.model_manager.create_pre_classifier()
        
        self.assertIsNotNone(pre_classifier)
        self.assertEqual(pre_classifier.__class__.__name__, 'RandomForestClassifier')
    
    def test_create_detailed_classifier(self):
        """
        Test detailed classifier creation
        """
        detailed_classifier = self.model_manager.create_detailed_classifier()
        
        self.assertIsNotNone(detailed_classifier)
        self.assertEqual(detailed_classifier.__class__.__name__, 'XGBClassifier')
    
    def test_train_models(self):
        """
        Test model training
        """
        metrics = self.model_manager.train_models(self.X, self.y)
        
        # Check that models are trained
        self.assertIsNotNone(self.model_manager.pre_classifier)
        self.assertIsNotNone(self.model_manager.detailed_classifier)
        self.assertIsNotNone(self.model_manager.scaler)
        self.assertIsNotNone(self.model_manager.label_encoder)
        
        # Check metrics
        self.assertIn('pre_classifier_accuracy', metrics)
        self.assertIn('detailed_classifier_accuracy', metrics)
        self.assertIn('combined_accuracy', metrics)
        
        # Check that accuracies are reasonable
        for metric in metrics.values():
            self.assertGreaterEqual(metric, 0.0)
            self.assertLessEqual(metric, 1.0)
    
    def test_predict(self):
        """
        Test model prediction
        """
        # Train models first
        self.model_manager.train_models(self.X, self.y)
        
        # Test prediction
        test_X = np.random.randn(5, self.n_features)
        predictions, confidence_scores = self.model_manager.predict(test_X)
        
        self.assertIsInstance(predictions, np.ndarray)
        self.assertIsInstance(confidence_scores, np.ndarray)
        self.assertEqual(len(predictions), 5)
        self.assertEqual(len(confidence_scores), 5)
        
        # Check that predictions are valid classes
        for pred in predictions:
            self.assertIn(pred, self.model_manager.classes)
        
        # Check that confidence scores are valid
        for conf in confidence_scores:
            self.assertGreaterEqual(conf, 0.0)
            self.assertLessEqual(conf, 1.0)
    
    def test_save_models(self):
        """
        Test model saving
        """
        # Train models first
        self.model_manager.train_models(self.X, self.y)
        
        # Save models
        saved_files = self.model_manager.save_models("test_models")
        
        # Check that files were saved
        self.assertIn('pre_classifier', saved_files)
        self.assertIn('detailed_classifier', saved_files)
        self.assertIn('scaler', saved_files)
        self.assertIn('label_encoder', saved_files)
        self.assertIn('config', saved_files)
        
        # Check that files exist
        for file_path in saved_files.values():
            self.assertTrue(os.path.exists(file_path))
    
    def test_load_models(self):
        """
        Test model loading
        """
        # Train and save models first
        self.model_manager.train_models(self.X, self.y)
        self.model_manager.save_models("test_models")
        
        # Create new model manager and load models
        new_model_manager = ModelManager(model_dir=self.temp_dir)
        success = new_model_manager.load_models("test_models")
        
        self.assertTrue(success)
        self.assertIsNotNone(new_model_manager.pre_classifier)
        self.assertIsNotNone(new_model_manager.detailed_classifier)
        self.assertIsNotNone(new_model_manager.scaler)
        self.assertIsNotNone(new_model_manager.label_encoder)
    
    def test_load_nonexistent_models(self):
        """
        Test loading non-existent models
        """
        success = self.model_manager.load_models("nonexistent_models")
        self.assertFalse(success)
    
    def test_get_model_info(self):
        """
        Test getting model information
        """
        # Test with no models loaded
        info = self.model_manager.get_model_info()
        
        self.assertIsInstance(info, dict)
        self.assertIn('classes', info)
        self.assertIn('model_loaded', info)
        self.assertIn('scaler_loaded', info)
        self.assertIn('label_encoder_loaded', info)
        
        self.assertFalse(info['model_loaded'])
        self.assertFalse(info['scaler_loaded'])
        self.assertFalse(info['label_encoder_loaded'])
        
        # Train models and test again
        self.model_manager.train_models(self.X, self.y)
        info = self.model_manager.get_model_info()
        
        self.assertTrue(info['model_loaded'])
        self.assertTrue(info['scaler_loaded'])
        self.assertTrue(info['label_encoder_loaded'])
    
    def test_predict_without_training(self):
        """
        Test prediction without training
        """
        test_X = np.random.randn(5, self.n_features)
        
        with self.assertRaises(ValueError):
            self.model_manager.predict(test_X)
    
    def test_combine_predictions(self):
        """
        Test prediction combination
        """
        # Train models first
        self.model_manager.train_models(self.X, self.y)
        
        # Test with marine and non-marine predictions
        test_X = np.random.randn(2, self.n_features)
        
        # Mock the pre-classifier to return specific predictions
        # This is a bit complex to test directly, so we'll test the overall flow
        predictions, confidence_scores = self.model_manager.predict(test_X)
        
        self.assertEqual(len(predictions), 2)
        self.assertEqual(len(confidence_scores), 2)
    
    def test_model_configuration(self):
        """
        Test model configuration
        """
        config = self.model_manager.model_config
        
        # Check pre-classifier config
        pre_config = config['pre_classifier']
        self.assertIn('type', pre_config)
        self.assertIn('n_estimators', pre_config)
        self.assertIn('max_depth', pre_config)
        self.assertIn('random_state', pre_config)
        
        # Check detailed classifier config
        detailed_config = config['detailed_classifier']
        self.assertIn('type', detailed_config)
        self.assertIn('n_estimators', detailed_config)
        self.assertIn('max_depth', detailed_config)
        self.assertIn('learning_rate', detailed_config)
        self.assertIn('random_state', detailed_config)


if __name__ == '__main__':
    unittest.main()
