"""
Comprehensive CRUD test
"""
import asyncio
import aiohttp
import json

BASE_URL = 'http://localhost:8000/api/contacts'

async def test_full_crud():
    async with aiohttp.ClientSession() as session:
        print("=" * 60)
        print("🧪 COMPREHENSIVE CONTACT CRUD TEST")
        print("=" * 60 + "\n")
        
        # Test 1: GET all contacts
        print("1️⃣  GET /api/contacts")
        async with session.get(BASE_URL) as resp:
            contacts = await resp.json()
            print(f"   Status: {resp.status}")
            print(f"   Found {len(contacts)} existing contacts\n")
        
        # Test 2: CREATE a new contact
        print("2️⃣  POST /api/contacts (Create)")
        new_contact = {
            "name": "Test Nurse Sarah",
            "role": "nurse",
            "phone_number": "+1234567890",
            "email": "sarah@test.com",
            "firebase_token": "",
            "priority": 1,
            "active": True
        }
        async with session.post(BASE_URL, json=new_contact) as resp:
            created = await resp.json()
            print(f"   Status: {resp.status}")
            print(f"   Created ID: {created.get('id')}")
            contact_id = created.get('id')
            print(f"   Name: {created.get('name')}\n")
        
        # Test 3: GET specific contact
        print("3️⃣  GET /api/contacts/{id} (Read)")
        async with session.get(f"{BASE_URL}/{contact_id}") as resp:
            contact = await resp.json()
            print(f"   Status: {resp.status}")
            print(f"   Retrieved: {contact.get('name')}")
            print(f"   Phone: {contact.get('phone_number')}\n")
        
        # Test 4: UPDATE the contact
        print("4️⃣  PUT /api/contacts/{id} (Update)")
        updated_data = {
            "name": "Test Nurse Sarah UPDATED",
            "role": "nurse",
            "phone_number": "+9999999999",
            "email": "sarah.updated@test.com",
            "firebase_token": "",
            "priority": 2,
            "active": True
        }
        async with session.put(f"{BASE_URL}/{contact_id}", json=updated_data) as resp:
            updated = await resp.json()
            print(f"   Status: {resp.status}")
            print(f"   Updated Name: {updated.get('name')}")
            print(f"   Updated Phone: {updated.get('phone_number')}")
            print(f"   Updated Priority: {updated.get('priority')}\n")
        
        # Test 5: Verify update
        print("5️⃣  GET /api/contacts/{id} (Verify Update)")
        async with session.get(f"{BASE_URL}/{contact_id}") as resp:
            contact = await resp.json()
            print(f"   Status: {resp.status}")
            print(f"   Name: {contact.get('name')}")
            print(f"   Phone: {contact.get('phone_number')}")
            if contact.get('phone_number') == "+9999999999":
                print("   ✅ Update verified!\n")
            else:
                print("   ❌ Update NOT reflected!\n")
        
        # Test 6: DELETE the contact
        print("6️⃣  DELETE /api/contacts/{id} (Delete)")
        async with session.delete(f"{BASE_URL}/{contact_id}") as resp:
            result = await resp.json()
            print(f"   Status: {resp.status}")
            print(f"   Message: {result.get('message')}\n")
        
        # Test 7: Verify deletion
        print("7️⃣  GET /api/contacts/{id} (Verify Deletion)")
        async with session.get(f"{BASE_URL}/{contact_id}") as resp:
            print(f"   Status: {resp.status}")
            if resp.status == 404:
                print("   ✅ Contact successfully deleted!\n")
            else:
                print("   ❌ Contact still exists!\n")
        
        # Test 8: Final state
        print("8️⃣  GET /api/contacts (Final State)")
        async with session.get(BASE_URL) as resp:
            contacts = await resp.json()
            print(f"   Status: {resp.status}")
            print(f"   Final count: {len(contacts)} contacts\n")
        
        print("=" * 60)
        print("✅ ALL CRUD OPERATIONS COMPLETED")
        print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_full_crud())
