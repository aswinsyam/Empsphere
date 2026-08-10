"""
Sequence Repository.

Handles atomic sequence generation for employee codes.
"""

from pymongo import ReturnDocument

from apps.common.database.mongo import mongo


class SequenceRepository:
    """
    Repository for generating sequential values.
    """

    COLLECTION_NAME = "sequences"

    def __init__(self):
        self.collection = mongo.get_collection(self.COLLECTION_NAME)

    def get_next_sequence(self, sequence_name: str) -> int:
        """
        Atomically increments and returns the next sequence value.
        """

        result = self.collection.find_one_and_update(
            {"_id": sequence_name},
            {"$inc": {"value": 1}},
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )

        return result["value"]