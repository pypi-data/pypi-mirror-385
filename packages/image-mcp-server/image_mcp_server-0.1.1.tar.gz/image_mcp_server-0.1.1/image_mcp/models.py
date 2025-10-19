"""
Data models for Image MCP Server.

Defines Pydantic models for requests, responses, and data validation
based on the data model specification.
"""

import base64
import uuid
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any, Union

from pydantic import BaseModel, Field, field_validator, HttpUrl


class ConfidenceLevel(str, Enum):
    """Confidence levels for analysis results."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class DetectedObject(BaseModel):
    """Represents a detected object in the image."""

    name: str = Field(description="Name of the detected object")
    confidence: float = Field(
        description="Confidence score (0.0 to 1.0)",
        ge=0.0,
        le=1.0
    )
    bounding_box: Optional[Dict[str, int]] = Field(
        None,
        description="Bounding box coordinates (x, y, width, height)"
    )

    class Config:
        schema_extra = {
            "example": {
                "name": "cat",
                "confidence": 0.95,
                "bounding_box": {"x": 100, "y": 50, "width": 200, "height": 150}
            }
        }


class ProcessingState(str, Enum):
    """States for request processing lifecycle."""
    RECEIVED = "received"
    DOWNLOADING = "downloading"
    PROCESSING = "processing"
    API_CALLING = "api_calling"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


class ImageAnalysisRequest(BaseModel):
    """
    Request model for image analysis through MCP protocol.

    Supports both direct image data (base64) and image URLs.
    Enforces size limits and format validation.
    """

    # Core image input - exactly one must be provided
    image_data: Optional[str] = Field(
        None,
        description="Base64 encoded image data (JPEG, PNG, GIF, WebP)",
        max_length=8_000_000,  # ~6MB base64 limit for 10MB original
        pattern=r'^[A-Za-z0-9+/]*={0,2}$'
    )

    image_url: Optional[HttpUrl] = Field(
        None,
        description="HTTP/HTTPS URL to fetch image from"
    )

    # Analysis parameters
    prompt: str = Field(
        default="Analyze this image in detail",
        description="Custom prompt for image analysis",
        max_length=1000
    )

    # Configuration options
    max_size_mb: int = Field(
        default=10,
        description="Maximum allowed image size in MB",
        ge=1,
        le=50
    )

    class Config:
        schema_extra = {
            "example": {
                "image_url": "https://example.com/image.jpg",
                "prompt": "Describe what you see in this image",
                "max_size_mb": 10
            }
        }

    @field_validator('image_data')
    @classmethod
    def validate_base64_image(cls, v, info):
        """Validate base64 image data format and size."""
        if v is None:
            return v

        try:
            # Decode base64 to validate
            image_bytes = base64.b64decode(v)

            # Check size limit
            max_size = info.data.get('max_size_mb', 10) * 1024 * 1024
            if len(image_bytes) > max_size:
                raise ValueError(f"Image size {len(image_bytes)} bytes exceeds limit {max_size} bytes")

            if len(image_bytes) == 0:
                raise ValueError("Image data cannot be empty")

        except base64.binascii.Error:
            raise ValueError("Invalid base64 format")

        return v

    @field_validator('image_url')
    @classmethod
    def validate_image_url(cls, v):
        """Validate image URL format and accessibility."""
        if v is None:
            return v

        # Ensure URL has image file extension
        url_str = str(v)
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}

        if not any(url_str.lower().endswith(ext) for ext in image_extensions):
            raise ValueError(f"URL must end with valid image extension: {image_extensions}")

        return v

    @field_validator('image_url', 'image_data')
    @classmethod
    def validate_image_source(cls, v, info):
        """Ensure exactly one image source is provided."""
        # Check if the other field is already set
        other_field = 'image_data' if info.field_name == 'image_url' else 'image_url'

        if v is not None and info.data.get(other_field) is not None:
            raise ValueError(f"Cannot provide both image_data and image_url")

        return v

    def get_image_source(self) -> dict:
        """Return the image source information."""
        if self.image_data:
            return {"type": "base64", "data": self.image_data}
        elif self.image_url:
            return {"type": "url", "url": str(self.image_url)}
        else:
            raise ValueError("No image source provided")


class ImageAnalysisResponse(BaseModel):
    """
    Response model containing structured image analysis results.

    Includes description, confidence metrics, detected objects, and metadata.
    """

    # Core analysis results
    description: str = Field(
        description="Detailed description of the image content",
        max_length=2000
    )

    confidence_level: ConfidenceLevel = Field(
        description="Overall confidence level of the analysis"
    )

    confidence_score: float = Field(
        description="Numerical confidence score (0.0 to 1.0)",
        ge=0.0,
        le=1.0
    )

    # Object detection
    objects: List[DetectedObject] = Field(
        default=[],
        description="List of detected objects with confidence scores"
    )

    # Additional analysis
    tags: List[str] = Field(
        default=[],
        description="Descriptive tags for the image",
        max_items=20
    )

    colors: List[str] = Field(
        default=[],
        description="Dominant colors detected in the image",
        max_items=10
    )

    # Metadata
    analysis_time: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when analysis was performed"
    )

    processing_time_ms: int = Field(
        description="Time taken to process the request in milliseconds"
    )

    model_used: str = Field(
        default="qwen3-vl-plus",
        description="Model used for analysis"
    )

    request_id: Optional[str] = Field(
        None,
        description="Unique identifier for the request"
    )

    # Image metadata
    image_format: Optional[str] = Field(
        None,
        description="Format of the processed image"
    )

    image_size_bytes: Optional[int] = Field(
        None,
        description="Size of the processed image in bytes"
    )

    class Config:
        schema_extra = {
            "example": {
                "description": "A orange cat sitting on a wooden table next to a laptop computer",
                "confidence_level": "high",
                "confidence_score": 0.92,
                "objects": [
                    {
                        "name": "cat",
                        "confidence": 0.95,
                        "bounding_box": {"x": 120, "y": 80, "width": 180, "height": 140}
                    },
                    {
                        "name": "laptop",
                        "confidence": 0.88,
                        "bounding_box": {"x": 50, "y": 100, "width": 200, "height": 120}
                    }
                ],
                "tags": ["cat", "laptop", "table", "indoor", "technology"],
                "colors": ["orange", "brown", "gray", "black"],
                "processing_time_ms": 1250,
                "image_format": "jpeg",
                "image_size_bytes": 2048576
            }
        }


class RequestState(BaseModel):
    """Tracks the state of an image analysis request."""

    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    state: ProcessingState = Field(default=ProcessingState.RECEIVED)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    error_message: Optional[str] = None
    processing_time_ms: Optional[int] = None

    def update_state(self, new_state: ProcessingState, error_msg: Optional[str] = None):
        """Update the processing state."""
        self.state = new_state
        self.updated_at = datetime.utcnow()
        if error_msg:
            self.error_message = error_msg

    def get_duration_ms(self) -> int:
        """Get total processing duration in milliseconds."""
        return int((self.updated_at - self.created_at).total_seconds() * 1000)


class ErrorResponse(BaseModel):
    """Standard error response format."""

    error_code: str = Field(description="Machine-readable error code")
    error_message: str = Field(description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    request_id: Optional[str] = Field(None, description="Request identifier")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        schema_extra = {
            "example": {
                "error_code": "INVALID_IMAGE_FORMAT",
                "error_message": "Unsupported image format. Supported formats: JPEG, PNG, GIF, WebP",
                "details": {"provided_format": "bmp", "supported_formats": ["JPEG", "PNG", "GIF", "WebP"]},
                "request_id": "req_123456789",
                "timestamp": "2025-10-19T10:30:00Z"
            }
        }