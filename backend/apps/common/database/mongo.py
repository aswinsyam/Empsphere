"""
MongoDB Connection Manager.

Provides a singleton MongoDB connection that is reused
throughout the application.

Usage:
    from apps.common.database.mongo import mongo

    users_collection = mongo.get_collection("users")
"""

from __future__ import annotations

from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection

from apps.common.config.settings import settings


class MongoConnection:
    """
    Singleton MongoDB connection manager.
    """

    _instance = None
    _client: MongoClient | None = None
    _database: Database | None = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)

            cls._client = MongoClient(
                settings.MONGO_URI,
                maxPoolSize=50,
                minPoolSize=5,
                serverSelectionTimeoutMS=5000,
            )

            cls._database = cls._client[settings.DATABASE_NAME]

        return cls._instance

    @property
    def database(self) -> Database:
        """
        Returns the active MongoDB database.
        """
        return self._database

    def get_collection(self, collection_name: str) -> Collection:
        """
        Returns a MongoDB collection.

        Args:
            collection_name (str): Collection name.

        Returns:
            Collection
        """
        return self._database[collection_name]


mongo = MongoConnection()
