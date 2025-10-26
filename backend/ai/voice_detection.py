"""
Voice Keyword Detection Module using Vosk
Detects keywords like "Help", "Nurse", "Doctor" offline
"""
import json
import logging
from typing import Optional, List, Tuple
import numpy as np
from collections import deque
from datetime import datetime

try:
    from vosk import Model, KaldiRecognizer
    VOSK_AVAILABLE = True
except ImportError:
    VOSK_AVAILABLE = False
    logging.warning("Vosk not available. Voice detection will be disabled.")

from config import settings

logger = logging.getLogger(__name__)


class VoiceDetector:
    """Detects voice keywords using Vosk offline speech recognition"""
    
    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path or settings.VOSK_MODEL_PATH
        self.keywords = [kw.lower() for kw in settings.VOICE_KEYWORDS]
        self.recognizer = None
        self.model = None
        
        # Detection tracking
        self.recent_detections = deque(maxlen=10)
        
        if VOSK_AVAILABLE:
            try:
                self._initialize_model()
            except Exception as e:
                logger.error(f"Failed to initialize Vosk model: {e}")
                logger.warning("Voice detection will be disabled")
        else:
            logger.warning("Vosk library not available")
    
    def _initialize_model(self):
        """Initialize Vosk model and recognizer"""
        try:
            self.model = Model(self.model_path)
            # Sample rate for audio processing (16kHz is standard)
            self.recognizer = KaldiRecognizer(self.model, 16000)
            self.recognizer.SetWords(True)
            logger.info("Vosk model initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing Vosk model: {e}")
            logger.info(f"Make sure Vosk model is downloaded to: {self.model_path}")
            raise
    
    def detect(self, audio_data: bytes) -> Tuple[bool, Optional[str], float]:
        """
        Detect keywords in audio data
        
        Args:
            audio_data: Raw audio bytes (16-bit PCM, 16kHz)
            
        Returns:
            Tuple of (alert_triggered, keyword_detected, confidence)
        """
        if not VOSK_AVAILABLE or not self.recognizer:
            return False, None, 0.0
        
        try:
            # Process audio
            if self.recognizer.AcceptWaveform(audio_data):
                result = json.loads(self.recognizer.Result())
                text = result.get("text", "").lower()
                
                # Check for keywords
                for keyword in self.keywords:
                    if keyword in text:
                        confidence = result.get("confidence", 0.8)
                        
                        # Log detection
                        self.recent_detections.append({
                            "keyword": keyword,
                            "text": text,
                            "confidence": confidence,
                            "timestamp": datetime.now()
                        })
                        
                        logger.info(f"Keyword detected: '{keyword}' in '{text}' (conf: {confidence:.2f})")
                        return True, keyword, confidence
            
            # Partial result (for real-time feedback)
            else:
                partial = json.loads(self.recognizer.PartialResult())
                text = partial.get("partial", "").lower()
                
                # Quick check for keywords in partial results
                for keyword in self.keywords:
                    if keyword in text:
                        logger.debug(f"Partial keyword match: '{keyword}' in '{text}'")
        
        except Exception as e:
            logger.error(f"Error in voice detection: {e}")
        
        return False, None, 0.0
    
    def detect_from_frame_audio(self, frame_audio: np.ndarray) -> Tuple[bool, Optional[str], float]:
        """
        Detect keywords from audio extracted from video frame
        
        Args:
            frame_audio: Audio numpy array
            
        Returns:
            Tuple of (alert_triggered, keyword_detected, confidence)
        """
        if not VOSK_AVAILABLE or not self.recognizer:
            return False, None, 0.0
        
        try:
            # Convert numpy array to bytes
            audio_bytes = frame_audio.tobytes()
            return self.detect(audio_bytes)
        except Exception as e:
            logger.error(f"Error processing frame audio: {e}")
            return False, None, 0.0
    
    def get_recent_detections(self) -> List[dict]:
        """Get list of recent keyword detections"""
        return list(self.recent_detections)
    
    def reset(self):
        """Reset the recognizer state"""
        if self.recognizer:
            try:
                self.recognizer = KaldiRecognizer(self.model, 16000)
                self.recognizer.SetWords(True)
                self.recent_detections.clear()
            except Exception as e:
                logger.error(f"Error resetting recognizer: {e}")
    
    def is_available(self) -> bool:
        """Check if voice detection is available"""
        return VOSK_AVAILABLE and self.recognizer is not None
    
    def __del__(self):
        """Cleanup resources"""
        self.recognizer = None
        self.model = None
