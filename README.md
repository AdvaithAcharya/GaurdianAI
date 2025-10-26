# GuardianAI – Low-Cost, Privacy-First Patient Distress Detection System

![GuardianAI Banner](https://img.shields.io/badge/GuardianAI-Patient%20Safety-blue)
![Python](https://img.shields.io/badge/Python-3.8+-green)
![React](https://img.shields.io/badge/React-18+-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 🚀 Overview

GuardianAI is a complete full-stack AI-powered patient monitoring system that converts existing CCTV/IP webcams into intelligent patient distress detection systems. It provides gesture, voice, and fall detection with real-time alerts sent to nurses and doctors via multiple channels.

### Key Features

- **🎯 Multi-Modal AI Detection**
  - Gesture detection (wave/tap) using MediaPipe
  - Voice keyword detection using Vosk (offline)
  - Fall detection using pose estimation
  
- **🔒 Privacy-First Architecture**
  - Real-time face blurring on video feeds
  - Local AI processing (no cloud storage)
  - Only alert logs stored in database

- **📱 Multi-Channel Alerts**
  - Firebase push notifications with continuous alerts
  - Twilio voice calls to landlines
  - Escalation logic with priority-based contacts
  
- **🏥 Multi-Room Support**
  - Handle multiple IP camera streams simultaneously
  - Room-based patient management
  - Concurrent video processing

- **💻 Real-Time Dashboard**
  - Live video feeds with privacy filtering
  - Active alert management
  - Alert history and logs
  - Nurse/doctor contacts management

## 📋 Table of Contents

- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)

## 🏗️ Architecture

```
GuardianAI/
├── backend/                    # Python FastAPI Backend
│   ├── ai/                    # AI Detection Modules
│   │   ├── gesture_detection.py
│   │   ├── voice_detection.py
│   │   ├── fall_detection.py
│   │   └── privacy_filter.py
│   ├── api/                   # REST API Endpoints
│   │   ├── alerts.py
│   │   ├── patients.py
│   │   ├── rooms.py
│   │   ├── contacts.py
│   │   └── streams.py
│   ├── main.py               # FastAPI Application
│   ├── config.py             # Configuration
│   ├── database.py           # MongoDB Connection
│   ├── models.py             # Data Models
│   ├── alert_manager.py      # Alert System
│   ├── video_processor.py    # Video Stream Handler
│   └── requirements.txt      # Python Dependencies
│
├── frontend/                  # React Dashboard
│   ├── src/
│   │   ├── components/       # React Components
│   │   │   ├── Dashboard.jsx
│   │   │   ├── AlertsPanel.jsx
│   │   │   ├── VideoGrid.jsx
│   │   │   ├── ContactsManager.jsx
│   │   │   └── Sidebar.jsx
│   │   ├── App.jsx          # Main App
│   │   └── index.css        # TailwindCSS Styles
│   ├── package.json
│   └── tailwind.config.js
│
├── README.md
└── .gitignore
```

### Data Flow

```
Camera Stream → AI Detection → Alert Creation → Multi-Channel Notification → Dashboard Update
                     ↓                              ↓
              Privacy Filter                  MongoDB Logging
```

## 🛠️ Tech Stack

### Backend / AI Engine
- **Python 3.8+**
- **FastAPI** - High-performance async API framework
- **OpenCV** - Video processing
- **MediaPipe** - Gesture and pose detection
- **Vosk** - Offline speech recognition
- **Motor** - Async MongoDB driver
- **Firebase Admin SDK** - Push notifications
- **Twilio** - Voice calls
- **MongoDB Atlas** - Database

### Frontend
- **React 18+** - UI framework
- **TailwindCSS v3** - Styling
- **Vite** - Build tool
- **WebSocket** - Real-time communication
- **Axios** - HTTP client

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- Node.js 16+ and npm
- MongoDB (local or Atlas)
- Git

### 1. Clone the Repository

```bash
git clone <repository-url>
cd GuardianAI
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Download Vosk model (for voice detection)
# Visit: https://alphacephei.com/vosk/models
# Download vosk-model-small-en-us-0.15
# Extract to backend/models/

# Copy environment file
copy .env.example .env

# Edit .env with your configuration
notepad .env
```

### 3. Frontend Setup

```bash
cd ../frontend

# Install dependencies
npm install

# Install additional required packages
npm install react-router-dom axios

# Copy environment file
copy .env.example .env

# Edit .env if needed
notepad .env
```

### 4. Database Setup

#### Option A: Local MongoDB

```bash
# Install MongoDB Community Edition
# Windows: https://www.mongodb.com/try/download/community
# Start MongoDB service
net start MongoDB
```

#### Option B: MongoDB Atlas (Cloud)

1. Create account at https://www.mongodb.com/cloud/atlas
2. Create a free cluster
3. Get connection string
4. Update `MONGODB_URL` in backend/.env

## ⚙️ Configuration

### Backend Configuration (backend/.env)

```env
# Application
DEBUG=True
HOST=0.0.0.0
PORT=8000

# MongoDB
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=guardianai

# Firebase (Optional - for push notifications)
FIREBASE_CREDENTIALS_PATH=path/to/firebase-credentials.json
FIREBASE_PROJECT_ID=your-project-id

# Twilio (Optional - for voice calls)
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+1234567890

# AI Detection Settings
GESTURE_THRESHOLD=3          # Number of waves to trigger alert
FALL_HEIGHT_THRESHOLD=0.3    # Height drop percentage
VOICE_KEYWORDS=["help", "nurse", "doctor", "emergency"]

# Privacy
ENABLE_FACE_BLUR=True
```

### Firebase Setup (Optional)

1. Create project at https://console.firebase.google.com/
2. Download service account key (JSON)
3. Save to backend/ directory
4. Update `FIREBASE_CREDENTIALS_PATH` in .env

### Twilio Setup (Optional)

1. Create account at https://www.twilio.com/
2. Get Account SID and Auth Token
3. Get phone number
4. Update Twilio settings in .env

## 🚀 Usage

### Start Backend

```bash
cd backend
python main.py
```

Backend will be available at: http://localhost:8000

### Start Frontend

```bash
cd frontend
npm run dev
```

Frontend will be available at: http://localhost:5173

### Access Dashboard

Navigate to http://localhost:5173 in your browser

## 📡 API Documentation

### Alerts Endpoints

```
GET    /api/alerts              # Get all alerts
GET    /api/alerts/{id}         # Get specific alert
POST   /api/alerts/{id}/acknowledge  # Acknowledge alert
POST   /api/alerts/{id}/resolve      # Resolve alert
GET    /api/alerts/{id}/logs    # Get alert logs
```

### Rooms Endpoints

```
GET    /api/rooms               # Get all rooms
POST   /api/rooms               # Create room
GET    /api/rooms/{id}          # Get specific room
PUT    /api/rooms/{id}          # Update room
DELETE /api/rooms/{id}          # Delete room
```

### Video Streams Endpoints

```
POST   /api/streams/start       # Start video stream
POST   /api/streams/stop/{room_id}  # Stop stream
GET    /api/streams/{room_id}/frame # Get latest frame
GET    /api/streams/{room_id}/stream # MJPEG stream
```

### Patients Endpoints

```
GET    /api/patients            # Get all patients
POST   /api/patients            # Create patient
GET    /api/patients/{id}       # Get patient
PUT    /api/patients/{id}       # Update patient
DELETE /api/patients/{id}       # Delete patient
```

### Contacts Endpoints

```
GET    /api/contacts            # Get all contacts
POST   /api/contacts            # Create contact
GET    /api/contacts/{id}       # Get contact
PUT    /api/contacts/{id}       # Update contact
DELETE /api/contacts/{id}       # Delete contact
```

### WebSocket

```
WS     /ws                      # Real-time updates
```

## 🏥 Testing the System

### 1. Add a Room

```bash
curl -X POST http://localhost:8000/api/rooms \
  -H "Content-Type: application/json" \
  -d '{
    "room_number": "101",
    "floor": 1,
    "camera_url": "0",
    "camera_enabled": true,
    "privacy_enabled": true
  }'
```

### 2. Start Video Stream

```bash
curl -X POST http://localhost:8000/api/streams/start \
  -H "Content-Type: application/json" \
  -d '{
    "room_id": "room_101",
    "camera_url": "0",
    "enable_gesture_detection": true,
    "enable_fall_detection": true,
    "enable_voice_detection": false,
    "enable_privacy_filter": true
  }'
```

### 3. Add a Nurse Contact

```bash
curl -X POST http://localhost:8000/api/contacts \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Nurse Jane",
    "role": "nurse",
    "phone_number": "+1234567890",
    "priority": 1,
    "active": true
  }'
```

## 📦 Deployment

### Docker Deployment

```bash
# Coming soon - Docker configurations
```

### Vercel (Frontend)

```bash
cd frontend
npm run build
vercel deploy
```

### Render (Backend)

1. Create account at https://render.com
2. Create new Web Service
3. Connect repository
4. Set build command: `pip install -r requirements.txt`
5. Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
6. Add environment variables

## 🔐 Security Considerations

- Use environment variables for sensitive data
- Enable HTTPS in production
- Use strong MongoDB passwords
- Restrict CORS origins
- Regularly update dependencies
- Keep Firebase/Twilio keys secure
- Use authentication for production

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support, please open an issue on GitHub or contact the development team.

## 🙏 Acknowledgments

- MediaPipe for gesture and pose detection
- Vosk for offline speech recognition
- OpenCV for video processing
- FastAPI for the excellent backend framework
- React and TailwindCSS for the beautiful UI

---

**Note**: This system is intended for demonstration and development purposes. For production medical use, ensure compliance with relevant healthcare regulations (HIPAA, etc.) and conduct thorough testing.
