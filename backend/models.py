"""
Pydantic models for GuardianAI
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class AlertType(str, Enum):
    """Alert type enumeration"""
    GESTURE = "gesture"
    VOICE = "voice"
    FALL = "fall"


class AlertStatus(str, Enum):
    """Alert status enumeration"""
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    ESCALATED = "escalated"


class Patient(BaseModel):
    """Patient model"""
    id: Optional[str] = Field(None, alias="_id")
    name: str
    age: Optional[int] = None
    room_id: str
    medical_notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "name": "John Doe",
                "age": 72,
                "room_id": "room_101",
                "medical_notes": "Post-surgery recovery"
            }
        }


class Room(BaseModel):
    """Room model"""
    id: Optional[str] = Field(None, alias="_id")
    room_number: str
    floor: Optional[int] = None
    camera_url: str
    camera_enabled: bool = True
    privacy_enabled: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "room_number": "101",
                "floor": 1,
                "camera_url": "rtsp://192.168.1.100:554/stream",
                "camera_enabled": True,
                "privacy_enabled": True
            }
        }


class Contact(BaseModel):
    """Nurse/Doctor contact model"""
    id: Optional[str] = Field(None, alias="_id")
    name: str
    role: str  # "nurse", "doctor", "emergency"
    # Require E.164 format (e.g., +15551234567)
    phone_number: str = Field(..., pattern=r"^\+[1-9]\d{7,14}$")
    firebase_token: Optional[str] = None
    email: Optional[str] = None
    priority: int = 1  # Lower number = higher priority for escalation
    active: bool = True
    created_at: Optional[datetime] = None
    
    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
        json_schema_extra = {
            "example": {
                "name": "Jane Smith",
                "role": "nurse",
                "phone_number": "+1234567890",
                "priority": 1,
                "active": True
            }
        }


class Alert(BaseModel):
    """Alert model"""
    id: Optional[str] = Field(None, alias="_id")
    alert_type: AlertType
    room_id: str
    patient_id: Optional[str] = None
    description: str
    status: AlertStatus = AlertStatus.ACTIVE
    confidence: Optional[float] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    acknowledged: bool = False
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    escalation_level: int = 0
    last_escalation_at: Optional[datetime] = None
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "alert_type": "gesture",
                "room_id": "room_101",
                "description": "Patient waved for help 3 times",
                "status": "active",
                "confidence": 0.95
            }
        }


class AlertLog(BaseModel):
    """Alert log model for tracking alert history"""
    id: Optional[str] = Field(None, alias="_id")
    alert_id: str
    action: str  # "created", "acknowledged", "escalated", "resolved"
    performed_by: Optional[str] = None
    details: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True


class VideoStreamConfig(BaseModel):
    """Video stream configuration"""
    room_id: str
    camera_url: str
    enable_gesture_detection: bool = True
    enable_voice_detection: bool = True
    enable_fall_detection: bool = True
    enable_privacy_filter: bool = True


class AlertResponse(BaseModel):
    """Response model for alert operations"""
    success: bool
    message: str
    alert_id: Optional[str] = None
