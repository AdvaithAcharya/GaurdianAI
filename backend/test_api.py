"""
Test API endpoint returns
"""
import asyncio
import aiohttp
import json

async def test_api():
    async with aiohttp.ClientSession() as session:
        # Test GET /api/contacts
        print("🧪 Testing GET /api/contacts")
        try:
            async with session.get('http://localhost:8000/api/contacts') as resp:
                print(f"Status: {resp.status}")
                data = await resp.json()
                print(f"Response: {json.dumps(data, indent=2, default=str)}\n")
                
                if data:
                    print(f"✅ Found {len(data)} contacts")
                    for contact in data:
                        print(f"  - {contact.get('name')} (ID: {contact.get('id')})")
                else:
                    print("⚠️  No contacts returned")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_api())
