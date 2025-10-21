"""Legnext Python SDK - Official client for the Legnext AI API."""

from legnext.client import AsyncClient, Client
from legnext.types import (
    BlendRequest,
    DescribeRequest,
    DiffusionRequest,
    EditRequest,
    EnhanceRequest,
    ExtendVideoRequest,
    InpaintRequest,
    JobStatus,
    LegnextAPIError,
    LegnextError,
    OutpaintRequest,
    PanRequest,
    RemixRequest,
    RemoveBackgroundRequest,
    RerollRequest,
    RetextureRequest,
    ShortenRequest,
    TaskResponse,
    TaskType,
    UploadPaintRequest,
    UpscaleRequest,
    VariationRequest,
    VideoDiffusionRequest,
    VideoUpscaleRequest,
)

__version__ = "0.1.3"

__all__ = [
    # Main clients
    "Client",
    "AsyncClient",
    # Common types
    "JobStatus",
    "TaskType",
    "TaskResponse",
    # Errors
    "LegnextError",
    "LegnextAPIError",
    # Request types (for advanced usage)
    "DiffusionRequest",
    "VariationRequest",
    "UpscaleRequest",
    "RerollRequest",
    "BlendRequest",
    "DescribeRequest",
    "ShortenRequest",
    "PanRequest",
    "OutpaintRequest",
    "InpaintRequest",
    "RemixRequest",
    "EditRequest",
    "UploadPaintRequest",
    "RetextureRequest",
    "RemoveBackgroundRequest",
    "EnhanceRequest",
    "VideoDiffusionRequest",
    "ExtendVideoRequest",
    "VideoUpscaleRequest",
]
