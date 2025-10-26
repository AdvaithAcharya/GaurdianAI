# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

GuardianAI is a privacy-first patient distress detection system that converts existing CCTV/IP cameras into intelligent patient monitoring systems. It uses real-time AI detection (gesture, voice, fall) with multi-channel alerting (Firebase push notifications, Twilio voice calls) and privacy filtering.

**Core Technologies:**
- Backend: Python 3.8+, FastAPI, Motor (async MongoDB), OpenCV, MediaPipe, Vosk
- Frontend: React 18+, Vite, TailwindCSS
- Database: MongoDB
- AI: MediaPipe (gesture/pose), Vosk (offline speech), OpenCV (video processing)

## Development Commands

### Backend (Python/FastAPI)

**Setup:**
```powershell
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

**Run:**
```powershell
cd backend
python main.py
```
Backend runs on `http://localhost:8000`. API docs at `http://localhost:8000/docs`.

**No automated tests are currently configured.** Run manual testing via API endpoints.

### Frontend (React/Vite)

**Setup:**
```powershell
cd frontend
npm install
copy .env.example .env  # If exists
```

**Run:**
```powershell
cd frontend
npm run dev
```
Frontend runs on `http://localhost:5173`.

**Build:**
```powershell
cd frontend
npm run build
```

**Lint:**
```powershell
cd frontend
npm run lint
```

### Full Stack

**Quick start (Windows PowerShell):**
```powershell
.\start.ps1
```
This automated script checks prerequisites, installs dependencies, and starts both backend and frontend in separate PowerShell windows.

**Docker (Alternative):**
```powershell
docker-compose up --build
docker-compose down
```

### Database

**Local MongoDB:**
- Ensure MongoDB is installed and running: `net start MongoDB`
- Default connection: `mongodb://localhost:27017`
- Database name: `guardianai`

**MongoDB Atlas (Cloud alternative):**
- Update `MONGODB_URL` in `backend/.env`

## Architecture Overview

### System Flow

```
Camera Stream → VideoStreamManager → AI Detectors → AlertManager → Multi-Channel Notifications
                      ↓                                     ↓
                Privacy Filter                         Database (MongoDB)
                      ↓
              WebSocket → Dashboard
```

### Backend Architecture

**Core Components:**
- `main.py`: FastAPI application entry point, WebSocket management, lifespan handlers
- `video_processor.py`: `VideoStreamManager` orchestrates multiple `VideoStream` instances (one per room/camera)
- `alert_manager.py`: `AlertManager` handles alert lifecycle, escalation logic, Firebase/Twilio notifications
- `database.py`: MongoDB async connection manager using Motor
- `config.py`: Pydantic settings loaded from `.env`
- `models.py`: Pydantic models for all data structures

**AI Detection Modules (`backend/ai/`):**
- `gesture_detection.py`: MediaPipe Hands - detects waves/taps, tracks gesture history over time
- `fall_detection.py`: MediaPipe Pose - detects sudden height drops, establishes baseline height per person
- `voice_detection.py`: Vosk offline speech recognition - detects configurable keywords
- `privacy_filter.py`: Real-time face blurring using OpenCV

**API Routes (`backend/api/`):**
- `alerts.py`: Alert CRUD, acknowledgment, resolution endpoints
- `patients.py`: Patient management
- `rooms.py`: Room/camera configuration
- `contacts.py`: Nurse/doctor contact management
- `streams.py`: Video stream control (start/stop streams, get frames)

### Key Design Patterns

**Async Processing:**
- Video processing runs in background tasks (`asyncio.create_task`) started during FastAPI lifespan
- Each `VideoStream` reads frames, processes with AI detectors, generates alerts
- `AlertManager.process_alerts()` runs continuously, handling escalation logic

**Alert Escalation:**
1. Alert created → saved to DB → added to `active_alerts`
2. Background task sends notifications to contacts (sorted by priority)
3. Waits `ALERT_ESCALATION_TIMEOUT` seconds
4. If not acknowledged, escalates to next priority level
5. Repeats up to `MAX_ESCALATION_ATTEMPTS` times
6. Acknowledgment cancels escalation task

**State Management:**
- `VideoStreamManager.streams`: Dict[room_id, VideoStream] - tracks all active video streams
- `AlertManager.active_alerts`: Dict[alert_id, Alert] - tracks unresolved alerts
- AI detectors maintain internal state (gesture history, baseline height) for temporal detection

**Privacy Architecture:**
- Face detection/blurring applied BEFORE any display or storage
- Only alert metadata stored in database (no video/images)
- Privacy filter optional per-room configuration

### Frontend Architecture

**Not fully examined** but based on README:
- React components in `src/components/`: Dashboard, AlertsPanel, VideoGrid, ContactsManager, Sidebar
- WebSocket connection to `/ws` for real-time updates
- REST API calls via Axios to backend endpoints

## Configuration

### Backend Environment Variables (`.env`)

**Critical settings:**
- `MONGODB_URL`: Database connection string
- `FIREBASE_CREDENTIALS_PATH`: Path to Firebase service account JSON (optional, for push notifications)
- `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_PHONE_NUMBER`: For voice calls (optional)

**AI Detection tuning:**
- `GESTURE_THRESHOLD`: Number of waves/taps to trigger alert (default: 3)
- `GESTURE_TIME_WINDOW`: Time window in seconds for gesture counting (default: 5)
- `FALL_HEIGHT_THRESHOLD`: Relative height drop percentage to trigger fall alert (default: 0.3 = 30%)
- `VOICE_KEYWORDS`: List of keywords for voice detection

**Video processing:**
- `MAX_CONCURRENT_STREAMS`: Maximum simultaneous camera streams (default: 10)
- `FRAME_SKIP`: Process every Nth frame to reduce CPU load (default: 2)
- `VIDEO_QUALITY`: JPEG quality for streaming 0-100 (default: 50)

**Privacy:**
- `ENABLE_FACE_BLUR`: Global privacy filter toggle (default: True)

### Vosk Model Setup

Voice detection requires downloading the Vosk model:
1. Visit: https://alphacephei.com/vosk/models
2. Download: `vosk-model-small-en-us-0.15`
3. Extract to: `backend/models/vosk-model-small-en-us-0.15/`
4. Update `VOSK_MODEL_PATH` in `.env` if different

## Common Development Patterns

### Adding a New AI Detector

1. Create detector class in `backend/ai/` with `detect(frame) -> (triggered, info, confidence)` method
2. Add detector initialization in `VideoStream.__init__()` based on config flag
3. Add detection call in `VideoStream.process_frame()`
4. Add configuration option to `VideoStreamConfig` model in `models.py`
5. Update API endpoint in `streams.py` to accept new config parameter

### Adding a New API Endpoint

1. Create/update router in `backend/api/`
2. Use existing patterns: async functions, database access via `database.get_collection()`
3. Include router in `main.py`: `app.include_router(your_router, prefix="/api/...", tags=["..."])`
4. Models defined in `models.py`, use Pydantic validation

### Working with Alerts

**Creating alerts:**
```python
from models import Alert, AlertType
alert = Alert(
    alert_type=AlertType.GESTURE,
    room_id="room_101",
    description="Patient waved 3 times",
    confidence=0.95
)
alert_id = await alert_manager.create_alert(alert)
```

**Acknowledging alerts:**
```python
await alert_manager.acknowledge_alert(alert_id, "Nurse Jane")
```

### Managing Video Streams

**Starting a stream:**
```python
from models import VideoStreamConfig
config = VideoStreamConfig(
    room_id="room_101",
    camera_url="0",  # 0 for webcam, or RTSP URL
    enable_gesture_detection=True,
    enable_fall_detection=True,
    enable_privacy_filter=True
)
await video_manager.add_stream(config)
```

**Stopping a stream:**
```python
await video_manager.remove_stream("room_101")
```

## Testing the System

### API Testing (PowerShell)

**Create a room:**
```powershell
curl -X POST http://localhost:8000/api/rooms `
  -H "Content-Type: application/json" `
  -d '{
    "room_number": "101",
    "floor": 1,
    "camera_url": "0",
    "camera_enabled": true,
    "privacy_enabled": true
  }'
```

**Start video stream:**
```powershell
curl -X POST http://localhost:8000/api/streams/start `
  -H "Content-Type: application/json" `
  -d '{
    "room_id": "room_101",
    "camera_url": "0",
    "enable_gesture_detection": true,
    "enable_fall_detection": true,
    "enable_voice_detection": false,
    "enable_privacy_filter": true
  }'
```

**Add contact:**
```powershell
curl -X POST http://localhost:8000/api/contacts `
  -H "Content-Type: application/json" `
  -d '{
    "name": "Nurse Jane",
    "role": "nurse",
    "phone_number": "+1234567890",
    "priority": 1,
    "active": true
  }'
```

### Manual Testing with Webcam

1. Start backend and frontend
2. Use dashboard at `http://localhost:5173`
3. Create a room with camera_url="0" (default webcam)
4. Start stream via dashboard
5. Perform gestures (wave hand) or simulate fall to trigger alerts

## Important Notes

- **No authentication/authorization** is implemented - add before production use
- **HIPAA compliance**: System stores only alert metadata, not video. Ensure compliance for medical use
- **Camera URLs**: Use "0" for webcam, RTSP URLs for IP cameras (format: `rtsp://username:password@ip:port/stream`)
- **Resource usage**: Each stream consumes CPU for AI processing. Adjust `FRAME_SKIP` and `MAX_CONCURRENT_STREAMS` based on hardware
- **Alert cooldown**: Detectors have built-in cooldowns (10s for gestures, 5s for falls) to prevent duplicate alerts
- **Baseline calibration**: Fall detector requires ~10 frames to establish baseline height - patient should be upright initially

## Troubleshooting

**MongoDB connection errors:**
- Check MongoDB is running: `Get-Service MongoDB` (Windows)
- Verify `MONGODB_URL` in `.env`
- Use MongoDB Atlas as alternative

**OpenCV/MediaPipe errors:**
- Ensure camera is not in use by another application
- Try different camera_url values (0, 1, 2) for different cameras
- Check camera permissions

**Import errors:**
```powershell
cd backend
pip install --upgrade -r requirements.txt
```

**Port conflicts:**
- Backend (8000): `netstat -ano | findstr :8000`, then `taskkill /PID <pid> /F`
- Frontend (5173): `netstat -ano | findstr :5173`, then `taskkill /PID <pid> /F`

**Firebase/Twilio not working:**
- These are optional - system works without them
- Logs will show warnings if credentials missing
- Alerts will still be visible in dashboard via WebSocket
