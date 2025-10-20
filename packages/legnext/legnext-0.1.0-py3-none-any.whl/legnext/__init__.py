"""Legnext Python SDK - Official client for the Legnext AI API."""

from legnext.client import AsyncClient, Client
from legnext.types import (
    AccountInfo,
    ActiveTask,
    ActiveTasksResponse,
    BlendRequest,
    DescribeRequest,
    DiffusionRequest,
    EditRequest,
    EnhanceRequest,
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
)

__version__ = "0.1.0"

__all__ = [
    # Main clients
    "Client",
    "AsyncClient",
    # Common types
    "JobStatus",
    "TaskType",
    "TaskResponse",
    "AccountInfo",
    "ActiveTask",
    "ActiveTasksResponse",
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
]
