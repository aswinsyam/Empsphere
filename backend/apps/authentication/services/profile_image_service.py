"""
Profile Image Service.
Handles profile image storage and retrieval using MongoDB GridFS.
"""
from __future__ import annotations

from typing import Optional

from bson import ObjectId
from gridfs import GridFS, NoFile

from apps.common.core.collections import Collections
from apps.common.database.mongo import mongo


class ProfileImageService:
    """Service for storing and retrieving profile images in MongoDB GridFS."""

    ALLOWED_CONTENT_TYPES = {
        "image/jpeg",
        "image/png",
        "image/webp",
        "image/gif",
    }
    MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB

    def __init__(self):
        self._fs = GridFS(mongo.get_collection(Collections.USERS).database)

    def validate_file(self, uploaded_file) -> None:
        """Validate uploaded file type and size."""
        content_type = getattr(uploaded_file, "content_type", "") or ""
        if content_type not in self.ALLOWED_CONTENT_TYPES:
            raise ValueError(
                f"Unsupported image type: {content_type}. "
                f"Allowed: {', '.join(sorted(self.ALLOWED_CONTENT_TYPES))}."
            )
        size = getattr(uploaded_file, "size", None)
        if size is not None and size > self.MAX_FILE_SIZE_BYTES:
            raise ValueError(
                f"Image size exceeds {self.MAX_FILE_SIZE_BYTES // (1024 * 1024)} MB limit."
            )

    def upload(self, user_id: str, uploaded_file) -> ObjectId:
        """Store an uploaded profile image in GridFS.

        If the user already has a profile image, the old GridFS file is
        deleted before storing the new one.

        Returns the GridFS file ObjectId.
        """
        self.validate_file(uploaded_file)
        users_collection = mongo.get_collection(Collections.USERS)
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise ValueError("User not found.")

        old_file_id = user.get("profile_image_id")
        if old_file_id:
            try:
                self._fs.delete(ObjectId(old_file_id))
            except NoFile:
                pass

        filename = uploaded_file.name
        content_type = getattr(uploaded_file, "content_type", "application/octet-stream")
        data = uploaded_file.read()

        file_id = self._fs.put(
            data,
            filename=filename,
            content_type=content_type,
            metadata={"user_id": user_id},
        )

        users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"profile_image_id": ObjectId(file_id)}},
        )

        return ObjectId(file_id)

    def get(self, file_id: str | ObjectId) -> Optional[dict]:
        """Retrieve a GridFS file by its ObjectId.

        Returns a dict with `data`, `filename`, `content_type`, or None.
        """
        try:
            grid_file = self._fs.get(ObjectId(file_id))
            return {
                "data": grid_file.read(),
                "filename": grid_file.filename,
                "content_type": grid_file.content_type or "application/octet-stream",
            }
        except NoFile:
            return None

    def delete(self, file_id: str | ObjectId) -> None:
        """Delete a GridFS file by its ObjectId."""
        try:
            self._fs.delete(ObjectId(file_id))
        except NoFile:
            pass

    def delete_by_user_id(self, user_id: str | ObjectId) -> None:
        """Delete the profile image for a user from GridFS."""
        users_collection = mongo.get_collection(Collections.USERS)
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        if user and user.get("profile_image_id"):
            try:
                self._fs.delete(ObjectId(user["profile_image_id"]))
            except NoFile:
                pass
            users_collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"profile_image_id": None}},
            )
