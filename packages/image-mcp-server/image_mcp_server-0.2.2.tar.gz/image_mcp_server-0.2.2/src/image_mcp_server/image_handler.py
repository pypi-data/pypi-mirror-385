"""
图片处理器

负责处理各种图片输入格式，统一转换为 base64 编码。
支持本地文件、HTTP URL 和剪贴板图片。
"""

import base64
import os
import io
from pathlib import Path
from typing import Optional, Tuple
import urllib.parse
import tempfile

try:
    from PIL import Image
    from PIL import UnidentifiedImageError
except ImportError:
    raise ImportError("PIL (Pillow) is required. Install with: pip install Pillow>=9.0.0")

try:
    import pyperclip
except ImportError:
    pyperclip = None


class ImageHandler:
    """图片处理器，负责读取和编码图片数据"""

    # 支持的图片格式
    SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.tiff'}

    def __init__(self):
        """初始化图片处理器"""
        self._check_dependencies()

    def _check_dependencies(self) -> None:
        """检查依赖项"""
        try:
            import PIL
        except ImportError:
            raise ImportError("PIL (Pillow) is required. Install with: pip install Pillow>=9.0.0")

    def _is_url(self, input_str: str) -> bool:
        """
        检查输入是否为 HTTP/HTTPS URL

        Args:
            input_str: 输入字符串

        Returns:
            bool: 是否为 URL
        """
        try:
            result = urllib.parse.urlparse(input_str)
            return result.scheme in ('http', 'https') and result.netloc != ''
        except:
            return False

    def _process_url_image(self, url: str) -> Tuple[str, str]:
        """
        处理 HTTP URL 图片

        Args:
            url: 图片 URL

        Returns:
            Tuple[str, str]: (base64编码的图片数据, MIME类型)

        Raises:
            Exception: URL 访问失败或图片处理失败
        """
        try:
            import requests  # 用于下载图片
        except ImportError:
            raise ImportError("requests is required for URL image processing. Install with: pip install requests")

        try:
            # 下载图片
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }

            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()

            # 获取 MIME 类型
            content_type = response.headers.get('content-type', 'image/jpeg')
            if not content_type.startswith('image/'):
                raise ValueError(f"URL 不是图片地址: {url}")

            # 使用 PIL 处理图片
            img = Image.open(io.BytesIO(response.content))

            # 转换为 RGB 格式（处理 RGBA 等格式）
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            elif img.mode not in ('RGB', 'L'):
                img = img.convert('RGB')

            # 保存到字节流
            buffer = io.BytesIO()
            img.save(buffer, format='JPEG', quality=95)
            buffer.seek(0)

            # 编码为 base64
            base64_data = base64.b64encode(buffer.getvalue()).decode('utf-8')

            return base64_data, content_type

        except Exception as e:
            raise Exception(f"处理 URL 图片时出错: {str(e)}")

    def process_image_input(self, image_input: str) -> Tuple[str, str]:
        """
        处理图片输入，返回 base64 编码和 MIME 类型

        Args:
            image_input: 图片输入，可以是文件路径、HTTP URL 或 'clipboard'

        Returns:
            Tuple[str, str]: (base64编码的图片数据, MIME类型)

        Raises:
            ValueError: 输入格式无效
            FileNotFoundError: 文件不存在
            Exception: 处理过程中的其他错误
        """
        if image_input.lower() == "clipboard":
            return self._process_clipboard_image()
        elif self._is_url(image_input):
            return self._process_url_image(image_input)
        else:
            return self._process_file_image(image_input)

    def _process_file_image(self, file_path: str) -> Tuple[str, str]:
        """
        处理本地图片文件

        Args:
            file_path: 图片文件路径

        Returns:
            Tuple[str, str]: (base64编码的图片数据, MIME类型)
        """
        # 转换为绝对路径
        path = Path(file_path).expanduser().resolve()

        # 检查文件是否存在
        if not path.exists():
            raise FileNotFoundError(f"图片文件不存在: {file_path}")

        # 检查文件格式
        if path.suffix.lower() not in self.SUPPORTED_FORMATS:
            raise ValueError(
                f"不支持的图片格式: {path.suffix}. "
                f"支持的格式: {', '.join(sorted(self.SUPPORTED_FORMATS))}"
            )

        try:
            # 读取图片
            with Image.open(path) as img:
                # 转换为 RGB 格式（处理 RGBA 等格式）
                if img.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                elif img.mode not in ('RGB', 'L'):
                    img = img.convert('RGB')

                # 保存到字节流
                buffer = io.BytesIO()
                img.save(buffer, format='JPEG', quality=95)
                buffer.seek(0)

                # 编码为 base64
                base64_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
                mime_type = self._get_mime_type(path.suffix)

                return base64_data, mime_type

        except UnidentifiedImageError:
            raise ValueError(f"无法识别的图片文件: {file_path}")
        except Exception as e:
            raise Exception(f"处理图片文件时出错: {str(e)}")

    def _process_clipboard_image(self) -> Tuple[str, str]:
        """
        处理剪贴板图片

        Returns:
            Tuple[str, str]: (base64编码的图片数据, MIME类型)

        Raises:
            RuntimeError: 剪贴板访问失败或没有图片
            ImportError: 缺少 pyperclip 依赖
        """
        if pyperclip is None:
            raise ImportError(
                "pyperclip is required for clipboard support. "
                "Install with: pip install pyperclip"
            )

        try:
            # 尝试获取剪贴板图片
            image = pyperclip.paste_image()
            if image is None:
                # 检查剪贴板中是否有其他数据
                try:
                    clipboard_data = pyperclip.paste()
                    if clipboard_data:
                        raise RuntimeError("剪贴板中有文本数据，但没有图片。请复制图片到剪贴板。")
                    else:
                        raise RuntimeError("剪贴板为空。请复制图片到剪贴板。")
                except:
                    raise RuntimeError("剪贴板为空或无法访问。请复制图片到剪贴板。")

            # 转换为 RGB 格式
            if image.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background
            elif image.mode not in ('RGB', 'L'):
                image = image.convert('RGB')

            # 保存到字节流
            buffer = io.BytesIO()
            image.save(buffer, format='JPEG', quality=95)
            buffer.seek(0)

            # 编码为 base64
            base64_data = base64.b64encode(buffer.getvalue()).decode('utf-8')

            return base64_data, "image/jpeg"

        except Exception as e:
            if isinstance(e, (RuntimeError, ImportError)):
                raise
            raise RuntimeError(f"处理剪贴板图片时出错: {str(e)}")

    def _get_mime_type(self, file_extension: str) -> str:
        """
        根据文件扩展名获取 MIME 类型

        Args:
            file_extension: 文件扩展名（包含点号）

        Returns:
            str: MIME 类型
        """
        extension = file_extension.lower()
        mime_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp',
            '.bmp': 'image/bmp',
            '.tiff': 'image/tiff',
        }
        return mime_types.get(extension, 'image/jpeg')

    def validate_image_input(self, image_input: str) -> bool:
        """
        验证图片输入是否有效

        Args:
            image_input: 图片输入

        Returns:
            bool: 是否有效
        """
        if image_input.lower() == "clipboard":
            return True

        # 检查是否为 URL
        if self._is_url(image_input):
            return True

        # 检查是否为本地文件
        try:
            path = Path(image_input)
            return (path.exists() and
                   path.suffix.lower() in self.SUPPORTED_FORMATS)
        except:
            return False


# 创建全局实例
image_handler = ImageHandler()