"""Create initial comments and attachments tables

Revision ID: 2025_01_20_0001
Revises:
Create Date: 2025-01-20 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = "2025_01_20_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create comments and attachments tables."""
    # Create comments table
    op.create_table(
        "comments",
        sa.Column("id", sa.Integer(), nullable=False, autoincrement=True),
        sa.Column("entity_type", sa.String(length=50), nullable=False),
        sa.Column("entity_id", sa.String(length=50), nullable=False),
        sa.Column("organisation_id", sa.Integer(), nullable=False),
        sa.Column("comment_text", sa.Text(), nullable=False),
        sa.Column("is_internal", sa.Boolean(), nullable=False, default=False),
        sa.Column("context", sa.JSON(), nullable=True),
        sa.Column("created_by_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, default=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.Column("deleted_by_id", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create indexes for comments
    op.create_index("idx_comments_entity", "comments", ["entity_type", "entity_id"])
    op.create_index("idx_comments_organisation", "comments", ["organisation_id"])
    op.create_index("idx_comments_created_at", "comments", ["created_at"])
    op.create_index("idx_comments_is_deleted", "comments", ["is_deleted"])

    # Create attachments table
    op.create_table(
        "attachments",
        sa.Column("id", sa.Integer(), nullable=False, autoincrement=True),
        sa.Column("entity_type", sa.String(length=50), nullable=False),
        sa.Column("entity_id", sa.String(length=50), nullable=False),
        sa.Column("organisation_id", sa.Integer(), nullable=False),
        sa.Column("file_name", sa.String(length=255), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=False),
        sa.Column("content_type", sa.String(length=100), nullable=False),
        sa.Column("storage_backend", sa.String(length=20), nullable=False),
        sa.Column("storage_path", sa.String(length=500), nullable=False),
        sa.Column("storage_container", sa.String(length=100), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("context", sa.JSON(), nullable=True),
        sa.Column("uploaded_by_id", sa.Integer(), nullable=False),
        sa.Column("uploaded_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, default=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.Column("deleted_by_id", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create indexes for attachments
    op.create_index("idx_attachments_entity", "attachments", ["entity_type", "entity_id"])
    op.create_index("idx_attachments_organisation", "attachments", ["organisation_id"])
    op.create_index("idx_attachments_uploaded_at", "attachments", ["uploaded_at"])
    op.create_index("idx_attachments_is_deleted", "attachments", ["is_deleted"])


def downgrade() -> None:
    """Drop comments and attachments tables."""
    op.drop_table("attachments")
    op.drop_table("comments")
