"""
Feature extraction module for MarACO API
Extracts audio features optimized for marine acoustic classification
"""

import numpy as np
import librosa
from typing import Union, List, Dict, Optional
from scipy.stats import skew, kurtosis
import warnings


class FeatureExtractor:
    """
    Feature extraction class for marine acoustic data
    """
    
    def __init__(self, 
                 n_mfcc: int = 13,
                 n_mels: int = 128,
                 n_fft: int = 2048,
                 hop_length: int = 512,
                 include_deltas: bool = True):
        """
        Initialize feature extractor
        
        Args:
            n_mfcc: Number of MFCC coefficients
            n_mels: Number of mel bins
            n_fft: FFT window size
            hop_length: Hop length for STFT
            include_deltas: Whether to include delta and delta-delta features
        """
        self.n_mfcc = n_mfcc
        self.n_mels = n_mels
        self.n_fft = n_fft
        self.hop_length = hop_length
        self.include_deltas = include_deltas
    
    def extract_mfcc(self, audio: np.ndarray, sr: int) -> np.ndarray:
        """
        Extract MFCC features
        
        Args:
            audio: Audio data
            sr: Sample rate
            
        Returns:
            MFCC features
        """
        try:
            mfcc = librosa.feature.mfcc(
                y=audio, 
                sr=sr, 
                n_mfcc=self.n_mfcc,
                n_fft=self.n_fft,
                hop_length=self.hop_length
            )
            return mfcc
        except Exception as e:
            warnings.warn(f"MFCC extraction failed: {str(e)}")
            return np.zeros((self.n_mfcc, 1))
    
    def extract_mel_spectrogram(self, audio: np.ndarray, sr: int) -> np.ndarray:
        """
        Extract mel spectrogram
        
        Args:
            audio: Audio data
            sr: Sample rate
            
        Returns:
            Mel spectrogram
        """
        try:
            mel_spec = librosa.feature.melspectrogram(
                y=audio,
                sr=sr,
                n_mels=self.n_mels,
                n_fft=self.n_fft,
                hop_length=self.hop_length
            )
            # Convert to log scale
            log_mel_spec = librosa.power_to_db(mel_spec, ref=np.max)
            return log_mel_spec
        except Exception as e:
            warnings.warn(f"Mel spectrogram extraction failed: {str(e)}")
            return np.zeros((self.n_mels, 1))
    
    def extract_spectral_features(self, audio: np.ndarray, sr: int) -> Dict[str, float]:
        """
        Extract spectral features
        
        Args:
            audio: Audio data
            sr: Sample rate
            
        Returns:
            Dictionary of spectral features
        """
        try:
            # Spectral centroid
            spectral_centroids = librosa.feature.spectral_centroid(y=audio, sr=sr)
            spectral_centroid_mean = np.mean(spectral_centroids)
            spectral_centroid_std = np.std(spectral_centroids)
            
            # Spectral rolloff
            spectral_rolloff = librosa.feature.spectral_rolloff(y=audio, sr=sr)
            spectral_rolloff_mean = np.mean(spectral_rolloff)
            spectral_rolloff_std = np.std(spectral_rolloff)
            
            # Spectral bandwidth
            spectral_bandwidth = librosa.feature.spectral_bandwidth(y=audio, sr=sr)
            spectral_bandwidth_mean = np.mean(spectral_bandwidth)
            spectral_bandwidth_std = np.std(spectral_bandwidth)
            
            # Zero crossing rate
            zcr = librosa.feature.zero_crossing_rate(audio)
            zcr_mean = np.mean(zcr)
            zcr_std = np.std(zcr)
            
            # Chroma features
            chroma = librosa.feature.chroma_stft(y=audio, sr=sr)
            chroma_mean = np.mean(chroma, axis=1)
            chroma_std = np.std(chroma, axis=1)
            
            return {
                'spectral_centroid_mean': spectral_centroid_mean,
                'spectral_centroid_std': spectral_centroid_std,
                'spectral_rolloff_mean': spectral_rolloff_mean,
                'spectral_rolloff_std': spectral_rolloff_std,
                'spectral_bandwidth_mean': spectral_bandwidth_mean,
                'spectral_bandwidth_std': spectral_bandwidth_std,
                'zcr_mean': zcr_mean,
                'zcr_std': zcr_std,
                'chroma_mean': chroma_mean.tolist(),
                'chroma_std': chroma_std.tolist()
            }
        except Exception as e:
            warnings.warn(f"Spectral feature extraction failed: {str(e)}")
            return {
                'spectral_centroid_mean': 0.0,
                'spectral_centroid_std': 0.0,
                'spectral_rolloff_mean': 0.0,
                'spectral_rolloff_std': 0.0,
                'spectral_bandwidth_mean': 0.0,
                'spectral_bandwidth_std': 0.0,
                'zcr_mean': 0.0,
                'zcr_std': 0.0,
                'chroma_mean': [0.0] * 12,
                'chroma_std': [0.0] * 12
            }
    
    def extract_temporal_features(self, audio: np.ndarray) -> Dict[str, float]:
        """
        Extract temporal features
        
        Args:
            audio: Audio data
            
        Returns:
            Dictionary of temporal features
        """
        try:
            # RMS energy
            rms = librosa.feature.rms(y=audio)
            rms_mean = np.mean(rms)
            rms_std = np.std(rms)
            
            # Statistical features
            audio_mean = np.mean(audio)
            audio_std = np.std(audio)
            audio_skew = skew(audio)
            audio_kurtosis = kurtosis(audio)
            
            # Energy features
            energy = np.sum(audio ** 2)
            energy_per_sample = energy / len(audio)
            
            return {
                'rms_mean': rms_mean,
                'rms_std': rms_std,
                'audio_mean': audio_mean,
                'audio_std': audio_std,
                'audio_skew': audio_skew,
                'audio_kurtosis': audio_kurtosis,
                'energy': energy,
                'energy_per_sample': energy_per_sample
            }
        except Exception as e:
            warnings.warn(f"Temporal feature extraction failed: {str(e)}")
            return {
                'rms_mean': 0.0,
                'rms_std': 0.0,
                'audio_mean': 0.0,
                'audio_std': 0.0,
                'audio_skew': 0.0,
                'audio_kurtosis': 0.0,
                'energy': 0.0,
                'energy_per_sample': 0.0
            }
    
    def extract_delta_features(self, features: np.ndarray) -> np.ndarray:
        """
        Extract delta and delta-delta features
        
        Args:
            features: Input features
            
        Returns:
            Delta features
        """
        try:
            delta = librosa.feature.delta(features)
            delta2 = librosa.feature.delta(features, order=2)
            return np.vstack([features, delta, delta2])
        except Exception as e:
            warnings.warn(f"Delta feature extraction failed: {str(e)}")
            return features
    
    def extract_all_features(self, audio: np.ndarray, sr: int) -> Dict[str, Union[np.ndarray, List, float]]:
        """
        Extract all features for marine acoustic classification
        
        Args:
            audio: Audio data
            sr: Sample rate
            
        Returns:
            Dictionary containing all extracted features
        """
        features = {}
        
        # MFCC features
        mfcc = self.extract_mfcc(audio, sr)
        features['mfcc'] = mfcc
        
        # Mel spectrogram
        mel_spec = self.extract_mel_spectrogram(audio, sr)
        features['mel_spectrogram'] = mel_spec
        
        # Spectral features
        spectral_features = self.extract_spectral_features(audio, sr)
        features.update(spectral_features)
        
        # Temporal features
        temporal_features = self.extract_temporal_features(audio)
        features.update(temporal_features)
        
        # Delta features if requested
        if self.include_deltas:
            mfcc_delta = self.extract_delta_features(mfcc)
            features['mfcc_with_deltas'] = mfcc_delta
        
        return features
    
    def extract_features_for_classification(self, audio: np.ndarray, sr: int) -> np.ndarray:
        """
        Extract features optimized for classification
        
        Args:
            audio: Audio data
            sr: Sample rate
            
        Returns:
            Feature vector for classification
        """
        features = self.extract_all_features(audio, sr)
        
        # Combine features into a single vector
        feature_vector = []
        
        # MFCC statistics
        mfcc = features['mfcc']
        feature_vector.extend([
            np.mean(mfcc, axis=1),
            np.std(mfcc, axis=1),
            np.min(mfcc, axis=1),
            np.max(mfcc, axis=1)
        ])
        
        # Spectral features
        spectral_keys = [
            'spectral_centroid_mean', 'spectral_centroid_std',
            'spectral_rolloff_mean', 'spectral_rolloff_std',
            'spectral_bandwidth_mean', 'spectral_bandwidth_std',
            'zcr_mean', 'zcr_std'
        ]
        for key in spectral_keys:
            feature_vector.append(features[key])
        
        # Chroma features
        feature_vector.extend(features['chroma_mean'])
        feature_vector.extend(features['chroma_std'])
        
        # Temporal features
        temporal_keys = [
            'rms_mean', 'rms_std', 'audio_mean', 'audio_std',
            'audio_skew', 'audio_kurtosis', 'energy', 'energy_per_sample'
        ]
        for key in temporal_keys:
            feature_vector.append(features[key])
        
        # Flatten and return
        feature_vector = np.concatenate([np.array(f).flatten() for f in feature_vector])
        return feature_vector
    
    def batch_extract_features(self, audio_list: List[np.ndarray], 
                             sr_list: List[int],
                             n_jobs: int = -1) -> List[np.ndarray]:
        """
        Extract features for multiple audio files in parallel
        
        Args:
            audio_list: List of audio arrays
            sr_list: List of sample rates
            n_jobs: Number of parallel jobs
            
        Returns:
            List of feature vectors
        """
        from joblib import Parallel, delayed
        
        def extract_single(audio, sr):
            try:
                return self.extract_features_for_classification(audio, sr)
            except Exception as e:
                warnings.warn(f"Feature extraction failed: {str(e)}")
                return np.zeros(100)  # Return zero vector as fallback
        
        results = Parallel(n_jobs=n_jobs)(
            delayed(extract_single)(audio, sr) 
            for audio, sr in zip(audio_list, sr_list)
        )
        
        return results
