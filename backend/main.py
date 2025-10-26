"""
GuardianAI - Main FastAPI Application
Privacy-First Patient Distress Detection System
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from contextlib import asynccontextmanager
import asyncio
from typing import List, Dict
import logging

from config import settings
from database import database
from models import Alert, Patient, Room, Contact, AlertLog
from video_processor import VideoStreamManager
from alert_manager import AlertManager
from api import alerts, patients, rooms, contacts, streams

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global managers
video_manager = VideoStreamManager()
alert_manager = AlertManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    await database.connect()
    logger.info("Connected to MongoDB")
    
    # Start background tasks
    asyncio.create_task(video_manager.process_streams())
    asyncio.create_task(alert_manager.process_alerts())
    
    yield
    
    # Shutdown
    await video_manager.stop_all()
    await database.disconnect()
    logger.info("Disconnected from MongoDB")


app = FastAPI(
    title="GuardianAI API",
    description="Low-Cost, Privacy-First Patient Distress Detection System",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(alerts.router, prefix="/api/alerts", tags=["alerts"])
app.include_router(patients.router, prefix="/api/patients", tags=["patients"])
app.include_router(rooms.router, prefix="/api/rooms", tags=["rooms"])
app.include_router(contacts.router, prefix="/api/contacts", tags=["contacts"])
app.include_router(streams.router, prefix="/api/streams", tags=["streams"])


# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"New WebSocket connection. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to client: {e}")


manager = ConnectionManager()


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "GuardianAI",
        "status": "operational",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "database": await database.is_connected(),
        "active_streams": video_manager.get_active_stream_count(),
        "active_alerts": alert_manager.get_active_alert_count()
    }


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and receive messages
            data = await websocket.receive_text()
            # Echo back for debugging
            await websocket.send_json({"type": "echo", "data": data})
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


# Make manager available to other modules
app.state.ws_manager = manager
app.state.video_manager = video_manager
app.state.alert_manager = alert_manager


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
