"""
Fix phone numbers to E.164 format for Twilio
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

async def fix_numbers():
    mongodb_url = "mongodb+srv://advaith23cs005_db_user:advaith123@cluster1.1tuvby8.mongodb.net/?retryWrites=true&w=majority&appName=Cluster1"
    client = AsyncIOMotorClient(mongodb_url)
    db = client["guardianai"]
    collection = db["contacts"]
    
    try:
        await client.admin.command('ping')
        print("✅ Connected to MongoDB\n")
        
        # Get all contacts
        contacts = await collection.find({}).to_list(length=100)
        print(f"📞 Found {len(contacts)} contacts:\n")
        
        for contact in contacts:
            old_phone = contact.get('phone_number', '')
            name = contact.get('name', 'Unknown')
            
            # Fix phone number format
            new_phone = old_phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
            
            # Add country code if missing
            if not new_phone.startswith('+'):
                # Assume Indian number if starts with 9, 8, 7, 6
                if new_phone and new_phone[0] in ['9', '8', '7', '6']:
                    if len(new_phone) == 10:
                        new_phone = '+91' + new_phone
                    else:
                        new_phone = '+' + new_phone
                else:
                    # Assume US/Canada for other patterns
                    new_phone = '+1' + new_phone
            
            print(f"{name}:")
            print(f"  Old: {old_phone}")
            print(f"  New: {new_phone}")
            
            if old_phone != new_phone:
                result = await collection.update_one(
                    {"_id": contact["_id"]},
                    {"$set": {"phone_number": new_phone}}
                )
                print(f"  ✅ Updated!")
            else:
                print(f"  ℹ️  No change needed")
            print()
        
        print("=" * 60)
        print("✅ All phone numbers fixed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(fix_numbers())
