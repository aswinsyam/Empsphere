"""
File storage manager.

Handles file uploads using Django's storage backend.
"""

import os

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from apps.common.core.defaults import MAX_UPLOAD_SIZE_MB
from apps.common.exceptions.custom_exception import ValidationException


class FileManager:
    """Saves and removes uploaded files."""

    @staticmethod
    def save(uploaded_file, directory: str) -> str:
        """Save a file under the given directory and return its path."""
        if uploaded_file.size > MAX_UPLOAD_SIZE_MB * 1024 * 1024:
            raise ValidationException(
                f"File size exceeds {MAX_UPLOAD_SIZE_MB}MB limit."
            )

        filename = default_storage.save(
            os.path.join(directory, uploaded_file.name),
            ContentFile(uploaded_file.read()),
        )

        return filename

    @staticmethod
    def delete(file_path: str) -> None:
        """Delete a stored file if it exists."""
        if file_path and default_storage.exists(file_path):
            default_storage.delete(file_path)
