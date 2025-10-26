"""
Test script to verify contact CRUD operations
"""
import asyncio
import sys
from bson import ObjectId
from database import database
from motor.motor_asyncio import AsyncIOMotorClient

async def test_contacts():
    """Test contact operations"""
    print("🧪 Testing Contact CRUD Operations\n")
    
    # Connect to database
    try:
        mongodb_url = "mongodb+srv://guardianai:8LJYhAZ8MZHkrQZZ@guardianai.jyq8u.mongodb.net/?retryWrites=true&w=majority&appName=GuardianAI"
        client = AsyncIOMotorClient(mongodb_url)
        db = client["guardianai"]
        collection = db["contacts"]
        
        await client.admin.command('ping')
        print("✅ Connected to MongoDB\n")
        
        # Test 1: Create a test contact
        print("📝 Test 1: Creating test contact...")
        test_contact = {
            "name": "Test Nurse",
            "role": "nurse",
            "phone_number": "+1234567890",
            "email": "test@example.com",
            "priority": 1,
            "active": True
        }
        result = await collection.insert_one(test_contact)
        contact_id = str(result.inserted_id)
        print(f"✅ Created contact with ID: {contact_id}\n")
        
        # Test 2: Read the contact
        print("📖 Test 2: Reading contact...")
        doc = await collection.find_one({"_id": ObjectId(contact_id)})
        if doc:
            doc["id"] = str(doc["_id"])
            print(f"✅ Found contact: {doc['name']}")
            print(f"   ID field: {doc['id']}\n")
        else:
            print("❌ Contact not found\n")
            
        # Test 3: Update the contact
        print("✏️  Test 3: Updating contact...")
        update_result = await collection.update_one(
            {"_id": ObjectId(contact_id)},
            {"$set": {"phone_number": "+9876543210"}}
        )
        if update_result.matched_count > 0:
            print(f"✅ Updated contact (matched: {update_result.matched_count})\n")
        else:
            print("❌ Update failed - contact not found\n")
            
        # Test 4: Verify update
        print("🔍 Test 4: Verifying update...")
        doc = await collection.find_one({"_id": ObjectId(contact_id)})
        if doc and doc["phone_number"] == "+9876543210":
            print(f"✅ Phone number updated: {doc['phone_number']}\n")
        else:
            print("❌ Update verification failed\n")
            
        # Test 5: Delete the contact
        print("🗑️  Test 5: Deleting contact...")
        delete_result = await collection.delete_one({"_id": ObjectId(contact_id)})
        if delete_result.deleted_count > 0:
            print(f"✅ Deleted contact (deleted: {delete_result.deleted_count})\n")
        else:
            print("❌ Delete failed - contact not found\n")
            
        # Test 6: Verify deletion
        print("🔍 Test 6: Verifying deletion...")
        doc = await collection.find_one({"_id": ObjectId(contact_id)})
        if doc is None:
            print("✅ Contact successfully deleted\n")
        else:
            print("❌ Deletion verification failed\n")
            
        # Close connection
        client.close()
        print("✅ All tests completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_contacts())
