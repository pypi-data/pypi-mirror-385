# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2025-01-21

### Added
- Comment threading support (parent-child relationships)
- Comment reactions (emoji reactions)
- User mentions in comments (@mentions)
- Notification system for mentions and replies
- Hierarchical attachments (attach files to comments)
- Multiple storage backends (Azure Blob, S3, Local filesystem)
- Presigned URL support for secure file access
- Document metadata tracking (type, category, virus scan status)
- FastAPI router integration
- Type-safe schemas with Pydantic v2
- Full async/await support
- Multi-tenancy with organization-level isolation
- Database migrations (Alembic + raw SQL)
- Comprehensive integration examples

### Documentation
- Complete README with installation and usage instructions
- Integration example showing FastAPI setup
- Database migration guides
- API documentation

## [0.2.0] - Unreleased

### Added
- Basic comment and attachment functionality
- SQLAlchemy models
- Initial schema definitions

## [0.1.0] - Initial Development

### Added
- Project structure
- Initial setup and configuration
