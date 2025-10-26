"""
MongoDB database connection and utilities
"""
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional
import logging

from config import settings

logger = logging.getLogger(__name__)


class Database:
    """MongoDB database manager"""
    
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.db: Optional[AsyncIOMotorDatabase] = None
    
    async def connect(self):
        """Connect to MongoDB"""
        try:
            # Use MONGO_URI if available, otherwise fall back to MONGODB_URL
            mongodb_url = settings.MONGO_URI if settings.MONGO_URI else settings.MONGODB_URL
            self.client = AsyncIOMotorClient(mongodb_url)
            self.db = self.client[settings.MONGODB_DB_NAME]
            
            # Test connection
            await self.client.admin.command('ping')
            logger.info(f"Connected to MongoDB: {settings.MONGODB_DB_NAME}")
            
            # Create indexes
            await self._create_indexes()
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB")
    
    async def is_connected(self) -> bool:
        """Check if database is connected"""
        try:
            if self.client:
                await self.client.admin.command('ping')
                return True
        except Exception:
            pass
        return False
    
    async def _create_indexes(self):
        """Create database indexes for optimal performance"""
        try:
            # Alerts indexes
            await self.db.alerts.create_index("timestamp")
            await self.db.alerts.create_index("room_id")
            await self.db.alerts.create_index("status")
            await self.db.alerts.create_index([("acknowledged", 1), ("timestamp", -1)])
            
            # Patients indexes
            await self.db.patients.create_index("room_id", unique=True)
            
            # Rooms indexes
            await self.db.rooms.create_index("room_number", unique=True)
            
            # Alert logs indexes
            await self.db.alert_logs.create_index("alert_id")
            await self.db.alert_logs.create_index("timestamp")
            
            logger.info("Database indexes created successfully")
        except Exception as e:
            logger.error(f"Error creating indexes: {e}")
    
    def get_collection(self, name: str):
        """Get a collection from the database"""
        if self.db is None:
            raise RuntimeError("Database not connected")
        return self.db[name]


# Global database instance
database = Database()
