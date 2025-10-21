"""
Integration Example: How to integrate swm-comments package into your FastAPI application

This example shows:
1. How to configure storage backends based on environment (local vs dev/prod)
2. How to integrate comment and attachment routers
3. How to use the package with your existing auth dependencies
"""

from fastapi import Depends, FastAPI
from sqlalchemy.ext.asyncio import AsyncSession

# Your existing imports
from your_app.database import get_db  # Your database session dependency
from your_app.auth.dependencies import get_current_user  # Your auth dependency
from your_app.models import User  # Your user model

# Import from swm-comments package
from swm_comments.routers import create_comment_router, create_attachment_router
from swm_comments.storage import AzureBlobStorage, LocalStorage
from swm_comments import models as comment_models

# ============================================================================
# Step 1: Configure Storage Backend Based on Environment
# ============================================================================

import os


def get_storage_backend():
    """
    Get storage backend based on environment configuration.

    For local development:
    - Uses LocalStorage with filesystem
    - Files stored in ./uploads directory

    For dev/production:
    - Uses AzureBlobStorage with connection string from config
    - Files stored in Azure Blob Storage
    """
    # Read from your config (local.yaml or dev.yaml)
    azure_connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    azure_container_name = os.getenv("AZURE_STORAGE_CONTAINER_NAME", "attachments")

    if azure_connection_string:
        # Production/Dev: Use Azure Blob Storage
        return AzureBlobStorage(
            connection_string=azure_connection_string, container_name=azure_container_name
        )
    else:
        # Local: Use local filesystem
        return LocalStorage(base_path="./uploads")


# Initialize storage backend
storage_backend = get_storage_backend()


# ============================================================================
# Step 2: Create Dependency Functions for User ID and Organisation ID
# ============================================================================


async def get_current_user_id(current_user: User = Depends(get_current_user)) -> int:
    """Extract user ID from authenticated user."""
    return current_user.id


async def get_current_organisation_id(current_user: User = Depends(get_current_user)) -> int:
    """Extract organisation ID from authenticated user."""
    return current_user.organisation_id


# ============================================================================
# Step 3: Create Routers with Your Dependencies
# ============================================================================

# Create comment router
comment_router = create_comment_router(
    db_session_dependency=Depends(get_db),
    user_id_dependency=Depends(get_current_user_id),
    org_id_dependency=Depends(get_current_organisation_id),
)

# Create attachment router with storage backend
attachment_router = create_attachment_router(
    storage_backend=storage_backend,
    db_session_dependency=Depends(get_db),
    user_id_dependency=Depends(get_current_user_id),
    org_id_dependency=Depends(get_current_organisation_id),
)


# ============================================================================
# Step 4: Include Routers in Your FastAPI App
# ============================================================================

app = FastAPI()

# Include routers with prefixes
app.include_router(comment_router, prefix="/api/comments", tags=["comments"])
app.include_router(attachment_router, prefix="/api/attachments", tags=["attachments"])


# ============================================================================
# Step 5: Add Comment Models to Your Alembic Migration
# ============================================================================

# In your main models/__init__.py or alembic/env.py:
# from swm_comments.models import Comment, Attachment
# These will be automatically picked up by Alembic for migrations


# ============================================================================
# Usage Examples
# ============================================================================


@app.get("/examples")
async def examples():
    """
    Example API calls you can make after integration:

    Comments:
    ---------
    POST /api/comments
    {
        "entity_type": "task",
        "entity_id": "123",
        "comment_text": "This task is blocked due to missing documents",
        "is_internal": true,
        "context": {"field": "documents", "section": "requirements"}
    }

    GET /api/comments?entity_type=task&entity_id=123
    GET /api/comments?entity_type=task&entity_id=123&include_internal=false
    GET /api/comments/{comment_id}
    PATCH /api/comments/{comment_id}
    DELETE /api/comments/{comment_id}

    Attachments:
    ------------
    POST /api/attachments
    Content-Type: multipart/form-data
    - file: [binary file data]
    - entity_type: "task"
    - entity_id: "123"
    - description: "Supporting document for task completion"

    GET /api/attachments?entity_type=task&entity_id=123
    GET /api/attachments/{attachment_id}
    GET /api/attachments/{attachment_id}/download  # Returns presigned URL
    DELETE /api/attachments/{attachment_id}
    """
    return {"message": "See docstring for usage examples"}


# ============================================================================
# Frontend Integration Example (React/TypeScript)
# ============================================================================

"""
// Create API client for comments
export const commentsApi = {
  createComment: async (data: CommentCreate) => {
    const response = await api.post("/api/comments", data);
    return response.data;
  },

  getComments: async (params: { entity_type: string; entity_id: string }) => {
    const response = await api.get("/api/comments", { params });
    return response.data;
  },

  updateComment: async (commentId: number, data: CommentUpdate) => {
    const response = await api.patch(`/api/comments/${commentId}`, data);
    return response.data;
  },

  deleteComment: async (commentId: number) => {
    await api.delete(`/api/comments/${commentId}`);
  },
};

// Create API client for attachments
export const attachmentsApi = {
  uploadAttachment: async (
    file: File,
    entityType: string,
    entityId: string,
    description?: string
  ) => {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("entity_type", entityType);
    formData.append("entity_id", entityId);
    if (description) formData.append("description", description);

    const response = await api.post("/api/attachments", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return response.data;
  },

  getAttachments: async (params: { entity_type: string; entity_id: string }) => {
    const response = await api.get("/api/attachments", { params });
    return response.data;
  },

  getDownloadUrl: async (attachmentId: number) => {
    const response = await api.get(`/api/attachments/${attachmentId}/download`);
    return response.data; // { url, expires_at, file_name }
  },

  deleteAttachment: async (attachmentId: number) => {
    await api.delete(`/api/attachments/${attachmentId}`);
  },
};

// React component example
const TaskComments = ({ taskId }: { taskId: number }) => {
  const { data: comments } = useQuery({
    queryKey: ["comments", "task", taskId],
    queryFn: () => commentsApi.getComments({ entity_type: "task", entity_id: String(taskId) }),
  });

  const createMutation = useMutation({
    mutationFn: commentsApi.createComment,
    onSuccess: () => queryClient.invalidateQueries(["comments", "task", taskId]),
  });

  const handleAddComment = (text: string) => {
    createMutation.mutate({
      entity_type: "task",
      entity_id: String(taskId),
      comment_text: text,
      is_internal: false,
    });
  };

  return (
    <div>
      <CommentList comments={comments || []} />
      <CommentInput onSubmit={handleAddComment} />
    </div>
  );
};
"""


# ============================================================================
# Configuration Examples
# ============================================================================

"""
# local.yaml (Local Development)
# -------------------------------
azure_storage_connection_string: null
azure_storage_container_name: null

# Files will be stored in ./uploads/ directory
# Example: uploads/1/task/123/20250120_143000_document.pdf


# dev.yaml (Development/UAT)
# ---------------------------
azure_storage_connection_string: "DefaultEndpointsProtocol=https;AccountName=yourdevaccount;..."
azure_storage_container_name: "service-workflow-documents"

# Files will be stored in Azure Blob Storage
# Example: https://yourdevaccount.blob.core.windows.net/service-workflow-documents/1/task/123/20250120_143000_document.pdf


# prod.yaml (Production)
# -----------------------
azure_storage_connection_string: "DefaultEndpointsProtocol=https;AccountName=yourprodaccount;..."
azure_storage_container_name: "attachments"

# Files will be stored in Azure Blob Storage with production credentials
"""
