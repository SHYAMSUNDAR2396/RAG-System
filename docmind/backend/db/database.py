import motor.motor_asyncio
import os
import logging

logger = logging.getLogger(__name__)

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")

try:
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
    db = client.docmind
    chat_sessions_collection = db.get_collection("chat_sessions")
    users_collection = db.get_collection("users")
    logger.info("Connected to MongoDB")
except Exception as e:
    logger.error("Failed to connect to MongoDB: %s", e)
    chat_sessions_collection = None
    users_collection = None
