"""
Contacts API endpoints
"""
from fastapi import APIRouter, HTTPException
from typing import List
from bson import ObjectId

from database import database
from models import Contact
from config import settings
from fastapi import HTTPException
import re

router = APIRouter()

_E164 = re.compile(r"^\+[1-9]\d{7,14}$")

def _assert_e164(raw: str):
    if not raw or not _E164.match(str(raw)):
        raise HTTPException(status_code=422, detail="phone_number must be E.164 format (e.g., +15551234567) and verified in Twilio for trial accounts")


@router.get("/")
async def get_contacts(active_only: bool = False):
    """Get all contacts"""
    try:
        collection = database.get_collection("contacts")
        query = {"active": True} if active_only else {}
        cursor = collection.find(query).sort("priority", 1)
        contacts = []
        
        async for doc in cursor:
            contact_dict = {
                "id": str(doc["_id"]),
                "name": doc.get("name", ""),
                "role": doc.get("role", ""),
                "phone_number": doc.get("phone_number", ""),
                "firebase_token": doc.get("firebase_token"),
                "email": doc.get("email"),
                "priority": doc.get("priority", 1),
                "active": doc.get("active", True),
                "created_at": doc.get("created_at")
            }
            contacts.append(contact_dict)
        
        return contacts
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{contact_id}")
async def get_contact(contact_id: str):
    """Get a specific contact"""
    try:
        collection = database.get_collection("contacts")
        doc = await collection.find_one({"_id": ObjectId(contact_id)})
        
        if not doc:
            raise HTTPException(status_code=404, detail="Contact not found")
        
        return {
            "id": str(doc["_id"]),
            "name": doc.get("name", ""),
            "role": doc.get("role", ""),
            "phone_number": doc.get("phone_number", ""),
            "firebase_token": doc.get("firebase_token"),
            "email": doc.get("email"),
            "priority": doc.get("priority", 1),
            "active": doc.get("active", True),
            "created_at": doc.get("created_at")
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/")
async def create_contact(contact: Contact):
    """Create a new contact"""
    try:
        from datetime import datetime
        collection = database.get_collection("contacts")
        _assert_e164(contact.phone_number)
        contact_dict = {
            "name": contact.name,
            "role": contact.role,
            "phone_number": contact.phone_number,
            "firebase_token": contact.firebase_token,
            "email": contact.email,
            "priority": contact.priority,
            "active": contact.active,
            "created_at": datetime.utcnow()
        }
        result = await collection.insert_one(contact_dict)
        
        return {
            "id": str(result.inserted_id),
            "name": contact.name,
            "role": contact.role,
            "phone_number": contact.phone_number,
            "firebase_token": contact.firebase_token,
            "email": contact.email,
            "priority": contact.priority,
            "active": contact.active,
            "created_at": contact_dict["created_at"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{contact_id}")
async def update_contact(contact_id: str, contact: Contact):
    """Update a contact"""
    try:
        collection = database.get_collection("contacts")
        _assert_e164(contact.phone_number)
        contact_dict = {
            "name": contact.name,
            "role": contact.role,
            "phone_number": contact.phone_number,
            "firebase_token": contact.firebase_token,
            "email": contact.email,
            "priority": contact.priority,
            "active": contact.active
        }
        
        result = await collection.update_one(
            {"_id": ObjectId(contact_id)},
            {"$set": contact_dict}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Contact not found")
        
        return {
            "id": contact_id,
            "name": contact.name,
            "role": contact.role,
            "phone_number": contact.phone_number,
            "firebase_token": contact.firebase_token,
            "email": contact.email,
            "priority": contact.priority,
            "active": contact.active,
            "created_at": contact.created_at
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{contact_id}")
async def delete_contact(contact_id: str):
    """Delete a contact"""
    try:
        collection = database.get_collection("contacts")
        result = await collection.delete_one({"_id": ObjectId(contact_id)})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Contact not found")
        
        return {"message": "Contact deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
