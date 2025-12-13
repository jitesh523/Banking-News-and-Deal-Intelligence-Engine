from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from app.core.config import get_settings
from loguru import logger

settings = get_settings()


class Database:
    """MongoDB database connection manager."""
    
    client: AsyncIOMotorClient = None
    db = None
    
    @classmethod
    async def connect_db(cls):
        """Connect to MongoDB."""
        try:
            cls.client = AsyncIOMotorClient(settings.mongodb_uri)
            cls.db = cls.client[settings.mongodb_db_name]
            
            # Test connection
            await cls.client.admin.command('ping')
            logger.info(f"Connected to MongoDB: {settings.mongodb_db_name}")
            
            # Create indexes
            await cls.create_indexes()
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    @classmethod
    async def close_db(cls):
        """Close MongoDB connection."""
        if cls.client:
            cls.client.close()
            logger.info("Closed MongoDB connection")
    
    @classmethod
    async def create_indexes(cls):
        """Create database indexes for performance."""
        try:
            # Articles collection indexes
            await cls.db.articles.create_index("article_id", unique=True)
            await cls.db.articles.create_index("published_date")
            await cls.db.articles.create_index("source")
            await cls.db.articles.create_index([("title", "text"), ("content", "text")])
            
            logger.info("Created database indexes")
        except Exception as e:
            logger.warning(f"Index creation warning: {e}")
    
    @classmethod
    def get_database(cls):
        """Get database instance."""
        return cls.db


# Synchronous client for non-async operations
def get_sync_db():
    """Get synchronous MongoDB client."""
    client = MongoClient(settings.mongodb_uri)
    return client[settings.mongodb_db_name]
