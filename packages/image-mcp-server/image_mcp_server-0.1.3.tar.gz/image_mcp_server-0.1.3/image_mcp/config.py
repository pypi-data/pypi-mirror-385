"""
Configuration management for Image MCP Server.

Handles environment variable configuration and validation for
DashScope API integration and server settings.
"""

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings
from typing import List, Optional, Dict, Any

from image_mcp.exceptions import ConfigurationError


class APIConfiguration(BaseSettings):
    """
    Configuration settings for DashScope API integration.

    Supports both China and Singapore regions with flexible authentication.
    """

    # Authentication
    dashscope_api_key: str = Field(
        ...,
        description="DashScope API key for authentication",
        min_length=10
    )

    # API endpoints
    dashscope_base_url: str = Field(
        default="https://dashscope.aliyuncs.com/compatible-mode/v1",
        description="DashScope API base URL"
    )

    # Model configuration
    model_name: str = Field(
        default="qwen3-vl-plus",
        description="Model name for image analysis"
    )

    # Request configuration
    request_timeout: int = Field(
        default=30,
        description="Request timeout in seconds",
        ge=5,
        le=300
    )

    max_retries: int = Field(
        default=3,
        description="Maximum number of retry attempts",
        ge=0,
        le=10
    )

    retry_delay: float = Field(
        default=1.0,
        description="Base delay between retries in seconds",
        ge=0.1,
        le=10.0
    )

    # Image processing limits
    max_image_size_mb: int = Field(
        default=10,
        description="Maximum allowed image size in MB",
        ge=1,
        le=50
    )

    supported_formats: List[str] = Field(
        default=["JPEG", "PNG", "GIF", "WEBP"],
        description="Supported image formats"
    )

    # Logging and monitoring
    enable_debug_logging: bool = Field(
        default=False,
        description="Enable debug logging"
    )

    log_level: str = Field(
        default="INFO",
        description="Logging level",
        pattern=r'^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$'
    )

    class Config:
        env_file = ".env"
        env_prefix = "IMAGE_MCP_"
        case_sensitive = False

    @field_validator('dashscope_api_key')
    @classmethod
    def validate_api_key(cls, v):
        """Validate API key format."""
        if not v or len(v.strip()) < 10:
            raise ValueError("API key must be at least 10 characters long")
        return v.strip()

    @field_validator('dashscope_base_url')
    @classmethod
    def validate_base_url(cls, v):
        """Validate and normalize base URL."""
        if not v.startswith(('http://', 'https://')):
            raise ValueError("Base URL must start with http:// or https://")

        # Remove trailing slash
        return v.rstrip('/')

    @field_validator('supported_formats')
    @classmethod
    def validate_formats(cls, v):
        """Validate supported image formats."""
        valid_formats = {"JPEG", "PNG", "GIF", "WEBP", "JPG"}

        # Handle None or empty values
        if not v:
            raise ValueError("Supported formats cannot be empty")

        for fmt in v:
            if not fmt:
                raise ValueError("Format cannot be empty string")
            fmt_upper = fmt.upper()
            if fmt_upper not in valid_formats:
                raise ValueError(f"Unsupported format: {fmt}. Valid formats: {valid_formats}")

        # Convert all formats to uppercase for consistency
        return [fmt.upper() for fmt in v]

    def get_region_config(self) -> Dict[str, Any]:
        """Get region-specific configuration."""
        if "dashscope-intl" in self.dashscope_base_url:
            return {
                "region": "singapore",
                "currency": "USD",
                "endpoint_notes": "International endpoint"
            }
        else:
            return {
                "region": "china",
                "currency": "CNY",
                "endpoint_notes": "China endpoint"
            }

    def validate_configuration(self) -> None:
        """
        Validate the complete configuration.

        Raises:
            ConfigurationError: If configuration is invalid
        """
        try:
            # Validate API key
            if not self.dashscope_api_key or len(self.dashscope_api_key.strip()) < 10:
                raise ConfigurationError(
                    "API key must be at least 10 characters long",
                    config_key="dashscope_api_key"
                )

            # Validate base URL
            if not self.dashscope_base_url.startswith(('http://', 'https://')):
                raise ConfigurationError(
                    "Base URL must start with http:// or https://",
                    config_key="dashscope_base_url"
                )

            # Validate timeout ranges
            if not (5 <= self.request_timeout <= 300):
                raise ConfigurationError(
                    f"Request timeout must be between 5 and 300 seconds, got {self.request_timeout}",
                    config_key="request_timeout"
                )

            if not (0 <= self.max_retries <= 10):
                raise ConfigurationError(
                    f"Max retries must be between 0 and 10, got {self.max_retries}",
                    config_key="max_retries"
                )

            if not (0.1 <= self.retry_delay <= 10.0):
                raise ConfigurationError(
                    f"Retry delay must be between 0.1 and 10.0 seconds, got {self.retry_delay}",
                    config_key="retry_delay"
                )

            if not (1 <= self.max_image_size_mb <= 50):
                raise ConfigurationError(
                    f"Max image size must be between 1 and 50 MB, got {self.max_image_size_mb}",
                    config_key="max_image_size_mb"
                )

            # Validate log level
            if self.log_level not in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
                raise ConfigurationError(
                    f"Invalid log level: {self.log_level}",
                    config_key="log_level"
                )

        except Exception as e:
            if isinstance(e, ConfigurationError):
                raise
            raise ConfigurationError(f"Configuration validation failed: {e}")

    def is_china_region(self) -> bool:
        """Check if configuration uses China region endpoint."""
        return "dashscope-intl" not in self.dashscope_base_url

    def is_singapore_region(self) -> bool:
        """Check if configuration uses Singapore region endpoint."""
        return "dashscope-intl" in self.dashscope_base_url

    def get_environment_summary(self) -> Dict[str, Any]:
        """Get a summary of current environment configuration."""
        return {
            "api_endpoint": self.dashscope_base_url,
            "model": self.model_name,
            "region": self.get_region_config()["region"],
            "timeout_seconds": self.request_timeout,
            "max_retries": self.max_retries,
            "max_image_size_mb": self.max_image_size_mb,
            "supported_formats": self.supported_formats,
            "debug_logging": self.enable_debug_logging,
            "log_level": self.log_level,
            "has_api_key": bool(self.dashscope_api_key and len(self.dashscope_api_key.strip()) >= 10),
            "api_key_preview": f"{self.dashscope_api_key[:8]}..." if self.dashscope_api_key and len(self.dashscope_api_key) > 8 else "None"
        }

    def clone_with_overrides(self, **overrides) -> "APIConfiguration":
        """Create a new configuration instance with specific overrides."""
        current_values = self.model_dump()
        current_values.update(overrides)
        return APIConfiguration(**current_values)

    def to_dict_safe(self) -> Dict[str, Any]:
        """Convert configuration to dictionary, excluding sensitive data."""
        config_dict = self.model_dump()

        # Mask API key
        if 'dashscope_api_key' in config_dict:
            api_key = config_dict['dashscope_api_key']
            if api_key and len(api_key) > 8:
                config_dict['dashscope_api_key'] = f"{api_key[:8]}..."
            elif api_key:
                config_dict['dashscope_api_key'] = "***MASKED***"

        return config_dict