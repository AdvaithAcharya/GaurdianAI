"""
Gesture Detection Module using MediaPipe
Detects hand waves and taps to trigger alerts
"""
import cv2
import mediapipe as mp
import numpy as np
from typing import Optional, Tuple, List
from collections import deque
from datetime import datetime, timedelta
import logging

from config import settings

logger = logging.getLogger(__name__)


class GestureDetector:
    """Detects hand gestures (wave, tap) using MediaPipe"""
    
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils
        
        # Gesture tracking
        self.gesture_history = deque(maxlen=30)  # Track last 30 frames
        self.wave_count = 0
        self.last_wave_time = None
        self.wave_direction = None
        
        # Configuration
        self.gesture_threshold = settings.GESTURE_THRESHOLD
        self.time_window = settings.GESTURE_TIME_WINDOW
        
    def detect(self, frame: np.ndarray) -> Tuple[bool, Optional[str], float]:
        """
        Detect gestures in a frame
        
        Args:
            frame: Input video frame (BGR format)
            
        Returns:
            Tuple of (alert_triggered, gesture_type, confidence)
        """
        # Convert to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        
        alert_triggered = False
        gesture_type = None
        confidence = 0.0
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Get wrist position
                wrist = hand_landmarks.landmark[self.mp_hands.HandLandmark.WRIST]
                x, y = wrist.x, wrist.y
                
                # Track hand movement
                self.gesture_history.append((x, y, datetime.now()))
                
                # Check for wave gesture
                is_wave, wave_conf = self._detect_wave()
                if is_wave:
                    self.wave_count += 1
                    self.last_wave_time = datetime.now()
                    
                    # Check if threshold reached
                    if self.wave_count >= self.gesture_threshold:
                        alert_triggered = True
                        gesture_type = "wave"
                        confidence = wave_conf
                        self.wave_count = 0  # Reset counter
                        logger.info(f"Wave gesture detected: {self.gesture_threshold} waves")
                
                # Check for tap gesture (hand moving up and down quickly)
                is_tap, tap_conf = self._detect_tap()
                if is_tap:
                    alert_triggered = True
                    gesture_type = "tap"
                    confidence = tap_conf
                    logger.info("Tap gesture detected")
        
        # Reset wave count if time window expired
        if self.last_wave_time and (datetime.now() - self.last_wave_time).seconds > self.time_window:
            self.wave_count = 0
            
        return alert_triggered, gesture_type, confidence
    
    def _detect_wave(self) -> Tuple[bool, float]:
        """Detect horizontal waving motion"""
        if len(self.gesture_history) < 10:
            return False, 0.0
        
        # Get recent positions
        recent_positions = list(self.gesture_history)[-10:]
        x_positions = [pos[0] for pos in recent_positions]
        
        # Calculate horizontal movement
        x_range = max(x_positions) - min(x_positions)
        
        # Check for significant horizontal movement (wave)
        if x_range > 0.15:  # Threshold for wave detection
            # Check for direction change (left-right-left or right-left-right)
            direction_changes = 0
            for i in range(1, len(x_positions)):
                if i > 1:
                    prev_dir = x_positions[i-1] - x_positions[i-2]
                    curr_dir = x_positions[i] - x_positions[i-1]
                    if prev_dir * curr_dir < 0:  # Direction changed
                        direction_changes += 1
            
            # Wave detected if there's at least one direction change
            if direction_changes >= 1:
                confidence = min(0.95, 0.6 + (x_range * 2))
                return True, confidence
        
        return False, 0.0
    
    def _detect_tap(self) -> Tuple[bool, float]:
        """Detect vertical tapping motion"""
        if len(self.gesture_history) < 15:
            return False, 0.0
        
        # Get recent positions
        recent_positions = list(self.gesture_history)[-15:]
        y_positions = [pos[1] for pos in recent_positions]
        times = [pos[2] for pos in recent_positions]
        
        # Calculate vertical movement speed
        y_diff = abs(y_positions[-1] - y_positions[0])
        time_diff = (times[-1] - times[0]).total_seconds()
        
        if time_diff > 0:
            speed = y_diff / time_diff
            
            # Detect rapid vertical movement
            if speed > 0.5 and y_diff > 0.1:
                confidence = min(0.9, 0.5 + speed)
                return True, confidence
        
        return False, 0.0
    
    def draw_landmarks(self, frame: np.ndarray) -> np.ndarray:
        """Draw hand landmarks on frame for visualization"""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(
                    frame,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS
                )
        
        return frame
    
    def reset(self):
        """Reset gesture detection state"""
        self.gesture_history.clear()
        self.wave_count = 0
        self.last_wave_time = None
        self.wave_direction = None
    
    def __del__(self):
        """Cleanup resources"""
        if hasattr(self, 'hands'):
            self.hands.close()
