"""
Custom exceptions for Image MCP Server.

Provides specific exception types for different error scenarios
with appropriate error codes and messages.
"""

from typing import Optional, Dict, Any


class ImageMCPError(Exception):
    """Base exception for Image MCP Server errors."""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__.upper()
        self.details = details or {}
        self.request_id = request_id


class ValidationError(ImageMCPError):
    """Raised when input validation fails."""

    def __init__(self, message: str, field: Optional[str] = None, **kwargs):
        super().__init__(message, error_code="VALIDATION_ERROR", **kwargs)
        self.field = field
        if field:
            self.details["field"] = field


class ImageProcessingError(ImageMCPError):
    """Raised when image processing fails."""

    def __init__(self, message: str, **kwargs):
        super().__init__(message, error_code="IMAGE_PROCESSING_ERROR", **kwargs)


class APIError(ImageMCPError):
    """Raised when DashScope API call fails."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        api_response: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        super().__init__(message, error_code="API_ERROR", **kwargs)
        self.status_code = status_code
        self.api_response = api_response

        if status_code:
            self.details["status_code"] = status_code
        if api_response:
            self.details["api_response"] = api_response


class ConfigurationError(ImageMCPError):
    """Raised when configuration is invalid."""

    def __init__(self, message: str, config_key: Optional[str] = None, **kwargs):
        super().__init__(message, error_code="CONFIGURATION_ERROR", **kwargs)
        self.config_key = config_key
        if config_key:
            self.details["config_key"] = config_key


class NetworkError(ImageMCPError):
    """Raised when network operations fail."""

    def __init__(self, message: str, url: Optional[str] = None, **kwargs):
        super().__init__(message, error_code="NETWORK_ERROR", **kwargs)
        self.url = url
        if url:
            self.details["url"] = url


class TimeoutError(ImageMCPError):
    """Raised when operations timeout."""

    def __init__(self, message: str, timeout_seconds: Optional[int] = None, **kwargs):
        super().__init__(message, error_code="TIMEOUT_ERROR", **kwargs)
        self.timeout_seconds = timeout_seconds
        if timeout_seconds:
            self.details["timeout_seconds"] = timeout_seconds


class RateLimitError(ImageMCPError):
    """Raised when API rate limits are exceeded."""

    def __init__(
        self,
        message: str,
        retry_after: Optional[int] = None,
        limit_type: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, error_code="RATE_LIMIT_ERROR", **kwargs)
        self.retry_after = retry_after
        self.limit_type = limit_type

        if retry_after:
            self.details["retry_after"] = retry_after
        if limit_type:
            self.details["limit_type"] = limit_type


class AuthenticationError(ImageMCPError):
    """Raised when API authentication fails."""

    def __init__(self, message: str, **kwargs):
        super().__init__(message, error_code="AUTHENTICATION_ERROR", **kwargs)


class UnsupportedFormatError(ValidationError):
    """Raised when image format is not supported."""

    def __init__(self, format_name: str, supported_formats: list, **kwargs):
        message = f"Unsupported image format: {format_name}. Supported formats: {supported_formats}"
        super().__init__(
            message,
            field="image_format",
            details={
                "provided_format": format_name,
                "supported_formats": supported_formats
            },
            **kwargs
        )


class ImageTooLargeError(ValidationError):
    """Raised when image size exceeds limits."""

    def __init__(self, size_bytes: int, max_size_bytes: int, **kwargs):
        message = f"Image size {size_bytes} bytes exceeds maximum {max_size_bytes} bytes"
        super().__init__(
            message,
            field="image_size",
            details={
                "provided_size": size_bytes,
                "max_size": max_size_bytes
            },
            **kwargs
        )


class InvalidBase64Error(ValidationError):
    """Raised when base64 data is malformed."""

    def __init__(self, message: str = "Invalid base64 format", **kwargs):
        super().__init__(message, field="image_data", **kwargs)


class MissingImageSourceError(ValidationError):
    """Raised when neither image_data nor image_url is provided."""

    def __init__(self, **kwargs):
        message = "Either image_data or image_url must be provided"
        super().__init__(message, **kwargs)


class ConflictingImageSourcesError(ValidationError):
    """Raised when both image_data and image_url are provided."""

    def __init__(self, **kwargs):
        message = "Cannot provide both image_data and image_url"
        super().__init__(message, **kwargs)


class URLNotAccessibleError(NetworkError):
    """Raised when image URL cannot be accessed."""

    def __init__(self, url: str, status_code: Optional[int] = None, **kwargs):
        message = f"Cannot access image URL: {url}"
        super().__init__(message, url=url, **kwargs)
        self.status_code = status_code
        if status_code:
            self.details["status_code"] = status_code


class EmptyImageError(ValidationError):
    """Raised when image data is empty."""

    def __init__(self, **kwargs):
        message = "Image data cannot be empty"
        super().__init__(message, field="image_data", **kwargs)


# Mapping of error codes to HTTP status codes for web interface
ERROR_STATUS_MAPPING = {
    "VALIDATION_ERROR": 400,
    "IMAGE_PROCESSING_ERROR": 400,
    "UNSUPPORTED_FORMAT_ERROR": 400,
    "IMAGE_TOO_LARGE_ERROR": 413,
    "INVALID_BASE64_ERROR": 400,
    "MISSING_IMAGE_SOURCE_ERROR": 400,
    "CONFLICTING_IMAGE_SOURCES_ERROR": 400,
    "URL_NOT_ACCESSIBLE_ERROR": 400,
    "EMPTY_IMAGE_ERROR": 400,
    "AUTHENTICATION_ERROR": 401,
    "RATE_LIMIT_ERROR": 429,
    "NETWORK_ERROR": 503,
    "TIMEOUT_ERROR": 408,
    "API_ERROR": 502,
    "CONFIGURATION_ERROR": 500,
    "IMAGE_MCP_ERROR": 500,
}


def get_http_status_for_error(error_code: str) -> int:
    """Get appropriate HTTP status code for error type."""
    return ERROR_STATUS_MAPPING.get(error_code, 500)