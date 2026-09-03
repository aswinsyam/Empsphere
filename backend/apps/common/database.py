"""
MongoDB connection.

Single shared connection used by every app in EmpSphere.

Usage:
    from apps.common.database import mongo, get_collection

    users = get_collection("users")
"""

from pymongo import MongoClient
from pymongo.database import Database

from apps.common.settings import settings

_client = MongoClient(
    settings.MONGO_URI,
    maxPoolSize=50,
    minPoolSize=5,
    serverSelectionTimeoutMS=5000,
)

mongo: Database = _client[settings.DATABASE_NAME]


def get_collection(name: str):
    """Return a MongoDB collection by name."""
    return mongo[name]
