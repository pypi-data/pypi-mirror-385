"""Response models for the Legnext SDK."""

from typing import Any, Optional

from pydantic import BaseModel, Field

from .enums import JobStatus, TaskType
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
    output: Optional[ImageOutput] = Field(None, description="Output results (null until completed)")
    meta: Optional[Meta] = Field(None, description="Task metadata")
    detail: Optional[dict[str, Any]] = Field(None, description="Additional task details")
    logs: Optional[list[str]] = Field(None, description="Processing logs")
    error: Optional[Error] = Field(None, description="Error details if failed")


class ErrorResponse(BaseModel):
    """Error response from API."""

    error: Error = Field(..., description="Error details")
