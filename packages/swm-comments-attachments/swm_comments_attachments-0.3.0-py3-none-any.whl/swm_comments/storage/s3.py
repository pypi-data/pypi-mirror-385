"""AWS S3 storage backend."""

from datetime import timedelta
from typing import BinaryIO

import boto3
from botocore.exceptions import ClientError

from .base import StorageBackend, StorageException


class S3Storage(StorageBackend):
    """AWS S3 storage backend.

    Stores files in AWS S3 with automatic presigned URL generation.

    Args:
        bucket_name: Name of the S3 bucket
        region: AWS region (e.g., 'us-east-1')
        access_key_id: AWS access key ID
        secret_access_key: AWS secret access key
    """

    def __init__(
        self,
        bucket_name: str,
        region: str = "us-east-1",
        access_key_id: str | None = None,
        secret_access_key: str | None = None,
    ):
        """Initialize S3 storage backend.

        Args:
            bucket_name: Name of the S3 bucket
            region: AWS region
            access_key_id: AWS access key ID (uses environment if not provided)
            secret_access_key: AWS secret access key (uses environment if not provided)
        """
        self.bucket_name = bucket_name
        self.region = region

        # Create S3 client
        session_kwargs = {"region_name": region}
        if access_key_id and secret_access_key:
            session_kwargs["aws_access_key_id"] = access_key_id
            session_kwargs["aws_secret_access_key"] = secret_access_key

        self.s3_client = boto3.client("s3", **session_kwargs)

        # Ensure bucket exists
        try:
            self.s3_client.head_bucket(Bucket=bucket_name)
        except ClientError:
            # Create bucket if it doesn't exist
            try:
                if region == "us-east-1":
                    self.s3_client.create_bucket(Bucket=bucket_name)
                else:
                    self.s3_client.create_bucket(
                        Bucket=bucket_name,
                        CreateBucketConfiguration={"LocationConstraint": region},
                    )
            except Exception as e:
                raise StorageException(f"Failed to create S3 bucket: {e}")

    async def upload_file(
        self,
        file_content: BinaryIO,
        storage_path: str,
        content_type: str,
        metadata: dict[str, str] | None = None,
    ) -> str:
        """Upload a file to S3.

        Args:
            file_content: File content as binary stream
            storage_path: S3 key where file should be stored
            content_type: MIME type of the file
            metadata: Optional metadata to attach to the object

        Returns:
            str: The storage path where file was uploaded

        Raises:
            StorageException: If upload fails
        """
        try:
            # Read file content
            content = file_content.read()

            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=storage_path,
                Body=content,
                ContentType=content_type,
                Metadata=metadata or {},
            )

            return storage_path

        except Exception as e:
            raise StorageException(f"Failed to upload file to S3: {e}")

    async def download_file(self, storage_path: str) -> bytes:
        """Download a file from S3.

        Args:
            storage_path: S3 key of the file

        Returns:
            bytes: File content as bytes

        Raises:
            StorageException: If download fails or file not found
        """
        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=storage_path)
            return response["Body"].read()

        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchKey":
                raise StorageException(f"File not found: {storage_path}")
            raise StorageException(f"Failed to download file from S3: {e}")
        except Exception as e:
            raise StorageException(f"Failed to download file from S3: {e}")

    async def delete_file(self, storage_path: str) -> bool:
        """Delete a file from S3.

        Args:
            storage_path: S3 key of the file to delete

        Returns:
            bool: True if deletion was successful

        Raises:
            StorageException: If deletion fails
        """
        try:
            # Check if object exists
            try:
                self.s3_client.head_object(Bucket=self.bucket_name, Key=storage_path)
            except ClientError as e:
                if e.response["Error"]["Code"] == "404":
                    return False
                raise

            # Delete object
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=storage_path)
            return True

        except Exception as e:
            raise StorageException(f"Failed to delete file from S3: {e}")

    async def get_presigned_url(
        self,
        storage_path: str,
        expiry_seconds: int = 3600,
    ) -> str:
        """Generate a presigned URL for S3.

        Args:
            storage_path: S3 key of the file
            expiry_seconds: How long the URL should be valid (default: 1 hour)

        Returns:
            str: Presigned URL for accessing the file

        Raises:
            StorageException: If URL generation fails
        """
        try:
            # Check if object exists
            try:
                self.s3_client.head_object(Bucket=self.bucket_name, Key=storage_path)
            except ClientError as e:
                if e.response["Error"]["Code"] == "404":
                    raise StorageException(f"File not found: {storage_path}")
                raise

            # Generate presigned URL
            url = self.s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket_name, "Key": storage_path},
                ExpiresIn=expiry_seconds,
            )

            return url

        except StorageException:
            raise
        except Exception as e:
            raise StorageException(f"Failed to generate presigned URL: {e}")

    async def file_exists(self, storage_path: str) -> bool:
        """Check if a file exists in S3.

        Args:
            storage_path: S3 key to check

        Returns:
            bool: True if file exists, False otherwise
        """
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=storage_path)
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                return False
            return False
        except Exception:
            return False

    async def get_file_size(self, storage_path: str) -> int:
        """Get the size of a file in bytes.

        Args:
            storage_path: S3 key of the file

        Returns:
            int: File size in bytes

        Raises:
            StorageException: If file not found or operation fails
        """
        try:
            response = self.s3_client.head_object(Bucket=self.bucket_name, Key=storage_path)
            return response["ContentLength"]

        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                raise StorageException(f"File not found: {storage_path}")
            raise StorageException(f"Failed to get file size: {e}")
        except Exception as e:
            raise StorageException(f"Failed to get file size: {e}")
