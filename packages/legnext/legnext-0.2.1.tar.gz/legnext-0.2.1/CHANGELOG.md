# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2025-01-21

### ⚠️ BREAKING CHANGES

This release includes significant API alignment updates to match the official Legnext API specification. **All users must update their code when upgrading.**

#### Major Parameter Changes

**blend()** - Now requires `aspect_ratio`:
```python
# OLD (0.1.x)
client.midjourney.blend(image_urls=["url1", "url2"])

# NEW (0.2.0)
client.midjourney.blend(img_urls=["url1", "url2"], aspect_ratio="1:1")
```

**describe()** - Parameter renamed:
```python
# OLD: image_url → NEW: img_url
client.midjourney.describe(img_url="https://...")
```

**pan()** - New required parameters:
```python
# OLD (0.1.x)
client.midjourney.pan(job_id="...", image_no=0, direction="left")

# NEW (0.2.0)
client.midjourney.pan(
    job_id="...",
    image_no=0,
    direction=2,  # Now integer: 0=UP, 1=DOWN, 2=LEFT, 3=RIGHT
    scale=1.5,    # Required: 1.1-3.0
    remix_prompt="..."  # Optional
)
```

**outpaint()** - New required parameters:
```python
# OLD (0.1.x)
client.midjourney.outpaint(job_id="...", image_no=0)

# NEW (0.2.0)
client.midjourney.outpaint(
    job_id="...",
    image_no=0,
    scale=1.3,  # Required: 1.1-2.0
    remix_prompt="..."  # Optional
)
```

**inpaint()** - Parameter renamed and made optional:
```python
# OLD: prompt (required) → NEW: remix_prompt (optional)
client.midjourney.inpaint(
    job_id="...",
    image_no=0,
    mask=mask_bytes,
    remix_prompt="..."  # Now optional
)
```

**remix()** - Parameters renamed:
```python
# OLD (0.1.x)
client.midjourney.remix(
    job_id="...",
    image_no=0,
    prompt="...",      # Renamed
    intensity=0.5      # Renamed & type changed
)

# NEW (0.2.0)
client.midjourney.remix(
    job_id="...",
    image_no=0,
    remix_prompt="...",  # New name
    mode=0               # New name, now integer (0=Low, 1=High)
)
```

**edit()** - Complete signature change with Canvas types:
```python
# OLD (0.1.x)
client.midjourney.edit(job_id="...", image_no=0, prompt="...")

# NEW (0.2.0)
from legnext.types import Canvas, CanvasImg, Mask, Polygon

client.midjourney.edit(
    job_id="...",
    image_no=0,
    canvas=Canvas(width=1024, height=1024),
    img_pos=CanvasImg(width=512, height=512, x=256, y=256),
    remix_prompt="...",
    mask=Mask(areas=[Polygon(width=1024, height=1024, points=[...])])
)
```

**upload_paint()** - Complete signature change:
```python
# OLD (0.1.x)
client.midjourney.upload_paint(
    image=image_bytes,
    prompt="...",
    x=100, y=100
)

# NEW (0.2.0)
from legnext.types import Canvas, CanvasImg, Mask

client.midjourney.upload_paint(
    img_url="https://...",
    canvas=Canvas(width=1024, height=1024),
    img_pos=CanvasImg(width=768, height=768, x=128, y=128),
    remix_prompt="...",
    mask=Mask(url="https://mask.png")
)
```

**retexture()** - Changed from job reference to image URL:
```python
# OLD (0.1.x)
client.midjourney.retexture(job_id="...", image_no=0, prompt="marble")

# NEW (0.2.0)
client.midjourney.retexture(img_url="https://...", remix_prompt="marble")
```

**remove_background()** - Changed from job reference to image URL:
```python
# OLD (0.1.x)
client.midjourney.remove_background(job_id="...", image_no=0)

# NEW (0.2.0)
client.midjourney.remove_background(img_url="https://...")
```

**extend_video()** - New required parameters:
```python
# OLD (0.1.x)
client.midjourney.extend_video(job_id="...")

# NEW (0.2.0)
client.midjourney.extend_video(
    job_id="...",
    video_no=0,  # Required: 0 or 1
    prompt="..."  # Optional
)
```

**video_upscale()** - New required parameter:
```python
# OLD (0.1.x)
client.midjourney.video_upscale(job_id="...")

# NEW (0.2.0)
client.midjourney.video_upscale(job_id="...", video_no=0)
```

### Added
- New Canvas type system for advanced editing operations:
  - `Canvas`: Canvas dimensions (width, height)
  - `CanvasImg`: Image position on canvas (width, height, x, y)
  - `Mask`: Mask definition (areas or url)
  - `Polygon`: Polygon area for masks (width, height, points)
- Exported Canvas types in public API for user access

### Changed
- **All 12 affected endpoints now match official API specification exactly**
- `PanDirection` enum changed from string values to integers (0-3)
- All async methods updated to match sync method signatures
- Fixed missing `/` prefix in 6 async endpoint URL paths

### Fixed
- `inpaint()` remix_prompt is now correctly optional (was incorrectly required)
- `retexture()` parameter name corrected to `remix_prompt` (was `prompt`)
- All parameter validations now match API constraints (ge, le, min_length, max_length)

## [0.1.6] - 2025-01-21

### Changed
- **Major**: Redesigned README with comprehensive API documentation for all 19 methods
- Added detailed parameter descriptions and code examples for each method
- Improved documentation structure with categorized API methods
- Added error handling guide and async batch processing examples

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
