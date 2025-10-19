"""
Audio utility functions for MarACO API
"""

import numpy as np
import librosa
import soundfile as sf
from pathlib import Path
from typing import Union, Dict, Tuple, Optional
import warnings


def validate_audio_file(file_path: Union[str, Path]) -> bool:
    """
    Validate if a file is a valid audio file
    
    Args:
        file_path: Path to audio file
        
    Returns:
        True if valid audio file, False otherwise
    """
    try:
        file_path = Path(file_path)
        
        if not file_path.exists():
            return False
        
        # Check file extension
        if file_path.suffix.lower() not in {'.wav', '.aiff', '.mp3', '.flac', '.m4a'}:
            return False
        
        # Try to load the file
        audio, sr = librosa.load(str(file_path), sr=None, mono=True)
        
        # Check if audio is valid
        if len(audio) == 0 or sr <= 0:
            return False
        
        return True
        
    except Exception:
        return False


def get_audio_info(file_path: Union[str, Path]) -> Dict[str, Union[int, float, str]]:
    """
    Get audio file information
    
    Args:
        file_path: Path to audio file
        
    Returns:
        Dictionary with audio information
    """
    try:
        file_path = Path(file_path)
        
        # Load audio
        audio, sr = librosa.load(str(file_path), sr=None, mono=True)
        
        # Calculate duration
        duration = len(audio) / sr
        
        # Calculate basic statistics
        rms = np.sqrt(np.mean(audio ** 2))
        peak = np.max(np.abs(audio))
        
        # Check for clipping
        clipping = peak > 0.99
        
        return {
            'file_path': str(file_path),
            'sample_rate': sr,
            'duration': duration,
            'samples': len(audio),
            'rms': rms,
            'peak': peak,
            'clipping': clipping,
            'channels': 1,  # librosa loads as mono
            'format': file_path.suffix.lower()
        }
        
    except Exception as e:
        return {
            'file_path': str(file_path),
            'error': str(e)
        }


def resample_audio(audio: np.ndarray, orig_sr: int, target_sr: int) -> np.ndarray:
    """
    Resample audio to target sample rate
    
    Args:
        audio: Audio data
        orig_sr: Original sample rate
        target_sr: Target sample rate
        
    Returns:
        Resampled audio data
    """
    if orig_sr == target_sr:
        return audio
    
    try:
        return librosa.resample(audio, orig_sr=orig_sr, target_sr=target_sr)
    except Exception as e:
        warnings.warn(f"Resampling failed: {str(e)}")
        return audio


def normalize_audio(audio: np.ndarray, target_level: float = 0.95) -> np.ndarray:
    """
    Normalize audio to target level
    
    Args:
        audio: Audio data
        target_level: Target peak level (0.0 to 1.0)
        
    Returns:
        Normalized audio data
    """
    if len(audio) == 0:
        return audio
    
    # Avoid division by zero
    max_val = np.max(np.abs(audio))
    if max_val == 0:
        return audio
    
    # Normalize to target level
    return audio * (target_level / max_val)


def segment_audio(audio: np.ndarray, sr: int, start_time: float = 0.0, 
                 duration: float = 5.0) -> np.ndarray:
    """
    Segment audio to specific time range
    
    Args:
        audio: Audio data
        sr: Sample rate
        start_time: Start time in seconds
        duration: Duration in seconds
        
    Returns:
        Segmented audio data
    """
    start_sample = int(start_time * sr)
    end_sample = int((start_time + duration) * sr)
    
    # Ensure we don't go out of bounds
    start_sample = max(0, start_sample)
    end_sample = min(len(audio), end_sample)
    
    if start_sample >= end_sample:
        return np.array([])
    
    return audio[start_sample:end_sample]


def pad_audio(audio: np.ndarray, target_length: int, mode: str = 'constant') -> np.ndarray:
    """
    Pad audio to target length
    
    Args:
        audio: Audio data
        target_length: Target length in samples
        mode: Padding mode ('constant', 'reflect', 'edge')
        
    Returns:
        Padded audio data
    """
    if len(audio) >= target_length:
        return audio[:target_length]
    
    padding = target_length - len(audio)
    
    if mode == 'constant':
        return np.pad(audio, (0, padding), mode='constant')
    elif mode == 'reflect':
        return np.pad(audio, (0, padding), mode='reflect')
    elif mode == 'edge':
        return np.pad(audio, (0, padding), mode='edge')
    else:
        raise ValueError(f"Unknown padding mode: {mode}")


def trim_silence(audio: np.ndarray, sr: int, top_db: float = 20.0) -> np.ndarray:
    """
    Trim silence from audio
    
    Args:
        audio: Audio data
        sr: Sample rate
        top_db: Silence threshold in dB
        
    Returns:
        Trimmed audio data
    """
    try:
        return librosa.effects.trim(audio, top_db=top_db)[0]
    except Exception as e:
        warnings.warn(f"Silence trimming failed: {str(e)}")
        return audio


def apply_preemphasis(audio: np.ndarray, coef: float = 0.97) -> np.ndarray:
    """
    Apply pre-emphasis filter
    
    Args:
        audio: Audio data
        coef: Pre-emphasis coefficient
        
    Returns:
        Pre-emphasized audio data
    """
    try:
        return librosa.effects.preemphasis(audio, coef=coef)
    except Exception as e:
        warnings.warn(f"Pre-emphasis failed: {str(e)}")
        return audio


def detect_clipping(audio: np.ndarray, threshold: float = 0.99) -> bool:
    """
    Detect audio clipping
    
    Args:
        audio: Audio data
        threshold: Clipping threshold
        
    Returns:
        True if clipping detected, False otherwise
    """
    return np.max(np.abs(audio)) > threshold


def calculate_snr(audio: np.ndarray, noise_floor: float = 0.01) -> float:
    """
    Calculate signal-to-noise ratio
    
    Args:
        audio: Audio data
        noise_floor: Noise floor level
        
    Returns:
        SNR in dB
    """
    signal_power = np.mean(audio ** 2)
    noise_power = noise_floor ** 2
    
    if noise_power == 0:
        return float('inf')
    
    snr = 10 * np.log10(signal_power / noise_power)
    return snr


def batch_process_audio(files: list, 
                       target_sr: int = 16000,
                       duration: float = 5.0,
                       apply_trim: bool = True,
                       apply_normalize: bool = True) -> list:
    """
    Batch process audio files
    
    Args:
        files: List of audio file paths
        target_sr: Target sample rate
        duration: Target duration
        apply_trim: Whether to trim silence
        apply_normalize: Whether to normalize
        
    Returns:
        List of processed audio arrays
    """
    processed_audio = []
    
    for file_path in files:
        try:
            # Load audio
            audio, sr = librosa.load(str(file_path), sr=None, mono=True)
            
            # Resample if needed
            if sr != target_sr:
                audio = resample_audio(audio, sr, target_sr)
            
            # Trim silence
            if apply_trim:
                audio = trim_silence(audio, target_sr)
            
            # Segment to target duration
            target_length = int(duration * target_sr)
            if len(audio) > target_length:
                audio = audio[:target_length]
            elif len(audio) < target_length:
                audio = pad_audio(audio, target_length)
            
            # Normalize
            if apply_normalize:
                audio = normalize_audio(audio)
            
            processed_audio.append(audio)
            
        except Exception as e:
            warnings.warn(f"Failed to process {file_path}: {str(e)}")
            processed_audio.append(None)
    
    return processed_audio
