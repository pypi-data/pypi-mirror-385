# SWM Comments & Attachments

A generic, reusable Python package for adding comments and file attachments to any entity in FastAPI applications.

## Features

- **Generic Entity Support**: Attach comments/files to any entity using `entity_type` and `entity_id`
- **Hierarchical Attachments**: Attach files directly to comments (comment → attachments relationship)
- **Multiple Storage Backends**: Azure Blob Storage, AWS S3, or local filesystem
- **FastAPI Integration**: Ready-to-use routers and dependencies
- **Multi-tenancy**: Built-in organization-level isolation
- **Type-Safe**: Full TypeScript-style typing with Pydantic v2
- **Async**: Fully async/await compatible
- **Presigned URLs**: Secure file access without exposing storage credentials
- **Document Management**: Track document types, categories, virus scanning, and checksums

## Installation

### Option 1: Install from PyPI (when published)

```bash
pip install swm-comments-attachments
```

### Option 2: Install from local repository

```bash
cd swm-comments-attachments
pip install -e .
```

### Option 3: Add as dependency in pyproject.toml

```toml
[project.dependencies]
swm-comments-attachments = { path = "../swm-comments-attachments", develop = true }
```

## Database Setup

### Option 1: Run SQL Migration (Recommended for existing projects)

```bash
# Apply the migration to your database
mysql -u username -p database_name < database/migrations/001_create_comments_attachments_tables.sql
```

### Option 2: Use Alembic (if your project uses Alembic)

```bash
# Copy the migration to your project's alembic/versions/
cp alembic/versions/2025_01_20_0001-initial_comments_attachments_tables.py your_project/alembic/versions/

# Run migration
alembic upgrade head
```

### Option 3: Auto-create with SQLAlchemy

```python
from swm_comments.models import Base
from your_app.database import engine

# Create tables
async with engine.begin() as conn:
    await conn.run_sync(Base.metadata.create_all)
```

## Quick Start

### 1. Configure Storage Backend

```python
import os
from swm_comments.storage import AzureBlobStorage, LocalStorage

def get_storage_backend():
    """Get storage based on environment."""
    azure_connection = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

    if azure_connection:
        # Production/Dev: Use Azure Blob Storage
        return AzureBlobStorage(
            connection_string=azure_connection,
            container_name=os.getenv("AZURE_STORAGE_CONTAINER_NAME", "attachments")
        )
    else:
        # Local: Use filesystem
        return LocalStorage(base_path="./uploads")

storage = get_storage_backend()
```

### 2. Create Dependency Functions

```python
from fastapi import Depends
from your_app.auth import get_current_user
from your_app.database import get_db

async def get_current_user_id(current_user = Depends(get_current_user)) -> int:
    return current_user.id

async def get_current_organisation_id(current_user = Depends(get_current_user)) -> int:
    return current_user.organisation_id
```

### 3. Add Routers to FastAPI App

```python
from fastapi import FastAPI
from swm_comments.routers import create_comment_router, create_attachment_router

app = FastAPI()

# Create routers with your dependencies
comment_router = create_comment_router(
    db_session_dependency=Depends(get_db),
    user_id_dependency=Depends(get_current_user_id),
    org_id_dependency=Depends(get_current_organisation_id),
)

attachment_router = create_attachment_router(
    storage_backend=storage,
    db_session_dependency=Depends(get_db),
    user_id_dependency=Depends(get_current_user_id),
    org_id_dependency=Depends(get_current_organisation_id),
)

# Include routers
app.include_router(comment_router, prefix="/api/comments", tags=["comments"])
app.include_router(attachment_router, prefix="/api/attachments", tags=["attachments"])
```

### 4. Use the API

#### Add a comment to any entity

```bash
POST /api/comments
Content-Type: application/json

{
    "entity_type": "task",
    "entity_id": "123",
    "comment_text": "This task is blocked waiting for approval",
    "is_internal": false
}
```

#### Upload an attachment

```bash
POST /api/attachments
Content-Type: multipart/form-data

entity_type: task
entity_id: 123
file: <binary file>
description: Supporting document
```

#### Get download URL for attachment

```bash
GET /api/attachments/456/download

# Returns:
{
    "url": "https://...presigned-url...",
    "expires_at": "2025-01-20T15:30:00",
    "file_name": "document.pdf"
}
```

## Storage Backends

### Azure Blob Storage

```python
from swm_comments.storage import AzureBlobStorage

storage = AzureBlobStorage(
    connection_string="DefaultEndpointsProtocol=https;...",
    container_name="attachments"
)
```

### AWS S3

```python
from swm_comments.storage import S3Storage

storage = S3Storage(
    bucket_name="my-attachments",
    region="us-east-1",
    access_key_id="...",
    secret_access_key="..."
)
```

### Local Filesystem

```python
from swm_comments.storage import LocalStorage

storage = LocalStorage(base_path="/var/uploads")
```

## Database Models

The package provides two SQLAlchemy models:

- **Comment**: Text comments with optional internal/external visibility
  - `id` (int): Primary key
  - `entity_type` (str): Type of entity (e.g., "task", "property", "invoice")
  - `entity_id` (str): ID of the entity
  - `comment_text` (text): Comment content
  - `is_internal` (bool): Internal vs external visibility
  - `organisation_id` (int): Multi-tenancy isolation
  - `created_by_id` (int): User who created the comment
  - `created_at`, `updated_at` (datetime): Timestamps
  - `is_deleted` (bool): Soft delete flag
  - `context` (JSON): Optional additional metadata
  - `attachment_count` (computed): Number of attachments on this comment

- **Attachment**: File metadata with storage references
  - `id` (int): Primary key
  - `entity_type` (str): Type of entity
  - `entity_id` (str): ID of the entity
  - **`comment_id` (int, optional)**: Link to parent comment (hierarchical)
  - `file_name` (str): Original filename
  - `file_size` (int): File size in bytes
  - `content_type` (str): MIME type
  - `storage_backend` (str): Storage backend used
  - `storage_path` (str): Path in storage
  - `storage_container` (str): Container/bucket name
  - **`document_type_id` (int, optional)**: Document type classification
  - **`document_category` (enum)**: "normal" or "restricted"
  - **`virus_scan_status` (enum)**: "clean", "infected", "quarantined", "skipped", "pending"
  - **`checksum` (str)**: File integrity checksum (SHA-256)
  - `description` (str, optional): User-provided description
  - `organisation_id` (int): Multi-tenancy isolation
  - `uploaded_by_id` (int): User who uploaded the file
  - `uploaded_at` (datetime): Upload timestamp
  - `is_deleted` (bool): Soft delete flag
  - `context` (JSON): Optional additional metadata

### Hierarchical Attachments (Comment → Attachments)

**New in v2.0**: Attachments can now be linked directly to comments using the `comment_id` field. This creates a hierarchical relationship where files are associated with specific comments rather than just the entity.

**Benefits:**
- Better organization: Files grouped under relevant comments
- Cascade delete: Deleting a comment automatically deletes its attachments
- Visual indicators: Show attachment count on comments
- Contextual uploads: Users can attach files while discussing specific topics

**Usage:**
```python
# Upload an attachment to a comment
POST /api/attachments
Content-Type: multipart/form-data

entity_type: task
entity_id: 123
comment_id: 456  # Link to comment #456
file: <binary file>
```

**Backward Compatibility:** The `comment_id` field is optional. Attachments can still be linked directly to entities without a comment (entity-level attachments).

## API Examples

### List comments for an entity

```python
GET /api/comments?entity_type=task&entity_id=123
```

### Delete a comment

```python
DELETE /api/comments/{comment_id}
```

### Get attachment download URL

```python
GET /api/attachments/{attachment_id}/download
# Returns presigned URL valid for 1 hour
```

## Frontend Integration (React/TypeScript)

### API Client

```typescript
// api/comments.ts
import { api } from "./api";

export interface CommentCreate {
  entity_type: string;
  entity_id: string;
  comment_text: string;
  is_internal?: boolean;
  context?: Record<string, any>;
}

export interface Comment {
  id: number;
  entity_type: string;
  entity_id: string;
  comment_text: string;
  is_internal: boolean;
  created_by_id: number;
  created_at: string;
  updated_at?: string;
  organisation_id: number;
}

export const commentsApi = {
  create: async (data: CommentCreate): Promise<Comment> => {
    const response = await api.post("/api/comments", data);
    return response.data;
  },

  list: async (entityType: string, entityId: string): Promise<Comment[]> => {
    const response = await api.get("/api/comments", {
      params: { entity_type: entityType, entity_id: entityId },
    });
    return response.data;
  },

  update: async (id: number, data: Partial<CommentCreate>): Promise<Comment> => {
    const response = await api.patch(`/api/comments/${id}`, data);
    return response.data;
  },

  delete: async (id: number): Promise<void> => {
    await api.delete(`/api/comments/${id}`);
  },
};

export const attachmentsApi = {
  upload: async (
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

  list: async (entityType: string, entityId: string) => {
    const response = await api.get("/api/attachments", {
      params: { entity_type: entityType, entity_id: entityId },
    });
    return response.data;
  },

  getDownloadUrl: async (id: number) => {
    const response = await api.get(`/api/attachments/${id}/download`);
    return response.data;
  },

  delete: async (id: number): Promise<void> => {
    await api.delete(`/api/attachments/${id}`);
  },
};
```

### React Component Example

```tsx
// components/TaskComments.tsx
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { commentsApi } from "@/api/comments";

export const TaskComments = ({ taskId }: { taskId: number }) => {
  const queryClient = useQueryClient();

  const { data: comments, isLoading } = useQuery({
    queryKey: ["comments", "task", taskId],
    queryFn: () => commentsApi.list("task", String(taskId)),
  });

  const createMutation = useMutation({
    mutationFn: commentsApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries(["comments", "task", taskId]);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: commentsApi.delete,
    onSuccess: () => {
      queryClient.invalidateQueries(["comments", "task", taskId]);
    },
  });

  const handleAddComment = (text: string) => {
    createMutation.mutate({
      entity_type: "task",
      entity_id: String(taskId),
      comment_text: text,
      is_internal: false,
    });
  };

  if (isLoading) return <div>Loading comments...</div>;

  return (
    <div className="space-y-4">
      <div className="space-y-2">
        {comments?.map((comment) => (
          <div key={comment.id} className="border rounded p-3">
            <p className="text-sm">{comment.comment_text}</p>
            <div className="flex items-center justify-between mt-2">
              <span className="text-xs text-grey-600">
                {new Date(comment.created_at).toLocaleString()}
              </span>
              <button
                onClick={() => deleteMutation.mutate(comment.id)}
                className="text-xs text-red-600"
              >
                Delete
              </button>
            </div>
          </div>
        ))}
      </div>
      <CommentInput onSubmit={handleAddComment} />
    </div>
  );
};
```

## Multi-Tenancy

All operations are automatically scoped to the organization from the authenticated user:

```python
from swm_comments.routers import create_comment_router

# The router automatically filters all queries by organisation_id
# Users can only see comments from their own organization
comment_router = create_comment_router(
    db_session_dependency=Depends(get_db),
    user_id_dependency=Depends(get_current_user_id),
    org_id_dependency=Depends(get_current_organisation_id),  # Filters all queries
)
```

### Security Features

- **Automatic Organisation Filtering**: All queries filtered by `organisation_id`
- **Permission Checks**: Users can only edit/delete their own comments/attachments
- **Soft Deletes**: Data is never permanently deleted, just marked as deleted
- **Presigned URLs**: Secure file access with time-limited URLs

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Type checking
mypy src

# Linting
ruff check src
```

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions welcome! Please see CONTRIBUTING.md for guidelines.
