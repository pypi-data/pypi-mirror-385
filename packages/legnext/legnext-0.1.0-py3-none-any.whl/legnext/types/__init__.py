"""Type definitions for the Legnext SDK."""

from .enums import JobStatus, TaskType
from .errors import Error, LegnextAPIError, LegnextError
from .requests import (
    BlendRequest,
    DescribeRequest,
    DiffusionRequest,
    EditRequest,
    EnhanceRequest,
    ExtendVideoRequest,
    InpaintRequest,
    OutpaintRequest,
    PanRequest,
    RemixRequest,
    RemoveBackgroundRequest,
    RerollRequest,
    RetextureRequest,
    ShortenRequest,
    UploadPaintRequest,
    UpscaleRequest,
    VariationRequest,
    VideoDiffusionRequest,
    VideoUpscaleRequest,
)
from .responses import (
    AccountInfo,
    ActiveTask,
    ActiveTasksResponse,
    ErrorResponse,
    TaskResponse,
)
from .shared import Config, ImageOutput, Meta, WebhookConfig

__all__ = [
    # Enums
    "JobStatus",
    "TaskType",
    # Errors
    "LegnextError",
    "LegnextAPIError",
    "Error",
    # Requests
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
    # Responses
    "TaskResponse",
    "AccountInfo",
    "ActiveTask",
    "ActiveTasksResponse",
    "ErrorResponse",
    # Shared
    "ImageOutput",
    "Meta",
    "WebhookConfig",
    "Config",
]
