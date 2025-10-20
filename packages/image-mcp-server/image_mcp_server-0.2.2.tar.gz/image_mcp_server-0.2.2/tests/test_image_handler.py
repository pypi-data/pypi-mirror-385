"""测试图片处理器"""

import pytest
import base64
import io
from pathlib import Path
from PIL import Image
import sys
import os

# 添加 src 目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from image_mcp_server.image_handler import ImageHandler


class TestImageHandler:
    """图片处理器测试类"""

    def setup_method(self):
        """每个测试方法前的设置"""
        self.handler = ImageHandler()
        self.test_dir = Path(__file__).parent / "test_images"
        self.test_dir.mkdir(exist_ok=True)

        # 创建测试图片
        self.create_test_images()

    def create_test_images(self):
        """创建测试图片"""
        # 创建一个简单的测试图片
        img = Image.new('RGB', (100, 100), color='red')
        test_file = self.test_dir / "test.jpg"
        img.save(test_file, 'JPEG')

        # 创建 PNG 测试图片
        img_png = Image.new('RGBA', (50, 50), color=(255, 0, 0, 128))
        test_file_png = self.test_dir / "test.png"
        img_png.save(test_file_png, 'PNG')

    def teardown_method(self):
        """每个测试方法后的清理"""
        # 清理测试图片
        for file in self.test_dir.glob("*"):
            if file.is_file():
                file.unlink()

    def test_validate_image_input_file(self):
        """测试文件路径验证"""
        # 测试存在的文件
        valid_file = str(self.test_dir / "test.jpg")
        assert self.handler.validate_image_input(valid_file) is True

        # 测试不存在的文件
        invalid_file = str(self.test_dir / "not_exist.jpg")
        assert self.handler.validate_image_input(invalid_file) is False

        # 测试不支持的格式
        unsupported_file = str(self.test_dir / "test.txt")
        Path(unsupported_file).touch()
        assert self.handler.validate_image_input(unsupported_file) is False

    def test_validate_image_input_clipboard(self):
        """测试剪贴板输入验证"""
        assert self.handler.validate_image_input("clipboard") is True
        assert self.handler.validate_image_input("CLIPBOARD") is True
        assert self.handler.validate_image_input("Clipboard") is True

    def test_process_file_image(self):
        """测试处理文件图片"""
        test_file = str(self.test_dir / "test.jpg")

        base64_data, mime_type = self.handler.process_image_input(test_file)

        # 验证返回的数据
        assert isinstance(base64_data, str)
        assert len(base64_data) > 0
        assert mime_type == "image/jpeg"

        # 验证 base64 数据可以正确解码
        decoded_data = base64.b64decode(base64_data)
        assert len(decoded_data) > 0

    def test_process_png_image(self):
        """测试处理 PNG 图片"""
        test_file = str(self.test_dir / "test.png")

        base64_data, mime_type = self.handler.process_image_input(test_file)

        # 验证返回的数据
        assert isinstance(base64_data, str)
        assert len(base64_data) > 0
        assert mime_type == "image/png"

    def test_process_nonexistent_file(self):
        """测试处理不存在的文件"""
        with pytest.raises(FileNotFoundError):
            self.handler.process_image_input("/nonexistent/path/image.jpg")

    def test_process_unsupported_format(self):
        """测试处理不支持的格式"""
        # 创建一个不支持的文件
        unsupported_file = self.test_dir / "test.txt"
        unsupported_file.write_text("This is not an image")

        with pytest.raises(ValueError, match="不支持的图片格式"):
            self.handler.process_image_input(str(unsupported_file))

    def test_get_mime_type(self):
        """测试获取 MIME 类型"""
        assert self.handler._get_mime_type(".jpg") == "image/jpeg"
        assert self.handler._get_mime_type(".jpeg") == "image/jpeg"
        assert self.handler._get_mime_type(".png") == "image/png"
        assert self.handler._get_mime_type(".gif") == "image/gif"
        assert self.handler._get_mime_type(".webp") == "image/webp"
        assert self.handler._get_mime_type(".unknown") == "image/jpeg"  # 默认值

    def test_supported_formats(self):
        """测试支持的格式"""
        expected_formats = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.tiff'}
        assert self.handler.SUPPORTED_FORMATS == expected_formats

    def test_process_invalid_image(self):
        """测试处理无效图片文件"""
        # 创建一个假的图片文件（实际上是文本文件）
        fake_image = self.test_dir / "fake.jpg"
        fake_image.write_text("This is not a real image")

        with pytest.raises(ValueError, match="无法识别的图片文件"):
            self.handler.process_image_input(str(fake_image))