# Legnext Python SDK

Official Python client library for the [Legnext AI API](https://legnext.ai) - Professional image and video generation using Midjourney models.

## Features

- **Comprehensive API Coverage**: Support for all Legnext endpoints
- **Type Safety**: Full type hints with Pydantic models
- **Async Support**: Both synchronous and asynchronous clients
- **Modern Design**: Clean, intuitive API following OpenAI SDK patterns
- **Task Management**: Built-in polling and webhook support
- **Error Handling**: Robust error handling with automatic retries

## Installation

```bash
pip install legnext
```

Or with uv:

```bash
uv pip install legnext
```

## Quick Start

### Basic Usage

```python
from legnext import Client

client = Client(api_key="your-api-key")

# Generate an image
response = client.midjourney.diffusion(
    text="a beautiful sunset over mountains"
)

print(f"Job ID: {response.job_id}")
print(f"Status: {response.status}")

# Wait for completion
result = client.tasks.wait_for_completion(response.job_id)
print(f"Image URLs: {result.output.image_urls}")
```

### Async Usage

```python
import asyncio
from legnext import AsyncClient

async def main():
    async with AsyncClient(api_key="your-api-key") as client:
        response = await client.midjourney.diffusion(
            text="a futuristic cityscape"
        )
        result = await client.tasks.wait_for_completion(response.job_id)
        print(f"Generated: {result.output.image_urls}")

asyncio.run(main())
```

## API Coverage

### Midjourney Operations

**Image Generation:**
- `client.midjourney.diffusion(text)` - Text to image generation (POST /diffusion)
- `client.midjourney.variation(job_id, image_no, type)` - Create variations (POST /variation)
- `client.midjourney.upscale(job_id, image_no, type)` - Upscale images (POST /upscale)
- `client.midjourney.reroll(job_id)` - Re-generate with same prompt (POST /reroll)
- `client.midjourney.blend(image_urls)` - Blend 2-5 images (POST /blend)
- `client.midjourney.describe(image_url)` - Generate descriptions (POST /describe)
- `client.midjourney.shorten(prompt)` - Optimize prompts (POST /shorten)
- `client.midjourney.pan(job_id, image_no, direction)` - Extend in direction (POST /pan)
- `client.midjourney.outpaint(job_id, image_no)` - Expand all directions (POST /outpaint)
- `client.midjourney.inpaint(job_id, image_no, mask, prompt)` - Region editing (POST /inpaint)
- `client.midjourney.remix(job_id, image_no, prompt)` - Transform with new prompt (POST /remix)
- `client.midjourney.edit(job_id, image_no, prompt)` - Edit specific areas (POST /edit)
- `client.midjourney.upload_paint(image, prompt)` - Advanced editing (POST /upload-paint)
- `client.midjourney.retexture(job_id, image_no, prompt)` - Change textures (POST /retexture)
- `client.midjourney.remove_background(job_id, image_no)` - Remove background (POST /remove-background)
- `client.midjourney.enhance(job_id, image_no)` - Improve quality (POST /enhance)

**Video Generation:**
- `client.midjourney.video_diffusion(prompt, image_url, duration)` - Generate video (POST /video-diffusion)
- `client.midjourney.extend_video(job_id)` - Extend video (POST /extend-video)
- `client.midjourney.video_upscale(job_id)` - Upscale video (POST /video-upscale)

### Task Management

- `client.tasks.get()` - Get task status
- `client.tasks.wait_for_completion()` - Poll until complete

## Requirements

- Python 3.10+
- httpx >= 0.27.0
- pydantic >= 2.0.0

## Documentation

- [Official API Documentation](https://legnext.ai/docs)
- [Code Examples](./examples)

## Support

For questions or issues, please contact:
- Email: support@legnext.cn
- Website: https://legnext.ai

## License

Apache License 2.0 - See [LICENSE](LICENSE) for details.
