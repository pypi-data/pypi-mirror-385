"""Local filesystem storage backend for development."""

import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import BinaryIO

import aiofiles

from .base import StorageBackend, StorageException


class LocalStorage(StorageBackend):
    """Local filesystem storage backend for development and testing.

    Stores files in a local directory structure:
    base_path/
        ├── organisation_1/
        │   ├── task/
        │   │   └── 123/
        │   │       └── 20250120_143000_document.pdf
        │   └── property/
        └── organisation_2/

    Args:
        base_path: Root directory for file storage (default: ./uploads)
    """

    def __init__(self, base_path: str = "./uploads"):
        """Initialize local storage backend.

        Args:
            base_path: Root directory for file storage
        """
        self.base_path = Path(base_path)
        # Create base directory if it doesn't exist
        self.base_path.mkdir(parents=True, exist_ok=True)

    async def upload_file(
        self,
        file_content: BinaryIO,
        storage_path: str,
        content_type: str,
        metadata: dict[str, str] | None = None,
    ) -> str:
        """Upload a file to local filesystem.

        Args:
            file_content: File content as binary stream
            storage_path: Relative path where file should be stored
            content_type: MIME type (not used in local storage but kept for interface compatibility)
            metadata: Optional metadata (stored in .meta file alongside the file)

        Returns:
            str: The storage path where file was uploaded

        Raises:
            StorageException: If upload fails
        """
        try:
            # Get full path
            full_path = self.base_path / storage_path

            # Create parent directories
            full_path.parent.mkdir(parents=True, exist_ok=True)

            # Write file asynchronously
            async with aiofiles.open(full_path, "wb") as f:
                content = file_content.read()
                await f.write(content)

            # Store metadata if provided
            if metadata:
                meta_path = full_path.with_suffix(full_path.suffix + ".meta")
                async with aiofiles.open(meta_path, "w") as f:
                    import json

                    await f.write(json.dumps(metadata, indent=2))

            return storage_path

        except Exception as e:
            raise StorageException(f"Failed to upload file to local storage: {e}")

    async def download_file(self, storage_path: str) -> bytes:
        """Download a file from local filesystem.

        Args:
            storage_path: Relative path of the file

        Returns:
            bytes: File content as bytes

        Raises:
            StorageException: If download fails or file not found
        """
        try:
            full_path = self.base_path / storage_path

            if not full_path.exists():
                raise StorageException(f"File not found: {storage_path}")

            async with aiofiles.open(full_path, "rb") as f:
                return await f.read()

        except StorageException:
            raise
        except Exception as e:
            raise StorageException(f"Failed to download file from local storage: {e}")

    async def delete_file(self, storage_path: str) -> bool:
        """Delete a file from local filesystem.

        Args:
            storage_path: Relative path of the file to delete

        Returns:
            bool: True if deletion was successful

        Raises:
            StorageException: If deletion fails
        """
        try:
            full_path = self.base_path / storage_path

            if not full_path.exists():
                return False

            # Delete metadata file if exists
            meta_path = full_path.with_suffix(full_path.suffix + ".meta")
            if meta_path.exists():
                meta_path.unlink()

            # Delete main file
            full_path.unlink()
            return True

        except Exception as e:
            raise StorageException(f"Failed to delete file from local storage: {e}")

    async def get_presigned_url(
        self,
        storage_path: str,
        expiry_seconds: int = 3600,
    ) -> str:
        """Generate a presigned URL for local file access.

        For local storage, this just returns a file:// URL.
        In production, you'd use a temporary token or redirect through your API.

        Args:
            storage_path: Relative path of the file
            expiry_seconds: How long the URL should be valid (ignored for local)

        Returns:
            str: File URL

        Raises:
            StorageException: If file not found
        """
        try:
            full_path = self.base_path / storage_path

            if not full_path.exists():
                raise StorageException(f"File not found: {storage_path}")

            # For local dev, return absolute file path
            # In production with LocalStorage, you'd return an API endpoint
            return f"file://{full_path.absolute()}"

        except StorageException:
            raise
        except Exception as e:
            raise StorageException(f"Failed to generate presigned URL: {e}")

    async def file_exists(self, storage_path: str) -> bool:
        """Check if a file exists in local filesystem.

        Args:
            storage_path: Relative path to check

        Returns:
            bool: True if file exists, False otherwise
        """
        full_path = self.base_path / storage_path
        return full_path.exists()

    async def get_file_size(self, storage_path: str) -> int:
        """Get the size of a file in bytes.

        Args:
            storage_path: Relative path of the file

        Returns:
            int: File size in bytes

        Raises:
            StorageException: If file not found or operation fails
        """
        try:
            full_path = self.base_path / storage_path

            if not full_path.exists():
                raise StorageException(f"File not found: {storage_path}")

            return full_path.stat().st_size

        except StorageException:
            raise
        except Exception as e:
            raise StorageException(f"Failed to get file size: {e}")
