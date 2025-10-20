"""Response models for the Legnext SDK."""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field

from .enums import AccountPlan, AccountStatus, JobStatus, TaskType
from .errors import Error
from .shared import Config, ImageOutput, Meta


class TaskResponse(BaseModel):
    """Response from task operations."""

    job_id: str = Field(..., description="Unique job identifier")
    model: str = Field(..., description="Model used for processing")
    task_type: TaskType = Field(..., description="Type of task")
    status: JobStatus = Field(..., description="Current status")
    config: Optional[Config] = Field(None, description="Task configuration")
    input: Optional[dict[str, Any]] = Field(
        None, description="Input parameters (structure varies by task type)"
    )
    output: Optional[ImageOutput] = Field(
        None, description="Output results (null until completed)"
    )
    meta: Optional[Meta] = Field(None, description="Task metadata")
    detail: Optional[dict[str, Any]] = Field(None, description="Additional task details")
    logs: Optional[list[str]] = Field(None, description="Processing logs")
    error: Optional[Error] = Field(None, description="Error details if failed")


class ErrorResponse(BaseModel):
    """Error response from API."""

    error: Error = Field(..., description="Error details")


class QuotaInfo(BaseModel):
    """Quota information for account."""

    monthly_limit: Optional[float] = Field(None, description="Monthly credit limit")
    remaining: Optional[float] = Field(None, description="Remaining credits this month")
    reset_at: Optional[datetime] = Field(None, description="When the monthly quota resets")


class AccountInfo(BaseModel):
    """Account information response."""

    account_id: str = Field(..., description="Unique account identifier")
    email: Optional[str] = Field(None, description="Account email address")
    plan: AccountPlan = Field(..., description="Current subscription plan")
    balance: float = Field(..., description="Current account balance/credits")
    used: float = Field(..., description="Total used credits")
    quota: Optional[QuotaInfo] = Field(None, description="Quota information")
    status: AccountStatus = Field(..., description="Account status")
    created_at: datetime = Field(..., description="Account creation timestamp")
    updated_at: datetime = Field(..., description="Last account update timestamp")


class ActiveTask(BaseModel):
    """Information about an active task."""

    job_id: str = Field(..., description="Unique job identifier")
    task_type: TaskType = Field(..., description="Type of task")
    status: JobStatus = Field(..., description="Current status")
    created_at: datetime = Field(..., description="When the task was created")
    progress: float = Field(..., ge=0, le=100, description="Task progress percentage")
    estimated_time: Optional[int] = Field(
        None, description="Estimated remaining time in seconds"
    )


class ActiveTasksResponse(BaseModel):
    """Response containing active tasks."""

    account_id: str = Field(..., description="Account identifier")
    total_active: int = Field(..., description="Total number of active tasks")
    concurrent_limit: int = Field(..., description="Maximum concurrent tasks allowed")
    tasks: list[ActiveTask] = Field(..., description="List of currently active tasks")
    updated_at: datetime = Field(..., description="When this response was generated")
