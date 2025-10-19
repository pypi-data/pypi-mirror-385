"""
Noise reduction utilities for MarACO API
"""

import numpy as np
import librosa
from typing import Union, Optional
import warnings


def spectral_subtraction(audio: np.ndarray, sr: int, 
                        alpha: float = 2.0, beta: float = 0.01) -> np.ndarray:
    """
    Apply spectral subtraction for noise reduction
    
    Args:
        audio: Audio data
        sr: Sample rate
        alpha: Over-subtraction factor
        beta: Spectral floor factor
        
    Returns:
        Noise-reduced audio data
    """
    try:
        # Compute STFT
        stft = librosa.stft(audio, n_fft=2048, hop_length=512)
        magnitude = np.abs(stft)
        phase = np.angle(stft)
        
        # Estimate noise from first 0.5 seconds
        noise_frames = int(0.5 * sr / 512)
        noise_spectrum = np.mean(magnitude[:, :noise_frames], axis=1, keepdims=True)
        
        # Apply spectral subtraction
        enhanced_magnitude = magnitude - alpha * noise_spectrum
        enhanced_magnitude = np.maximum(enhanced_magnitude, beta * magnitude)
        
        # Reconstruct audio
        enhanced_stft = enhanced_magnitude * np.exp(1j * phase)
        enhanced_audio = librosa.istft(enhanced_stft, hop_length=512)
        
        return enhanced_audio
        
    except Exception as e:
        warnings.warn(f"Spectral subtraction failed: {str(e)}")
        return audio


def wiener_filter(audio: np.ndarray, sr: int, 
                 noise_estimation_frames: int = 10) -> np.ndarray:
    """
    Apply Wiener filter for noise reduction
    
    Args:
        audio: Audio data
        sr: Sample rate
        noise_estimation_frames: Number of frames for noise estimation
        
    Returns:
        Noise-reduced audio data
    """
    try:
        # Compute STFT
        stft = librosa.stft(audio, n_fft=2048, hop_length=512)
        magnitude = np.abs(stft)
        phase = np.angle(stft)
        
        # Estimate noise from first few frames
        noise_spectrum = np.mean(magnitude[:, :noise_estimation_frames], axis=1, keepdims=True)
        
        # Apply Wiener filter
        # Wiener filter: H(f) = |S(f)|^2 / (|S(f)|^2 + |N(f)|^2)
        signal_power = magnitude ** 2
        noise_power = noise_spectrum ** 2
        
        # Avoid division by zero
        wiener_gain = signal_power / (signal_power + noise_power + 1e-10)
        
        # Apply filter
        enhanced_magnitude = magnitude * wiener_gain
        
        # Reconstruct audio
        enhanced_stft = enhanced_magnitude * np.exp(1j * phase)
        enhanced_audio = librosa.istft(enhanced_stft, hop_length=512)
        
        return enhanced_audio
        
    except Exception as e:
        warnings.warn(f"Wiener filtering failed: {str(e)}")
        return audio


def median_filter(audio: np.ndarray, kernel_size: int = 5) -> np.ndarray:
    """
    Apply median filter for noise reduction
    
    Args:
        audio: Audio data
        kernel_size: Size of median filter kernel
        
    Returns:
        Filtered audio data
    """
    try:
        from scipy.ndimage import median_filter
        return median_filter(audio, size=kernel_size)
    except ImportError:
        warnings.warn("scipy not available for median filtering")
        return audio
    except Exception as e:
        warnings.warn(f"Median filtering failed: {str(e)}")
        return audio


def gaussian_filter(audio: np.ndarray, sigma: float = 1.0) -> np.ndarray:
    """
    Apply Gaussian filter for noise reduction
    
    Args:
        audio: Audio data
        sigma: Gaussian filter standard deviation
        
    Returns:
        Filtered audio data
    """
    try:
        from scipy.ndimage import gaussian_filter1d
        return gaussian_filter1d(audio, sigma=sigma)
    except ImportError:
        warnings.warn("scipy not available for Gaussian filtering")
        return audio
    except Exception as e:
        warnings.warn(f"Gaussian filtering failed: {str(e)}")
        return audio


def adaptive_noise_reduction(audio: np.ndarray, sr: int, 
                           noise_threshold: float = 0.1) -> np.ndarray:
    """
    Apply adaptive noise reduction
    
    Args:
        audio: Audio data
        sr: Sample rate
        noise_threshold: Noise threshold for adaptation
        
    Returns:
        Noise-reduced audio data
    """
    try:
        # Compute STFT
        stft = librosa.stft(audio, n_fft=2048, hop_length=512)
        magnitude = np.abs(stft)
        phase = np.angle(stft)
        
        # Estimate noise level
        noise_level = np.percentile(magnitude, 10)  # Use 10th percentile as noise level
        
        # Adaptive threshold
        adaptive_threshold = noise_level * noise_threshold
        
        # Apply noise reduction
        enhanced_magnitude = np.where(
            magnitude > adaptive_threshold,
            magnitude - adaptive_threshold,
            magnitude * 0.1  # Reduce noise below threshold
        )
        
        # Reconstruct audio
        enhanced_stft = enhanced_magnitude * np.exp(1j * phase)
        enhanced_audio = librosa.istft(enhanced_stft, hop_length=512)
        
        return enhanced_audio
        
    except Exception as e:
        warnings.warn(f"Adaptive noise reduction failed: {str(e)}")
        return audio


def bandpass_filter(audio: np.ndarray, sr: int, 
                   low_freq: float = 80.0, high_freq: float = 8000.0) -> np.ndarray:
    """
    Apply bandpass filter
    
    Args:
        audio: Audio data
        sr: Sample rate
        low_freq: Low cutoff frequency
        high_freq: High cutoff frequency
        
    Returns:
        Filtered audio data
    """
    try:
        from scipy.signal import butter, filtfilt
        
        # Design Butterworth bandpass filter
        nyquist = sr / 2
        low = low_freq / nyquist
        high = high_freq / nyquist
        
        b, a = butter(4, [low, high], btype='band')
        
        # Apply filter
        filtered_audio = filtfilt(b, a, audio)
        
        return filtered_audio
        
    except ImportError:
        warnings.warn("scipy not available for bandpass filtering")
        return audio
    except Exception as e:
        warnings.warn(f"Bandpass filtering failed: {str(e)}")
        return audio


def noise_reduction_pipeline(audio: np.ndarray, sr: int, 
                           method: str = 'spectral_subtraction',
                           **kwargs) -> np.ndarray:
    """
    Apply noise reduction pipeline
    
    Args:
        audio: Audio data
        sr: Sample rate
        method: Noise reduction method
        **kwargs: Additional parameters for the method
        
    Returns:
        Noise-reduced audio data
    """
    if method == 'spectral_subtraction':
        return spectral_subtraction(audio, sr, **kwargs)
    elif method == 'wiener_filter':
        return wiener_filter(audio, sr, **kwargs)
    elif method == 'median_filter':
        return median_filter(audio, **kwargs)
    elif method == 'gaussian_filter':
        return gaussian_filter(audio, **kwargs)
    elif method == 'adaptive':
        return adaptive_noise_reduction(audio, sr, **kwargs)
    elif method == 'bandpass':
        return bandpass_filter(audio, sr, **kwargs)
    else:
        warnings.warn(f"Unknown noise reduction method: {method}")
        return audio
