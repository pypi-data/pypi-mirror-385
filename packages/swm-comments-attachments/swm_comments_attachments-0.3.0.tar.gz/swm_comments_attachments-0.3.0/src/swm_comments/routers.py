"""FastAPI routers for comments and attachments."""

from datetime import datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Attachment, Comment
from .schemas import (
    AttachmentDownloadURL,
    AttachmentQueryParams,
    AttachmentResponse,
    CommentCreate,
    CommentQueryParams,
    CommentResponse,
    CommentUpdate,
)
from .storage import StorageBackend


# ============================================================================
# Dependency injection helpers
# ============================================================================


def get_current_user_id() -> int:
    """Get current user ID from JWT token.

    This is a placeholder - you should replace this with your actual auth dependency.
    In your SWM app, you'd use something like:

    from service_workflow_management_system.modules.auth.dependencies import (
        get_current_user
    )

    async def get_current_user_id(
        current_user: AuthenticatedUser = Depends(get_current_user)
    ) -> int:
        return current_user.id
    """
    # TODO: Replace with actual auth dependency
    return 1


def get_current_organisation_id() -> int:
    """Get current organisation ID from JWT token.

    This is a placeholder - you should replace this with your actual auth dependency.
    In your SWM app, you'd use something like:

    async def get_current_organisation_id(
        current_user: AuthenticatedUser = Depends(get_current_user)
    ) -> int:
        return current_user.organisation_id
    """
    # TODO: Replace with actual auth dependency
    return 1


# ============================================================================
# Comment Router Factory
# ============================================================================


def create_comment_router(
    db_session_dependency: Annotated[AsyncSession, Depends()],
    user_id_dependency: Annotated[int, Depends()] = Depends(get_current_user_id),
    org_id_dependency: Annotated[int, Depends()] = Depends(get_current_organisation_id),
) -> APIRouter:
    """Create a comment router with custom dependencies.

    Args:
        db_session_dependency: Dependency that returns AsyncSession
        user_id_dependency: Dependency that returns current user ID
        org_id_dependency: Dependency that returns current organisation ID

    Returns:
        APIRouter: Configured router for comments

    Example:
        from your_app.database import get_db
        from your_app.auth import get_current_user_id, get_current_organisation_id

        router = create_comment_router(
            db_session_dependency=Depends(get_db),
            user_id_dependency=Depends(get_current_user_id),
            org_id_dependency=Depends(get_current_organisation_id),
        )

        app.include_router(router, prefix="/api/comments", tags=["comments"])
    """
    router = APIRouter()

    @router.post("/", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
    async def create_comment(
        comment: CommentCreate,
        db: AsyncSession = db_session_dependency,
        user_id: int = user_id_dependency,
        org_id: int = org_id_dependency,
    ) -> CommentResponse:
        """Create a new comment."""
        # Create comment
        db_comment = Comment(
            entity_type=comment.entity_type,
            entity_id=comment.entity_id,
            comment_text=comment.comment_text,
            is_internal=comment.is_internal,
            context=comment.context,
            organisation_id=org_id,
            created_by_id=user_id,
        )

        db.add(db_comment)
        await db.commit()
        await db.refresh(db_comment)

        return CommentResponse.model_validate(db_comment)

    @router.get("/", response_model=list[CommentResponse])
    async def list_comments(
        params: Annotated[CommentQueryParams, Depends()],
        db: AsyncSession = db_session_dependency,
        org_id: int = org_id_dependency,
    ) -> list[CommentResponse]:
        """List comments for an entity."""
        # Build query
        query = select(Comment).where(Comment.organisation_id == org_id)

        if params.entity_type:
            query = query.where(Comment.entity_type == params.entity_type)

        if params.entity_id:
            query = query.where(Comment.entity_id == params.entity_id)

        if not params.include_internal:
            query = query.where(Comment.is_internal == False)  # noqa: E712

        if not params.include_deleted:
            query = query.where(Comment.is_deleted == False)  # noqa: E712

        query = query.offset(params.skip).limit(params.limit)
        query = query.order_by(Comment.created_at.desc())

        # Execute query
        result = await db.execute(query)
        comments = result.scalars().all()

        # Get attachment counts for each comment
        comment_responses = []
        for comment in comments:
            # Count non-deleted attachments for this comment
            count_query = select(func.count(Attachment.id)).where(
                Attachment.comment_id == comment.id,
                Attachment.is_deleted == False,  # noqa: E712
            )
            count_result = await db.execute(count_query)
            attachment_count = count_result.scalar() or 0

            # Create response with attachment count
            comment_dict = {
                **comment.__dict__,
                "attachment_count": attachment_count,
            }
            comment_responses.append(CommentResponse.model_validate(comment_dict))

        return comment_responses

    @router.get("/{comment_id}", response_model=CommentResponse)
    async def get_comment(
        comment_id: int,
        db: AsyncSession = db_session_dependency,
        org_id: int = org_id_dependency,
    ) -> CommentResponse:
        """Get a specific comment by ID."""
        query = select(Comment).where(
            Comment.id == comment_id,
            Comment.organisation_id == org_id,
            Comment.is_deleted == False,  # noqa: E712
        )

        result = await db.execute(query)
        comment = result.scalar_one_or_none()

        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found"
            )

        return CommentResponse.model_validate(comment)

    @router.patch("/{comment_id}", response_model=CommentResponse)
    async def update_comment(
        comment_id: int,
        comment_update: CommentUpdate,
        db: AsyncSession = db_session_dependency,
        user_id: int = user_id_dependency,
        org_id: int = org_id_dependency,
    ) -> CommentResponse:
        """Update a comment."""
        # Get comment
        query = select(Comment).where(
            Comment.id == comment_id,
            Comment.organisation_id == org_id,
            Comment.is_deleted == False,  # noqa: E712
        )

        result = await db.execute(query)
        db_comment = result.scalar_one_or_none()

        if not db_comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found"
            )

        # Only allow creator to update
        if db_comment.created_by_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only edit your own comments",
            )

        # Update fields
        if comment_update.comment_text is not None:
            db_comment.comment_text = comment_update.comment_text

        if comment_update.is_internal is not None:
            db_comment.is_internal = comment_update.is_internal

        if comment_update.context is not None:
            db_comment.context = comment_update.context

        db_comment.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(db_comment)

        return CommentResponse.model_validate(db_comment)

    @router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
    async def delete_comment(
        comment_id: int,
        db: AsyncSession = db_session_dependency,
        user_id: int = user_id_dependency,
        org_id: int = org_id_dependency,
    ) -> None:
        """Soft delete a comment."""
        # Get comment
        query = select(Comment).where(
            Comment.id == comment_id,
            Comment.organisation_id == org_id,
            Comment.is_deleted == False,  # noqa: E712
        )

        result = await db.execute(query)
        db_comment = result.scalar_one_or_none()

        if not db_comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found"
            )

        # Only allow creator to delete
        if db_comment.created_by_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete your own comments",
            )

        # Soft delete
        db_comment.is_deleted = True
        db_comment.deleted_at = datetime.utcnow()
        db_comment.deleted_by_id = user_id

        await db.commit()

    return router


# ============================================================================
# Attachment Router Factory
# ============================================================================


def create_attachment_router(
    storage_backend: StorageBackend,
    db_session_dependency: Annotated[AsyncSession, Depends()],
    user_id_dependency: Annotated[int, Depends()] = Depends(get_current_user_id),
    org_id_dependency: Annotated[int, Depends()] = Depends(get_current_organisation_id),
) -> APIRouter:
    """Create an attachment router with custom dependencies.

    Args:
        storage_backend: Storage backend instance (Azure, S3, or Local)
        db_session_dependency: Dependency that returns AsyncSession
        user_id_dependency: Dependency that returns current user ID
        org_id_dependency: Dependency that returns current organisation ID

    Returns:
        APIRouter: Configured router for attachments

    Example:
        from swm_comments.storage import AzureBlobStorage

        storage = AzureBlobStorage(
            connection_string="...",
            container_name="attachments"
        )

        router = create_attachment_router(
            storage_backend=storage,
            db_session_dependency=Depends(get_db),
            user_id_dependency=Depends(get_current_user_id),
            org_id_dependency=Depends(get_current_organisation_id),
        )

        app.include_router(router, prefix="/api/attachments", tags=["attachments"])
    """
    router = APIRouter()

    @router.post("/", response_model=AttachmentResponse, status_code=status.HTTP_201_CREATED)
    async def upload_attachment(
        file: UploadFile = File(...),
        entity_type: str = Form(...),
        entity_id: str = Form(...),
        comment_id: int | None = Form(None),
        description: str | None = Form(None),
        db: AsyncSession = db_session_dependency,
        user_id: int = user_id_dependency,
        org_id: int = org_id_dependency,
    ) -> AttachmentResponse:
        """Upload an attachment."""
        # Validate file
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="No filename provided"
            )

        # Generate storage path
        storage_path = storage_backend.generate_storage_path(
            organisation_id=org_id,
            entity_type=entity_type,
            entity_id=entity_id,
            file_name=file.filename,
        )

        # Upload to storage
        try:
            await storage_backend.upload_file(
                file_content=file.file,
                storage_path=storage_path,
                content_type=file.content_type or "application/octet-stream",
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload file: {e}",
            )

        # Get file size
        file_size = await storage_backend.get_file_size(storage_path)

        # Create attachment record
        db_attachment = Attachment(
            entity_type=entity_type,
            entity_id=entity_id,
            comment_id=comment_id,
            file_name=file.filename,
            file_size=file_size,
            content_type=file.content_type or "application/octet-stream",
            storage_backend=storage_backend.__class__.__name__.lower().replace("storage", ""),
            storage_path=storage_path,
            description=description,
            organisation_id=org_id,
            uploaded_by_id=user_id,
        )

        db.add(db_attachment)
        await db.commit()
        await db.refresh(db_attachment)

        return AttachmentResponse.model_validate(db_attachment)

    @router.get("/", response_model=list[AttachmentResponse])
    async def list_attachments(
        params: Annotated[AttachmentQueryParams, Depends()],
        db: AsyncSession = db_session_dependency,
        org_id: int = org_id_dependency,
    ) -> list[AttachmentResponse]:
        """List attachments for an entity or comment."""
        # Build query
        query = select(Attachment).where(Attachment.organisation_id == org_id)

        if params.entity_type:
            query = query.where(Attachment.entity_type == params.entity_type)

        if params.entity_id:
            query = query.where(Attachment.entity_id == params.entity_id)

        if params.comment_id is not None:
            query = query.where(Attachment.comment_id == params.comment_id)

        if not params.include_deleted:
            query = query.where(Attachment.is_deleted == False)  # noqa: E712

        query = query.offset(params.skip).limit(params.limit)
        query = query.order_by(Attachment.uploaded_at.desc())

        # Execute query
        result = await db.execute(query)
        attachments = result.scalars().all()

        return [AttachmentResponse.model_validate(a) for a in attachments]

    @router.get("/{attachment_id}", response_model=AttachmentResponse)
    async def get_attachment(
        attachment_id: int,
        db: AsyncSession = db_session_dependency,
        org_id: int = org_id_dependency,
    ) -> AttachmentResponse:
        """Get a specific attachment by ID."""
        query = select(Attachment).where(
            Attachment.id == attachment_id,
            Attachment.organisation_id == org_id,
            Attachment.is_deleted == False,  # noqa: E712
        )

        result = await db.execute(query)
        attachment = result.scalar_one_or_none()

        if not attachment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Attachment not found"
            )

        return AttachmentResponse.model_validate(attachment)

    @router.get("/{attachment_id}/download", response_model=AttachmentDownloadURL)
    async def get_attachment_download_url(
        attachment_id: int,
        db: AsyncSession = db_session_dependency,
        org_id: int = org_id_dependency,
    ) -> AttachmentDownloadURL:
        """Get presigned download URL for an attachment."""
        # Get attachment
        query = select(Attachment).where(
            Attachment.id == attachment_id,
            Attachment.organisation_id == org_id,
            Attachment.is_deleted == False,  # noqa: E712
        )

        result = await db.execute(query)
        attachment = result.scalar_one_or_none()

        if not attachment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Attachment not found"
            )

        # Generate presigned URL
        try:
            url = await storage_backend.get_presigned_url(attachment.storage_path)
            expires_at = datetime.utcnow() + timedelta(hours=1)

            return AttachmentDownloadURL(
                url=url, expires_at=expires_at, file_name=attachment.file_name
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate download URL: {e}",
            )

    @router.delete("/{attachment_id}", status_code=status.HTTP_204_NO_CONTENT)
    async def delete_attachment(
        attachment_id: int,
        db: AsyncSession = db_session_dependency,
        user_id: int = user_id_dependency,
        org_id: int = org_id_dependency,
    ) -> None:
        """Soft delete an attachment."""
        # Get attachment
        query = select(Attachment).where(
            Attachment.id == attachment_id,
            Attachment.organisation_id == org_id,
            Attachment.is_deleted == False,  # noqa: E712
        )

        result = await db.execute(query)
        db_attachment = result.scalar_one_or_none()

        if not db_attachment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Attachment not found"
            )

        # Only allow uploader to delete
        if db_attachment.uploaded_by_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete your own attachments",
            )

        # Soft delete
        db_attachment.is_deleted = True
        db_attachment.deleted_at = datetime.utcnow()
        db_attachment.deleted_by_id = user_id

        await db.commit()

        # Optionally delete from storage (commented out for safety - soft delete only)
        # await storage_backend.delete_file(db_attachment.storage_path)

    return router
