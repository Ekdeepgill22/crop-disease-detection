# database.py
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import ConnectionFailure
from app.config import settings
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class Database:
    client: Optional[AsyncIOMotorClient] = None
    database: Optional[AsyncIOMotorDatabase] = None

database = Database()

async def connect_to_mongo():
    """Create database connection"""
    try:
        database.client = AsyncIOMotorClient(settings.MONGODB_URL)
        database.database = database.client[settings.DATABASE_NAME]
        
        # Test connection
        await database.client.admin.command('ping')
        logger.info("Connected to MongoDB successfully")
        
        # Create indexes
        await create_indexes()
        
    except ConnectionFailure as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise

async def close_mongo_connection():
    """Close database connection"""
    if database.client:
        database.client.close()
        logger.info("MongoDB connection closed")

def _get_db() -> AsyncIOMotorDatabase:
    """Get database instance with proper error handling"""
    if database.database is None:
        raise ConnectionError("Database connection not available")
    return database.database

async def create_indexes():
    """Create database indexes for better performance"""
    try:
        db = _get_db()
        
        # User collection indexes
        await db.users.create_index("email", unique=True)
        await db.users.create_index("phone_number", unique=True)
        
        # Diagnosis collection indexes
        await db.diagnoses.create_index("user_id")
        await db.diagnoses.create_index("created_at")
        
        logger.info("Database indexes created successfully")
    except Exception as e:
        logger.error(f"Error creating indexes: {e}")

def get_database() -> Optional[AsyncIOMotorDatabase]:
    return database.database