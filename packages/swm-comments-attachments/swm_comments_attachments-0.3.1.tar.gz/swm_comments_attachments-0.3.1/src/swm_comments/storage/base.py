"""Abstract base class for storage backends."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import BinaryIO


class StorageException(Exception):
    """Custom exception for storage operations."""

    pass


class StorageBackend(ABC):
    """Abstract base class for storage backends.

    All storage backends must implement these methods to provide
    a consistent interface for file upload, download, and management.
    """

    @abstractmethod
    async def upload_file(
        self,
        file_content: BinaryIO,
        storage_path: str,
        content_type: str,
        metadata: dict[str, str] | None = None,
    ) -> str:
        """Upload a file to the storage backend.

        Args:
            file_content: File content as binary stream
            storage_path: Relative path where file should be stored
            content_type: MIME type of the file
            metadata: Optional metadata to store with the file

        Returns:
            str: The storage path where file was uploaded

        Raises:
            StorageException: If upload fails
        """
        pass

    @abstractmethod
    async def download_file(self, storage_path: str) -> bytes:
        """Download a file from the storage backend.

        Args:
            storage_path: Relative path of the file

        Returns:
            bytes: File content as bytes

        Raises:
            StorageException: If download fails or file not found
        """
        pass

    @abstractmethod
    async def delete_file(self, storage_path: str) -> bool:
        """Delete a file from the storage backend.

        Args:
            storage_path: Relative path of the file to delete

        Returns:
            bool: True if deletion was successful

        Raises:
            StorageException: If deletion fails
        """
        pass

    @abstractmethod
    async def get_presigned_url(
        self,
        storage_path: str,
        expiry_seconds: int = 3600,
    ) -> str:
        """Generate a presigned URL for secure file access.

        Args:
            storage_path: Relative path of the file
            expiry_seconds: How long the URL should be valid (default: 1 hour)

        Returns:
            str: Presigned URL for file access

        Raises:
            StorageException: If URL generation fails
        """
        pass

    @abstractmethod
    async def file_exists(self, storage_path: str) -> bool:
        """Check if a file exists in the storage backend.

        Args:
            storage_path: Relative path to check

        Returns:
            bool: True if file exists, False otherwise
        """
        pass

    @abstractmethod
    async def get_file_size(self, storage_path: str) -> int:
        """Get the size of a file in bytes.

        Args:
            storage_path: Relative path of the file

        Returns:
            int: File size in bytes

        Raises:
            StorageException: If file not found or operation fails
        """
        pass

    def generate_storage_path(
        self,
        organisation_id: int,
        entity_type: str,
        entity_id: str,
        file_name: str,
    ) -> str:
        """Generate a standardized storage path for a file.

        Creates a path with format:
        {organisation_id}/{entity_type}/{entity_id}/{timestamp}_{filename}

        This ensures:
        - Organization-level isolation
        - Entity-specific grouping
        - Unique file names (timestamp prefix)
        - No path traversal issues

        Args:
            organisation_id: Organization ID for multi-tenancy
            entity_type: Type of entity (e.g., "task", "property")
            entity_id: ID of the entity
            file_name: Original file name

        Returns:
            str: Generated storage path

        Example:
            >>> backend.generate_storage_path(1, "task", "123", "document.pdf")
            "1/task/123/20250120_143052_document.pdf"
        """
        # Generate timestamp prefix to prevent conflicts
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

        # Sanitize file name to prevent path traversal
        safe_file_name = file_name.replace("/", "_").replace("\\", "_")

        # Build path with organization isolation
        return f"{organisation_id}/{entity_type}/{entity_id}/{timestamp}_{safe_file_name}"
