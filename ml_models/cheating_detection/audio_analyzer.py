import numpy as np
import librosa
import soundfile as sf
from collections import deque
import logging
from sklearn.ensemble import IsolationForest

logger = logging.getLogger(__name__)

class AudioAnalyzer:
    def __init__(self, sample_rate=16000, frame_length=2048):
        """Initialize audio analyzer for anomaly detection"""
        self.sample_rate = sample_rate
        self.frame_length = frame_length
        self.hop_length = frame_length // 2
        
        # Buffer for audio features
        self.feature_buffer = deque(maxlen=50)
        
        # Anomaly detector
        self.anomaly_detector = IsolationForest(
            contamination=0.1,
            random_state=42
        )
        self.is_trained = False
        
        # Voice activity detection parameters
        self.energy_threshold = 0.02
        self.zcr_threshold = 0.1
    
    def extract_features(self, audio_data):
        """Extract audio features for analysis"""
        features = {}
        
        try:
            # Convert to float32 if needed
            if audio_data.dtype != np.float32:
                audio_data = audio_data.astype(np.float32)
            
            # Time domain features
            features['rms'] = np.sqrt(np.mean(audio_data**2))
            features['zcr'] = np.mean(librosa.zero_crossings(audio_data))
            
            # Frequency domain features
            stft = librosa.stft(audio_data, n_fft=self.frame_length, 
                               hop_length=self.hop_length)
            magnitude = np.abs(stft)
            
            # Spectral features
            features['spectral_centroid'] = np.mean(
                librosa.feature.spectral_centroid(S=magnitude, sr=self.sample_rate)
            )
            features['spectral_rolloff'] = np.mean(
                librosa.feature.spectral_rolloff(S=magnitude, sr=self.sample_rate)
            )
            features['spectral_bandwidth'] = np.mean(
                librosa.feature.spectral_bandwidth(S=magnitude, sr=self.sample_rate)
            )
            
            # MFCC features
            mfccs = librosa.feature.mfcc(y=audio_data, sr=self.sample_rate, n_mfcc=13)
            for i in range(13):
                features[f'mfcc_{i}'] = np.mean(mfccs[i])
            
        except Exception as e:
            logger.error(f"Feature extraction error: {str(e)}")
            return None
        
        return features
    
    def detect_voice_activity(self, audio_data):
        """Detect if there's voice activity in the audio"""
        features = self.extract_features(audio_data)
        if features is None:
            return False
        
        # Simple VAD based on energy and ZCR
        is_voice = (features['rms'] > self.energy_threshold and 
                   features['zcr'] > self.zcr_threshold)
        
        return is_voice
    
    def detect_anomaly(self, audio_data):
        """Detect audio anomalies"""
        features = self.extract_features(audio_data)
        if features is None:
            return False, 0.0
        
        # Convert features to array
        feature_vector = np.array(list(features.values())).reshape(1, -1)
        
        # Add to buffer for training
        self.feature_buffer.append(feature_vector[0])
        
        # Train or update anomaly detector
        if len(self.feature_buffer) >= 20 and not self.is_trained:
            self.anomaly_detector.fit(np.array(self.feature_buffer))
            self.is_trained = True
        
        # Detect anomaly
        if self.is_trained:
            anomaly_score = self.anomaly_detector.decision_function(feature_vector)[0]
            is_anomaly = self.anomaly_detector.predict(feature_vector)[0] == -1
            
            # Convert score to confidence (0-1)
            confidence = 1 / (1 + np.exp(anomaly_score))
            
            return is_anomaly, confidence
        
        return False, 0.0
