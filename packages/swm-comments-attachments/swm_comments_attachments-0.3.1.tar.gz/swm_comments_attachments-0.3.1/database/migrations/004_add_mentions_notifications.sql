-- ============================================================================
-- Migration: 004_add_mentions_notifications.sql
-- Description: Add @mentions and notifications system
-- Author: Claude Code
-- Date: 2025-10-21
-- ============================================================================

-- Create comment_mentions table (track who was mentioned in comments)
CREATE TABLE IF NOT EXISTS comment_mentions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    comment_id INT NOT NULL,
    mentioned_user_id INT NOT NULL,
    mentioned_by_user_id INT NOT NULL,
    organisation_id INT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Foreign keys
    CONSTRAINT fk_mention_comment FOREIGN KEY (comment_id)
        REFERENCES comments(id) ON DELETE CASCADE,

    -- Unique constraint: user can only be mentioned once per comment
    CONSTRAINT unique_user_comment_mention UNIQUE (comment_id, mentioned_user_id),

    -- Indexes
    INDEX idx_comment_mentions_comment (comment_id),
    INDEX idx_comment_mentions_user (mentioned_user_id),
    INDEX idx_comment_mentions_org (organisation_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create notifications table (general notification system)
CREATE TABLE IF NOT EXISTS notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    notification_type ENUM('mention', 'reply', 'reaction', 'assignment') NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    reference_type VARCHAR(50) NULL,
    reference_id INT NULL,
    link_url VARCHAR(500) NULL,
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    organisation_id INT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    read_at TIMESTAMP NULL,

    -- Indexes
    INDEX idx_notifications_user (user_id),
    INDEX idx_notifications_read (is_read),
    INDEX idx_notifications_org (organisation_id),
    INDEX idx_notifications_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- Rollback Instructions
-- ============================================================================
-- DROP TABLE IF EXISTS comment_mentions;
-- DROP TABLE IF EXISTS notifications;
