"""Azure Blob Storage backend for production."""

from datetime import datetime, timedelta
from typing import BinaryIO

from azure.storage.blob.aio import BlobServiceClient, ContainerClient
from azure.storage.blob import BlobSasPermissions, generate_blob_sas

from .base import StorageBackend, StorageException


class AzureBlobStorage(StorageBackend):
    """Azure Blob Storage backend for production deployments.

    Stores files in Azure Blob Storage with automatic presigned URL generation.

    Args:
        connection_string: Azure Storage connection string
        container_name: Name of the blob container
    """

    def __init__(self, connection_string: str, container_name: str):
        """Initialize Azure Blob Storage backend.

        Args:
            connection_string: Azure Storage connection string
            container_name: Name of the blob container
        """
        self.connection_string = connection_string
        self.container_name = container_name
        self._blob_service_client: BlobServiceClient | None = None
        self._container_client: ContainerClient | None = None

    async def _get_blob_service_client(self) -> BlobServiceClient:
        """Get or create blob service client."""
        if self._blob_service_client is None:
            self._blob_service_client = BlobServiceClient.from_connection_string(
                self.connection_string
            )
        return self._blob_service_client

    async def _get_container_client(self) -> ContainerClient:
        """Get or create container client."""
        if self._container_client is None:
            blob_service_client = await self._get_blob_service_client()
            self._container_client = blob_service_client.get_container_client(
                self.container_name
            )
            # Create container if it doesn't exist
            try:
                await self._container_client.create_container()
            except Exception:
                # Container already exists, which is fine
                pass
        return self._container_client

    async def upload_file(
        self,
        file_content: BinaryIO,
        storage_path: str,
        content_type: str,
        metadata: dict[str, str] | None = None,
    ) -> str:
        """Upload a file to Azure Blob Storage.

        Args:
            file_content: File content as binary stream
            storage_path: Blob path where file should be stored
            content_type: MIME type of the file
            metadata: Optional metadata to attach to the blob

        Returns:
            str: The storage path where file was uploaded

        Raises:
            StorageException: If upload fails
        """
        try:
            container_client = await self._get_container_client()
            blob_client = container_client.get_blob_client(storage_path)

            # Read file content
            content = file_content.read()

            # Upload to blob storage
            await blob_client.upload_blob(
                content,
                overwrite=True,
                content_settings={
                    "content_type": content_type,
                },
                metadata=metadata or {},
            )

            return storage_path

        except Exception as e:
            raise StorageException(f"Failed to upload file to Azure Blob Storage: {e}")

    async def download_file(self, storage_path: str) -> bytes:
        """Download a file from Azure Blob Storage.

        Args:
            storage_path: Blob path of the file

        Returns:
            bytes: File content as bytes

        Raises:
            StorageException: If download fails or file not found
        """
        try:
            container_client = await self._get_container_client()
            blob_client = container_client.get_blob_client(storage_path)

            # Download blob
            stream = await blob_client.download_blob()
            content = await stream.readall()
            return content

        except Exception as e:
            raise StorageException(f"Failed to download file from Azure Blob Storage: {e}")

    async def delete_file(self, storage_path: str) -> bool:
        """Delete a file from Azure Blob Storage.

        Args:
            storage_path: Blob path of the file to delete

        Returns:
            bool: True if deletion was successful

        Raises:
            StorageException: If deletion fails
        """
        try:
            container_client = await self._get_container_client()
            blob_client = container_client.get_blob_client(storage_path)

            # Check if blob exists
            if not await blob_client.exists():
                return False

            # Delete blob
            await blob_client.delete_blob()
            return True

        except Exception as e:
            raise StorageException(f"Failed to delete file from Azure Blob Storage: {e}")

    async def get_presigned_url(
        self,
        storage_path: str,
        expiry_seconds: int = 3600,
    ) -> str:
        """Generate a presigned URL (SAS URL) for Azure Blob Storage.

        Args:
            storage_path: Blob path of the file
            expiry_seconds: How long the URL should be valid (default: 1 hour)

        Returns:
            str: Presigned SAS URL for accessing the file

        Raises:
            StorageException: If URL generation fails
        """
        try:
            container_client = await self._get_container_client()
            blob_client = container_client.get_blob_client(storage_path)

            # Check if blob exists
            if not await blob_client.exists():
                raise StorageException(f"File not found: {storage_path}")

            # Extract account key from connection string
            account_name = None
            account_key = None
            for part in self.connection_string.split(";"):
                if part.startswith("AccountName="):
                    account_name = part.split("=", 1)[1]
                elif part.startswith("AccountKey="):
                    account_key = part.split("=", 1)[1]

            if not account_name or not account_key:
                raise StorageException("Could not extract account credentials from connection string")

            # Generate SAS token
            sas_token = generate_blob_sas(
                account_name=account_name,
                account_key=account_key,
                container_name=self.container_name,
                blob_name=storage_path,
                permission=BlobSasPermissions(read=True),
                expiry=datetime.utcnow() + timedelta(seconds=expiry_seconds),
            )

            # Construct full URL with SAS token
            blob_url = blob_client.url
            presigned_url = f"{blob_url}?{sas_token}"

            return presigned_url

        except StorageException:
            raise
        except Exception as e:
            raise StorageException(f"Failed to generate presigned URL: {e}")

    async def file_exists(self, storage_path: str) -> bool:
        """Check if a file exists in Azure Blob Storage.

        Args:
            storage_path: Blob path to check

        Returns:
            bool: True if file exists, False otherwise
        """
        try:
            container_client = await self._get_container_client()
            blob_client = container_client.get_blob_client(storage_path)
            return await blob_client.exists()
        except Exception:
            return False

    async def get_file_size(self, storage_path: str) -> int:
        """Get the size of a file in bytes.

        Args:
            storage_path: Blob path of the file

        Returns:
            int: File size in bytes

        Raises:
            StorageException: If file not found or operation fails
        """
        try:
            container_client = await self._get_container_client()
            blob_client = container_client.get_blob_client(storage_path)

            # Get blob properties
            properties = await blob_client.get_blob_properties()
            return properties.size

        except Exception as e:
            raise StorageException(f"Failed to get file size: {e}")

    async def close(self) -> None:
        """Close the blob service client."""
        if self._blob_service_client:
            await self._blob_service_client.close()
            self._blob_service_client = None
            self._container_client = None
