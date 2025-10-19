"""
DashScope API client wrapper for Image MCP Server.

Handles communication with Alibaba Cloud's DashScope API using
OpenAI-compatible interface with retry logic and error handling.
"""

import json
import base64
import logging
import asyncio
from typing import Dict, Any, Optional
from io import BytesIO

import openai
from openai import AsyncOpenAI
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log
)

from image_mcp.config import APIConfiguration
from image_mcp.exceptions import (
    APIError,
    AuthenticationError,
    RateLimitError,
    NetworkError,
    TimeoutError,
    ConfigurationError
)
from image_mcp.logging import get_logger, RequestLogger


class DashScopeClient:
    """
    Client for interacting with DashScope API using OpenAI-compatible interface.

    Provides image analysis capabilities with automatic retry logic,
    error handling, and structured logging.
    """

    def __init__(self, config: APIConfiguration):
        """
        Initialize the DashScope client.

        Args:
            config: API configuration settings

        Raises:
            ConfigurationError: If configuration is invalid
        """
        self.config = config
        self.logger = get_logger("client")
        self.request_logger = RequestLogger(self.logger)

        # Validate configuration
        self._validate_config()

        # Initialize OpenAI client with DashScope compatibility
        self._client = AsyncOpenAI(
            api_key=config.dashscope_api_key,
            base_url=config.dashscope_base_url,
            timeout=config.request_timeout
        )

        self.logger.info(
            "DashScope client initialized",
            extra={
                "model": config.model_name,
                "base_url": config.dashscope_base_url,
                "timeout": config.request_timeout,
                "max_retries": config.max_retries
            }
        )

    def _validate_config(self) -> None:
        """Validate client configuration."""
        if not self.config.dashscope_api_key or len(self.config.dashscope_api_key.strip()) < 10:
            raise ConfigurationError(
                "API key must be at least 10 characters long",
                config_key="dashscope_api_key"
            )

        if not self.config.dashscope_base_url.startswith(('http://', 'https://')):
            raise ConfigurationError(
                "Base URL must start with http:// or https://",
                config_key="dashscope_base_url"
            )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((
            openai.APIError,
            openai.APITimeoutError,
            openai.RateLimitError
        )),
        before_sleep=before_sleep_log(get_logger("client"), logging.WARNING)
    )
    async def analyze_image(
        self,
        image_data: str,
        prompt: str,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Analyze an image using base64 data.

        Args:
            image_data: Base64 encoded image data
            prompt: Analysis prompt
            max_tokens: Maximum tokens in response (optional)

        Returns:
            Dictionary containing analysis results

        Raises:
            APIError: If API call fails
            AuthenticationError: If authentication fails
            RateLimitError: If rate limit is exceeded
            TimeoutError: If request times out
            NetworkError: If network error occurs
        """
        request_id = f"req_{hash(image_data + prompt) % 1000000:06d}"
        self.request_logger.start_request(
            request_id,
            image_source="base64",
            prompt_length=len(prompt),
            max_tokens=max_tokens
        )

        try:
            # Prepare image data URL
            image_format = self._detect_image_format(image_data)
            data_url = f"data:image/{image_format.lower()};base64,{image_data}"

            # Prepare messages for the API
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": data_url
                            }
                        }
                    ]
                }
            ]

            self.request_logger.log_step("api_call_started", model=self.config.model_name)

            # Make API call
            response = await self._client.chat.completions.create(
                model=self.config.model_name,
                messages=messages,
                max_tokens=max_tokens or 1000,
                temperature=0.7,
                response_format={"type": "json_object"}
            )

            self.request_logger.log_step("api_call_completed")

            # Process response
            if not response.choices or not response.choices[0].message:
                raise APIError("No response content from API")

            content = response.choices[0].message.content
            if not content:
                raise APIError("Empty response content from API")

            # Parse JSON response
            try:
                analysis_result = json.loads(content)
            except json.JSONDecodeError as e:
                raise APIError(f"Invalid JSON response from API: {e}")

            # Add metadata
            analysis_result.update({
                "model_used": self.config.model_name,
                "processing_metadata": {
                    "response_id": response.id,
                    "usage": response.usage.model_dump() if response.usage else None
                }
            })

            self.request_logger.complete_request(
                response_tokens=response.usage.completion_tokens if response.usage else 0,
                total_tokens=response.usage.total_tokens if response.usage else 0
            )

            self.logger.info(
                "Image analysis completed successfully",
                extra={
                    "request_id": request_id,
                    "image_format": image_format,
                    "response_tokens": response.usage.completion_tokens if response.usage else 0
                }
            )

            return analysis_result

        except openai.AuthenticationError as e:
            error_msg = f"Authentication failed: {e}"
            self.request_logger.fail_request(e, error_type="authentication_error")
            self.logger.error(error_msg, extra={"request_id": request_id})
            raise AuthenticationError(error_msg)

        except openai.RateLimitError as e:
            retry_after = None
            if hasattr(e, 'response') and e.response.headers:
                retry_after = e.response.headers.get('retry-after')

            error_msg = f"Rate limit exceeded: {e}"
            self.request_logger.fail_request(
                e,
                error_type="rate_limit_error",
                retry_after=retry_after
            )
            self.logger.warning(error_msg, extra={"request_id": request_id})
            raise RateLimitError(error_msg, retry_after=retry_after)

        except openai.APITimeoutError as e:
            error_msg = f"Request timeout: {e}"
            self.request_logger.fail_request(e, error_type="timeout_error")
            self.logger.error(error_msg, extra={"request_id": request_id})
            raise TimeoutError(error_msg, timeout_seconds=self.config.request_timeout)

        except openai.APIError as e:
            error_msg = f"API error: {e}"
            self.request_logger.fail_request(e, error_type="api_error")
            self.logger.error(error_msg, extra={"request_id": request_id})
            raise APIError(error_msg)

        except Exception as e:
            error_msg = f"Unexpected error: {e}"
            self.request_logger.fail_request(e, error_type="unexpected_error")
            self.logger.error(error_msg, extra={"request_id": request_id})
            raise APIError(error_msg)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((
            openai.APIError,
            openai.APITimeoutError,
            openai.RateLimitError
        ))
    )
    async def analyze_image_with_url(
        self,
        image_url: str,
        prompt: str,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Analyze an image from URL.

        Args:
            image_url: URL of the image to analyze
            prompt: Analysis prompt
            max_tokens: Maximum tokens in response (optional)

        Returns:
            Dictionary containing analysis results

        Raises:
            APIError: If API call fails
            NetworkError: If URL is not accessible
        """
        request_id = f"req_{hash(image_url + prompt) % 1000000:06d}"
        self.request_logger.start_request(
            request_id,
            image_source="url",
            image_url=image_url,
            prompt_length=len(prompt),
            max_tokens=max_tokens
        )

        try:
            # Prepare messages for the API
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_url
                            }
                        }
                    ]
                }
            ]

            self.request_logger.log_step("api_call_started", model=self.config.model_name)

            # Make API call
            response = await self._client.chat.completions.create(
                model=self.config.model_name,
                messages=messages,
                max_tokens=max_tokens or 1000,
                temperature=0.7,
                response_format={"type": "json_object"}
            )

            self.request_logger.log_step("api_call_completed")

            # Process response
            if not response.choices or not response.choices[0].message:
                raise APIError("No response content from API")

            content = response.choices[0].message.content
            if not content:
                raise APIError("Empty response content from API")

            # Parse JSON response
            try:
                analysis_result = json.loads(content)
            except json.JSONDecodeError as e:
                raise APIError(f"Invalid JSON response from API: {e}")

            # Add metadata
            analysis_result.update({
                "model_used": self.config.model_name,
                "processing_metadata": {
                    "response_id": response.id,
                    "usage": response.usage.model_dump() if response.usage else None
                }
            })

            self.request_logger.complete_request(
                response_tokens=response.usage.completion_tokens if response.usage else 0,
                total_tokens=response.usage.total_tokens if response.usage else 0
            )

            self.logger.info(
                "Image analysis from URL completed successfully",
                extra={
                    "request_id": request_id,
                    "image_url": image_url,
                    "response_tokens": response.usage.completion_tokens if response.usage else 0
                }
            )

            return analysis_result

        except openai.AuthenticationError as e:
            error_msg = f"Authentication failed: {e}"
            self.request_logger.fail_request(e, error_type="authentication_error")
            self.logger.error(error_msg, extra={"request_id": request_id})
            raise AuthenticationError(error_msg)

        except openai.RateLimitError as e:
            retry_after = None
            if hasattr(e, 'response') and e.response.headers:
                retry_after = e.response.headers.get('retry-after')

            error_msg = f"Rate limit exceeded: {e}"
            self.request_logger.fail_request(
                e,
                error_type="rate_limit_error",
                retry_after=retry_after
            )
            self.logger.warning(error_msg, extra={"request_id": request_id})
            raise RateLimitError(error_msg, retry_after=retry_after)

        except openai.APITimeoutError as e:
            error_msg = f"Request timeout: {e}"
            self.request_logger.fail_request(e, error_type="timeout_error")
            self.logger.error(error_msg, extra={"request_id": request_id})
            raise TimeoutError(error_msg, timeout_seconds=self.config.request_timeout)

        except openai.APIError as e:
            error_msg = f"API error: {e}"
            self.request_logger.fail_request(e, error_type="api_error")
            self.logger.error(error_msg, extra={"request_id": request_id})
            raise APIError(error_msg)

        except Exception as e:
            error_msg = f"Unexpected error: {e}"
            self.request_logger.fail_request(e, error_type="unexpected_error")
            self.logger.error(error_msg, extra={"request_id": request_id})
            raise APIError(error_msg)

    def _detect_image_format(self, base64_data: str) -> str:
        """
        Detect image format from base64 data.

        Args:
            base64_data: Base64 encoded image data

        Returns:
            Image format string (JPEG, PNG, GIF, WebP)

        Raises:
            APIError: If format is not supported
        """
        try:
            # Decode base64 to check header bytes
            image_bytes = base64.b64decode(base64_data)

            # Check image format based on header bytes
            if image_bytes.startswith(b'\x89PNG\r\n\x1a\n'):
                return "PNG"
            elif image_bytes.startswith(b'\xff\xd8\xff'):
                return "JPEG"
            elif image_bytes.startswith(b'GIF87a') or image_bytes.startswith(b'GIF89a'):
                return "GIF"
            elif image_bytes.startswith(b'RIFF') and b'WEBP' in image_bytes[:12]:
                return "WebP"
            else:
                # Try to detect from data URL pattern
                if len(base64_data) > 100:
                    # Common patterns for different formats
                    if base64_data.startswith('/9j/'):
                        return "JPEG"
                    elif base64_data.startswith('iVBORw0K'):
                        return "PNG"
                    elif base64_data.startswith('R0lGOD'):
                        return "GIF"
                    elif base64_data.startswith('UklGR'):
                        return "WebP"

                raise APIError(f"Unsupported image format. Supported formats: {self.config.supported_formats}")

        except Exception as e:
            if isinstance(e, APIError):
                raise
            raise APIError(f"Failed to detect image format: {e}")

    async def test_connection(self) -> bool:
        """
        Test connection to the API.

        Returns:
            True if connection is successful, False otherwise
        """
        try:
            # Simple test with minimal data
            await self._client.models.list()
            self.logger.info("API connection test successful")
            return True
        except Exception as e:
            self.logger.error(f"API connection test failed: {e}")
            return False

    async def close(self):
        """Close the client and cleanup resources."""
        if hasattr(self._client, 'close'):
            await self._client.close()
        self.logger.info("DashScope client closed")