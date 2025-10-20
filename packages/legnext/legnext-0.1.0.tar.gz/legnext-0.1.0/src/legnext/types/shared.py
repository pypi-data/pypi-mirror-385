"""Shared type definitions used across the SDK."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl

from .enums import ServiceMode, UsageType


class WebhookConfig(BaseModel):
    """Webhook configuration for callbacks."""

    endpoint: HttpUrl = Field(description="Webhook URL for callbacks")
    secret: Optional[str] = Field(None, description="Webhook secret for validation")


class Config(BaseModel):
    """Configuration for API requests."""

    service_mode: Optional[ServiceMode] = Field(None, description="Service mode")
    webhook_config: Optional[WebhookConfig] = Field(None, description="Webhook configuration")


class Usage(BaseModel):
    """Usage information for a task."""

    type: UsageType = Field(description="Type of usage quota")
    frozen: int = Field(description="Frozen quota points")
    consume: int = Field(description="Consumed quota points")


class Meta(BaseModel):
    """Metadata about task execution."""

    created_at: datetime = Field(description="When the job was created")
    started_at: Optional[datetime] = Field(None, description="When processing started")
    ended_at: Optional[datetime] = Field(None, description="When processing completed")
    usage: Optional[Usage] = Field(None, description="Usage information")


class ImageOutput(BaseModel):
    """Output from image generation operations."""

    image_url: Optional[HttpUrl] = Field(
        None, description="Single image URL (for single image operations)"
    )
    image_urls: Optional[list[HttpUrl]] = Field(
        None, description="Array of image URLs (typically 4 images for generation)"
    )
    seed: Optional[str] = Field(None, description="Seed used for generation (for reproducibility)")
