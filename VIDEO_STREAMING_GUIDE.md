# GuardianAI Video Streaming Guide

## ✅ Implementation Complete!

The video streaming feature has been fully implemented with support for:
- ✅ CCTV/IP Camera streaming (RTSP, HTTP)
- ✅ Local webcam support
- ✅ Mobile device camera streaming
- ✅ Real-time AI detection on all video sources
- ✅ MJPEG live streaming to dashboard
- ✅ Stream control (start/stop) from web interface

---

## 🎥 Features

### 1. **Video Grid Dashboard**
- Live MJPEG video feeds from all active cameras
- Start/Stop streaming controls
- Real-time stream status indicators
- Privacy filter indication
- Supports multiple concurrent streams

### 2. **Rooms Management**
- Add/Edit/Delete rooms
- Configure camera URLs (RTSP, HTTP, webcam, mobile)
- Enable/disable camera and privacy filters
- Quick setup buttons for webcam and mobile cameras

### 3. **Mobile Camera Streaming**
- Stream from any mobile device (phone/tablet)
- Works with front or rear camera
- Adjustable frame rate (5-30 FPS)
- Real-time statistics (frames sent, alerts detected)
- Two access methods:
  - Integrated page in main dashboard (`/mobile-camera`)
  - Standalone HTML page for easy mobile access

---

## 🚀 Quick Start Guide

### Step 1: Start the Backend

```powershell
cd C:\Users\hp\GuardianAI\backend
python main.py
```

Backend will be running at: `http://localhost:8000`

### Step 2: Start the Frontend

```powershell
cd C:\Users\hp\GuardianAI\frontend
npm run dev
```

Frontend will be running at: `http://localhost:5173`

### Step 3: Add a Room

1. Navigate to **Rooms** page (`http://localhost:5173/rooms`)
2. Click **"Add Room"**
3. Choose one of these options:

#### Option A: Use Webcam (for testing)
- Room Number: `101`
- Camera URL: Click **"Use Webcam (0)"** button
- Enable Camera: ✅
- Enable Privacy Filter: ✅
- Click **"Create Room"**

#### Option B: Use IP Camera (CCTV)
- Room Number: `102`
- Camera URL: `rtsp://192.168.1.100:554/stream` (your camera URL)
- Enable Camera: ✅
- Enable Privacy Filter: ✅
- Click **"Create Room"**

#### Option C: Use Mobile Device
- Room Number: `103`
- Camera URL: Click **"Use Mobile Camera"** button (sets to `mobile`)
- Enable Camera: ✅
- Enable Privacy Filter: ✅
- Click **"Create Room"**

### Step 4: View Live Feeds

1. Navigate to **Video Feeds** page (`http://localhost:5173/video`)
2. You'll see all configured rooms
3. Click **"Start"** on any room to begin streaming
4. Live video will appear with AI detection running

---

## 📱 Mobile Camera Streaming

There are **2 ways** to stream from a mobile device:

### Method 1: Main Dashboard (Recommended for Desktop/Laptop)
1. Go to `http://localhost:5173/mobile-camera`
2. Select the room configured for mobile streaming
3. Adjust frame rate if needed
4. Click **"Start Streaming"**
5. Allow camera access when prompted
6. Video will be processed with AI detection

### Method 2: Standalone HTML Page (Recommended for Mobile Devices)
1. On your mobile device, open a browser
2. Navigate to: `http://localhost:5173/mobile-stream.html`
   - Replace `localhost` with your computer's IP if on same network
   - Example: `http://192.168.1.100:5173/mobile-stream.html`
3. Enter backend URL (e.g., `http://192.168.1.100:8000`)
4. Select room from dropdown
5. Choose frame rate (10 FPS is good balance)
6. Tap **"Start Streaming"**
7. Allow camera access
8. Keep the page open while streaming

---

## 🔧 Configuration Options

### Camera URL Formats

| Camera Type | URL Format | Example |
|-------------|------------|---------|
| Local Webcam | `0`, `1`, `2` | `0` |
| RTSP Camera | `rtsp://ip:port/path` | `rtsp://192.168.1.100:554/stream` |
| HTTP Stream | `http://ip:port/path` | `http://192.168.1.100:8080/video` |
| Mobile Device | `mobile` | `mobile` |

### Frame Rate Recommendations

| FPS | Use Case | Bandwidth |
|-----|----------|-----------|
| 5-10 FPS | Low bandwidth, basic monitoring | Low |
| 10-15 FPS | Balanced detection & performance | Medium |
| 15-30 FPS | High accuracy, fast movements | High |

### Privacy Filter
- **Enabled**: Blurs faces in real-time using MediaPipe
- **Disabled**: Shows raw video feed
- Can be toggled per room

---

## 🏥 Demo Setup Example

Here's a complete example setup for demonstration:

### Room 1: Desk Monitor (Webcam)
```
Room Number: 101
Camera URL: 0
Camera Enabled: ✅
Privacy Enabled: ✅
```
**Purpose**: Monitor patient at desk using laptop webcam

### Room 2: Mobile Monitoring (Phone)
```
Room Number: 102
Camera URL: mobile
Camera Enabled: ✅
Privacy Enabled: ✅
```
**Purpose**: Use phone as mobile camera to monitor bed-bound patient

### Room 3: IP Camera (CCTV)
```
Room Number: 103
Camera URL: rtsp://192.168.1.100:554/stream
Camera Enabled: ✅
Privacy Enabled: ✅
```
**Purpose**: Permanent CCTV monitoring of patient room

---

## 🎯 Testing the System

### Test Gesture Detection
1. Start a video stream
2. Wave your hand 3 times in front of camera
3. Check Dashboard → you should see a new alert
4. Alert will show: "Patient wave gesture detected"

### Test Fall Detection
1. Start a video stream
2. Sit or stand in front of camera (establish baseline height)
3. Quickly crouch down or lie on floor
4. Alert should trigger: "Fall detected"

### Test Mobile Streaming
1. Create mobile room
2. Open mobile streaming page on phone
3. Start streaming
4. Wave at phone camera
5. Check dashboard on computer for alerts

---

## 🔗 Network Configuration

### For Same Network Streaming

If your mobile device and computer are on the same WiFi:

1. Find your computer's IP address:
```powershell
ipconfig
```
Look for `IPv4 Address` under your active network adapter

2. Update backend URL on mobile device:
```
http://YOUR_COMPUTER_IP:8000
```
Example: `http://192.168.1.50:8000`

3. Access frontend from mobile:
```
http://YOUR_COMPUTER_IP:5173
```

### Firewall Configuration

If streaming doesn't work, ensure Windows Firewall allows:
- Port 8000 (Backend)
- Port 5173 (Frontend - dev server)

```powershell
# Allow ports (run as Administrator)
New-NetFirewallRule -DisplayName "GuardianAI Backend" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
New-NetFirewallRule -DisplayName "GuardianAI Frontend" -Direction Inbound -LocalPort 5173 -Protocol TCP -Action Allow
```

---

## 🎨 User Interface Guide

### Video Grid Page
- **Green Badge "LIVE"**: Stream is active
- **Gray Badge "Offline"**: Stream is stopped
- **Blue Badge "Privacy On"**: Face blurring enabled
- **Start Button**: Begin streaming and AI detection
- **Stop Button**: End streaming

### Rooms Management Page
- **Green "Mobile" Badge**: Mobile camera room
- **Blue "Webcam" Badge**: Local webcam
- **Status Enabled/Disabled**: Camera active state
- **Privacy On/Off**: Privacy filter state
- **Edit**: Modify room configuration
- **Delete**: Remove room

### Mobile Camera Page
- **Frame Counter**: Total frames sent to backend
- **Alert Counter**: Number of AI detections
- **FPS Slider**: Adjust streaming speed
- **Pulsing Red Dot**: Active streaming indicator

---

## 🔍 Troubleshooting

### Video not showing on dashboard
- Check if stream is started (green "LIVE" badge)
- Verify backend is running (`http://localhost:8000/health`)
- Check browser console for errors
- Try refreshing the page

### Mobile streaming not working
- Ensure room is created with `camera_url: mobile`
- Verify backend URL is correct
- Check network connectivity
- Allow camera permissions in browser
- Make sure backend can receive requests from mobile IP

### Camera not detected
- For webcam: Try camera index `1` or `2` instead of `0`
- For RTSP: Verify camera URL with VLC player first
- For mobile: Check if room is configured correctly

### Low frame rate
- Reduce FPS setting on mobile
- Check network bandwidth
- Reduce VIDEO_QUALITY in backend `.env` (default: 50)

### High CPU usage
- Reduce number of concurrent streams
- Increase FRAME_SKIP in backend `.env` (default: 2)
- Lower FPS on mobile streams
- Disable privacy filter if not needed

---

## 🎓 Advanced Usage

### Custom RTSP Camera Configuration
```python
# Common RTSP URL formats:
# Hikvision: rtsp://username:password@ip:554/Streaming/Channels/101
# Dahua: rtsp://username:password@ip:554/cam/realmonitor?channel=1&subtype=0
# Generic: rtsp://ip:554/stream1
```

### Multiple Mobile Devices
1. Create separate rooms for each mobile device
2. Use different room numbers (e.g., Mobile-1, Mobile-2)
3. Each device opens the streaming page
4. Select their respective room
5. All streams appear on Video Grid page

### Integration with Existing CCTV
1. Get RTSP URL from your CCTV system
2. Test URL with VLC: `Media > Open Network Stream`
3. Add room with tested RTSP URL
4. Start stream on Video Grid page

---

## 📊 Performance Specs

| Metric | Value |
|--------|-------|
| Max Concurrent Streams | 10 (configurable) |
| Video Quality | 50% JPEG (configurable) |
| Frame Skip | Every 2nd frame (configurable) |
| Privacy Filter | Real-time MediaPipe |
| Gesture Detection | MediaPipe Hands |
| Fall Detection | MediaPipe Pose |
| Latency | < 1 second |

---

## 🎉 What's Working

✅ Live MJPEG streaming from all camera types
✅ Real-time AI detection on video streams
✅ Mobile camera streaming with configurable FPS
✅ Standalone mobile streaming page
✅ Room management with CRUD operations
✅ Start/stop streaming controls
✅ Privacy filter (face blurring)
✅ Multi-camera support (up to 10 streams)
✅ WebSocket real-time alerts
✅ Alert acknowledgment system
✅ MongoDB Atlas data persistence

---

## 🚀 Next Steps

1. **Test with Real Patients**: Deploy in actual hospital/care environment
2. **Add Authentication**: Secure access with login system
3. **Setup Firebase**: Enable push notifications to staff phones
4. **Setup Twilio**: Enable voice call alerts
5. **Download Vosk Model**: Enable voice keyword detection
6. **Production Deployment**: Deploy to cloud (Render, AWS, etc.)

---

## 📞 Support

For issues or questions:
1. Check console logs (browser and backend)
2. Verify all services are running
3. Review `.env` configuration
4. Check network connectivity
5. Ensure MongoDB Atlas is accessible

---

**Congratulations!** 🎉 Your GuardianAI video streaming system is now fully operational!
