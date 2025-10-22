"""Legnext Python SDK - Official client for the Legnext AI API."""

from legnext.client import AsyncClient, Client
from legnext.types import (
    BlendRequest,
    Canvas,
    CanvasImg,
    DescribeRequest,
    DiffusionRequest,
    EditRequest,
    EnhanceRequest,
    ExtendVideoRequest,
    InpaintRequest,
    JobStatus,
    LegnextAPIError,
    LegnextError,
    Mask,
    OutpaintRequest,
    PanDirection,
    PanRequest,
    Polygon,
    RemixRequest,
    RemoveBackgroundRequest,
    RerollRequest,
    RetextureRequest,
    ShortenRequest,
    TaskResponse,
    TaskType,
    UploadPaintRequest,
    UpscaleRequest,
    Usage,
    UsageType,
    VariationRequest,
    VideoDiffusionRequest,
    VideoUpscaleRequest,
)

__version__ = "0.2.1"

__all__ = [
    # Main clients
    "Client",
    "AsyncClient",
    # Common types
    "JobStatus",
    "TaskType",
    "UsageType",
    "PanDirection",
    "TaskResponse",
    "Usage",
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
    # Canvas types (for edit/upload_paint operations)
    "Canvas",
    "CanvasImg",
    "Mask",
    "Polygon",
]
