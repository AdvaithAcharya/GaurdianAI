"""
Check contacts in MongoDB
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def check_contacts():
    mongodb_url = "mongodb+srv://advaith23cs005_db_user:advaith123@cluster1.1tuvby8.mongodb.net/?retryWrites=true&w=majority&appName=Cluster1"
    client = AsyncIOMotorClient(mongodb_url)
    db = client["guardianai"]
    collection = db["contacts"]
    
    try:
        await client.admin.command('ping')
        print("✅ Connected to MongoDB\n")
        
        # Get all contacts
        cursor = collection.find({})
        contacts = await cursor.to_list(length=100)
        
        print(f"📊 Found {len(contacts)} contacts:\n")
        
        for contact in contacts:
            print(f"ID: {contact['_id']}")
            print(f"Name: {contact.get('name', 'N/A')}")
            print(f"Role: {contact.get('role', 'N/A')}")
            print(f"Phone: {contact.get('phone_number', 'N/A')}")
            print(f"Active: {contact.get('active', False)}")
            print("-" * 50)
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(check_contacts())
