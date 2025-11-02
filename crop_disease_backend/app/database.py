# database.py
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from app.config import settings
import logging
from typing import Optional
import asyncio

logger = logging.getLogger(__name__)

class Database:
    client: Optional[AsyncIOMotorClient] = None
    database: Optional[AsyncIOMotorDatabase] = None
    connected: bool = False

database = Database()

async def connect_to_mongo():
    """Create database connection with retry logic"""
    max_retries = 3
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Attempting to connect to MongoDB (attempt {attempt + 1}/{max_retries})")
            
            # Create client with timeout settings
            database.client = AsyncIOMotorClient(
                settings.MONGODB_URL,
                serverSelectionTimeoutMS=5000,  # 5 second timeout
                connectTimeoutMS=5000,
                socketTimeoutMS=5000,
                maxPoolSize=10,
                minPoolSize=1
            )
            
            # Test connection
            await database.client.admin.command('ping')
            database.database = database.client[settings.DATABASE_NAME]
            database.connected = True
            
            logger.info("Connected to MongoDB successfully")
            
            # Create indexes
            await create_indexes()
            return True
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.warning(f"MongoDB connection attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                await asyncio.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                logger.error("All MongoDB connection attempts failed")
                database.connected = False
                return False
        except Exception as e:
            logger.error(f"Unexpected error connecting to MongoDB: {e}")
            database.connected = False
            return False
    
    return False

async def close_mongo_connection():
    """Close database connection"""
    if database.client:
        database.client.close()
        database.connected = False
        logger.info("MongoDB connection closed")

def get_database() -> AsyncIOMotorDatabase:
    """Get database instance with proper error handling"""
    if not database.connected or database.database is None:
        raise ConnectionError("Database connection not available. Please ensure MongoDB is running and properly configured.")
    return database.database

async def create_indexes():
    """Create database indexes for better performance"""
    try:
        if not database.connected or not database.database:
            return
            
        db = database.database
        
        # User collection indexes
        try:
            await db.users.create_index("email", unique=True)
            await db.users.create_index("phone_number", unique=True)
        except Exception as e:
            logger.warning(f"Error creating user indexes (may already exist): {e}")
        
        # Diagnosis collection indexes
        try:
            await db.diagnoses.create_index("user_id")
            await db.diagnoses.create_index("created_at")
        except Exception as e:
            logger.warning(f"Error creating diagnosis indexes (may already exist): {e}")
        
        logger.info("Database indexes created successfully")
    except Exception as e:
        logger.error(f"Error creating indexes: {e}")

async def ensure_connection():
    """Ensure database connection is active"""
    try:
        if not database.connected or database.database is None:
            logger.info("Database not connected, attempting to connect...")
            await connect_to_mongo()
        else:
            # Test if connection is still alive
            if database.client is not None:
                await database.client.admin.command('ping')
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        # Try to reconnect
        await connect_to_mongo()

def is_database_connected() -> bool:
    """Check if database is connected"""
    return database.connected and database.database is not None