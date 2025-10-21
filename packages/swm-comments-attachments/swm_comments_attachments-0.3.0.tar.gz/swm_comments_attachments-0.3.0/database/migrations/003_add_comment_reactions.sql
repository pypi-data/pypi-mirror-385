-- ============================================================================
-- Migration: 003_add_comment_reactions.sql
-- Description: Add comment reactions (thumbs up, heart, etc.)
-- Author: Claude Code
-- Date: 2025-10-21
-- ============================================================================

-- Create comment_reactions table
CREATE TABLE IF NOT EXISTS comment_reactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    comment_id INT NOT NULL,
    user_id INT NOT NULL,
    reaction_type ENUM('thumbs_up', 'heart', 'smile', 'party', 'rocket', 'eyes') NOT NULL,
    organisation_id INT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Foreign keys
    CONSTRAINT fk_reaction_comment FOREIGN KEY (comment_id)
        REFERENCES comments(id) ON DELETE CASCADE,

    -- Unique constraint: one reaction type per user per comment
    CONSTRAINT unique_user_comment_reaction UNIQUE (comment_id, user_id, reaction_type),

    -- Index for fast lookups
    INDEX idx_comment_reactions (comment_id),
    INDEX idx_comment_reactions_org (organisation_id),
    INDEX idx_comment_reactions_user (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- Rollback Instructions
-- ============================================================================
-- DROP TABLE IF EXISTS comment_reactions;
