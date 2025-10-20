"""Request models for the Legnext SDK."""

from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator

from .enums import PanDirection


class DiffusionRequest(BaseModel):
    """Request for text-to-image generation."""

    text: str = Field(
        ..., min_length=1, max_length=8192, description="Text prompt for image generation"
    )
    callback: Optional[HttpUrl] = Field(
        None, description="Optional webhook URL for completion notification"
    )


class VariationRequest(BaseModel):
    """Request for creating image variations."""

    job_id: str = Field(..., alias="jobId", description="ID of the original image generation task")
    image_no: int = Field(
        ..., alias="imageNo", ge=0, le=3, description="Image number to vary (0-3)"
    )
    type: int = Field(..., ge=0, le=1, description="Variation intensity (0=Subtle, 1=Strong)")
    remix_prompt: Optional[str] = Field(
        None,
        alias="remixPrompt",
        min_length=1,
        max_length=8192,
        description="Optional additional prompt for guided variation",
    )
    callback: Optional[HttpUrl] = Field(None, description="Optional webhook URL")

    model_config = ConfigDict(populate_by_name=True)


class UpscaleRequest(BaseModel):
    """Request for upscaling images."""

    job_id: str = Field(..., alias="jobId", description="ID of the original image generation task")
    image_no: int = Field(..., alias="imageNo", ge=0, le=3, description="Image number to upscale")
    type: int = Field(..., ge=0, le=1, description="Upscaling type (0=Subtle, 1=Creative)")
    callback: Optional[HttpUrl] = Field(None, description="Optional webhook URL")

    model_config = ConfigDict(populate_by_name=True)


class RerollRequest(BaseModel):
    """Request for rerolling a task."""

    job_id: str = Field(..., alias="jobId", description="ID of the task to reroll")
    callback: Optional[HttpUrl] = Field(None, description="Optional webhook URL")

    model_config = ConfigDict(populate_by_name=True)


class BlendRequest(BaseModel):
    """Request for blending multiple images."""

    image_urls: list[HttpUrl] = Field(
        ..., alias="imageUrls", min_length=2, max_length=5, description="2-5 image URLs to blend"
    )
    callback: Optional[HttpUrl] = Field(None, description="Optional webhook URL")

    model_config = ConfigDict(populate_by_name=True)


class DescribeRequest(BaseModel):
    """Request for describing an image."""

    image_url: HttpUrl = Field(..., alias="imageUrl", description="URL of image to describe")
    callback: Optional[HttpUrl] = Field(None, description="Optional webhook URL")

    model_config = ConfigDict(populate_by_name=True)


class ShortenRequest(BaseModel):
    """Request for shortening a prompt."""

    prompt: str = Field(..., min_length=1, max_length=8192, description="Prompt to shorten")
    callback: Optional[HttpUrl] = Field(None, description="Optional webhook URL")


class PanRequest(BaseModel):
    """Request for pan/extend operation."""

    job_id: str = Field(..., alias="jobId", description="ID of the original image")
    image_no: int = Field(..., alias="imageNo", ge=0, le=3, description="Image number to extend")
    direction: PanDirection = Field(..., description="Direction to extend")
    callback: Optional[HttpUrl] = Field(None, description="Optional webhook URL")

    model_config = ConfigDict(populate_by_name=True)


class OutpaintRequest(BaseModel):
    """Request for outpaint operation."""

    job_id: str = Field(..., alias="jobId", description="ID of the original image")
    image_no: int = Field(..., alias="imageNo", ge=0, le=3, description="Image number to extend")
    callback: Optional[HttpUrl] = Field(None, description="Optional webhook URL")

    model_config = ConfigDict(populate_by_name=True)


class InpaintRequest(BaseModel):
    """Request for inpaint operation."""

    job_id: str = Field(..., alias="jobId", description="ID of the original image")
    image_no: int = Field(..., alias="imageNo", ge=0, le=3, description="Image number to edit")
    mask: bytes = Field(..., description="Mask image (PNG) indicating regions to modify")
    prompt: str = Field(
        ..., min_length=1, max_length=8192, description="Text prompt for the edited region"
    )
    callback: Optional[HttpUrl] = Field(None, description="Optional webhook URL")

    model_config = ConfigDict(populate_by_name=True)


class RemixRequest(BaseModel):
    """Request for remix operation."""

    job_id: str = Field(..., alias="jobId", description="ID of the original image")
    image_no: int = Field(..., alias="imageNo", ge=0, le=3, description="Image number to remix")
    prompt: str = Field(..., min_length=1, max_length=8192, description="New prompt for remix")
    intensity: Optional[float] = Field(None, ge=0, le=1, description="Remix intensity (0-1)")
    callback: Optional[HttpUrl] = Field(None, description="Optional webhook URL")

    model_config = ConfigDict(populate_by_name=True)


class EditRequest(BaseModel):
    """Request for edit operation."""

    job_id: str = Field(..., alias="jobId", description="ID of the original image")
    image_no: int = Field(..., alias="imageNo", ge=0, le=3, description="Image number to edit")
    prompt: str = Field(..., min_length=1, max_length=8192, description="Edit instructions")
    callback: Optional[HttpUrl] = Field(None, description="Optional webhook URL")

    model_config = ConfigDict(populate_by_name=True)


class UploadPaintRequest(BaseModel):
    """Request for upload paint operation."""

    image: bytes = Field(..., description="Image file to paint on")
    prompt: str = Field(..., min_length=1, max_length=8192, description="Painting instructions")
    x: Optional[float] = Field(None, description="X coordinate for canvas position")
    y: Optional[float] = Field(None, description="Y coordinate for canvas position")
    callback: Optional[HttpUrl] = Field(None, description="Optional webhook URL")


class RetextureRequest(BaseModel):
    """Request for retexture operation."""

    job_id: str = Field(..., alias="jobId", description="ID of the original image")
    image_no: int = Field(..., alias="imageNo", ge=0, le=3, description="Image number to retexture")
    prompt: str = Field(..., min_length=1, max_length=8192, description="Texture description")
    callback: Optional[HttpUrl] = Field(None, description="Optional webhook URL")

    model_config = ConfigDict(populate_by_name=True)


class RemoveBackgroundRequest(BaseModel):
    """Request for background removal."""

    job_id: str = Field(..., alias="jobId", description="ID of the original image")
    image_no: int = Field(..., alias="imageNo", ge=0, le=3, description="Image number to process")
    callback: Optional[HttpUrl] = Field(None, description="Optional webhook URL")

    model_config = ConfigDict(populate_by_name=True)


class EnhanceRequest(BaseModel):
    """Request for enhance operation."""

    job_id: str = Field(..., alias="jobId", description="ID of the draft mode image to enhance")
    image_no: int = Field(..., alias="imageNo", ge=0, le=3, description="Image number to enhance")
    callback: Optional[HttpUrl] = Field(None, description="Optional webhook URL")

    model_config = ConfigDict(populate_by_name=True)


class VideoDiffusionRequest(BaseModel):
    """Request for video generation."""

    prompt: Optional[str] = Field(
        None, min_length=1, max_length=8192, description="Text prompt for video generation"
    )
    image_url: Optional[HttpUrl] = Field(
        None, alias="imageUrl", description="Optional image to use as video source"
    )
    duration: Optional[int] = Field(None, ge=1, description="Video duration in seconds")
    callback: Optional[HttpUrl] = Field(None, description="Optional webhook URL")

    @field_validator("prompt")
    @classmethod
    def validate_prompt_or_image(cls, v: Optional[str], info: Any) -> Optional[str]:
        """Validate that either prompt or image_url is provided."""
        if v is None and info.data.get("image_url") is None:
            raise ValueError("Either 'prompt' or 'image_url' must be provided")
        return v

    model_config = ConfigDict(populate_by_name=True)


class ExtendVideoRequest(BaseModel):
    """Request for extending video."""

    job_id: str = Field(..., alias="jobId", description="ID of the original video task")
    callback: Optional[HttpUrl] = Field(None, description="Optional webhook URL")

    model_config = ConfigDict(populate_by_name=True)


class VideoUpscaleRequest(BaseModel):
    """Request for video upscaling."""

    job_id: str = Field(..., alias="jobId", description="ID of the original video task")
    callback: Optional[HttpUrl] = Field(None, description="Optional webhook URL")

    model_config = ConfigDict(populate_by_name=True)
