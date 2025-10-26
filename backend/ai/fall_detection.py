"""
Fall Detection Module using Pose Estimation
Detects sudden height drops indicating falls
"""
import cv2
import mediapipe as mp
import numpy as np
from typing import Optional, Tuple
from collections import deque
from datetime import datetime, timedelta
import logging

from config import settings

logger = logging.getLogger(__name__)


class FallDetector:
    """Detects patient falls using pose estimation"""
    
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils
        
        # Fall detection tracking
        self.height_history = deque(maxlen=30)  # Track last 30 frames
        self.baseline_height = None
        self.fall_detected_time = None
        self.in_fall_state = False
        
        # Configuration
        self.height_threshold = settings.FALL_HEIGHT_THRESHOLD
        self.confirmation_frames = 5  # Frames to confirm fall
        self.fall_cooldown = 5  # Seconds before detecting another fall
        
    def detect(self, frame: np.ndarray) -> Tuple[bool, Optional[dict], float]:
        """
        Detect falls in a frame
        
        Args:
            frame: Input video frame (BGR format)
            
        Returns:
            Tuple of (alert_triggered, fall_info, confidence)
        """
        # Convert to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(rgb_frame)
        
        alert_triggered = False
        fall_info = None
        confidence = 0.0
        
        if results.pose_landmarks:
            # Calculate person's height in frame
            landmarks = results.pose_landmarks.landmark
            
            # Use nose and ankle landmarks to estimate height
            nose = landmarks[self.mp_pose.PoseLandmark.NOSE]
            left_ankle = landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE]
            right_ankle = landmarks[self.mp_pose.PoseLandmark.RIGHT_ANKLE]
            
            # Get average ankle position
            ankle_y = (left_ankle.y + right_ankle.y) / 2
            
            # Calculate relative height (nose to ankle)
            current_height = abs(ankle_y - nose.y)
            
            # Track height history
            self.height_history.append({
                'height': current_height,
                'timestamp': datetime.now()
            })
            
            # Establish baseline height
            if self.baseline_height is None and len(self.height_history) > 10:
                heights = [h['height'] for h in self.height_history]
                self.baseline_height = np.median(heights)
                logger.info(f"Baseline height established: {self.baseline_height:.3f}")
            
            # Detect fall
            if self.baseline_height is not None:
                height_drop = self.baseline_height - current_height
                relative_drop = height_drop / self.baseline_height
                
                # Check if height dropped significantly
                if relative_drop > self.height_threshold:
                    # Confirm fall over multiple frames
                    recent_drops = self._count_recent_drops()
                    
                    if recent_drops >= self.confirmation_frames and not self.in_fall_state:
                        # Check cooldown
                        if self._is_cooldown_expired():
                            alert_triggered = True
                            self.in_fall_state = True
                            self.fall_detected_time = datetime.now()
                            
                            # Calculate confidence based on drop magnitude
                            confidence = min(0.95, 0.6 + (relative_drop * 2))
                            
                            fall_info = {
                                'height_drop': height_drop,
                                'relative_drop': relative_drop,
                                'baseline_height': self.baseline_height,
                                'current_height': current_height,
                                'nose_position': (nose.x, nose.y),
                                'ankle_position': (ankle_y,)
                            }
                            
                            logger.warning(
                                f"FALL DETECTED! Drop: {relative_drop:.2%} "
                                f"(from {self.baseline_height:.3f} to {current_height:.3f})"
                            )
                
                # Reset fall state if person stands up
                if self.in_fall_state and relative_drop < 0.1:
                    self.in_fall_state = False
                    logger.info("Person appears to have stood up")
                    
                    # Recalibrate baseline
                    self.baseline_height = None
                    self.height_history.clear()
        
        else:
            # No pose detected - person might be out of frame or fallen
            if len(self.height_history) > 0:
                logger.debug("No pose detected in frame")
        
        return alert_triggered, fall_info, confidence
    
    def _count_recent_drops(self) -> int:
        """Count how many recent frames show height drop"""
        if len(self.height_history) < self.confirmation_frames:
            return 0
        
        recent_frames = list(self.height_history)[-self.confirmation_frames:]
        drop_count = 0
        
        for frame_data in recent_frames:
            height = frame_data['height']
            if self.baseline_height - height > self.height_threshold * self.baseline_height:
                drop_count += 1
        
        return drop_count
    
    def _is_cooldown_expired(self) -> bool:
        """Check if cooldown period has expired"""
        if self.fall_detected_time is None:
            return True
        
        elapsed = (datetime.now() - self.fall_detected_time).seconds
        return elapsed > self.fall_cooldown
    
    def draw_landmarks(self, frame: np.ndarray) -> np.ndarray:
        """Draw pose landmarks on frame for visualization"""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(rgb_frame)
        
        if results.pose_landmarks:
            self.mp_draw.draw_landmarks(
                frame,
                results.pose_landmarks,
                self.mp_pose.POSE_CONNECTIONS,
                landmark_drawing_spec=self.mp_draw.DrawingSpec(
                    color=(0, 255, 0), thickness=2, circle_radius=2
                ),
                connection_drawing_spec=self.mp_draw.DrawingSpec(
                    color=(0, 255, 0), thickness=2
                )
            )
            
            # Draw height indicator
            if self.baseline_height is not None:
                h, w = frame.shape[:2]
                cv2.putText(
                    frame,
                    f"Baseline: {self.baseline_height:.3f}",
                    (10, h - 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0),
                    2
                )
        
        return frame
    
    def reset(self):
        """Reset fall detection state"""
        self.height_history.clear()
        self.baseline_height = None
        self.fall_detected_time = None
        self.in_fall_state = False
    
    def __del__(self):
        """Cleanup resources"""
        if hasattr(self, 'pose'):
            self.pose.close()
