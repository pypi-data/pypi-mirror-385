"""
Test runner for MarACO API
"""

import unittest
import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import test modules
from tests.test_preprocessor import TestAudioPreprocessor
from tests.test_feature_extractor import TestFeatureExtractor
from tests.test_classifier import TestMarineAcousticClassifier
from tests.test_model import TestModelManager


def run_tests():
    """
    Run all tests
    """
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(unittest.makeSuite(TestAudioPreprocessor))
    test_suite.addTest(unittest.makeSuite(TestFeatureExtractor))
    test_suite.addTest(unittest.makeSuite(TestMarineAcousticClassifier))
    test_suite.addTest(unittest.makeSuite(TestModelManager))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Return exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    exit(run_tests())
