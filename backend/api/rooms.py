"""
Rooms API endpoints
"""
from fastapi import APIRouter, HTTPException
from typing import List

from database import database
from models import Room

router = APIRouter()


@router.get("/", response_model=List[Room])
async def get_rooms():
    """Get all rooms"""
    try:
        collection = database.get_collection("rooms")
        cursor = collection.find({})
        rooms = []
        
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            rooms.append(Room(**doc))
        
        return rooms
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{room_id}", response_model=Room)
async def get_room(room_id: str):
    """Get a specific room"""
    try:
        collection = database.get_collection("rooms")
        doc = await collection.find_one({"_id": room_id})
        
        if not doc:
            raise HTTPException(status_code=404, detail="Room not found")
        
        doc["_id"] = str(doc["_id"])
        return Room(**doc)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", response_model=Room)
async def create_room(room: Room):
    """Create a new room"""
    try:
        collection = database.get_collection("rooms")
        room_dict = room.model_dump(by_alias=True, exclude={"id"})
        result = await collection.insert_one(room_dict)
        
        room.id = str(result.inserted_id)
        return room
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{room_id}", response_model=Room)
async def update_room(room_id: str, room: Room):
    """Update a room"""
    try:
        collection = database.get_collection("rooms")
        room_dict = room.model_dump(by_alias=True, exclude={"id"})
        
        result = await collection.update_one(
            {"_id": room_id},
            {"$set": room_dict}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Room not found")
        
        room.id = room_id
        return room
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{room_id}")
async def delete_room(room_id: str):
    """Delete a room"""
    try:
        collection = database.get_collection("rooms")
        result = await collection.delete_one({"_id": room_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Room not found")
        
        return {"message": "Room deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
