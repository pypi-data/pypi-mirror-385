"""Tests for type models."""

import pytest
from pydantic import ValidationError

from legnext.types import (
    DiffusionRequest,
    JobStatus,
    TaskResponse,
    TaskType,
    VariationRequest,
)


def test_job_status_enum():
    """Test JobStatus enum values."""
    assert JobStatus.PENDING == "pending"
    assert JobStatus.COMPLETED == "completed"
    assert JobStatus.FAILED == "failed"


def test_task_type_enum():
    """Test TaskType enum values."""
    assert TaskType.DIFFUSION == "diffusion"
    assert TaskType.VARIATION == "variation"
    assert TaskType.UPSCALE == "upscale"


def test_diffusion_request_valid():
    """Test valid DiffusionRequest."""
    request = DiffusionRequest(text="a beautiful sunset")
    assert request.text == "a beautiful sunset"
    assert request.callback is None


def test_diffusion_request_validation():
    """Test DiffusionRequest validation."""
    # Text too short
    with pytest.raises(ValidationError):
        DiffusionRequest(text="")

    # Text too long
    with pytest.raises(ValidationError):
        DiffusionRequest(text="x" * 10000)


def test_variation_request_valid():
    """Test valid VariationRequest."""
    request = VariationRequest(job_id="test-job", image_no=0, type=1)
    assert request.job_id == "test-job"
    assert request.image_no == 0
    assert request.type == 1


def test_variation_request_validation():
    """Test VariationRequest validation."""
    # Invalid image_no (must be 0-3)
    with pytest.raises(ValidationError):
        VariationRequest(job_id="test", image_no=5, type=0)

    # Invalid type (must be 0-1)
    with pytest.raises(ValidationError):
        VariationRequest(job_id="test", image_no=0, type=2)


def test_task_response_parsing(mock_task_response):
    """Test TaskResponse parsing."""
    response = TaskResponse.model_validate(mock_task_response)
    assert response.job_id == mock_task_response["job_id"]
    assert response.status == JobStatus.COMPLETED
    assert len(response.output.image_urls) == 4
