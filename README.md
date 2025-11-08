# GuardianAI – Privacy-First Patient Distress Detection

![GuardianAI Banner](https://img.shields.io/badge/GuardianAI-Patient%20Safety-blue)
![Python](https://img.shields.io/badge/Python-3.10+-green)
![React](https://img.shields.io/badge/React-19-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)

## Overview
GuardianAI turns existing CCTV/IP camera setups into an AI-assisted patient safety system. It detects distress signals (e.g., waving) and triggers real-time alerts with optional voice-call escalation via Twilio. The UI has been fully redesigned with a full-screen dark/glassmorphic theme and a creative landing hero using WebGL (DarkVeil).

## What’s new
- Production-ready alert pipeline
  - POST /api/alert stores alert, broadcasts over WebSocket, and can trigger a Twilio call in the background
  - /status and /health endpoints expose service/db status
- AI detector integration
  - MediaPipe Pose Landmarker for simple temporal wave detection (ai_detector.py)
  - Detector can notify backend via HTTP (httpx) to create alerts
- Twilio-only voice provider
  - FreeClimb integration removed; Twilio is the exclusive provider now
  - Trial-mode notes: calls only to verified E.164 numbers
- Contacts data model hardening
  - Enforced E.164 format (e.g., +15551234567)
  - MongoDB unique index on phone_number with a partial filter (avoids null duplicates)
- Frontend creative redesign
  - New Landing with DarkVeil WebGL background (ogl) and header hidden on Landing only
  - Dashboard hub with glassmorphic cards and animated interactions
  - Uniform glassmorphism across Alerts, Contacts, Analytics, and Screen Monitoring
  - Screen Monitoring page to capture a window/screen and stream frames to backend

## Architecture (high level)
- Backend (FastAPI)
  - REST + WebSocket
  - MongoDB (Motor)
  - Optional Twilio voice call on alert
  - ai_detector.py (MediaPipe) for wave detection helper
- Frontend (React + Vite + TailwindCSS)
  - Routes: Landing (/), Dashboard (/dashboard), Alerts, Contacts, Analytics, Screen Monitoring
  - Dark/glassmorphic design and WebGL landing effect (ogl)

## Tech stack
- Backend: Python, FastAPI, Motor (MongoDB), python-dotenv, Twilio, httpx
- AI: MediaPipe (pose landmarker)
- Frontend: React 19, Vite, TailwindCSS, WebSocket, Axios, framer-motion, @heroicons/react, ogl
- Database: MongoDB (local/Atlas)

## Quick start (commands)

Backend (from repo root):
```bash
# create and activate venv
python -m venv backend/venv
# Windows PowerShell
./backend/venv/Scripts/Activate.ps1
# macOS/Linux
# source backend/venv/bin/activate

# install deps and configure env
pip install -r backend/requirements.txt
# copy sample env and edit
# Windows
copy backend\.env.sample backend\.env
# macOS/Linux
# cp backend/.env.sample backend/.env && nano backend/.env

# run API (FastAPI)
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Frontend (new terminal):
```bash
cd frontend
npm install
npm run dev
```

Alternative package managers:
```bash
# pnpmcd frontend && pnpm install && pnpm dev
# yarn
cd frontend && yarn && yarn dev
# bun
cd frontend && bun install && bun dev
```

## Installation
1) Backend
- Create venv and install requirements (see backend/requirements.txt)
- Provide .env with at least:
  - MONGODB_URL, MONGODB_DB_NAME
  - TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER (optional but required for calls)
- Start: uvicorn main:app --reload --port 8000

2) Frontend
- cd frontend
- Install deps: npm install
- Start dev: npm run dev

Note: The frontend depends on ogl (for DarkVeil) and framer-motion; both are listed in package.json.

## Configuration (backend/.env)
- Mongo
  - MONGODB_URL=mongodb://localhost:27017
  - MONGODB_DB_NAME=guardianai
- Twilio (optional for voice calls)
  - TWILIO_ACCOUNT_SID=...
  - TWILIO_AUTH_TOKEN=...
  - TWILIO_PHONE_NUMBER=+1XXXXXXXXXX
- Other
  - DEBUG, HOST, PORT, etc.

Twilio trial tips
- Only call verified E.164 numbers
- Ensure your Twilio number is voice-capable and geo-permissions allow the destination

Mongo indexes (applied at startup)
- Drop legacy index on phone (if present)
- Create unique index on phone_number with partialFilterExpression (exists, type string)

## API quick reference
- Service
  - GET /health → { db_connected: bool, ... }
  - GET /status → { twilio_configured: bool, ... }
- Alerts
  - GET /api/alerts
  - POST /api/alert { patient_id?, alert_type, details? } → creates alert, broadcasts, triggers call if configured
- Contacts
  - GET/POST /api/contacts, GET/PUT/DELETE /api/contacts/{id}
  - Server enforces E.164 for phone_number
- Streams (when enabled)
  - POST /api/streams/mobile/{session_id}/frame { frame: dataURL } → ingests a captured frame (used by Screen Monitoring)
- WebSocket
  - WS /ws → alert_* events broadcast to all subscribers

Example: create an alert
```bash
curl -X POST http://localhost:8000/api/alert \
  -H "Content-Type: application/json" \
  -d '{
    "alert_type": "wave_detected",
    "patient_id": "P-1001",
    "details": {"source": "ai_detector"}
  }'
```

## Frontend overview
- Landing (/) with DarkVeil (WebGL) hero background and CTAs; app header hidden on Landing
- Dashboard hub with glassmorphic cards to navigate features
- Alerts panel: live list powered by WebSocket and REST
- Contacts Manager: add/edit/delete, toggle active, E.164 validation
- Analytics: glassmorphic stats by status/type/day
- Screen Monitoring: capture window/screen and stream frames to backend; controls for mode and FPS

## Development
- Backend: uvicorn main:app --reload --host 0.0.0.0 --port 8000
- Frontend: npm run dev (Vite)

## Security & privacy
- Keep secrets in .env; do not commit
- Use HTTPS in production; restrict CORS
- Store only necessary alert metadata; process video locally where possible

## License
MIT

## Acknowledgments
- MediaPipe (pose/landmarker)
- FastAPI
- React + Tailwind
- Twilio
