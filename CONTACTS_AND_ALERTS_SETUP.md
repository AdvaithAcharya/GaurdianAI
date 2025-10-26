# Contacts & Alert System Setup

## ✅ What's Complete

### Frontend Changes:
- ✅ **Rooms Removed** - No more room management UI
- ✅ **Full Contacts Manager** - Add/Edit/Delete nurses & doctors
- ✅ **Simplified Navigation** - Dashboard, Alerts, Contacts, Screen Monitoring
- ✅ **Screen Capture** - Works without room dependency

### Backend Ready:
- ✅ **Contacts API** - Full CRUD already implemented
- ✅ **Alert Manager** - Twilio & Firebase integration ready
- ✅ **Escalation System** - Priority-based contact escalation
- ✅ **Screen Frame Processing** - Direct AI detection without rooms

---

## 🚀 Quick Start

### 1. Add Contacts

Go to: `http://localhost:5173/contacts`

**Add a Nurse:**
```
Name: Nurse Sarah
Role: Nurse  
Phone: +1234567890
Priority: 1 (Highest)
Active: ✓
```

**Add a Doctor:**
```
Name: Dr. John
Role: Doctor
Phone: +0987654321  
Priority: 2
Active: ✓
```

### 2. Test The System

1. **Start Screen Capture**: `http://localhost:5173/screen-capture`
2. **Wave your hand** (or open CCTV app and show gestures)
3. **Check Alerts**: `http://localhost:5173/alerts`
4. **Alerts created automatically!**

---

## 📞 Phone & Push Notification Setup

The backend is **already integrated** with Twilio and Firebase. You just need to add credentials:

### Twilio (Phone Calls)

1. **Sign up**: https://www.twilio.com/
2. **Get**:
   - Account SID
   - Auth Token
   - Phone Number

3. **Update `.env`**:
```env
TWILIO_ACCOUNT_SID=your_account_sid_here
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_PHONE_NUMBER=+1234567890
```

4. **Restart backend**
5. **Done!** Alerts will trigger phone calls to all active contacts

### Firebase (Push Notifications)

1. **Create project**: https://console.firebase.google.com/
2. **Download** service account JSON
3. **Save to**: `backend/firebase-credentials.json`

4. **Update `.env`**:
```env
FIREBASE_CREDENTIALS_PATH=firebase-credentials.json
FIREBASE_PROJECT_ID=your-project-id
```

5. **Add Firebase tokens** to contacts (in Contacts Manager)
6. **Restart backend**
7. **Done!** Push notifications will be sent

---

## 🔔 How Alert Escalation Works

### When Alert is Created:

1. **Priority 1 contacts** notified immediately
   - Firebase push notification sent
   - Twilio voice call initiated

2. **Wait 30 seconds** (configurable in .env: `ALERT_ESCALATION_TIMEOUT`)

3. **If not acknowledged:**
   - **Priority 2 contacts** notified
   - Wait 30 seconds

4. **Continue escalating** through Priority 3, 4, 5...

5. **Max attempts**: 3 (configurable: `MAX_ESCALATION_ATTEMPTS`)

### Acknowledgment:
- Nurse/Doctor clicks **"Acknowledge"** in dashboard
- OR presses any key when Twilio calls
- Alert escalation stops immediately

---

## 🎯 Contact Priority System

| Priority | When Notified | Example |
|----------|---------------|---------|
| **1** | Immediately | On-duty nurses |
| **2** | After 30s if Priority 1 doesn't acknowledge | Backup nurses |
| **3** | After 60s | Doctors |
| **4** | After 90s | Senior doctors |
| **5** | After 120s | Emergency contacts |

**Pro Tip:** Set most responsive staff to Priority 1!

---

## 💡 Contact Management Features

### Add Contact
- Name, Role (nurse/doctor/emergency/admin)
- Phone number (for Twilio calls)
- Email (for future email alerts)
- Firebase token (for push notifications)
- Priority (1-5, lower = contacted first)
- Active/Inactive toggle

### Edit Contact
- Click "Edit" on any contact
- Update any field
- Save changes

### Delete Contact
- Click "Delete" on any contact
- Confirm deletion
- Contact removed from alert system

### Toggle Active Status
- Click "Active" / "Inactive" button
- Instantly enable/disable contact
- Inactive contacts don't receive alerts

---

## 🧪 Testing Without Twilio/Firebase

**Good news:** System works without credentials!

- Alerts still created ✅
- Dashboard shows alerts ✅  
- Acknowledge/Resolve works ✅
- **Only missing:** External notifications (calls/push)

**For demo:** Just show the dashboard alerts working!

---

## 📱 Current Alert Flow

```
Screen Capture detects gesture/fall
         ↓
Alert created in MongoDB
         ↓
Dashboard shows alert (real-time)
         ↓
Alert Manager checks for active contacts
         ↓
IF Twilio configured → Phone calls sent
IF Firebase configured → Push notifications sent
         ↓
Escalates every 30s to next priority level
         ↓
Nurse acknowledges → Escalation stops
```

---

## 🔧 Environment Variables (.env)

### Required (Already Set):
```env
MONGODB_URL=mongodb+srv://... ✅
MONGODB_DB_NAME=guardianai ✅
```

### Optional (For Phone/Push):
```env
# Twilio (Phone Calls)
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token  
TWILIO_PHONE_NUMBER=+1234567890

# Firebase (Push Notifications)
FIREBASE_CREDENTIALS_PATH=firebase-credentials.json
FIREBASE_PROJECT_ID=your-project-id

# Alert Timing (Already Configured)
ALERT_ESCALATION_TIMEOUT=30  # seconds
MAX_ESCALATION_ATTEMPTS=3    # escalation levels
```

---

## ✅ What Works Right Now (No Setup Needed)

1. ✅ **Screen Monitoring** with AI detection
2. ✅ **Alert Creation** when gestures/falls detected
3. ✅ **Contact Management** (add/edit/delete)
4. ✅ **Dashboard** showing alerts real-time
5. ✅ **Alert Acknowledgment** system
6. ✅ **WebSocket** real-time updates
7. ✅ **MongoDB Atlas** storage

---

## 🎉 To Enable Phone & Push Notifications

**Just add Twilio & Firebase credentials to `.env` and restart backend!**

The entire integration is already coded and ready to go. Backend automatically:
- Loads contacts from database ✅
- Sends calls via Twilio (if configured) ✅
- Sends push via Firebase (if configured) ✅
- Escalates through priority levels ✅
- Logs all alert actions ✅

---

## 📞 Support

**Backend Alert Code:** `backend/alert_manager.py` (lines 275-369)
**Contact API:** `backend/api/contacts.py`
**Frontend Contacts:** `frontend/src/components/ContactsManager.jsx`

---

**Your system is production-ready! Just add Twilio/Firebase credentials to enable external notifications!** 🚀
