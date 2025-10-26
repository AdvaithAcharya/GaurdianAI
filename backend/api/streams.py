"""
Video Streams API endpoints
"""
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from typing import List
import asyncio

from models import VideoStreamConfig

router = APIRouter()


@router.post("/start")
async def start_stream(config: VideoStreamConfig, request: Request):
    """Start a new video stream"""
    try:
        video_manager = request.app.state.video_manager
        success = await video_manager.add_stream(config)
        
        if success:
            return {"message": f"Stream started for room {config.room_id}", "success": True}
        else:
            raise HTTPException(status_code=400, detail="Failed to start stream")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stop/{room_id}")
async def stop_stream(room_id: str, request: Request):
    """Stop a video stream"""
    try:
        video_manager = request.app.state.video_manager
        success = await video_manager.remove_stream(room_id)
        
        if success:
            return {"message": f"Stream stopped for room {room_id}", "success": True}
        else:
            raise HTTPException(status_code=404, detail="Stream not found")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{room_id}/frame")
async def get_stream_frame(room_id: str, request: Request):
    """Get the latest frame from a stream as JPEG"""
    try:
        video_manager = request.app.state.video_manager
        frame_bytes = video_manager.get_stream_frame(room_id)
        
        if frame_bytes:
            return StreamingResponse(
                iter([frame_bytes]),
                media_type="image/jpeg",
                headers={"Cache-Control": "no-cache"}
            )
        else:
            raise HTTPException(status_code=404, detail="No frame available")
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{room_id}/stream")
async def stream_video(room_id: str, request: Request):
    """Stream video frames as MJPEG"""
    async def generate_frames():
        video_manager = request.app.state.video_manager
        
        while True:
            try:
                frame_bytes = video_manager.get_stream_frame(room_id)
                
                if frame_bytes:
                    yield (
                        b'--frame\r\n'
                        b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n'
                    )
                
                await asyncio.sleep(0.033)  # ~30 FPS
            
            except Exception as e:
                print(f"Error streaming frame: {e}")
                break
    
    return StreamingResponse(
        generate_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )


@router.get("/")
async def get_active_streams(request: Request):
    """Get list of active streams"""
    try:
        video_manager = request.app.state.video_manager
        stream_count = video_manager.get_active_stream_count()
        
        streams = []
        for room_id in video_manager.streams.keys():
            streams.append({"room_id": room_id})
        
        return {
            "count": stream_count,
            "streams": streams
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/mobile/{room_id}/frame")
async def upload_mobile_frame(room_id: str, request: Request):
    """Receive video frame from mobile/screen capture"""
    try:
        import base64
        import numpy as np
        import cv2
        from ai import GestureDetector, FallDetector, PrivacyFilter
        from models import Alert, AlertType
        from datetime import datetime
        
        # Get JSON body with base64 encoded frame
        body = await request.json()
        frame_data = body.get('frame')
        
        if not frame_data:
            raise HTTPException(status_code=400, detail="No frame data provided")
        
        # Remove data URL prefix if present
        if 'base64,' in frame_data:
            frame_data = frame_data.split('base64,')[1]
        
        # Decode base64 to image
        img_bytes = base64.b64decode(frame_data)
        nparr = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            raise HTTPException(status_code=400, detail="Invalid image data")
        
        # Process frame directly with AI (no stream needed)
        alerts_detected = 0
        alert_manager = request.app.state.alert_manager
        
        # Initialize detectors if not in session
        if not hasattr(request.app.state, f'gesture_detector_{room_id}'):
            setattr(request.app.state, f'gesture_detector_{room_id}', GestureDetector())
            setattr(request.app.state, f'fall_detector_{room_id}', FallDetector())
            setattr(request.app.state, f'privacy_filter_{room_id}', PrivacyFilter())
            setattr(request.app.state, f'last_alert_time_{room_id}', {})
        
        gesture_detector = getattr(request.app.state, f'gesture_detector_{room_id}')
        fall_detector = getattr(request.app.state, f'fall_detector_{room_id}')
        last_alert_time = getattr(request.app.state, f'last_alert_time_{room_id}')
        
        # Gesture detection
        triggered, gesture_type, confidence = gesture_detector.detect(frame)
        if triggered:
            # Check cooldown (10 seconds)
            now = datetime.now()
            if 'gesture' not in last_alert_time or (now - last_alert_time.get('gesture', now)).seconds > 10:
                alert = Alert(
                    alert_type=AlertType.GESTURE,
                    room_id=room_id,
                    description=f"Screen Monitor: {gesture_type} gesture detected ({int(confidence*100)}% confidence)",
                    confidence=confidence
                )
                await alert_manager.create_alert(alert)
                last_alert_time['gesture'] = now
                alerts_detected += 1
        
        # Fall detection
        triggered, fall_info, confidence = fall_detector.detect(frame)
        if triggered:
            now = datetime.now()
            if 'fall' not in last_alert_time or (now - last_alert_time.get('fall', now)).seconds > 10:
                alert = Alert(
                    alert_type=AlertType.FALL,
                    room_id=room_id,
                    description=f"Screen Monitor: Fall detected - height drop: {fall_info['relative_drop']:.1%}",
                    confidence=confidence
                )
                await alert_manager.create_alert(alert)
                last_alert_time['fall'] = now
                alerts_detected += 1
        
        return {"success": True, "alerts_detected": alerts_detected}
    
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"Error processing frame: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
