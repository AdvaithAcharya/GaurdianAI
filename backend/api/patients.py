"""
Patients API endpoints
"""
from fastapi import APIRouter, HTTPException
from typing import List

from database import database
from models import Patient

router = APIRouter()


@router.get("/", response_model=List[Patient])
async def get_patients():
    """Get all patients"""
    try:
        collection = database.get_collection("patients")
        cursor = collection.find({})
        patients = []
        
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            patients.append(Patient(**doc))
        
        return patients
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{patient_id}", response_model=Patient)
async def get_patient(patient_id: str):
    """Get a specific patient"""
    try:
        collection = database.get_collection("patients")
        doc = await collection.find_one({"_id": patient_id})
        
        if not doc:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        doc["_id"] = str(doc["_id"])
        return Patient(**doc)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", response_model=Patient)
async def create_patient(patient: Patient):
    """Create a new patient"""
    try:
        collection = database.get_collection("patients")
        patient_dict = patient.model_dump(by_alias=True, exclude={"id"})
        result = await collection.insert_one(patient_dict)
        
        patient.id = str(result.inserted_id)
        return patient
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{patient_id}", response_model=Patient)
async def update_patient(patient_id: str, patient: Patient):
    """Update a patient"""
    try:
        collection = database.get_collection("patients")
        patient_dict = patient.model_dump(by_alias=True, exclude={"id"})
        
        result = await collection.update_one(
            {"_id": patient_id},
            {"$set": patient_dict}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        patient.id = patient_id
        return patient
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{patient_id}")
async def delete_patient(patient_id: str):
    """Delete a patient"""
    try:
        collection = database.get_collection("patients")
        result = await collection.delete_one({"_id": patient_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        return {"message": "Patient deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
