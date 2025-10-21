-- ============================================================================
-- Create Comments and Attachments Tables
-- ============================================================================
-- Description: Creates generic comments and attachments tables that can be
--              attached to any entity using entity_type + entity_id pattern
-- Author: SWM Development Team
-- Date: 2025-01-20
-- ============================================================================

-- Create comments table
CREATE TABLE IF NOT EXISTS comments (
    id INT AUTO_INCREMENT PRIMARY KEY,

    -- Polymorphic association
    entity_type VARCHAR(50) NOT NULL COMMENT 'Type of entity (task, property, invoice, etc.)',
    entity_id VARCHAR(50) NOT NULL COMMENT 'ID of the entity',

    -- Multi-tenancy
    organisation_id INT NOT NULL COMMENT 'Organization for multi-tenancy isolation',

    -- Content
    comment_text TEXT NOT NULL COMMENT 'The comment text',
    is_internal TINYINT(1) NOT NULL DEFAULT 0 COMMENT 'Is this an internal comment (not visible to clients)',
    context JSON NULL COMMENT 'Optional JSON context (e.g., field name, section)',

    -- Audit fields
    created_by_id INT NOT NULL COMMENT 'User who created the comment',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NULL ON UPDATE CURRENT_TIMESTAMP,

    -- Soft delete
    is_deleted TINYINT(1) NOT NULL DEFAULT 0,
    deleted_at DATETIME NULL,
    deleted_by_id INT NULL,

    -- Indexes for performance
    INDEX idx_comments_entity (entity_type, entity_id),
    INDEX idx_comments_organisation (organisation_id),
    INDEX idx_comments_created_at (created_at),
    INDEX idx_comments_is_deleted (is_deleted)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Generic comments that can be attached to any entity';

-- Create attachments table
CREATE TABLE IF NOT EXISTS attachments (
    id INT AUTO_INCREMENT PRIMARY KEY,

    -- Polymorphic association
    entity_type VARCHAR(50) NOT NULL COMMENT 'Type of entity (task, property, invoice, etc.)',
    entity_id VARCHAR(50) NOT NULL COMMENT 'ID of the entity',

    -- Hierarchical association (attachments can belong to comments)
    comment_id INT NULL COMMENT 'Optional FK to comments table for hierarchical attachments',

    -- Multi-tenancy
    organisation_id INT NOT NULL COMMENT 'Organization for multi-tenancy isolation',

    -- File metadata
    file_name VARCHAR(255) NOT NULL COMMENT 'Original filename',
    file_size INT NOT NULL COMMENT 'File size in bytes',
    content_type VARCHAR(100) NOT NULL COMMENT 'MIME type of the file',

    -- Storage backend info
    storage_backend VARCHAR(20) NOT NULL COMMENT 'Storage backend used (local, azure, s3)',
    storage_path VARCHAR(500) NOT NULL COMMENT 'Path/key where file is stored',
    storage_container VARCHAR(100) NULL COMMENT 'Container/bucket name (for cloud storage)',

    -- Document classification
    document_type_id INT NULL COMMENT 'Optional FK to document_types table',
    document_category ENUM('normal', 'restricted') NOT NULL DEFAULT 'normal' COMMENT 'Document access category',
    virus_scan_status ENUM('clean', 'infected', 'quarantined', 'skipped', 'pending') NOT NULL DEFAULT 'clean' COMMENT 'Virus scan status',
    checksum VARCHAR(64) NULL COMMENT 'File checksum (SHA-256) for integrity verification',

    -- Optional fields
    description TEXT NULL COMMENT 'Optional description of the attachment',
    context JSON NULL COMMENT 'Optional JSON context',

    -- Audit fields
    uploaded_by_id INT NOT NULL COMMENT 'User who uploaded the file',
    uploaded_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Soft delete
    is_deleted TINYINT(1) NOT NULL DEFAULT 0,
    deleted_at DATETIME NULL,
    deleted_by_id INT NULL,

    -- Indexes for performance
    INDEX idx_attachments_entity (entity_type, entity_id),
    INDEX idx_attachments_comment (comment_id),
    INDEX idx_attachments_organisation (organisation_id),
    INDEX idx_attachments_uploaded_at (uploaded_at),
    INDEX idx_attachments_is_deleted (is_deleted),
    INDEX idx_attachments_category (document_category),

    -- Foreign key constraint for hierarchical relationship
    CONSTRAINT fk_attachment_comment
        FOREIGN KEY (comment_id)
        REFERENCES comments(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Generic attachments that can be attached to any entity or to comments';

-- ============================================================================
-- Verification Queries
-- ============================================================================

-- Check table structure
-- DESCRIBE comments;
-- DESCRIBE attachments;

-- Check indexes
-- SHOW INDEX FROM comments;
-- SHOW INDEX FROM attachments;
