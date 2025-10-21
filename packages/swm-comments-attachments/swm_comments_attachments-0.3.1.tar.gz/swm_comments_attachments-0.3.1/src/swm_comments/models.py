"""SQLAlchemy models for comments and attachments."""

from datetime import datetime
from typing import Any

from sqlalchemy import JSON, Boolean, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all models."""

    pass


class Comment(Base):
    """Generic comment model that can be attached to any entity.

    This model uses entity_type and entity_id for polymorphic associations,
    allowing comments to be added to tasks, properties, service requests, etc.

    Example:
        # Comment on a task
        Comment(
            entity_type="task",
            entity_id="123",
            comment_text="This task is blocked",
            organisation_id=1,
            created_by_id=5
        )

        # Comment on a property
        Comment(
            entity_type="property",
            entity_id="456",
            comment_text="Property needs inspection",
            organisation_id=1,
            created_by_id=5
        )
    """

    __tablename__ = "comments"

    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Entity association (polymorphic)
    entity_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="Type of entity: 'task', 'property', 'service_request', etc.",
    )
    entity_id: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="ID of the entity this comment belongs to",
    )

    # Threading support (optional parent comment for replies)
    parent_comment_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("comments.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=True,
        index=True,
        comment="Optional FK to parent comment for threaded replies",
    )

    # Multi-tenancy
    organisation_id: Mapped[int] = mapped_column(
        Integer, nullable=False, index=True, comment="Organization this comment belongs to"
    )

    # Comment content
    comment_text: Mapped[str] = mapped_column(
        Text, nullable=False, comment="The actual comment text"
    )

    # Visibility control
    is_internal: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        comment="If True, only internal users can see this comment",
    )

    # Optional context (JSON for flexibility)
    context: Mapped[dict[str, Any] | None] = mapped_column(
        JSON,
        nullable=True,
        comment="Additional metadata like mentions, tags, etc.",
    )

    # Audit fields
    created_by_id: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="User ID who created this comment"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, comment="When comment was created"
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True, onupdate=datetime.utcnow, comment="When comment was last updated"
    )

    # Soft delete
    is_deleted: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, comment="Soft delete flag"
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True, comment="When comment was deleted"
    )
    deleted_by_id: Mapped[int | None] = mapped_column(
        Integer, nullable=True, comment="User ID who deleted this comment"
    )

    # Relationships
    attachments: Mapped[list["Attachment"]] = relationship(
        "Attachment",
        back_populates="comment",
        cascade="all, delete-orphan",
        foreign_keys="Attachment.comment_id",
    )
    reactions: Mapped[list["CommentReaction"]] = relationship(
        "CommentReaction",
        back_populates="comment",
        cascade="all, delete-orphan",
        foreign_keys="CommentReaction.comment_id",
    )
    mentions: Mapped[list["CommentMention"]] = relationship(
        "CommentMention",
        back_populates="comment",
        cascade="all, delete-orphan",
        foreign_keys="CommentMention.comment_id",
    )
    # Threading relationships
    parent: Mapped["Comment | None"] = relationship(
        "Comment",
        remote_side="Comment.id",
        back_populates="replies",
        foreign_keys=[parent_comment_id],
    )
    replies: Mapped[list["Comment"]] = relationship(
        "Comment",
        back_populates="parent",
        cascade="all, delete-orphan",
        foreign_keys="Comment.parent_comment_id",
    )

    # Composite index for efficient queries
    __table_args__ = (
        # Index for finding all comments for a specific entity
        {"mysql_engine": "InnoDB"},
    )

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"<Comment(id={self.id}, entity_type={self.entity_type}, "
            f"entity_id={self.entity_id}, organisation_id={self.organisation_id})>"
        )


class Attachment(Base):
    """Generic attachment model that can be attached to any entity.

    Stores file metadata and references to the actual file in blob storage.
    Supports multiple storage backends (Azure, S3, local).

    Example:
        # Document attached to a task
        Attachment(
            entity_type="task",
            entity_id="123",
            file_name="passport.pdf",
            file_size=2048576,
            content_type="application/pdf",
            storage_backend="azure",
            storage_path="org1/tasks/123/passport.pdf",
            organisation_id=1,
            uploaded_by_id=5
        )
    """

    __tablename__ = "attachments"

    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Entity association (polymorphic)
    entity_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="Type of entity: 'task', 'property', etc.",
    )
    entity_id: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="ID of the entity this attachment belongs to",
    )

    # Hierarchical association (optional)
    comment_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("comments.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=True,
        index=True,
        comment="Optional FK to comments table for hierarchical attachments",
    )

    # Multi-tenancy
    organisation_id: Mapped[int] = mapped_column(
        Integer, nullable=False, index=True, comment="Organization this attachment belongs to"
    )

    # File metadata
    file_name: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="Original filename"
    )
    file_size: Mapped[int] = mapped_column(Integer, nullable=False, comment="File size in bytes")
    content_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="MIME type (e.g., 'application/pdf', 'image/jpeg')",
    )

    # Storage backend info
    storage_backend: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Storage type: 'azure', 's3', 'local'",
    )
    storage_path: Mapped[str] = mapped_column(
        String(500), nullable=False, comment="Path/key in storage backend"
    )
    storage_container: Mapped[str | None] = mapped_column(
        String(100), nullable=True, comment="Container/bucket name (for Azure/S3)"
    )

    # Document classification
    document_type_id: Mapped[int | None] = mapped_column(
        Integer, nullable=True, comment="Optional FK to document_types table"
    )
    document_category: Mapped[str] = mapped_column(
        Enum("normal", "restricted", name="document_category_enum"),
        nullable=False,
        default="normal",
        server_default="normal",
        index=True,
        comment="Document access category",
    )
    virus_scan_status: Mapped[str] = mapped_column(
        Enum("clean", "infected", "quarantined", "skipped", "pending", name="virus_scan_status_enum"),
        nullable=False,
        default="clean",
        server_default="clean",
        comment="Virus scan status",
    )
    checksum: Mapped[str | None] = mapped_column(
        String(64), nullable=True, comment="File checksum (SHA-256) for integrity verification"
    )

    # Optional fields
    description: Mapped[str | None] = mapped_column(Text, nullable=True, comment="File description")
    context: Mapped[dict[str, Any] | None] = mapped_column(
        JSON, nullable=True, comment="Additional metadata"
    )

    # Audit fields
    uploaded_by_id: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="User ID who uploaded this file"
    )
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, comment="When file was uploaded"
    )

    # Soft delete
    is_deleted: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, comment="Soft delete flag"
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True, comment="When attachment was deleted"
    )
    deleted_by_id: Mapped[int | None] = mapped_column(
        Integer, nullable=True, comment="User ID who deleted this attachment"
    )

    # Relationships
    comment: Mapped["Comment | None"] = relationship(
        "Comment",
        back_populates="attachments",
        foreign_keys=[comment_id],
    )

    # Composite index for efficient queries
    __table_args__ = ({"mysql_engine": "InnoDB"},)

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"<Attachment(id={self.id}, entity_type={self.entity_type}, "
            f"entity_id={self.entity_id}, file_name={self.file_name})>"
        )


class CommentMention(Base):
    """Track @mentions in comments.

    When a user mentions another user in a comment (e.g., @username),
    a record is created to track who was mentioned and by whom.

    Example:
        # User 5 mentions User 10 in a comment
        CommentMention(
            comment_id=123,
            mentioned_user_id=10,
            mentioned_by_user_id=5,
            organisation_id=1
        )
    """

    __tablename__ = "comment_mentions"

    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Comment association
    comment_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("comments.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
        comment="FK to comments table",
    )

    # User who was mentioned
    mentioned_user_id: Mapped[int] = mapped_column(
        Integer, nullable=False, index=True, comment="User ID who was mentioned"
    )

    # User who mentioned
    mentioned_by_user_id: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="User ID who created the mention"
    )

    # Multi-tenancy
    organisation_id: Mapped[int] = mapped_column(
        Integer, nullable=False, index=True, comment="Organization this mention belongs to"
    )

    # Audit fields
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, comment="When mention was created"
    )

    # Relationships
    comment: Mapped["Comment"] = relationship(
        "Comment",
        back_populates="mentions",
        foreign_keys=[comment_id],
    )

    # Composite index and unique constraint
    __table_args__ = ({"mysql_engine": "InnoDB"},)

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"<CommentMention(id={self.id}, comment_id={self.comment_id}, "
            f"mentioned_user_id={self.mentioned_user_id})>"
        )


class Notification(Base):
    """General notification system for users.

    Supports various notification types: mentions, replies, reactions, assignments, etc.

    Example:
        # Notify user they were mentioned
        Notification(
            user_id=10,
            notification_type="mention",
            title="You were mentioned",
            message="User #5 mentioned you in a comment",
            reference_type="comment",
            reference_id=123,
            link_url="/tasks/456",
            organisation_id=1
        )
    """

    __tablename__ = "notifications"

    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # User this notification is for
    user_id: Mapped[int] = mapped_column(
        Integer, nullable=False, index=True, comment="User ID this notification is for"
    )

    # Notification details
    notification_type: Mapped[str] = mapped_column(
        Enum("mention", "reply", "reaction", "assignment", name="notification_type_enum"),
        nullable=False,
        comment="Type of notification",
    )
    title: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="Short notification title"
    )
    message: Mapped[str] = mapped_column(Text, nullable=False, comment="Notification message")

    # Reference to related entity
    reference_type: Mapped[str | None] = mapped_column(
        String(50), nullable=True, comment="Type of referenced entity (e.g., 'comment', 'task')"
    )
    reference_id: Mapped[int | None] = mapped_column(
        Integer, nullable=True, comment="ID of referenced entity"
    )
    link_url: Mapped[str | None] = mapped_column(
        String(500), nullable=True, comment="URL to navigate to when notification is clicked"
    )

    # Read status
    is_read: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, index=True, comment="Whether notification has been read"
    )
    read_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True, comment="When notification was read"
    )

    # Multi-tenancy
    organisation_id: Mapped[int] = mapped_column(
        Integer, nullable=False, index=True, comment="Organization this notification belongs to"
    )

    # Audit fields
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, index=True, comment="When notification was created"
    )

    # Composite index for efficient queries
    __table_args__ = ({"mysql_engine": "InnoDB"},)

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"<Notification(id={self.id}, user_id={self.user_id}, "
            f"type={self.notification_type}, is_read={self.is_read})>"
        )


class CommentReaction(Base):
    """Reactions to comments (thumbs up, heart, etc.).

    Users can react to comments with predefined emoji reactions.
    Each user can only have one reaction of each type per comment.

    Example:
        # User likes a comment
        CommentReaction(
            comment_id=123,
            user_id=5,
            reaction_type="thumbs_up",
            organisation_id=1
        )
    """

    __tablename__ = "comment_reactions"

    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Comment association
    comment_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("comments.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
        comment="FK to comments table",
    )

    # User who reacted
    user_id: Mapped[int] = mapped_column(
        Integer, nullable=False, index=True, comment="User ID who added this reaction"
    )

    # Reaction type
    reaction_type: Mapped[str] = mapped_column(
        Enum("thumbs_up", "heart", "smile", "party", "rocket", "eyes", name="reaction_type_enum"),
        nullable=False,
        comment="Type of reaction emoji",
    )

    # Multi-tenancy
    organisation_id: Mapped[int] = mapped_column(
        Integer, nullable=False, index=True, comment="Organization this reaction belongs to"
    )

    # Audit fields
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, comment="When reaction was added"
    )

    # Relationships
    comment: Mapped["Comment"] = relationship(
        "Comment",
        back_populates="reactions",
        foreign_keys=[comment_id],
    )

    # Composite index and unique constraint
    __table_args__ = ({"mysql_engine": "InnoDB"},)

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"<CommentReaction(id={self.id}, comment_id={self.comment_id}, "
            f"user_id={self.user_id}, reaction_type={self.reaction_type})>"
        )
