"""
Directly trigger a test alert to verify notifications
"""
import asyncio
import sys
sys.path.insert(0, '.')

from alert_manager import AlertManager
from models import Alert, AlertType
from database import database
from config import settings
from datetime import datetime

async def trigger_alert():
    print("=" * 60)
    print("🚨 TRIGGERING TEST ALERT")
    print("=" * 60 + "\n")
    
    # Connect to database
    await database.connect()
    print("✅ Connected to MongoDB\n")
    
    # Initialize alert manager
    alert_manager = AlertManager()
    print("✅ Alert Manager initialized\n")
    
    # Check Twilio status
    if alert_manager.twilio_client:
        print(f"✅ Twilio client initialized")
        print(f"   Account SID: {settings.TWILIO_ACCOUNT_SID[:15]}...")
        print(f"   Phone: {settings.TWILIO_PHONE_NUMBER}\n")
    else:
        print("⚠️  Twilio client NOT initialized\n")
    
    # Get active contacts
    contacts = await alert_manager._get_contacts()
    print(f"📞 Active Contacts: {len(contacts)}")
    for c in contacts:
        print(f"   - {c.get('name')}: {c.get('phone_number')} (Priority {c.get('priority')})")
    print()
    
    if not contacts:
        print("❌ No active contacts! Add contacts first.")
        await database.disconnect()
        return
    
    # Create test alert
    print("🚨 Creating TEST ALERT...")
    alert = Alert(
        alert_type=AlertType.GESTURE,
        room_id="TEST-ROOM-001",
        description="TEST ALERT: Wave gesture detected - This is a test of the alert system",
        confidence=0.99,
        timestamp=datetime.utcnow()
    )
    
    alert_id = await alert_manager.create_alert(alert)
    print(f"✅ Alert created: {alert_id}\n")
    
    # Wait for notifications to be sent
    print("⏳ Waiting 5 seconds for notifications to be sent...")
    print("   (Check backend terminal for Twilio logs)")
    await asyncio.sleep(5)
    
    # Check alert status
    print("\n📊 Alert Status:")
    if alert_id in alert_manager.active_alerts:
        active_alert = alert_manager.active_alerts[alert_id]
        print(f"   Status: {active_alert.status}")
        print(f"   Acknowledged: {active_alert.acknowledged}")
        print(f"   Escalation Level: {active_alert.escalation_level}")
    
    print("\n" + "=" * 60)
    print("✅ TEST COMPLETE")
    print("=" * 60)
    print("\nCheck your phone for incoming call!")
    print("Check backend logs for:")
    print("  - 'INFO:alert_manager:Twilio call initiated to...'")
    print("  - or 'ERROR:alert_manager:Error sending Twilio call'")
    
    # Cleanup
    await database.disconnect()

if __name__ == "__main__":
    try:
        asyncio.run(trigger_alert())
    except KeyboardInterrupt:
        print("\n\n❌ Test interrupted")
