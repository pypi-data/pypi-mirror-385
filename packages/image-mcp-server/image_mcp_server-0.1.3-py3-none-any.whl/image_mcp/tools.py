"""
Image analysis tools for Image MCP Server.

Provides FastMCP tool implementations for image understanding
using DashScope Qwen3-VL-Plus model with validation and processing.
"""

import time
import uuid
from typing import Dict, Any, Optional

from fastmcp import FastMCP

from image_mcp.config import APIConfiguration
from image_mcp.models import ImageAnalysisRequest, ImageAnalysisResponse
from image_mcp.client import DashScopeClient
from image_mcp.processor import ImageProcessor
from image_mcp.exceptions import (
    ImageMCPError,
    ValidationError,
    ImageProcessingError,
    APIError,
    get_http_status_for_error
)
from image_mcp.logging import get_logger, RequestLogger


class ImageAnalyzer:
    """
    FastMCP tool for analyzing images using Qwen3-VL-Plus model.

    Supports both base64 image data and image URLs with comprehensive
    validation, processing, and error handling.
    """

    def __init__(
        self,
        config: APIConfiguration,
        client: Optional[DashScopeClient] = None
    ):
        """
        Initialize the image analyzer.

        Args:
            config: Configuration settings
            client: Optional pre-configured API client
        """
        self.config = config
        self.logger = get_logger("tools")
        self.request_logger = RequestLogger(self.logger)

        # Initialize components
        self.client = client or DashScopeClient(config)
        self.processor = ImageProcessor(config)

        self.logger.info(
            "Image analyzer initialized",
            extra={
                "model": config.model_name,
                "max_size_mb": config.max_image_size_mb,
                "supported_formats": config.supported_formats
            }
        )

    def register_tools(self, mcp_server: FastMCP) -> None:
        """
        Register image analysis tools with the MCP server.

        Args:
            mcp_server: FastMCP server instance
        """
        @mcp_server.tool()
        async def analyze_image(
            image_data: Optional[str] = None,
            image_url: Optional[str] = None,
            prompt: str = "Analyze this image in detail",
            max_size_mb: int = 10
        ) -> Dict[str, Any]:
            """
            Analyze an image using DashScope Qwen3-VL-Plus model.

            Supports both direct image data (base64) and image URLs.
            Returns structured analysis with descriptions, confidence scores,
            detected objects, tags, and colors.

            Args:
                image_data: Base64 encoded image data (JPEG, PNG, GIF, WebP)
                image_url: HTTP/HTTPS URL to fetch image from
                prompt: Custom prompt for image analysis
                max_size_mb: Maximum allowed image size in MB

            Returns:
                Dictionary containing structured analysis results

            Raises:
                ValidationError: If input validation fails
                ImageProcessingError: If image processing fails
                APIError: If API call fails
            """
            return await self.analyze_image(
                image_data=image_data,
                image_url=image_url,
                prompt=prompt,
                max_size_mb=max_size_mb
            )

        self.logger.info("Image analysis tools registered with MCP server")

    async def analyze_image(
        self,
        image_data: Optional[str] = None,
        image_url: Optional[str] = None,
        prompt: str = "Analyze this image in detail",
        max_size_mb: int = 10
    ) -> Dict[str, Any]:
        """
        Analyze an image using Qwen3-VL-Plus model.

        Args:
            image_data: Base64 encoded image data
            image_url: HTTP/HTTPS URL to fetch image from
            prompt: Custom prompt for image analysis
            max_size_mb: Maximum allowed image size in MB

        Returns:
            Dictionary containing structured analysis results

        Raises:
            ValidationError: If input validation fails
            ImageProcessingError: If image processing fails
            APIError: If API call fails
        """
        request_id = str(uuid.uuid4())
        start_time = time.time()

        self.request_logger.start_request(
            request_id,
            has_base64=image_data is not None,
            has_url=image_url is not None,
            prompt_length=len(prompt),
            max_size_mb=max_size_mb
        )

        try:
            # Create and validate request
            request = ImageAnalysisRequest(
                image_data=image_data,
                image_url=image_url,
                prompt=prompt,
                max_size_mb=max_size_mb
            )

            self.request_logger.log_step("request_validated")

            # Process image
            image_info = await self._process_image(request)
            self.request_logger.log_step("image_processed")

            # Analyze with API
            analysis_result = await self._analyze_with_api(request, image_info)
            self.request_logger.log_step("api_analysis_completed")

            # Create response
            processing_time_ms = int((time.time() - start_time) * 1000)
            response = self._create_response(
                analysis_result,
                image_info,
                processing_time_ms,
                request_id
            )

            self.request_logger.complete_request(
                processing_time_ms=processing_time_ms,
                image_format=image_info["format"],
                confidence_score=response.confidence_score
            )

            self.logger.info(
                "Image analysis completed successfully",
                extra={
                    "request_id": request_id,
                    "processing_time_ms": processing_time_ms,
                    "image_format": image_info["format"],
                    "confidence_score": response.confidence_score
                }
            )

            return response.model_dump()

        except (ValidationError, ImageProcessingError, APIError) as e:
            self.request_logger.fail_request(e)
            self.logger.error(
                f"Image analysis failed: {e}",
                extra={
                    "request_id": request_id,
                    "error_type": type(e).__name__,
                    "error_message": str(e)
                }
            )
            raise
        except Exception as e:
            error = ImageMCPError(f"Unexpected error during image analysis: {e}")
            self.request_logger.fail_request(error)
            self.logger.error(
                f"Unexpected error in image analysis: {e}",
                extra={"request_id": request_id},
                exc_info=True
            )
            raise error

    async def _process_image(self, request: ImageAnalysisRequest) -> Dict[str, Any]:
        """
        Process image from request.

        Args:
            request: Validated image analysis request

        Returns:
            Dictionary with processed image information

        Raises:
            ImageProcessingError: If processing fails
        """
        try:
            if request.image_data:
                # Process base64 image
                return await self.processor.process_image_from_base64(
                    request.image_data,
                    request.max_size_mb
                )
            else:
                # Process image from URL
                return await self.processor.process_image_from_url(
                    str(request.image_url),
                    request.max_size_mb
                )
        except Exception as e:
            if isinstance(e, (ImageProcessingError, ValidationError)):
                raise
            raise ImageProcessingError(f"Failed to process image: {e}")

    async def _analyze_with_api(
        self,
        request: ImageAnalysisRequest,
        image_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze image using the API client.

        Args:
            request: Validated image analysis request
            image_info: Processed image information

        Returns:
            Dictionary with API analysis results

        Raises:
            APIError: If API call fails
        """
        try:
            if request.image_data:
                # Analyze base64 image
                return await self.client.analyze_image(
                    request.image_data,
                    request.prompt
                )
            else:
                # Analyze image from URL
                return await self.client.analyze_image_with_url(
                    str(request.image_url),
                    request.prompt
                )
        except Exception as e:
            if isinstance(e, APIError):
                raise
            raise APIError(f"API analysis failed: {e}")

    def _create_response(
        self,
        analysis_result: Dict[str, Any],
        image_info: Dict[str, Any],
        processing_time_ms: int,
        request_id: str
    ) -> ImageAnalysisResponse:
        """
        Create structured response from API result.

        Args:
            analysis_result: Raw API analysis result
            image_info: Processed image information
            processing_time_ms: Processing time in milliseconds
            request_id: Request identifier

        Returns:
            Structured image analysis response
        """
        # Extract and validate required fields from API result
        description = analysis_result.get("description", "No description provided")
        confidence_level = analysis_result.get("confidence_level", "medium")
        confidence_score = float(analysis_result.get("confidence_score", 0.5))

        # Ensure confidence score is within valid range
        confidence_score = max(0.0, min(1.0, confidence_score))

        # Extract optional fields
        objects = analysis_result.get("objects", [])
        tags = analysis_result.get("tags", [])
        colors = analysis_result.get("colors", [])

        # Create response
        return ImageAnalysisResponse(
            description=description,
            confidence_level=confidence_level,
            confidence_score=confidence_score,
            objects=objects,
            tags=tags,
            colors=colors,
            processing_time_ms=processing_time_ms,
            model_used=analysis_result.get("model_used", self.config.model_name),
            request_id=request_id,
            image_format=image_info["format"],
            image_size_bytes=image_info["size_bytes"]
        )

    def _validate_image_size(self, base64_data: str, max_size_mb: int) -> None:
        """
        Validate image size against limits.

        Args:
            base64_data: Base64 encoded image data
            max_size_mb: Maximum allowed size in MB

        Raises:
            ImageTooLargeError: If image is too large
        """
        try:
            image_bytes = base64.b64decode(base64_data)
            max_size_bytes = max_size_mb * 1024 * 1024

            if len(image_bytes) > max_size_bytes:
                from image_mcp.exceptions import ImageTooLargeError
                raise ImageTooLargeError(
                    size_bytes=len(image_bytes),
                    max_size_bytes=max_size_bytes
                )
        except base64.binascii.Error:
            from image_mcp.exceptions import InvalidBase64Error
            raise InvalidBase64Error()

    def _detect_image_format(self, base64_data: str) -> str:
        """
        Detect image format from base64 data.

        Args:
            base64_data: Base64 encoded image data

        Returns:
            Detected image format

        Raises:
            UnsupportedFormatError: If format is not supported
        """
        try:
            image_bytes = base64.b64decode(base64_data)

            # Check image headers
            if image_bytes.startswith(b'\x89PNG\r\n\x1a\n'):
                return "PNG"
            elif image_bytes.startswith(b'\xff\xd8\xff'):
                return "JPEG"
            elif image_bytes.startswith(b'GIF87a') or image_bytes.startswith(b'GIF89a'):
                return "GIF"
            elif image_bytes.startswith(b'RIFF') and b'WEBP' in image_bytes[:12]:
                return "WebP"
            else:
                from image_mcp.exceptions import UnsupportedFormatError
                raise UnsupportedFormatError(
                    "unknown",
                    self.config.supported_formats
                )
        except base64.binascii.Error:
            from image_mcp.exceptions import InvalidBase64Error
            raise InvalidBase64Error()

    def _decode_base64_image(self, base64_data: str) -> bytes:
        """
        Decode base64 image data.

        Args:
            base64_data: Base64 encoded image data

        Returns:
            Decoded image bytes

        Raises:
            ImageProcessingError: If decoding fails
        """
        try:
            return base64.b64decode(base64_data)
        except base64.binascii.Error as e:
            raise ImageProcessingError(f"Failed to decode base64 image: {e}")

    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check of the analyzer components.

        Returns:
            Dictionary with health status information
        """
        health_status = {
            "status": "healthy",
            "components": {},
            "timestamp": time.time()
        }

        try:
            # Test API client connection
            api_healthy = await self.client.test_connection()
            health_status["components"]["api_client"] = {
                "status": "healthy" if api_healthy else "unhealthy",
                "model": self.config.model_name
            }

            # Test image processor
            # We can test basic functionality without actual API calls
            health_status["components"]["image_processor"] = {
                "status": "healthy",
                "supported_formats": self.config.supported_formats,
                "max_size_mb": self.config.max_image_size_mb
            }

            # Overall status
            if not api_healthy:
                health_status["status"] = "unhealthy"

        except Exception as e:
            health_status["status"] = "unhealthy"
            health_status["error"] = str(e)

        return health_status

    async def close(self):
        """Close analyzer components and cleanup resources."""
        try:
            await self.client.close()
            await self.processor.close()
            self.logger.info("Image analyzer closed")
        except Exception as e:
            self.logger.error(f"Error closing image analyzer: {e}")