"""
Test alert system with contacts
"""
import asyncio
import aiohttp
import json

async def test_alert_system():
    async with aiohttp.ClientSession() as session:
        print("=" * 60)
        print("🧪 TESTING ALERT SYSTEM WITH CONTACTS")
        print("=" * 60 + "\n")
        
        # Step 1: Check contacts
        print("1️⃣  Checking active contacts...")
        async with session.get('http://localhost:8000/api/contacts') as resp:
            contacts = await resp.json()
            active_contacts = [c for c in contacts if c.get('active')]
            print(f"   Found {len(active_contacts)} active contacts")
            for c in active_contacts:
                print(f"   - {c.get('name')}: {c.get('phone_number')} (Priority {c.get('priority')})")
            print()
        
        if not active_contacts:
            print("⚠️  No active contacts! Alert calls won't be sent.")
            print("   Add a contact at http://localhost:5173/contacts\n")
            return
        
        # Step 2: Create a test alert
        print("2️⃣  Creating test alert...")
        alert_data = {
            "alert_type": "gesture",
            "room_id": "test-room-001",
            "description": "Test alert - Wave gesture detected (3 waves)",
            "status": "active",
            "confidence": 0.95
        }
        
        async with session.post('http://localhost:8000/api/alerts', json=alert_data) as resp:
            if resp.status == 200:
                alert = await resp.json()
                alert_id = alert.get('id')
                print(f"   ✅ Alert created: {alert_id}")
                print(f"   Description: {alert.get('description')}\n")
            else:
                print(f"   ❌ Failed to create alert: {resp.status}")
                return
        
        # Step 3: Wait for notifications to be sent
        print("3️⃣  Alert system processing...")
        print("   • Firebase push notifications (if tokens configured)")
        print("   • Twilio voice calls (if credentials configured)")
        print()
        await asyncio.sleep(3)
        
        # Step 4: Check alert status
        print("4️⃣  Checking alert status...")
        async with session.get(f'http://localhost:8000/api/alerts') as resp:
            alerts = await resp.json()
            test_alert = next((a for a in alerts if a.get('id') == alert_id), None)
            if test_alert:
                print(f"   Status: {test_alert.get('status')}")
                print(f"   Escalation level: {test_alert.get('escalation_level', 0)}")
                print(f"   Acknowledged: {test_alert.get('acknowledged')}\n")
        
        # Step 5: Acknowledge the alert
        print("5️⃣  Acknowledging alert...")
        async with session.post(
            f'http://localhost:8000/api/alerts/{alert_id}/acknowledge',
            json={"acknowledged_by": "Test System"}
        ) as resp:
            if resp.status == 200:
                print("   ✅ Alert acknowledged successfully\n")
            else:
                print(f"   ❌ Failed to acknowledge: {resp.status}\n")
        
        print("=" * 60)
        print("✅ ALERT SYSTEM TEST COMPLETED")
        print("=" * 60)
        print("\nCheck backend logs for Twilio call details!")
        print("Expected log: 'INFO:alert_manager:Twilio call initiated to ...'")

if __name__ == "__main__":
    asyncio.run(test_alert_system())
