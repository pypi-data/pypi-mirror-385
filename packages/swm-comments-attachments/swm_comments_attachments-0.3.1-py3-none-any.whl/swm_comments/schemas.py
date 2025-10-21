"""Pydantic schemas for comments and attachments."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator


# ============================================================================
# Comment Schemas
# ============================================================================


class CommentBase(BaseModel):
    """Base schema for comments with common fields."""

    entity_type: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Type of entity: 'task', 'property', 'service_request', etc.",
        examples=["task", "property", "invoice"],
    )
    entity_id: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="ID of the entity this comment belongs to",
        examples=["123", "prop-456"],
    )
    parent_comment_id: int | None = Field(
        default=None,
        description="Optional parent comment ID for threaded replies",
    )
    comment_text: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="The actual comment text",
    )
    is_internal: bool = Field(
        default=False,
        description="If True, only internal users can see this comment",
    )
    context: dict[str, Any] | None = Field(
        default=None,
        description="Additional metadata like mentions, tags, etc.",
    )


class CommentCreate(CommentBase):
    """Schema for creating a new comment."""

    pass


class CommentUpdate(BaseModel):
    """Schema for updating an existing comment."""

    comment_text: str | None = Field(
        default=None,
        min_length=1,
        max_length=5000,
        description="Updated comment text",
    )
    is_internal: bool | None = Field(
        default=None,
        description="Updated visibility",
    )
    context: dict[str, Any] | None = Field(
        default=None,
        description="Updated metadata",
    )


class CommentResponse(CommentBase):
    """Schema for comment responses (includes generated fields)."""

    id: int = Field(..., description="Comment ID")
    organisation_id: int = Field(..., description="Organization ID")
    created_by_id: int = Field(..., description="User ID who created this comment")
    created_at: datetime = Field(..., description="When comment was created")
    updated_at: datetime | None = Field(None, description="When comment was last updated")
    is_deleted: bool = Field(False, description="Soft delete flag")
    attachment_count: int = Field(default=0, description="Number of attachments on this comment")
    reply_count: int = Field(default=0, description="Number of replies to this comment")

    model_config = {"from_attributes": True}


# ============================================================================
# Attachment Schemas
# ============================================================================


class AttachmentBase(BaseModel):
    """Base schema for attachments with common fields."""

    entity_type: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Type of entity this attachment belongs to",
        examples=["task", "property"],
    )
    entity_id: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="ID of the entity this attachment belongs to",
    )
    comment_id: int | None = Field(
        default=None,
        description="Optional FK to comment for hierarchical attachments",
    )
    description: str | None = Field(
        default=None,
        max_length=500,
        description="Optional file description",
    )
    context: dict[str, Any] | None = Field(
        default=None,
        description="Additional metadata",
    )


class AttachmentCreate(AttachmentBase):
    """Schema for creating a new attachment (metadata only, file uploaded separately)."""

    file_name: str = Field(..., min_length=1, max_length=255, description="Original filename")
    file_size: int = Field(..., gt=0, description="File size in bytes")
    content_type: str = Field(
        ..., min_length=1, max_length=100, description="MIME type (e.g., 'application/pdf')"
    )

    @field_validator("file_size")
    @classmethod
    def validate_file_size(cls, v: int) -> int:
        """Validate file size is within limits (max 100MB)."""
        max_size = 100 * 1024 * 1024  # 100 MB
        if v > max_size:
            raise ValueError(f"File size exceeds maximum allowed size of {max_size} bytes")
        return v

    @field_validator("content_type")
    @classmethod
    def validate_content_type(cls, v: str) -> str:
        """Validate content type is in allowed list."""
        allowed_types = [
            "application/pdf",
            "image/jpeg",
            "image/png",
            "image/gif",
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/vnd.ms-excel",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "text/plain",
            "text/csv",
        ]
        if v not in allowed_types:
            raise ValueError(f"Content type '{v}' is not allowed")
        return v


class AttachmentResponse(AttachmentBase):
    """Schema for attachment responses (includes generated fields)."""

    id: int = Field(..., description="Attachment ID")
    organisation_id: int = Field(..., description="Organization ID")
    file_name: str = Field(..., description="Original filename")
    file_size: int = Field(..., description="File size in bytes")
    content_type: str = Field(..., description="MIME type")
    storage_backend: str = Field(..., description="Storage type: 'azure', 's3', 'local'")
    document_type_id: int | None = Field(None, description="Optional FK to document_types table")
    document_category: str = Field(default="normal", description="Document access category: 'normal' or 'restricted'")
    virus_scan_status: str = Field(default="clean", description="Virus scan status")
    checksum: str | None = Field(None, description="File checksum (SHA-256)")
    uploaded_by_id: int = Field(..., description="User ID who uploaded this file")
    uploaded_at: datetime = Field(..., description="When file was uploaded")
    is_deleted: bool = Field(False, description="Soft delete flag")

    model_config = {"from_attributes": True}


class AttachmentDownloadURL(BaseModel):
    """Schema for presigned download URLs."""

    url: str = Field(..., description="Presigned URL for downloading the file")
    expires_at: datetime = Field(..., description="When the URL expires")
    file_name: str = Field(..., description="Original filename")


# ============================================================================
# Query Parameters
# ============================================================================


class CommentQueryParams(BaseModel):
    """Query parameters for listing comments."""

    entity_type: str | None = Field(None, description="Filter by entity type")
    entity_id: str | None = Field(None, description="Filter by entity ID")
    parent_comment_id: int | None = Field(None, description="Filter by parent comment ID (get replies)")
    include_internal: bool = Field(
        default=True, description="Include internal comments (admin/internal users only)"
    )
    include_deleted: bool = Field(default=False, description="Include soft-deleted comments")
    skip: int = Field(default=0, ge=0, description="Number of records to skip")
    limit: int = Field(default=100, ge=1, le=1000, description="Maximum number of records to return")


class AttachmentQueryParams(BaseModel):
    """Query parameters for listing attachments."""

    entity_type: str | None = Field(None, description="Filter by entity type")
    entity_id: str | None = Field(None, description="Filter by entity ID")
    comment_id: int | None = Field(None, description="Filter by comment ID for hierarchical attachments")
    include_deleted: bool = Field(default=False, description="Include soft-deleted attachments")
    skip: int = Field(default=0, ge=0, description="Number of records to skip")
    limit: int = Field(default=100, ge=1, le=1000, description="Maximum number of records to return")


# ============================================================================
# Comment Reaction Schemas
# ============================================================================


class ReactionType(str):
    """Valid reaction types."""

    THUMBS_UP = "thumbs_up"
    HEART = "heart"
    SMILE = "smile"
    PARTY = "party"
    ROCKET = "rocket"
    EYES = "eyes"


class ReactionCreate(BaseModel):
    """Schema for creating a reaction."""

    reaction_type: str = Field(
        ...,
        description="Type of reaction: thumbs_up, heart, smile, party, rocket, eyes",
        examples=["thumbs_up", "heart"],
    )

    @field_validator("reaction_type")
    @classmethod
    def validate_reaction_type(cls, v: str) -> str:
        """Validate reaction type is one of the allowed values."""
        allowed = ["thumbs_up", "heart", "smile", "party", "rocket", "eyes"]
        if v not in allowed:
            raise ValueError(f"reaction_type must be one of: {', '.join(allowed)}")
        return v


class ReactionResponse(BaseModel):
    """Schema for reaction responses."""

    id: int = Field(..., description="Reaction ID")
    comment_id: int = Field(..., description="Comment this reaction belongs to")
    user_id: int = Field(..., description="User who added this reaction")
    reaction_type: str = Field(..., description="Type of reaction")
    organisation_id: int = Field(..., description="Organization ID")
    created_at: datetime = Field(..., description="When reaction was created")

    model_config = {"from_attributes": True}


class ReactionSummary(BaseModel):
    """Summary of reactions for a comment."""

    reaction_type: str = Field(..., description="Type of reaction")
    count: int = Field(..., description="Number of users who reacted")
    user_ids: list[int] = Field(default_factory=list, description="List of user IDs who reacted")
    current_user_reacted: bool = Field(default=False, description="Whether current user has this reaction")


# ============================================================================
# Notification Schemas
# ============================================================================


class NotificationResponse(BaseModel):
    """Schema for notification responses."""

    id: int = Field(..., description="Notification ID")
    user_id: int = Field(..., description="User this notification is for")
    notification_type: str = Field(..., description="Type of notification")
    title: str = Field(..., description="Notification title")
    message: str = Field(..., description="Notification message")
    reference_type: str | None = Field(None, description="Type of referenced entity")
    reference_id: int | None = Field(None, description="ID of referenced entity")
    link_url: str | None = Field(None, description="URL to navigate to")
    is_read: bool = Field(..., description="Whether notification has been read")
    read_at: datetime | None = Field(None, description="When notification was read")
    organisation_id: int = Field(..., description="Organization ID")
    created_at: datetime = Field(..., description="When notification was created")

    model_config = {"from_attributes": True}


class NotificationUpdate(BaseModel):
    """Schema for updating notification (mark as read)."""

    is_read: bool = Field(..., description="Mark as read/unread")


class NotificationQueryParams(BaseModel):
    """Query parameters for listing notifications."""

    is_read: bool | None = Field(None, description="Filter by read status")
    notification_type: str | None = Field(None, description="Filter by notification type")
    skip: int = Field(default=0, ge=0, description="Number of records to skip")
    limit: int = Field(default=50, ge=1, le=200, description="Maximum number of records to return")
