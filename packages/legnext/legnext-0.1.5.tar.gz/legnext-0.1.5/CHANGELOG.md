# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.5] - 2025-01-21

### Fixed
- **Critical**: Fixed tasks API URL path from `/job/{id}` to `/v1/job/{id}` (resolves 404 errors)
- Fixed empty string URL validation in WebhookConfig and ImageOutput models

### Changed
- Cleaned up repository for customer-facing distribution
- Removed development-specific files from version control
- Simplified README to focus on usage rather than development
- Updated project URLs to remove placeholders

## [0.1.1] - 2025-01-20

### Added
- Initial public release of Legnext Python SDK
- Complete implementation of 19 Midjourney API operations
  - Image generation: diffusion, variation, upscale, reroll
  - Image composition: blend, describe, shorten
  - Image extension: pan, outpaint
  - Image editing: inpaint, remix, edit, upload_paint
  - Image enhancement: retexture, remove_background, enhance
  - Video generation: video_diffusion, extend_video, video_upscale
- Synchronous and asynchronous client support
- Type-safe request/response models with Pydantic v2
- Task polling with configurable timeout and progress callbacks
- Webhook verification and handling utilities
- Comprehensive documentation and examples

### Removed
- Account management endpoints (get_info, get_active_tasks)

### Fixed
- PyPI publish workflow to use standard Python build tools
