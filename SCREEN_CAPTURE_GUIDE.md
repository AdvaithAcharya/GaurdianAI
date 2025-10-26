# Screen Capture Monitoring Guide

## ✅ NEW FEATURE: Monitor Any CCTV App!

You can now monitor video from **any CCTV app, video player, or screen window** with AI detection!

---

## 🎯 What This Does

Instead of connecting directly to cameras, **capture your screen** where CCTV footage is playing:

- Open your existing CCTV monitoring app
- Start screen capture in GuardianAI
- AI analyzes the captured video feed
- Alerts generated when gestures/falls detected

**Benefits:**
- ✅ Works with **any CCTV software** (no integration needed)
- ✅ Monitor **existing security systems** without changing setup
- ✅ Capture **video files or playback** for testing
- ✅ Monitor **multiple cameras** displayed on screen

---

## 🚀 Quick Start

### Step 1: Create Screen Capture Room

1. Go to: `http://localhost:5173/rooms`
2. Click **"Add Room"**
3. Room Number: `Screen-Room`
4. Click **"🖥️ Screen Capture"** button
5. Click **"Create Room"**

### Step 2: Start Screen Capture

1. **Open your CCTV app/video** in another window
   - Can be: VLC, CCTV app, security software, YouTube video, etc.
2. Go to: `http://localhost:5173/screen-capture`
3. Select your screen room from dropdown
4. Choose capture mode:
   - **Entire Screen**: Captures everything on your screen
   - **Specific Window**: Captures just one app/window
5. Click **"🎥 Start Screen Capture"**
6. Browser will ask what to share:
   - Select **"Entire Screen"** or **"Window"**
   - Select your CCTV app window
   - Click **"Share"**
7. **AI monitoring starts automatically!**

---

## 📺 Use Cases

### 1. **Monitor Existing CCTV System**
```
Scenario: Hospital has old CCTV system with monitoring software
Solution: 
- Open existing CCTV monitoring app
- Use Screen Capture to monitor it with AI
- No need to change existing setup!
```

### 2. **Test with Video Files**
```
Scenario: Want to test detection with sample videos
Solution:
- Play patient video in VLC/YouTube
- Capture that window
- Test gesture/fall detection
```

### 3. **Monitor Multiple Cameras**
```
Scenario: CCTV app shows 4 cameras in grid view
Solution:
- Capture entire screen
- AI monitors all 4 camera feeds at once
- Single alert system for all
```

### 4. **Temporary Monitoring**
```
Scenario: Need quick setup without camera configuration  
Solution:
- Use phone to record video call/stream
- Display on computer
- Capture that window
```

---

## 🎮 Demo Walkthrough

### Test with YouTube Video

1. **Create Screen Room** (Steps above)

2. **Open YouTube video:**
   - Search: "patient in hospital bed"
   - Play any patient monitoring demo video
   - Make it fullscreen or windowed

3. **Start Screen Capture:**
   - GuardianAI → Screen Capture page
   - Choose "Specific Window"
   - Click Start
   - Select YouTube window
   - Click Share

4. **Test Detection:**
   - Find video with hand movements
   - AI will detect gestures
   - Check Alerts page for detections!

---

## 💡 Tips & Best Practices

### For Best Results:

**Video Quality:**
- ✅ Use high resolution (720p or 1080p)
- ✅ Good lighting in captured video
- ✅ Clear, unobstructed view of people
- ❌ Avoid very low quality/grainy footage

**Performance:**
- Start with 10 FPS (good balance)
- Increase FPS for faster movements
- Reduce FPS if computer slows down
- Close other heavy applications

**Window Selection:**
- "Entire Screen" = Monitor everything
- "Specific Window" = Better performance, focus on one app

**Testing:**
- Test with sample videos first
- Verify gestures are detected
- Adjust FPS and quality as needed

---

## 🔧 Configuration

### Capture Modes

| Mode | When to Use | Performance |
|------|-------------|-------------|
| **Entire Screen** | Multiple cameras visible | Medium CPU |
| **Specific Window** | Single CCTV app | Low CPU |

### Frame Rate Guide

| FPS | Use Case | CPU Usage |
|-----|----------|-----------|
| 5-8 | Slow movements, low bandwidth | Low |
| 10-15 | Normal monitoring (recommended) | Medium |
| 20-30 | Fast movements, high accuracy | High |

---

## 🎬 Compatible Sources

Screen Capture works with:

✅ **CCTV Software:**
- Hikvision iVMS-4200
- Dahua Smart PSS
- Blue Iris
- ZoneMinder
- Any security camera software

✅ **Video Players:**
- VLC Media Player
- Windows Media Player
- YouTube videos
- Recorded CCTV footage

✅ **Video Calls:**
- Zoom
- Teams
- Google Meet
- WhatsApp Video Call

✅ **Streaming Apps:**
- Browser tabs with video
- Mobile screen mirroring apps
- Remote desktop sessions

---

## 🚨 Alert Flow

```
CCTV App Window
      ↓
Screen Capture (Browser)
      ↓
Frame sent to Backend
      ↓
AI Detection (MediaPipe)
      ↓
Alert Created (if detected)
      ↓
Dashboard Shows Alert
      ↓
Notifications Sent (Firebase/Twilio)
```

---

## 🔍 Troubleshooting

### "No screen capture rooms found"
**Solution:** Create room with camera URL = `screen`

### Can't see window to select
**Solution:**
- Make sure CCTV app is actually open
- Try "Entire Screen" instead
- Refresh browser and try again

### AI not detecting gestures
**Solution:**
- Make sure video shows clear people
- Increase FPS (try 15-20)
- Check video quality (should be clear)
- Verify gestures are visible (hand waving clearly visible)

### Performance issues / lag
**Solution:**
- Reduce FPS to 5-8
- Use "Specific Window" instead of "Entire Screen"
- Close other applications
- Reduce video resolution in CCTV app

### Browser asks for permission
**Solution:**
- Click "Allow" when asked to share screen
- Select the correct window/screen
- Check "Share audio" is off (we don't need audio)

---

## 📊 Statistics

While screen capturing, you'll see:
- **Frames Analyzed**: Total frames sent to AI
- **Alerts Detected**: Number of AI detections

These update in real-time!

---

## 🎯 Real-World Setup Example

### Hospital ICU Monitoring

**Existing Setup:**
- 10 IP cameras in ICU
- Old CCTV monitoring PC with vendor software
- Shows 4-camera grid view

**GuardianAI Integration:**
```
1. Keep existing CCTV system running
2. On monitoring PC, open GuardianAI in browser
3. Create 4 screen-capture rooms (one per camera)
4. Capture the 4-camera grid
5. AI monitors all 4 cameras
6. Alerts sent to nurses' phones
7. No changes to existing CCTV infrastructure!
```

**Benefits:**
- No new cameras needed
- No camera reconfiguration
- Works with legacy systems
- Easy to add/remove

---

## 🔐 Privacy Note

- Screen capture happens **only when you actively start it**
- You can see exactly what's being captured (preview shown)
- Click "Stop Capture" anytime to stop
- No recording stored (only real-time AI analysis)
- Browser enforces security (must explicitly share)

---

## ⚡ Quick Commands

```powershell
# Make sure backend and frontend are running

# Backend
cd C:\Users\hp\GuardianAI\backend
python main.py

# Frontend  
cd C:\Users\hp\GuardianAI\frontend
npm run dev

# Then navigate to:
http://localhost:5173/screen-capture
```

---

## 🎉 What's New

With this feature, you can now monitor:
- ✅ Existing CCTV systems (no integration needed)
- ✅ Any video source on your computer
- ✅ Legacy security systems
- ✅ Demo videos for testing
- ✅ Multiple cameras at once
- ✅ Video playback (not just live feeds)

**GuardianAI now works with ANY video source!** 🚀

---

## 📞 Support

Having issues?
1. Check if room with `camera_url: screen` is created
2. Verify backend is running
3. Make sure you click "Share" when browser asks
4. Try "Entire Screen" if window selection doesn't work

---

**Congratulations!** You can now monitor any CCTV system with GuardianAI! 🎉
