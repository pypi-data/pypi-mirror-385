"""SWM Comments & Attachments - Generic comments and file attachments for FastAPI."""

from .models import Comment, Attachment, CommentReaction, CommentMention, Notification
from .schemas import (
    CommentCreate,
    CommentUpdate,
    CommentResponse,
    AttachmentCreate,
    AttachmentResponse,
    ReactionCreate,
    ReactionResponse,
    ReactionSummary,
    NotificationResponse,
    NotificationUpdate,
    NotificationQueryParams,
)
from .routers import create_comment_router, create_attachment_router
from .storage import StorageBackend, AzureBlobStorage, S3Storage, LocalStorage

__version__ = "0.3.1"
__all__ = [
    "Comment",
    "Attachment",
    "CommentReaction",
    "CommentMention",
    "Notification",
    "CommentCreate",
    "CommentUpdate",
    "CommentResponse",
    "AttachmentCreate",
    "AttachmentResponse",
    "ReactionCreate",
    "ReactionResponse",
    "ReactionSummary",
    "NotificationResponse",
    "NotificationUpdate",
    "NotificationQueryParams",
    "create_comment_router",
    "create_attachment_router",
    "StorageBackend",
    "AzureBlobStorage",
    "S3Storage",
    "LocalStorage",
]
