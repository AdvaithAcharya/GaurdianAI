# Mobile Camera Connection Guide

## Your Computer's IP Address
**Your IP:** `10.18.53.47`

## Quick Fix Steps

### 1. Restart Backend (REQUIRED)
The CORS settings were just updated. You MUST restart the backend:

```powershell
# Press Ctrl+C in the backend terminal to stop it
# Then start it again:
cd C:\Users\hp\GuardianAI\backend
python main.py
```

### 2. Mobile Device Setup

**On your mobile device browser, use:**
```
http://10.18.53.47:5173/mobile-stream.html
```

**Backend URL to enter in the page:**
```
http://10.18.53.47:8000
```

### 3. Create a Mobile Room First

Before using mobile streaming, you need a room configured for mobile:

1. On computer, go to: `http://localhost:5173/rooms`
2. Click "Add Room"
3. Room Number: `Mobile-1`
4. Click "Use Mobile Camera" button (this sets URL to `mobile`)
5. Click "Create Room"

### 4. Test Connection

On mobile browser:
1. Open: `http://10.18.53.47:5173/mobile-stream.html`
2. Backend URL: `http://10.18.53.47:8000`
3. Should see "No mobile rooms found" OR a dropdown with "Mobile-1"
4. If you see the dropdown, you're connected! ✅

## Common Issues

### "Failed to connect to backend"
**Solution:**
- ✅ Restart backend after CORS update
- ✅ Make sure both devices on same WiFi network
- ✅ Check Windows Firewall (see below)

### Firewall Blocking Connections
If still not working, allow ports through Windows Firewall:

```powershell
# Run as Administrator in PowerShell
New-NetFirewallRule -DisplayName "GuardianAI Backend" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
New-NetFirewallRule -DisplayName "GuardianAI Frontend" -Direction Inbound -LocalPort 5173 -Protocol TCP -Action Allow
```

### Different WiFi Network
- Your computer: `10.18.53.47`
- Mobile must be on **same WiFi network**
- Check your mobile's WiFi settings

### Backend Not Accessible
Test from mobile browser first:
```
http://10.18.53.47:8000/health
```
Should show: `{"status":"healthy",...}`

## Alternative: Use Computer's Webcam Instead

If mobile still doesn't work, you can test with your computer's webcam:

1. Go to: `http://localhost:5173/rooms`
2. Add Room with Camera URL: `0` (use webcam)
3. Go to: `http://localhost:5173/video`
4. Click "Start"
5. Wave at your webcam → alerts will be created!

## Verification Checklist

- [ ] Backend restarted after CORS change
- [ ] Mobile and computer on same WiFi
- [ ] Firewall rules added
- [ ] Mobile room created in Rooms page
- [ ] Can access `http://10.18.53.47:8000/health` from mobile
- [ ] Mobile browser is Chrome/Safari (not old browsers)

## Quick Debug

### Test Backend from Computer
```powershell
# Should return list of rooms
curl http://localhost:8000/api/rooms
```

### Test Backend from Mobile
Open mobile browser and go to:
```
http://10.18.53.47:8000/api/rooms
```
Should show JSON response with rooms list.

---

**After restarting backend, everything should work!** 🎉
