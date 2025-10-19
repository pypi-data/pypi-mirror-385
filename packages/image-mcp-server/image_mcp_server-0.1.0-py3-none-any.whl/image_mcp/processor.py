"""
Image processing utilities for Image MCP Server.

Handles image download, validation, format detection, and processing
with support for various image formats and sources.
"""

import base64
import io
import re
from typing import Tuple, Optional, Dict, Any
from pathlib import Path
from urllib.parse import urlparse

import httpx
from PIL import Image, UnidentifiedImageError

from image_mcp.config import APIConfiguration
from image_mcp.exceptions import (
    ImageProcessingError,
    ValidationError,
    NetworkError,
    UnsupportedFormatError,
    ImageTooLargeError,
    URLNotAccessibleError,
    InvalidBase64Error,
    EmptyImageError
)
from image_mcp.logging import get_logger


class ImageProcessor:
    """
    Utility class for processing images from various sources.

    Handles base64 decoding, URL downloads, format validation,
    size limits, and image format conversion.
    """

    def __init__(self, config: APIConfiguration):
        """
        Initialize the image processor.

        Args:
            config: Configuration settings
        """
        self.config = config
        self.logger = get_logger("processor")

        # Initialize HTTP client for downloads
        self._http_client = httpx.AsyncClient(
            timeout=httpx.Timeout(config.request_timeout),
            follow_redirects=True,
            headers={
                "User-Agent": "Image-MCP-Server/1.0"
            }
        )

        self.logger.info(
            "Image processor initialized",
            extra={
                "max_size_mb": config.max_image_size_mb,
                "supported_formats": config.supported_formats,
                "timeout": config.request_timeout
            }
        )

    async def process_image_from_base64(
        self,
        base64_data: str,
        max_size_mb: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Process image from base64 data.

        Args:
            base64_data: Base64 encoded image data
            max_size_mb: Maximum allowed size in MB (overrides config)

        Returns:
            Dictionary with processed image information

        Raises:
            ValidationError: If base64 data is invalid
            ImageProcessingError: If processing fails
        """
        max_size = (max_size_mb or self.config.max_image_size_mb) * 1024 * 1024

        try:
            self.logger.debug("Processing base64 image", extra={"data_length": len(base64_data)})

            # Validate and decode base64
            image_bytes = self._decode_base64_image(base64_data)

            # Validate image size
            self._validate_image_size(image_bytes, max_size)

            # Detect image format
            image_format = self._detect_image_format_from_bytes(image_bytes)

            # Validate image content
            image_info = self._validate_image_content(image_bytes)

            result = {
                "data": image_bytes,
                "format": image_format,
                "size_bytes": len(image_bytes),
                "dimensions": image_info["dimensions"],
                "mode": image_info["mode"],
                "has_transparency": image_info["has_transparency"]
            }

            self.logger.info(
                "Base64 image processed successfully",
                extra={
                    "format": image_format,
                    "size_bytes": len(image_bytes),
                    "dimensions": f"{image_info['dimensions'][0]}x{image_info['dimensions'][1]}"
                }
            )

            return result

        except (ValidationError, ImageProcessingError):
            raise
        except Exception as e:
            raise ImageProcessingError(f"Failed to process base64 image: {e}")

    async def process_image_from_url(
        self,
        image_url: str,
        max_size_mb: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Process image from URL.

        Args:
            image_url: URL of the image to process
            max_size_mb: Maximum allowed size in MB (overrides config)

        Returns:
            Dictionary with processed image information

        Raises:
            ValidationError: If URL is invalid
            NetworkError: If download fails
            ImageProcessingError: If processing fails
        """
        max_size = (max_size_mb or self.config.max_image_size_mb) * 1024 * 1024

        try:
            self.logger.info("Processing image from URL", extra={"url": image_url})

            # Validate URL
            self._validate_image_url(image_url)

            # Download image
            image_bytes = await self._download_image(image_url)

            # Validate image size
            self._validate_image_size(image_bytes, max_size)

            # Detect image format
            image_format = self._detect_image_format_from_bytes(image_bytes)

            # Validate image content
            image_info = self._validate_image_content(image_bytes)

            result = {
                "data": image_bytes,
                "format": image_format,
                "size_bytes": len(image_bytes),
                "dimensions": image_info["dimensions"],
                "mode": image_info["mode"],
                "has_transparency": image_info["has_transparency"],
                "source_url": image_url
            }

            self.logger.info(
                "URL image processed successfully",
                extra={
                    "url": image_url,
                    "format": image_format,
                    "size_bytes": len(image_bytes),
                    "dimensions": f"{image_info['dimensions'][0]}x{image_info['dimensions'][1]}"
                }
            )

            return result

        except (ValidationError, NetworkError, ImageProcessingError):
            raise
        except Exception as e:
            raise ImageProcessingError(f"Failed to process image from URL {image_url}: {e}")

    def _decode_base64_image(self, base64_data: str) -> bytes:
        """
        Decode base64 image data.

        Args:
            base64_data: Base64 encoded image data

        Returns:
            Decoded image bytes

        Raises:
            InvalidBase64Error: If base64 data is invalid
            EmptyImageError: If image data is empty
        """
        if not base64_data or not base64_data.strip():
            raise EmptyImageError()

        try:
            # Remove any whitespace or newlines
            clean_data = re.sub(r'\s+', '', base64_data)
            image_bytes = base64.b64decode(clean_data)

            if len(image_bytes) == 0:
                raise EmptyImageError()

            return image_bytes

        except base64.binascii.Error as e:
            raise InvalidBase64Error(f"Failed to decode base64 data: {e}")

    async def _download_image(self, image_url: str) -> bytes:
        """
        Download image from URL.

        Args:
            image_url: URL to download from

        Returns:
            Downloaded image bytes

        Raises:
            NetworkError: If download fails
        """
        try:
            response = await self._http_client.get(image_url)
            response.raise_for_status()

            content_type = response.headers.get('content-type', '').lower()
            if not content_type.startswith('image/'):
                raise NetworkError(
                    f"URL does not point to an image (content-type: {content_type})",
                    url=image_url
                )

            return response.content

        except httpx.HTTPStatusError as e:
            raise URLNotAccessibleError(
                f"HTTP error {e.response.status_code}: {e.response.reason_phrase}",
                url=image_url,
                status_code=e.response.status_code
            )
        except httpx.RequestError as e:
            raise NetworkError(f"Failed to download image: {e}", url=image_url)

    def _validate_image_size(self, image_bytes: bytes, max_size_bytes: int) -> None:
        """
        Validate image size against limits.

        Args:
            image_bytes: Image data to validate
            max_size_bytes: Maximum allowed size in bytes

        Raises:
            ImageTooLargeError: If image is too large
            EmptyImageError: If image is empty
        """
        if len(image_bytes) == 0:
            raise EmptyImageError()

        if len(image_bytes) > max_size_bytes:
            raise ImageTooLargeError(
                size_bytes=len(image_bytes),
                max_size_bytes=max_size_bytes
            )

    def _detect_image_format_from_bytes(self, image_bytes: bytes) -> str:
        """
        Detect image format from byte data.

        Args:
            image_bytes: Image byte data

        Returns:
            Detected image format

        Raises:
            UnsupportedFormatError: If format is not supported
        """
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
            raise UnsupportedFormatError(
                "unknown",
                self.config.supported_formats
            )

    def _validate_image_content(self, image_bytes: bytes) -> Dict[str, Any]:
        """
        Validate image content and extract metadata.

        Args:
            image_bytes: Image byte data

        Returns:
            Dictionary with image metadata

        Raises:
            ImageProcessingError: If image content is invalid
        """
        try:
            with Image.open(io.BytesIO(image_bytes)) as img:
                # Get image dimensions
                width, height = img.size

                # Check if image has transparency
                has_transparency = (
                    img.mode in ('RGBA', 'LA') or
                    (img.mode == 'P' and 'transparency' in img.info)
                )

                # Verify image can be loaded
                img.verify()

                # Reopen for further processing (verify() closes the image)
                with Image.open(io.BytesIO(image_bytes)) as img:
                    # Convert to RGB if needed for consistency
                    if img.mode not in ('RGB', 'RGBA'):
                        img = img.convert('RGB')

                return {
                    "dimensions": (width, height),
                    "mode": img.mode,
                    "has_transparency": has_transparency
                }

        except UnidentifiedImageError as e:
            raise ImageProcessingError(f"Cannot identify image format: {e}")
        except Exception as e:
            raise ImageProcessingError(f"Invalid image content: {e}")

    def _validate_image_url(self, image_url: str) -> None:
        """
        Validate image URL format and accessibility.

        Args:
            image_url: URL to validate

        Raises:
            ValidationError: If URL format is invalid
        """
        try:
            parsed = urlparse(image_url)

            if not parsed.scheme or not parsed.netloc:
                raise ValidationError("Invalid URL format")

            if parsed.scheme not in ('http', 'https'):
                raise ValidationError("URL must use HTTP or HTTPS protocol")

            # Check file extension
            path = parsed.path.lower()
            valid_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}

            if not any(path.endswith(ext) for ext in valid_extensions):
                raise ValidationError(
                    f"URL must end with valid image extension: {valid_extensions}"
                )

        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(f"Invalid URL: {e}")

    def convert_to_rgb(self, image_bytes: bytes, image_format: str) -> bytes:
        """
        Convert image to RGB format if needed.

        Args:
            image_bytes: Original image bytes
            image_format: Current image format

        Returns:
            RGB image bytes as JPEG

        Raises:
            ImageProcessingError: If conversion fails
        """
        try:
            with Image.open(io.BytesIO(image_bytes)) as img:
                # Convert to RGB
                if img.mode != 'RGB':
                    img = img.convert('RGB')

                # Save as JPEG
                output = io.BytesIO()
                img.save(output, format='JPEG', quality=90)
                return output.getvalue()

        except Exception as e:
            raise ImageProcessingError(f"Failed to convert image to RGB: {e}")

    def resize_if_needed(
        self,
        image_bytes: bytes,
        max_width: Optional[int] = None,
        max_height: Optional[int] = None
    ) -> bytes:
        """
        Resize image if it exceeds specified dimensions.

        Args:
            image_bytes: Original image bytes
            max_width: Maximum width (optional)
            max_height: Maximum height (optional)

        Returns:
            Resized image bytes or original if no resize needed

        Raises:
            ImageProcessingError: If resize fails
        """
        if not max_width and not max_height:
            return image_bytes

        try:
            with Image.open(io.BytesIO(image_bytes)) as img:
                width, height = img.size

                # Check if resize is needed
                if (max_width and width > max_width) or (max_height and height > max_height):
                    # Calculate new dimensions
                    if max_width and max_height:
                        # Maintain aspect ratio
                        ratio = min(max_width / width, max_height / height)
                        new_width = int(width * ratio)
                        new_height = int(height * ratio)
                    elif max_width:
                        ratio = max_width / width
                        new_width = max_width
                        new_height = int(height * ratio)
                    else:  # max_height only
                        ratio = max_height / height
                        new_width = int(width * ratio)
                        new_height = max_height

                    # Resize image
                    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

                    # Save resized image
                    output = io.BytesIO()
                    img.save(output, format=img.format or 'JPEG', quality=90)
                    return output.getvalue()

                return image_bytes

        except Exception as e:
            raise ImageProcessingError(f"Failed to resize image: {e}")

    async def close(self):
        """Close the HTTP client and cleanup resources."""
        await self._http_client.aclose()
        self.logger.info("Image processor closed")