-- ============================================================================
-- Add Hierarchical Attachments and Document Classification
-- ============================================================================
-- Description: Adds comment_id FK and document classification fields to
--              existing attachments table for hierarchical relationships
-- Author: SWM Development Team
-- Date: 2025-10-21
-- Migration: Alter existing attachments table
-- ============================================================================

-- Add new columns to attachments table
ALTER TABLE attachments
    -- Hierarchical association (attachments can belong to comments)
    ADD COLUMN comment_id INT NULL COMMENT 'Optional FK to comments table for hierarchical attachments' AFTER entity_id,

    -- Document classification fields
    ADD COLUMN document_type_id INT NULL COMMENT 'Optional FK to document_types table' AFTER storage_container,
    ADD COLUMN document_category ENUM('normal', 'restricted') NOT NULL DEFAULT 'normal' COMMENT 'Document access category' AFTER document_type_id,
    ADD COLUMN virus_scan_status ENUM('clean', 'infected', 'quarantined', 'skipped', 'pending') NOT NULL DEFAULT 'clean' COMMENT 'Virus scan status' AFTER document_category,
    ADD COLUMN checksum VARCHAR(64) NULL COMMENT 'File checksum (SHA-256) for integrity verification' AFTER virus_scan_status,

    -- Add indexes
    ADD INDEX idx_attachments_comment (comment_id),
    ADD INDEX idx_attachments_category (document_category),

    -- Add foreign key constraint for hierarchical relationship
    ADD CONSTRAINT fk_attachment_comment
        FOREIGN KEY (comment_id)
        REFERENCES comments(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE;

-- ============================================================================
-- Verification Queries
-- ============================================================================

-- Check table structure
-- DESCRIBE attachments;

-- Check indexes
-- SHOW INDEX FROM attachments;

-- Check foreign keys
-- SELECT
--     CONSTRAINT_NAME,
--     COLUMN_NAME,
--     REFERENCED_TABLE_NAME,
--     REFERENCED_COLUMN_NAME
-- FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
-- WHERE TABLE_NAME = 'attachments'
--   AND REFERENCED_TABLE_NAME IS NOT NULL;

-- ============================================================================
-- Rollback Script (if needed)
-- ============================================================================

-- To rollback this migration:
-- ALTER TABLE attachments
--     DROP FOREIGN KEY fk_attachment_comment,
--     DROP INDEX idx_attachments_comment,
--     DROP INDEX idx_attachments_category,
--     DROP COLUMN comment_id,
--     DROP COLUMN document_type_id,
--     DROP COLUMN document_category,
--     DROP COLUMN virus_scan_status,
--     DROP COLUMN checksum;
