"""
Mongo Manager.

Reusable wrapper around MongoDB operations.
"""

from pymongo.collection import Collection

from apps.common.database.mongo import mongo


class MongoManager:
    """
    Provides reusable access to MongoDB collections.
    """

    @staticmethod
    def collection(name: str) -> Collection:
        """
        Return a MongoDB collection.
        """
        return mongo.get_collection(name)