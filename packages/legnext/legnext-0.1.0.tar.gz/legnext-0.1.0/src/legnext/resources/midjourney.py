"""Midjourney operations resource.

All methods directly map to API endpoints for clarity.
Method names and parameters match the API specification exactly.
"""

from typing import Any, BinaryIO, Dict, Union

from pydantic import HttpUrl

from legnext._internal.http_client import AsyncHTTPClient, HTTPClient
from legnext.types.requests import (
    BlendRequest,
    DescribeRequest,
    DiffusionRequest,
    EditRequest,
    EnhanceRequest,
    ExtendVideoRequest,
    OutpaintRequest,
    PanRequest,
    RemixRequest,
    RemoveBackgroundRequest,
    RerollRequest,
    RetextureRequest,
    ShortenRequest,
    UpscaleRequest,
    VariationRequest,
    VideoDiffusionRequest,
    VideoUpscaleRequest,
)
from legnext.types.responses import TaskResponse


class MidjourneyResource:
    """Synchronous Midjourney operations resource.

    All methods directly correspond to API endpoints.
    """

    def __init__(self, http: HTTPClient) -> None:
        """Initialize the Midjourney resource."""
        self._http = http

    # Image Generation Endpoints

    def diffusion(
        self, text: str, callback: Union[HttpUrl, str, None] = None
    ) -> TaskResponse:
        """Text to image generation (POST /diffusion).

        Args:
            text: Text prompt for image generation (1-8192 characters)
            callback: Optional webhook URL for completion notification

        Returns:
            Task response with job information

        Example:
            ```python
            response = client.midjourney.diffusion(
                text="a beautiful sunset over mountains"
            )
            ```
        """
        request = DiffusionRequest(text=text, callback=callback)
        data = self._http.request("POST", "/diffusion", json=request.model_dump(by_alias=True))
        return TaskResponse.model_validate(data)

    def variation(
        self,
        job_id: str,
        image_no: int,
        type: int,
        remix_prompt: Union[str, None] = None,
        callback: Union[HttpUrl, str, None] = None,
    ) -> TaskResponse:
        """Create image variation (POST /variation).

        Args:
            job_id: ID of the original image generation task
            image_no: Image number to vary (0-3)
            type: Variation type (0=Subtle, 1=Strong)
            remix_prompt: Optional additional prompt for guided variation
            callback: Optional webhook URL

        Returns:
            Task response
        """
        request = VariationRequest(
            job_id=job_id,
            image_no=image_no,
            type=type,
            remix_prompt=remix_prompt,
            callback=callback,
        )
        data = self._http.request("POST", "/variation", json=request.model_dump(by_alias=True))
        return TaskResponse.model_validate(data)

    def upscale(
        self, job_id: str, image_no: int, type: int, callback: Union[HttpUrl, str, None] = None
    ) -> TaskResponse:
        """Upscale image (POST /upscale).

        Args:
            job_id: ID of the original image generation task
            image_no: Image number to upscale (0-3)
            type: Upscaling type (0=Subtle, 1=Creative)
            callback: Optional webhook URL

        Returns:
            Task response
        """
        request = UpscaleRequest(
            job_id=job_id, image_no=image_no, type=type, callback=callback
        )
        data = self._http.request("POST", "/upscale", json=request.model_dump(by_alias=True))
        return TaskResponse.model_validate(data)

    def reroll(self, job_id: str, callback: Union[HttpUrl, str, None] = None) -> TaskResponse:
        """Re-execute task to generate new variations (POST /reroll).

        Args:
            job_id: ID of the task to reroll
            callback: Optional webhook URL

        Returns:
            Task response
        """
        request = RerollRequest(job_id=job_id, callback=callback)
        data = self._http.request("POST", "/reroll", json=request.model_dump(by_alias=True))
        return TaskResponse.model_validate(data)

    def blend(
        self, image_urls: list[Union[HttpUrl, str]], callback: Union[HttpUrl, str, None] = None
    ) -> TaskResponse:
        """Blend 2-5 images together (POST /blend).

        Args:
            image_urls: 2-5 image URLs to blend
            callback: Optional webhook URL

        Returns:
            Task response
        """
        request = BlendRequest(image_urls=image_urls, callback=callback)
        data = self._http.request("POST", "/blend", json=request.model_dump(by_alias=True))
        return TaskResponse.model_validate(data)

    def describe(
        self, image_url: Union[HttpUrl, str], callback: Union[HttpUrl, str, None] = None
    ) -> TaskResponse:
        """Generate text descriptions from an image (POST /describe).

        Args:
            image_url: URL of image to describe
            callback: Optional webhook URL

        Returns:
            Task response
        """
        request = DescribeRequest(image_url=image_url, callback=callback)
        data = self._http.request("POST", "/describe", json=request.model_dump(by_alias=True))
        return TaskResponse.model_validate(data)

    def shorten(self, prompt: str, callback: Union[HttpUrl, str, None] = None) -> TaskResponse:
        """Simplify a prompt to essential elements (POST /shorten).

        Args:
            prompt: Prompt to shorten
            callback: Optional webhook URL

        Returns:
            Task response
        """
        request = ShortenRequest(prompt=prompt, callback=callback)
        data = self._http.request("POST", "/shorten", json=request.model_dump(by_alias=True))
        return TaskResponse.model_validate(data)

    def pan(
        self, job_id: str, image_no: int, direction: str, callback: Union[HttpUrl, str, None] = None
    ) -> TaskResponse:
        """Extend image in a specific direction (POST /pan).

        Args:
            job_id: ID of the original image
            image_no: Image number to extend (0-3)
            direction: Direction to extend (left, right, up, down)
            callback: Optional webhook URL

        Returns:
            Task response
        """
        request = PanRequest(
            job_id=job_id, image_no=image_no, direction=direction, callback=callback
        )
        data = self._http.request("POST", "/pan", json=request.model_dump(by_alias=True))
        return TaskResponse.model_validate(data)

    def outpaint(
        self, job_id: str, image_no: int, callback: Union[HttpUrl, str, None] = None
    ) -> TaskResponse:
        """Expand image in all directions (POST /outpaint).

        Args:
            job_id: ID of the original image
            image_no: Image number to expand (0-3)
            callback: Optional webhook URL

        Returns:
            Task response
        """
        request = OutpaintRequest(job_id=job_id, image_no=image_no, callback=callback)
        data = self._http.request("POST", "/outpaint", json=request.model_dump(by_alias=True))
        return TaskResponse.model_validate(data)

    def inpaint(
        self,
        job_id: str,
        image_no: int,
        mask: Union[bytes, BinaryIO],
        prompt: str,
        callback: Union[HttpUrl, str, None] = None,
    ) -> TaskResponse:
        """Selectively modify regions using masks (POST /inpaint).

        Args:
            job_id: ID of the original image
            image_no: Image number to edit (0-3)
            mask: Mask image (PNG) or file-like object
            prompt: Text prompt for the masked region
            callback: Optional webhook URL

        Returns:
            Task response
        """
        files = {"mask": mask if isinstance(mask, bytes) else mask.read()}
        data_dict: Dict[str, Any] = {
            "jobId": job_id,
            "imageNo": str(image_no),
            "prompt": prompt,
        }
        if callback:
            data_dict["callback"] = callback

        data = self._http.request("POST", "/inpaint", data=data_dict, files=files)
        return TaskResponse.model_validate(data)

    def remix(
        self,
        job_id: str,
        image_no: int,
        prompt: str,
        intensity: Union[float, None] = None,
        callback: Union[HttpUrl, str, None] = None,
    ) -> TaskResponse:
        """Transform images with new prompts (POST /remix).

        Args:
            job_id: ID of the original image
            image_no: Image number to remix (0-3)
            prompt: New prompt for remix
            intensity: Remix intensity (0-1)
            callback: Optional webhook URL

        Returns:
            Task response
        """
        request = RemixRequest(
            job_id=job_id,
            image_no=image_no,
            prompt=prompt,
            intensity=intensity,
            callback=callback,
        )
        data = self._http.request("POST", "/remix", json=request.model_dump(by_alias=True))
        return TaskResponse.model_validate(data)

    def edit(
        self, job_id: str, image_no: int, prompt: str, callback: Union[HttpUrl, str, None] = None
    ) -> TaskResponse:
        """Edit and repaint specific areas (POST /edit).

        Args:
            job_id: ID of the original image
            image_no: Image number to edit (0-3)
            prompt: Edit instructions
            callback: Optional webhook URL

        Returns:
            Task response
        """
        request = EditRequest(
            job_id=job_id, image_no=image_no, prompt=prompt, callback=callback
        )
        data = self._http.request("POST", "/edit", json=request.model_dump(by_alias=True))
        return TaskResponse.model_validate(data)

    def upload_paint(
        self,
        image: Union[bytes, BinaryIO],
        prompt: str,
        x: Union[float, None] = None,
        y: Union[float, None] = None,
        callback: Union[HttpUrl, str, None] = None,
    ) -> TaskResponse:
        """Advanced editing with custom canvas positioning (POST /upload-paint).

        Args:
            image: Image file or bytes
            prompt: Painting instructions
            x: X coordinate for canvas position
            y: Y coordinate for canvas position
            callback: Optional webhook URL

        Returns:
            Task response
        """
        files = {"image": image if isinstance(image, bytes) else image.read()}
        data_dict: Dict[str, Any] = {"prompt": prompt}
        if x is not None:
            data_dict["x"] = str(x)
        if y is not None:
            data_dict["y"] = str(y)
        if callback:
            data_dict["callback"] = callback

        data = self._http.request("POST", "/upload-paint", data=data_dict, files=files)
        return TaskResponse.model_validate(data)

    def retexture(
        self, job_id: str, image_no: int, prompt: str, callback: Union[HttpUrl, str, None] = None
    ) -> TaskResponse:
        """Transform materials and textures (POST /retexture).

        Args:
            job_id: ID of the original image
            image_no: Image number to retexture (0-3)
            prompt: Texture description
            callback: Optional webhook URL

        Returns:
            Task response
        """
        request = RetextureRequest(
            job_id=job_id, image_no=image_no, prompt=prompt, callback=callback
        )
        data = self._http.request("POST", "/retexture", json=request.model_dump(by_alias=True))
        return TaskResponse.model_validate(data)

    def remove_background(
        self, job_id: str, image_no: int, callback: Union[HttpUrl, str, None] = None
    ) -> TaskResponse:
        """Remove background from an image (POST /remove-background).

        Args:
            job_id: ID of the original image
            image_no: Image number to process (0-3)
            callback: Optional webhook URL

        Returns:
            Task response
        """
        request = RemoveBackgroundRequest(
            job_id=job_id, image_no=image_no, callback=callback
        )
        data = self._http.request(
            "POST", "/remove-background", json=request.model_dump(by_alias=True)
        )
        return TaskResponse.model_validate(data)

    def enhance(
        self, job_id: str, image_no: int, callback: Union[HttpUrl, str, None] = None
    ) -> TaskResponse:
        """Improve image quality and detail (POST /enhance).

        Note: Requires original image created with `--v7 --draft`

        Args:
            job_id: ID of the draft mode image
            image_no: Image number to enhance (0-3)
            callback: Optional webhook URL

        Returns:
            Task response
        """
        request = EnhanceRequest(job_id=job_id, image_no=image_no, callback=callback)
        data = self._http.request("POST", "/enhance", json=request.model_dump(by_alias=True))
        return TaskResponse.model_validate(data)

    # Video Generation Endpoints

    def video_diffusion(
        self,
        prompt: Union[str, None] = None,
        image_url: Union[HttpUrl, str, None] = None,
        duration: Union[int, None] = None,
        callback: Union[HttpUrl, str, None] = None,
    ) -> TaskResponse:
        """Generate video from text or image (POST /video-diffusion).

        Args:
            prompt: Text prompt for video generation
            image_url: Image URL to use as video source
            duration: Video duration in seconds
            callback: Optional webhook URL

        Returns:
            Task response

        Note:
            Either prompt or image_url must be provided
        """
        request = VideoDiffusionRequest(
            prompt=prompt, image_url=image_url, duration=duration, callback=callback
        )
        data = self._http.request(
            "POST", "/video-diffusion", json=request.model_dump(by_alias=True, exclude_none=True)
        )
        return TaskResponse.model_validate(data)

    def extend_video(
        self, job_id: str, callback: Union[HttpUrl, str, None] = None
    ) -> TaskResponse:
        """Extend existing video (POST /extend-video).

        Args:
            job_id: ID of the original video task
            callback: Optional webhook URL

        Returns:
            Task response
        """
        request = ExtendVideoRequest(job_id=job_id, callback=callback)
        data = self._http.request(
            "POST", "/extend-video", json=request.model_dump(by_alias=True)
        )
        return TaskResponse.model_validate(data)

    def video_upscale(
        self, job_id: str, callback: Union[HttpUrl, str, None] = None
    ) -> TaskResponse:
        """Upscale video quality (POST /video-upscale).

        Args:
            job_id: ID of the original video task
            callback: Optional webhook URL

        Returns:
            Task response
        """
        request = VideoUpscaleRequest(job_id=job_id, callback=callback)
        data = self._http.request(
            "POST", "/video-upscale", json=request.model_dump(by_alias=True)
        )
        return TaskResponse.model_validate(data)


class AsyncMidjourneyResource:
    """Asynchronous Midjourney operations resource.

    All methods directly correspond to API endpoints.
    """

    def __init__(self, http: AsyncHTTPClient) -> None:
        """Initialize the async Midjourney resource."""
        self._http = http

    # Image Generation Endpoints

    async def diffusion(
        self, text: str, callback: Union[HttpUrl, str, None] = None
    ) -> TaskResponse:
        """Text to image generation (POST /diffusion) - async."""
        request = DiffusionRequest(text=text, callback=callback)
        data = await self._http.request(
            "POST", "/diffusion", json=request.model_dump(by_alias=True)
        )
        return TaskResponse.model_validate(data)

    async def variation(
        self,
        job_id: str,
        image_no: int,
        type: int,
        remix_prompt: Union[str, None] = None,
        callback: Union[HttpUrl, str, None] = None,
    ) -> TaskResponse:
        """Create image variation (POST /variation) - async."""
        request = VariationRequest(
            job_id=job_id,
            image_no=image_no,
            type=type,
            remix_prompt=remix_prompt,
            callback=callback,
        )
        data = await self._http.request(
            "POST", "/variation", json=request.model_dump(by_alias=True)
        )
        return TaskResponse.model_validate(data)

    async def upscale(
        self, job_id: str, image_no: int, type: int, callback: Union[HttpUrl, str, None] = None
    ) -> TaskResponse:
        """Upscale image (POST /upscale) - async."""
        request = UpscaleRequest(
            job_id=job_id, image_no=image_no, type=type, callback=callback
        )
        data = await self._http.request(
            "POST", "/upscale", json=request.model_dump(by_alias=True)
        )
        return TaskResponse.model_validate(data)

    async def reroll(
        self, job_id: str, callback: Union[HttpUrl, str, None] = None
    ) -> TaskResponse:
        """Re-execute task (POST /reroll) - async."""
        request = RerollRequest(job_id=job_id, callback=callback)
        data = await self._http.request(
            "POST", "/reroll", json=request.model_dump(by_alias=True)
        )
        return TaskResponse.model_validate(data)

    async def blend(
        self, image_urls: list[Union[HttpUrl, str]], callback: Union[HttpUrl, str, None] = None
    ) -> TaskResponse:
        """Blend images (POST /blend) - async."""
        request = BlendRequest(image_urls=image_urls, callback=callback)
        data = await self._http.request(
            "POST", "/blend", json=request.model_dump(by_alias=True)
        )
        return TaskResponse.model_validate(data)

    async def describe(
        self, image_url: Union[HttpUrl, str], callback: Union[HttpUrl, str, None] = None
    ) -> TaskResponse:
        """Describe image (POST /describe) - async."""
        request = DescribeRequest(image_url=image_url, callback=callback)
        data = await self._http.request(
            "POST", "/describe", json=request.model_dump(by_alias=True)
        )
        return TaskResponse.model_validate(data)

    async def shorten(
        self, prompt: str, callback: Union[HttpUrl, str, None] = None
    ) -> TaskResponse:
        """Shorten prompt (POST /shorten) - async."""
        request = ShortenRequest(prompt=prompt, callback=callback)
        data = await self._http.request(
            "POST", "/shorten", json=request.model_dump(by_alias=True)
        )
        return TaskResponse.model_validate(data)

    async def pan(
        self, job_id: str, image_no: int, direction: str, callback: Union[HttpUrl, str, None] = None
    ) -> TaskResponse:
        """Pan/extend image (POST /pan) - async."""
        request = PanRequest(
            job_id=job_id, image_no=image_no, direction=direction, callback=callback
        )
        data = await self._http.request("POST", "/pan", json=request.model_dump(by_alias=True))
        return TaskResponse.model_validate(data)

    async def outpaint(
        self, job_id: str, image_no: int, callback: Union[HttpUrl, str, None] = None
    ) -> TaskResponse:
        """Outpaint (POST /outpaint) - async."""
        request = OutpaintRequest(job_id=job_id, image_no=image_no, callback=callback)
        data = await self._http.request(
            "POST", "/outpaint", json=request.model_dump(by_alias=True)
        )
        return TaskResponse.model_validate(data)

    async def inpaint(
        self,
        job_id: str,
        image_no: int,
        mask: Union[bytes, BinaryIO],
        prompt: str,
        callback: Union[HttpUrl, str, None] = None,
    ) -> TaskResponse:
        """Inpaint (POST /inpaint) - async."""
        files = {"mask": mask if isinstance(mask, bytes) else mask.read()}
        data_dict: Dict[str, Any] = {
            "jobId": job_id,
            "imageNo": str(image_no),
            "prompt": prompt,
        }
        if callback:
            data_dict["callback"] = callback

        data = await self._http.request("POST", "/inpaint", data=data_dict, files=files)
        return TaskResponse.model_validate(data)

    async def remix(
        self,
        job_id: str,
        image_no: int,
        prompt: str,
        intensity: Union[float, None] = None,
        callback: Union[HttpUrl, str, None] = None,
    ) -> TaskResponse:
        """Remix (POST /remix) - async."""
        request = RemixRequest(
            job_id=job_id,
            image_no=image_no,
            prompt=prompt,
            intensity=intensity,
            callback=callback,
        )
        data = await self._http.request("POST", "/remix", json=request.model_dump(by_alias=True))
        return TaskResponse.model_validate(data)

    async def edit(
        self, job_id: str, image_no: int, prompt: str, callback: Union[HttpUrl, str, None] = None
    ) -> TaskResponse:
        """Edit (POST /edit) - async."""
        request = EditRequest(
            job_id=job_id, image_no=image_no, prompt=prompt, callback=callback
        )
        data = await self._http.request("POST", "/edit", json=request.model_dump(by_alias=True))
        return TaskResponse.model_validate(data)

    async def upload_paint(
        self,
        image: Union[bytes, BinaryIO],
        prompt: str,
        x: Union[float, None] = None,
        y: Union[float, None] = None,
        callback: Union[HttpUrl, str, None] = None,
    ) -> TaskResponse:
        """Upload paint (POST /upload-paint) - async."""
        files = {"image": image if isinstance(image, bytes) else image.read()}
        data_dict: Dict[str, Any] = {"prompt": prompt}
        if x is not None:
            data_dict["x"] = str(x)
        if y is not None:
            data_dict["y"] = str(y)
        if callback:
            data_dict["callback"] = callback

        data = await self._http.request("POST", "/upload-paint", data=data_dict, files=files)
        return TaskResponse.model_validate(data)

    async def retexture(
        self, job_id: str, image_no: int, prompt: str, callback: Union[HttpUrl, str, None] = None
    ) -> TaskResponse:
        """Retexture (POST /retexture) - async."""
        request = RetextureRequest(
            job_id=job_id, image_no=image_no, prompt=prompt, callback=callback
        )
        data = await self._http.request(
            "POST", "/retexture", json=request.model_dump(by_alias=True)
        )
        return TaskResponse.model_validate(data)

    async def remove_background(
        self, job_id: str, image_no: int, callback: Union[HttpUrl, str, None] = None
    ) -> TaskResponse:
        """Remove background (POST /remove-background) - async."""
        request = RemoveBackgroundRequest(
            job_id=job_id, image_no=image_no, callback=callback
        )
        data = await self._http.request(
            "POST", "/remove-background", json=request.model_dump(by_alias=True)
        )
        return TaskResponse.model_validate(data)

    async def enhance(
        self, job_id: str, image_no: int, callback: Union[HttpUrl, str, None] = None
    ) -> TaskResponse:
        """Enhance (POST /enhance) - async."""
        request = EnhanceRequest(job_id=job_id, image_no=image_no, callback=callback)
        data = await self._http.request(
            "POST", "/enhance", json=request.model_dump(by_alias=True)
        )
        return TaskResponse.model_validate(data)

    # Video Generation Endpoints

    async def video_diffusion(
        self,
        prompt: Union[str, None] = None,
        image_url: Union[HttpUrl, str, None] = None,
        duration: Union[int, None] = None,
        callback: Union[HttpUrl, str, None] = None,
    ) -> TaskResponse:
        """Generate video (POST /video-diffusion) - async."""
        request = VideoDiffusionRequest(
            prompt=prompt, image_url=image_url, duration=duration, callback=callback
        )
        data = await self._http.request(
            "POST", "/video-diffusion", json=request.model_dump(by_alias=True, exclude_none=True)
        )
        return TaskResponse.model_validate(data)

    async def extend_video(
        self, job_id: str, callback: Union[HttpUrl, str, None] = None
    ) -> TaskResponse:
        """Extend video (POST /extend-video) - async."""
        request = ExtendVideoRequest(job_id=job_id, callback=callback)
        data = await self._http.request(
            "POST", "/extend-video", json=request.model_dump(by_alias=True)
        )
        return TaskResponse.model_validate(data)

    async def video_upscale(
        self, job_id: str, callback: Union[HttpUrl, str, None] = None
    ) -> TaskResponse:
        """Upscale video (POST /video-upscale) - async."""
        request = VideoUpscaleRequest(job_id=job_id, callback=callback)
        data = await self._http.request(
            "POST", "/video-upscale", json=request.model_dump(by_alias=True)
        )
        return TaskResponse.model_validate(data)
