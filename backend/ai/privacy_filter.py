"""
Privacy Filter Module
Real-time face blurring for patient privacy
"""
import cv2
import numpy as np
from typing import List, Tuple
import logging

from config import settings

logger = logging.getLogger(__name__)


class PrivacyFilter:
    """Applies privacy filters to video frames"""
    
    def __init__(self):
        # Load face detection cascade
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        
        # Alternative: Use DNN-based face detection for better accuracy
        self.use_dnn = False
        self.dnn_net = None
        
        # Configuration
        self.blur_kernel_size = settings.BLUR_KERNEL_SIZE
        self.enabled = settings.ENABLE_FACE_BLUR
        
        # Ensure kernel size is odd
        if self.blur_kernel_size % 2 == 0:
            self.blur_kernel_size += 1
        
        # Try to load DNN model for better face detection
        try:
            self._load_dnn_model()
        except Exception as e:
            logger.warning(f"DNN face detection not available: {e}")
            logger.info("Using Haar Cascade for face detection")
    
    def _load_dnn_model(self):
        """Load DNN-based face detection model (optional, more accurate)"""
        # This would load a pre-trained DNN model
        # For now, we'll stick with Haar Cascade for simplicity
        pass
    
    def apply(self, frame: np.ndarray) -> np.ndarray:
        """
        Apply privacy filter to frame
        
        Args:
            frame: Input video frame (BGR format)
            
        Returns:
            Frame with faces blurred
        """
        if not self.enabled:
            return frame
        
        try:
            # Detect faces
            faces = self._detect_faces(frame)
            
            # Blur each detected face
            for (x, y, w, h) in faces:
                # Extract face region
                face_region = frame[y:y+h, x:x+w]
                
                # Apply Gaussian blur
                blurred_face = cv2.GaussianBlur(
                    face_region,
                    (self.blur_kernel_size, self.blur_kernel_size),
                    0
                )
                
                # Replace face region with blurred version
                frame[y:y+h, x:x+w] = blurred_face
            
            return frame
        
        except Exception as e:
            logger.error(f"Error applying privacy filter: {e}")
            return frame
    
    def _detect_faces(self, frame: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Detect faces in frame
        
        Args:
            frame: Input frame
            
        Returns:
            List of face bounding boxes (x, y, w, h)
        """
        # Convert to grayscale for detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect faces using Haar Cascade
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),
            flags=cv2.CASCADE_SCALE_IMAGE
        )
        
        return faces
    
    def apply_pixelation(self, frame: np.ndarray) -> np.ndarray:
        """
        Alternative privacy method: pixelation instead of blur
        
        Args:
            frame: Input video frame
            
        Returns:
            Frame with faces pixelated
        """
        if not self.enabled:
            return frame
        
        try:
            faces = self._detect_faces(frame)
            
            for (x, y, w, h) in faces:
                # Extract face region
                face_region = frame[y:y+h, x:x+w]
                
                # Pixelate by downscaling and upscaling
                pixel_size = 15
                small = cv2.resize(
                    face_region,
                    (pixel_size, pixel_size),
                    interpolation=cv2.INTER_LINEAR
                )
                pixelated_face = cv2.resize(
                    small,
                    (w, h),
                    interpolation=cv2.INTER_NEAREST
                )
                
                # Replace face region
                frame[y:y+h, x:x+w] = pixelated_face
            
            return frame
        
        except Exception as e:
            logger.error(f"Error applying pixelation: {e}")
            return frame
    
    def draw_face_boxes(self, frame: np.ndarray, color: Tuple[int, int, int] = (0, 255, 0)) -> np.ndarray:
        """
        Draw bounding boxes around detected faces (for debugging)
        
        Args:
            frame: Input frame
            color: Box color (BGR)
            
        Returns:
            Frame with face boxes drawn
        """
        faces = self._detect_faces(frame)
        
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
            cv2.putText(
                frame,
                "Face (Blurred)",
                (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                color,
                2
            )
        
        return frame
    
    def set_enabled(self, enabled: bool):
        """Enable or disable privacy filter"""
        self.enabled = enabled
        logger.info(f"Privacy filter {'enabled' if enabled else 'disabled'}")
    
    def is_enabled(self) -> bool:
        """Check if privacy filter is enabled"""
        return self.enabled
