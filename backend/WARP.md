# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

GuardianAI is a privacy-first patient distress detection system that converts existing CCTV/IP webcams into intelligent monitoring systems. The backend is a Python FastAPI application that handles AI-powered detection (gesture, voice, fall), multi-channel alerting (Firebase push + Twilio calls), and real-time video stream processing.

## Development Commands

### Environment Setup
```powershell
# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment configuration
copy .env.example .env
# Edit .env with your MongoDB URL, Firebase credentials, Twilio keys, etc.
```

### Running the Application
```powershell
# Development mode (with auto-reload)
python main.py

# Production mode (via uvicorn directly)
uvicorn main:app --host 0.0.0.0 --port 8000

# With custom host/port
uvicorn main:app --host 127.0.0.1 --port 8080
```

### Testing and API Exploration
```powershell
# Access interactive API documentation
# Navigate to: http://localhost:8000/docs (Swagger UI)
# Navigate to: http://localhost:8000/redoc (ReDoc)

# Health check
curl http://localhost:8000/health
```

### Docker
```powershell
# Build image
docker build -t guardianai-backend .

# Run container
docker run -p 8000:8000 --env-file .env guardianai-backend
```

### Database
```powershell
# Local MongoDB service (Windows)
net start MongoDB

# Connect to MongoDB shell
mongosh guardianai
```

## Architecture Overview

### Core Application Structure

**Main Application (main.py)**
- FastAPI app with lifespan management (startup/shutdown hooks)
- Global managers: `video_manager` (VideoStreamManager) and `alert_manager` (AlertManager)
- Background tasks for video processing and alert handling are started on app startup
- WebSocket support for real-time updates via ConnectionManager
- All managers are stored in `app.state` for access across routers

**Database Layer (database.py)**
- Uses Motor (async MongoDB driver) for all database operations
- Collections: `alerts`, `patients`, `rooms`, `contacts`, `alert_logs`
- Database indexes are automatically created on startup for performance
- Notable: `patients.room_id` and `rooms.room_number` have unique indexes

**Data Models (models.py)**
- Pydantic models for data validation and serialization
- Key models: Alert, Patient, Room, Contact, AlertLog, VideoStreamConfig
- AlertType enum: GESTURE, VOICE, FALL
- AlertStatus enum: ACTIVE, ACKNOWLEDGED, RESOLVED, ESCALATED

### AI Detection Pipeline

**Video Processing Flow**
1. VideoStreamManager manages multiple concurrent streams (limit: MAX_CONCURRENT_STREAMS)
2. Each VideoStream reads frames from camera URL (supports RTSP, local camera index)
3. Frame processing order: Privacy Filter → Gesture Detection → Fall Detection → Voice Detection
4. Frame skipping is controlled by FRAME_SKIP setting for performance
5. Alerts have cooldown period to prevent duplicate triggers

**AI Modules (ai/ directory)**
- `GestureDetector`: Uses MediaPipe Hands to detect wave/tap gestures. Tracks hand positions over time to identify patterns.
- `FallDetector`: Uses MediaPipe Pose to track body height. Detects sudden height drops via nose-to-ankle distance comparison.
- `VoiceDetector`: Uses Vosk for offline speech-to-text, searches for keywords in transcriptions.
- `PrivacyFilter`: Uses MediaPipe Face Detection to blur faces in video frames.

**Detection Thresholds (configurable via .env)**
- `GESTURE_THRESHOLD`: Number of consecutive gestures to trigger alert (default: 3)
- `GESTURE_TIME_WINDOW`: Seconds within which gestures must occur (default: 5)
- `FALL_HEIGHT_THRESHOLD`: Relative height drop to trigger fall alert (default: 0.3 or 30%)

### Alert Management System

**Alert Lifecycle**
1. **Creation**: AI detection triggers alert → saved to database → added to active_alerts dictionary
2. **Processing**: Background asyncio task handles escalation logic with configurable timeout
3. **Notification**: Multi-channel delivery (Firebase push + Twilio calls) based on contact priority
4. **Acknowledgment**: Staff acknowledges → escalation task cancelled → status updated to ACKNOWLEDGED
5. **Resolution**: Alert resolved → removed from active_alerts → status updated to RESOLVED

**Escalation Logic**
- Alerts escalate through contact priority levels (priority 1, 2, 3, etc.)
- Escalation timeout is controlled by `ALERT_ESCALATION_TIMEOUT` setting (default: 30 seconds)
- Maximum escalation attempts: `MAX_ESCALATION_ATTEMPTS` (default: 3)
- Each escalation sends notifications to all contacts at that priority level or lower

**Notification Channels**
- Firebase: Push notifications with alert details and metadata
- Twilio: Voice calls with TwiML script reading alert information
- Both are optional (system works without credentials)

### API Structure (api/ directory)

**Routers**
- `alerts.py`: Alert CRUD, acknowledgment, resolution, and log retrieval
- `patients.py`: Patient management with room assignment
- `rooms.py`: Room/camera configuration management
- `contacts.py`: Nurse/doctor contact management with priority system
- `streams.py`: Video stream control (start/stop), frame retrieval, MJPEG streaming

**Important Patterns**
- All routers use dependency injection via `Depends()` for database access
- MongoDB ObjectIds are converted to strings for JSON serialization
- WebSocket broadcasts are handled via `app.state.ws_manager`
- Video frames are returned as JPEG bytes with configurable quality (VIDEO_QUALITY setting)

### Configuration System

**Settings Hierarchy**
1. Default values in `config.py` (Settings class)
2. Environment variables from `.env` file (using pydantic-settings)
3. All settings accessible via `settings` singleton

**Critical Settings**
- `MONGODB_URL`: Connection string for MongoDB
- `VOSK_MODEL_PATH`: Path to downloaded Vosk speech model (must be downloaded separately)
- `ENABLE_FACE_BLUR`: Toggle privacy filter (default: True)
- `MAX_CONCURRENT_STREAMS`: Limit on simultaneous video streams (default: 10)

## Important Development Notes

### Video Stream Handling
- Camera URLs support formats: RTSP URLs (`rtsp://...`), HTTP URLs, or integer indices for local cameras (`0`, `1`)
- OpenCV backends fallback: default → CAP_FFMPEG if stream fails to open
- Latest frame is stored per stream for retrieval via API
- MJPEG streaming generates multipart/x-mixed-replace response for live video

### Alert Processing
- Alert processing runs in separate asyncio tasks per alert
- Tasks are cancelled when alerts are acknowledged to stop escalation
- `alert_manager.process_alerts()` is a keep-alive background task
- All alert actions are logged to `alert_logs` collection for audit trail

### Privacy Considerations
- Face blurring uses MediaPipe Face Detection with configurable kernel size
- No video frames are stored in database (only processed in memory)
- Only alert metadata and logs are persisted

### Firebase and Twilio Setup
- Both are optional dependencies (gracefully skipped if credentials missing)
- Firebase requires service account JSON file
- Twilio requires account SID, auth token, and phone number
- System functions without these (alerts still created, just no external notifications)

### External Dependencies to Download
- Vosk model: Download from https://alphacephei.com/vosk/models (recommend vosk-model-small-en-us-0.15)
- Extract to `models/vosk-model-small-en-us-0.15/` directory

## Common Development Workflows

### Adding a New Detection Type
1. Create detector class in `ai/` directory
2. Add initialization in `VideoStream.__init__()` (video_processor.py)
3. Add detection call in `VideoStream.process_frame()`
4. Update `AlertType` enum in models.py if needed
5. Add configuration settings to config.py

### Adding a New API Endpoint
1. Create or modify router in `api/` directory
2. Use async functions with FastAPI decorators (@router.get, @router.post, etc.)
3. Include router in main.py via `app.include_router()`
4. Access managers via `request.app.state.video_manager` or `request.app.state.alert_manager`

### Modifying Alert Escalation Logic
- Logic is in `AlertManager._process_alert()` method (alert_manager.py)
- Escalation contacts filtering in `AlertManager._send_notifications()`
- Notification sending is async and non-blocking (failures logged but don't stop escalation)

### WebSocket Broadcasting
- Use `app.state.ws_manager.broadcast(message_dict)` to send real-time updates
- All connected clients receive the message
- Connection management is handled by ConnectionManager class in main.py
