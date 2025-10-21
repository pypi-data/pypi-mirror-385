"""Storage backends for attachments."""

from .base import StorageBackend
from .azure import AzureBlobStorage
from .s3 import S3Storage
from .local import LocalStorage

__all__ = [
    "StorageBackend",
    "AzureBlobStorage",
    "S3Storage",
    "LocalStorage",
]
