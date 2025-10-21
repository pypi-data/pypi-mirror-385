-- ============================================================================
-- Migration: 005_add_comment_threading.sql
-- Description: Add support for nested/threaded comments (replies)
-- Author: Claude Code
-- Date: 2025-10-21
-- ============================================================================

-- Add parent_comment_id column to comments table
ALTER TABLE comments
ADD COLUMN parent_comment_id INT NULL AFTER entity_id,
ADD CONSTRAINT fk_comment_parent FOREIGN KEY (parent_comment_id)
    REFERENCES comments(id) ON DELETE CASCADE ON UPDATE CASCADE;

-- Add index for efficient querying of replies
CREATE INDEX idx_comments_parent ON comments(parent_comment_id);

-- ============================================================================
-- Rollback Instructions
-- ============================================================================
-- ALTER TABLE comments DROP FOREIGN KEY fk_comment_parent;
-- ALTER TABLE comments DROP INDEX idx_comments_parent;
-- ALTER TABLE comments DROP COLUMN parent_comment_id;
