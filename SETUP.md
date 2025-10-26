# GuardianAI Setup Guide

## Quick Start (Windows PowerShell)

1. **Run the automated setup script:**
   ```powershell
   .\start.ps1
   ```

This will automatically:
- Check system requirements
- Install dependencies
- Start MongoDB
- Launch backend and frontend services

## Manual Setup

### Step 1: Backend Setup

```powershell
cd backend

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
copy .env.example .env

# Edit .env with your settings
notepad .env

# Run backend
python main.py
```

### Step 2: Frontend Setup

```powershell
cd frontend

# Install dependencies
npm install

# Copy environment file
copy .env.example .env

# Run frontend
npm run dev
```

### Step 3: Access Application

- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Frontend Dashboard**: http://localhost:5173

## Optional: Download Vosk Model

For voice detection to work, download the Vosk model:

1. Visit: https://alphacephei.com/vosk/models
2. Download: `vosk-model-small-en-us-0.15`
3. Extract to: `backend/models/vosk-model-small-en-us-0.15/`

## Docker Setup (Alternative)

```powershell
# Build and start all services
docker-compose up --build

# Stop services
docker-compose down
```

## Testing the System

### 1. Create a Room
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

### 2. Add a Contact
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

### 3. Start Video Stream
Use the dashboard at http://localhost:5173

## Troubleshooting

### MongoDB Connection Error
- Ensure MongoDB is installed and running
- Check `MONGODB_URL` in backend/.env
- Alternative: Use MongoDB Atlas (cloud)

### Module Import Errors
```powershell
cd backend
pip install --upgrade -r requirements.txt
```

### Frontend Port Already in Use
```powershell
# Kill process on port 5173
netstat -ano | findstr :5173
taskkill /PID <process_id> /F

# Or change port in vite.config.js
```

### Backend Port Already in Use
```powershell
# Kill process on port 8000
netstat -ano | findstr :8000
taskkill /PID <process_id> /F
```

## Production Deployment

### Environment Variables to Set

**Backend (.env)**:
- `DEBUG=False`
- `MONGODB_URL=<production-mongodb-url>`
- `FIREBASE_CREDENTIALS_PATH=<path-to-firebase-json>`
- `TWILIO_ACCOUNT_SID=<your-sid>`
- `TWILIO_AUTH_TOKEN=<your-token>`
- `TWILIO_PHONE_NUMBER=<your-number>`

**Frontend (.env)**:
- `VITE_API_BASE_URL=<production-backend-url>`
- `VITE_WS_URL=<production-websocket-url>`

### Deployment Platforms

**Backend Options:**
- Render
- Heroku
- AWS EC2
- Google Cloud Run
- DigitalOcean

**Frontend Options:**
- Vercel
- Netlify
- AWS S3 + CloudFront
- Firebase Hosting

## Next Steps

1. ✅ Complete environment configuration
2. ✅ Setup MongoDB database
3. ✅ Configure Firebase (optional)
4. ✅ Configure Twilio (optional)
5. ✅ Test with webcam
6. ✅ Add patients and rooms
7. ✅ Start monitoring!

## Need Help?

- Check the main README.md for detailed documentation
- Review API docs at http://localhost:8000/docs
- Open an issue on GitHub

---

**Ready to save lives with AI! 🚀**
