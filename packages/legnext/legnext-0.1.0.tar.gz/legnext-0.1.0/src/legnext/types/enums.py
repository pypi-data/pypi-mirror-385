"""Enumeration types for the Legnext SDK."""

from enum import Enum


class JobStatus(str, Enum):
    """Current status of a job."""

    PENDING = "pending"
    STAGED = "staged"
    PROCESSING = "processing"
    FAILED = "failed"
    COMPLETED = "completed"


class TaskType(str, Enum):
    """Type of task being performed."""

    DIFFUSION = "diffusion"
    VARIATION = "variation"
    UPSCALE = "upscale"
    REROLL = "reroll"
    BLEND = "blend"
    DESCRIBE = "describe"
    SHORTEN = "shorten"
    PAN = "pan"
    OUTPAINT = "outpaint"
    INPAINT = "inpaint"
    REMIX = "remix"
    EDIT = "edit"
    UPLOAD_PAINT = "upload-paint"
    RETEXTURE = "retexture"
    REMOVE_BACKGROUND = "remove-background"
    ENHANCE = "enhance"
    VIDEO_DIFFUSION = "video-diffusion"
    EXTEND_VIDEO = "extend-video"
    VIDEO_UPSCALE = "video-upscale"


class ServiceMode(str, Enum):
    """Service mode for the API."""

    PUBLIC = "public"
    PRIVATE = "private"


class UsageType(str, Enum):
    """Type of usage quota."""

    POINT = "point"
    CREDIT = "credit"


class AccountPlan(str, Enum):
    """Account subscription plan."""

    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    PREMIUM = "premium"


class AccountStatus(str, Enum):
    """Account status."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    LIMITED = "limited"


class PanDirection(str, Enum):
    """Direction for pan/extend operation."""

    LEFT = "left"
    RIGHT = "right"
    UP = "up"
    DOWN = "down"
