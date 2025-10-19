"""
Audio preprocessing module for MarACO API
Handles audio loading, noise reduction, and standardization
"""

import numpy as np
import librosa
import soundfile as sf
from typing import Union, Tuple, Optional
import warnings
from pathlib import Path


class AudioPreprocessor:
    """
    Audio preprocessing class for marine acoustic data
    """
    
    def __init__(self, 
                 target_sr: int = 16000,
                 duration: float = 5.0,
                 min_duration: float = 0.5,
                 max_duration: float = 30.0):
        """
        Initialize audio preprocessor
        
        Args:
            target_sr: Target sample rate for resampling
            duration: Target duration in seconds
            min_duration: Minimum acceptable duration
            max_duration: Maximum acceptable duration
        """
        self.target_sr = target_sr
        self.duration = duration
        self.min_duration = min_duration
        self.max_duration = max_duration
        
        # Supported audio formats
        self.supported_formats = {'.wav', '.aiff', '.mp3', '.flac', '.m4a'}
    
    def load_audio(self, file_path: Union[str, Path]) -> Tuple[np.ndarray, int]:
        """
        Load audio file with error handling
        
        Args:
            file_path: Path to audio file
            
        Returns:
            Tuple of (audio_data, sample_rate)
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Audio file not found: {file_path}")
        
        if file_path.suffix.lower() not in self.supported_formats:
            raise ValueError(f"Unsupported audio format: {file_path.suffix}")
        
        try:
            # Load audio with librosa for better format support
            audio, sr = librosa.load(str(file_path), sr=None, mono=True)
            return audio, sr
        except Exception as e:
            raise RuntimeError(f"Failed to load audio file {file_path}: {str(e)}")
    
    def resample_audio(self, audio: np.ndarray, sr: int) -> np.ndarray:
        """
        Resample audio to target sample rate
        
        Args:
            audio: Audio data
            sr: Current sample rate
            
        Returns:
            Resampled audio data
        """
        if sr == self.target_sr:
            return audio
        
        try:
            return librosa.resample(audio, orig_sr=sr, target_sr=self.target_sr)
        except Exception as e:
            warnings.warn(f"Resampling failed: {str(e)}")
            return audio
    
    def normalize_audio(self, audio: np.ndarray) -> np.ndarray:
        """
        Normalize audio to [-1, 1] range
        
        Args:
            audio: Audio data
            
        Returns:
            Normalized audio data
        """
        if len(audio) == 0:
            return audio
        
        # Avoid division by zero
        max_val = np.max(np.abs(audio))
        if max_val == 0:
            return audio
        
        return audio / max_val
    
    def reduce_noise(self, audio: np.ndarray, sr: int) -> np.ndarray:
        """
        Apply noise reduction using spectral subtraction
        
        Args:
            audio: Audio data
            sr: Sample rate
            
        Returns:
            Noise-reduced audio data
        """
        try:
            # Simple spectral subtraction for noise reduction
            # Compute STFT
            stft = librosa.stft(audio, n_fft=2048, hop_length=512)
            magnitude = np.abs(stft)
            phase = np.angle(stft)
            
            # Estimate noise from first 0.5 seconds
            noise_frames = int(0.5 * sr / 512)
            noise_spectrum = np.mean(magnitude[:, :noise_frames], axis=1, keepdims=True)
            
            # Apply spectral subtraction
            alpha = 2.0  # Over-subtraction factor
            beta = 0.01  # Spectral floor factor
            
            # Compute spectral subtraction
            enhanced_magnitude = magnitude - alpha * noise_spectrum
            enhanced_magnitude = np.maximum(enhanced_magnitude, beta * magnitude)
            
            # Reconstruct audio
            enhanced_stft = enhanced_magnitude * np.exp(1j * phase)
            enhanced_audio = librosa.istft(enhanced_stft, hop_length=512)
            
            return enhanced_audio
            
        except Exception as e:
            warnings.warn(f"Noise reduction failed: {str(e)}")
            return audio
    
    def segment_audio(self, audio: np.ndarray, sr: int) -> np.ndarray:
        """
        Segment audio to target duration
        
        Args:
            audio: Audio data
            sr: Sample rate
            
        Returns:
            Segmented audio data
        """
        target_length = int(self.duration * sr)
        audio_length = len(audio)
        
        if audio_length < int(self.min_duration * sr):
            raise ValueError(f"Audio too short: {audio_length/sr:.2f}s < {self.min_duration}s")
        
        if audio_length > int(self.max_duration * sr):
            # Take the middle portion for long audio
            start = (audio_length - target_length) // 2
            return audio[start:start + target_length]
        
        if audio_length < target_length:
            # Pad with zeros for short audio
            padding = target_length - audio_length
            return np.pad(audio, (0, padding), mode='constant')
        
        # Take the first portion for exact or longer audio
        return audio[:target_length]
    
    def preprocess_audio(self, file_path: Union[str, Path], 
                        apply_noise_reduction: bool = True) -> np.ndarray:
        """
        Complete audio preprocessing pipeline
        
        Args:
            file_path: Path to audio file
            apply_noise_reduction: Whether to apply noise reduction
            
        Returns:
            Preprocessed audio data
        """
        # Load audio
        audio, sr = self.load_audio(file_path)
        
        # Resample if needed
        audio = self.resample_audio(audio, sr)
        
        # Apply noise reduction
        if apply_noise_reduction:
            audio = self.reduce_noise(audio, self.target_sr)
        
        # Segment to target duration
        audio = self.segment_audio(audio, self.target_sr)
        
        # Normalize
        audio = self.normalize_audio(audio)
        
        return audio
    
    def batch_preprocess(self, file_paths: list, 
                        apply_noise_reduction: bool = True,
                        n_jobs: int = -1) -> list:
        """
        Preprocess multiple audio files in parallel
        
        Args:
            file_paths: List of audio file paths
            apply_noise_reduction: Whether to apply noise reduction
            n_jobs: Number of parallel jobs (-1 for all CPUs)
            
        Returns:
            List of preprocessed audio arrays
        """
        from joblib import Parallel, delayed
        
        def process_single(file_path):
            try:
                return self.preprocess_audio(file_path, apply_noise_reduction)
            except Exception as e:
                warnings.warn(f"Failed to process {file_path}: {str(e)}")
                return None
        
        results = Parallel(n_jobs=n_jobs)(
            delayed(process_single)(fp) for fp in file_paths
        )
        
        # Filter out None results
        return [result for result in results if result is not None]
