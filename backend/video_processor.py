"""
Video Stream Processor
Handles multiple IP camera streams with AI detection
"""
import cv2
import asyncio
import numpy as np
from typing import Dict, Optional, Tuple
from datetime import datetime
import logging
from threading import Thread
import queue

from config import settings
from ai import GestureDetector, VoiceDetector, FallDetector, PrivacyFilter
from models import Alert, AlertType, VideoStreamConfig

logger = logging.getLogger(__name__)


class VideoStream:
    """Handles a single video stream"""
    
    def __init__(self, room_id: str, camera_url: str, config: VideoStreamConfig):
        self.room_id = room_id
        self.camera_url = camera_url
        self.config = config
        
        # Video capture
        self.capture = None
        self.is_running = False
        self.frame_queue = queue.Queue(maxsize=10)
        self.latest_frame = None
        self.frame_count = 0
        
        # AI detectors
        self.gesture_detector = GestureDetector() if config.enable_gesture_detection else None
        self.voice_detector = VoiceDetector() if config.enable_voice_detection else None
        self.fall_detector = FallDetector() if config.enable_fall_detection else None
        self.privacy_filter = PrivacyFilter() if config.enable_privacy_filter else None
        
        # Detection state
        self.last_alert_time = {}
        self.alert_cooldown = 10  # seconds between same type of alerts
    
    async def start(self) -> bool:
        """Start video stream capture"""
        try:
            self.capture = cv2.VideoCapture(self.camera_url)
            
            # Try to open with different backends if default fails
            if not self.capture.isOpened():
                logger.warning(f"Failed to open {self.camera_url} with default backend, trying alternatives")
                
                # Try with CAP_FFMPEG
                self.capture = cv2.VideoCapture(self.camera_url, cv2.CAP_FFMPEG)
                
                if not self.capture.isOpened():
                    logger.error(f"Failed to open camera stream: {self.camera_url}")
                    return False
            
            self.is_running = True
            logger.info(f"Video stream started for room {self.room_id}: {self.camera_url}")
            return True
        
        except Exception as e:
            logger.error(f"Error starting video stream for {self.room_id}: {e}")
            return False
    
    def stop(self):
        """Stop video stream capture"""
        self.is_running = False
        if self.capture:
            self.capture.release()
        logger.info(f"Video stream stopped for room {self.room_id}")
    
    async def read_frame(self) -> Optional[np.ndarray]:
        """Read a frame from the stream"""
        if not self.capture or not self.is_running:
            return None
        
        try:
            ret, frame = self.capture.read()
            if ret:
                self.frame_count += 1
                
                # Skip frames based on FRAME_SKIP setting
                if self.frame_count % settings.FRAME_SKIP != 0:
                    return None
                
                return frame
            else:
                logger.warning(f"Failed to read frame from {self.room_id}")
                return None
        
        except Exception as e:
            logger.error(f"Error reading frame from {self.room_id}: {e}")
            return None
    
    async def process_frame(self, frame: np.ndarray) -> Tuple[np.ndarray, list]:
        """
        Process frame with AI detection
        
        Args:
            frame: Input frame
            
        Returns:
            Tuple of (processed_frame, detected_alerts)
        """
        alerts = []
        
        try:
            # Apply privacy filter first
            if self.privacy_filter and self.config.enable_privacy_filter:
                frame = self.privacy_filter.apply(frame)
            
            # Gesture detection
            if self.gesture_detector and self.config.enable_gesture_detection:
                triggered, gesture_type, confidence = self.gesture_detector.detect(frame)
                if triggered and self._can_create_alert(AlertType.GESTURE):
                    alert = Alert(
                        alert_type=AlertType.GESTURE,
                        room_id=self.room_id,
                        description=f"Patient {gesture_type} gesture detected ({int(confidence*100)}% confidence)",
                        confidence=confidence
                    )
                    alerts.append(alert)
                    self.last_alert_time[AlertType.GESTURE] = datetime.now()
            
            # Fall detection
            if self.fall_detector and self.config.enable_fall_detection:
                triggered, fall_info, confidence = self.fall_detector.detect(frame)
                if triggered and self._can_create_alert(AlertType.FALL):
                    description = f"Fall detected - height drop: {fall_info['relative_drop']:.1%}"
                    alert = Alert(
                        alert_type=AlertType.FALL,
                        room_id=self.room_id,
                        description=description,
                        confidence=confidence
                    )
                    alerts.append(alert)
                    self.last_alert_time[AlertType.FALL] = datetime.now()
            
            # Voice detection (would need audio stream integration)
            # This is a placeholder - actual implementation would require audio extraction
            if self.voice_detector and self.config.enable_voice_detection:
                # Voice detection requires audio stream
                # For now, we'll skip it in the video processing
                pass
            
            # Store latest frame
            self.latest_frame = frame
            
            return frame, alerts
        
        except Exception as e:
            logger.error(f"Error processing frame for {self.room_id}: {e}")
            return frame, []
    
    def _can_create_alert(self, alert_type: AlertType) -> bool:
        """Check if enough time has passed since last alert of this type"""
        if alert_type not in self.last_alert_time:
            return True
        
        elapsed = (datetime.now() - self.last_alert_time[alert_type]).seconds
        return elapsed >= self.alert_cooldown
    
    def get_latest_frame_jpeg(self) -> Optional[bytes]:
        """Get latest frame as JPEG bytes"""
        if self.latest_frame is None:
            return None
        
        try:
            _, buffer = cv2.imencode('.jpg', self.latest_frame, [cv2.IMWRITE_JPEG_QUALITY, settings.VIDEO_QUALITY])
            return buffer.tobytes()
        except Exception as e:
            logger.error(f"Error encoding frame: {e}")
            return None


class VideoStreamManager:
    """Manages multiple video streams"""
    
    def __init__(self):
        self.streams: Dict[str, VideoStream] = {}
        self.is_running = False
        self.alert_callback = None
    
    async def add_stream(self, config: VideoStreamConfig) -> bool:
        """
        Add a new video stream
        
        Args:
            config: Video stream configuration
            
        Returns:
            Success status
        """
        try:
            if config.room_id in self.streams:
                logger.warning(f"Stream for room {config.room_id} already exists")
                return False
            
            if len(self.streams) >= settings.MAX_CONCURRENT_STREAMS:
                logger.error(f"Maximum concurrent streams ({settings.MAX_CONCURRENT_STREAMS}) reached")
                return False
            
            stream = VideoStream(config.room_id, config.camera_url, config)
            success = await stream.start()
            
            if success:
                self.streams[config.room_id] = stream
                logger.info(f"Stream added for room {config.room_id}")
                return True
            
            return False
        
        except Exception as e:
            logger.error(f"Error adding stream: {e}")
            return False
    
    async def remove_stream(self, room_id: str) -> bool:
        """Remove a video stream"""
        if room_id in self.streams:
            self.streams[room_id].stop()
            del self.streams[room_id]
            logger.info(f"Stream removed for room {room_id}")
            return True
        return False
    
    async def stop_all(self):
        """Stop all video streams"""
        self.is_running = False
        for stream in self.streams.values():
            stream.stop()
        self.streams.clear()
        logger.info("All video streams stopped")
    
    async def process_streams(self):
        """Main processing loop for all streams"""
        self.is_running = True
        logger.info("Video stream processing started")
        
        while self.is_running:
            try:
                # Process each stream
                for room_id, stream in list(self.streams.items()):
                    if not stream.is_running:
                        continue
                    
                    # Read frame
                    frame = await stream.read_frame()
                    if frame is None:
                        continue
                    
                    # Process frame
                    processed_frame, alerts = await stream.process_frame(frame)
                    
                    # Handle detected alerts
                    if alerts and self.alert_callback:
                        for alert in alerts:
                            await self.alert_callback(alert)
                
                # Small delay to prevent CPU overload
                await asyncio.sleep(0.01)
            
            except Exception as e:
                logger.error(f"Error in stream processing loop: {e}")
                await asyncio.sleep(1)
    
    def set_alert_callback(self, callback):
        """Set callback function for alert detection"""
        self.alert_callback = callback
    
    def get_stream(self, room_id: str) -> Optional[VideoStream]:
        """Get a specific video stream"""
        return self.streams.get(room_id)
    
    def get_active_stream_count(self) -> int:
        """Get count of active streams"""
        return len(self.streams)
    
    def get_stream_frame(self, room_id: str) -> Optional[bytes]:
        """Get latest frame from a stream as JPEG"""
        stream = self.streams.get(room_id)
        if stream:
            return stream.get_latest_frame_jpeg()
        return None
