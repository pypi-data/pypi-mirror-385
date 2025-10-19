"""
Real-time detection example for MarACO API
"""

import numpy as np
import time
import threading
from collections import deque
from maraco import MarineAcousticClassifier


class RealTimeDetector:
    """
    Real-time marine acoustic detection
    """
    
    def __init__(self, 
                 sample_rate: int = 16000,
                 chunk_duration: float = 5.0,
                 buffer_duration: float = 10.0):
        """
        Initialize real-time detector
        
        Args:
            sample_rate: Audio sample rate
            chunk_duration: Duration of each analysis chunk
            buffer_duration: Duration of audio buffer
        """
        self.sample_rate = sample_rate
        self.chunk_duration = chunk_duration
        self.buffer_duration = buffer_duration
        
        # Calculate buffer size
        self.chunk_size = int(sample_rate * chunk_duration)
        self.buffer_size = int(sample_rate * buffer_duration)
        
        # Initialize classifier
        self.classifier = MarineAcousticClassifier()
        
        if not self.classifier.is_model_loaded():
            raise RuntimeError("No pre-trained models found. Please train models first.")
        
        # Audio buffer
        self.audio_buffer = deque(maxlen=self.buffer_size)
        self.is_running = False
        self.detection_thread = None
        
        # Detection results
        self.latest_detection = None
        self.detection_history = deque(maxlen=100)
    
    def add_audio_chunk(self, audio_chunk: np.ndarray):
        """
        Add audio chunk to buffer
        
        Args:
            audio_chunk: Audio data array
        """
        self.audio_buffer.extend(audio_chunk)
    
    def analyze_audio(self):
        """
        Analyze current audio buffer
        """
        if len(self.audio_buffer) < self.chunk_size:
            return None
        
        # Get the most recent chunk
        recent_chunk = np.array(list(self.audio_buffer)[-self.chunk_size:])
        
        # Make prediction
        result = self.classifier.predict_stream(
            recent_chunk, 
            self.sample_rate
        )
        
        return result
    
    def start_detection(self):
        """
        Start real-time detection
        """
        if self.is_running:
            return
        
        self.is_running = True
        self.detection_thread = threading.Thread(target=self._detection_loop)
        self.detection_thread.start()
        print("Real-time detection started")
    
    def stop_detection(self):
        """
        Stop real-time detection
        """
        self.is_running = False
        if self.detection_thread:
            self.detection_thread.join()
        print("Real-time detection stopped")
    
    def _detection_loop(self):
        """
        Main detection loop
        """
        while self.is_running:
            if len(self.audio_buffer) >= self.chunk_size:
                result = self.analyze_audio()
                if result:
                    self.latest_detection = result
                    self.detection_history.append(result)
                    
                    # Print detection result
                    print(f"[{time.strftime('%H:%M:%S')}] "
                          f"Class: {result['class']}, "
                          f"Confidence: {result['confidence']:.3f}, "
                          f"Time: {result['processing_time']:.3f}s")
            
            time.sleep(0.1)  # Check every 100ms
    
    def get_latest_detection(self):
        """
        Get the latest detection result
        
        Returns:
            Latest detection result or None
        """
        return self.latest_detection
    
    def get_detection_history(self, n: int = 10):
        """
        Get recent detection history
        
        Args:
            n: Number of recent detections to return
            
        Returns:
            List of recent detection results
        """
        return list(self.detection_history)[-n:]
    
    def get_class_statistics(self):
        """
        Get statistics about detected classes
        
        Returns:
            Dictionary with class statistics
        """
        if not self.detection_history:
            return {}
        
        class_counts = {}
        total_confidence = {}
        
        for detection in self.detection_history:
            class_name = detection['class']
            confidence = detection['confidence']
            
            class_counts[class_name] = class_counts.get(class_name, 0) + 1
            total_confidence[class_name] = total_confidence.get(class_name, 0) + confidence
        
        # Calculate average confidence for each class
        avg_confidence = {}
        for class_name in class_counts:
            avg_confidence[class_name] = total_confidence[class_name] / class_counts[class_name]
        
        return {
            'class_counts': dict(class_counts),
            'avg_confidence': avg_confidence,
            'total_detections': len(self.detection_history)
        }


def simulate_audio_stream(detector: RealTimeDetector, duration: float = 60.0):
    """
    Simulate an audio stream for testing
    
    Args:
        detector: RealTimeDetector instance
        duration: Duration of simulation in seconds
    """
    print(f"Simulating audio stream for {duration} seconds...")
    
    # Generate synthetic audio with different characteristics
    sample_rate = detector.sample_rate
    total_samples = int(sample_rate * duration)
    chunk_size = int(sample_rate * 0.1)  # 100ms chunks
    
    for i in range(0, total_samples, chunk_size):
        # Generate different types of audio patterns
        t = np.linspace(i / sample_rate, (i + chunk_size) / sample_rate, chunk_size)
        
        # Simulate different marine sounds
        if i < total_samples // 4:
            # Simulate whale calls (low frequency)
            audio_chunk = 0.1 * np.sin(2 * np.pi * 20 * t) * np.exp(-t)
        elif i < total_samples // 2:
            # Simulate sonar (high frequency pulses)
            audio_chunk = 0.2 * np.sin(2 * np.pi * 1000 * t) * (np.sin(2 * np.pi * 0.5 * t) > 0)
        elif i < 3 * total_samples // 4:
            # Simulate vessel noise (broadband)
            audio_chunk = 0.15 * np.random.randn(chunk_size)
        else:
            # Simulate silence/ambient noise
            audio_chunk = 0.01 * np.random.randn(chunk_size)
        
        # Add some noise
        audio_chunk += 0.05 * np.random.randn(chunk_size)
        
        # Add to detector
        detector.add_audio_chunk(audio_chunk)
        
        time.sleep(0.1)  # Simulate real-time processing


def main():
    """
    Main function for real-time detection example
    """
    print("MarACO API - Real-time Detection Example")
    print("=" * 50)
    
    try:
        # Initialize detector
        detector = RealTimeDetector(
            sample_rate=16000,
            chunk_duration=5.0,
            buffer_duration=10.0
        )
        
        # Start detection
        detector.start_detection()
        
        # Simulate audio stream
        simulate_audio_stream(detector, duration=30.0)
        
        # Get statistics
        print("\nDetection Statistics:")
        stats = detector.get_class_statistics()
        for class_name, count in stats['class_counts'].items():
            avg_conf = stats['avg_confidence'][class_name]
            print(f"  {class_name}: {count} detections (avg confidence: {avg_conf:.3f})")
        
        # Stop detection
        detector.stop_detection()
        
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
