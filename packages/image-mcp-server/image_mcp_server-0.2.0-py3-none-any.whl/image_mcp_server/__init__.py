"""
Image MCP Server

一个简洁的 MCP 服务器，用于图片内容分析，支持本地文件和剪贴板图片。
基于阿里云通义千问3-VL-Plus模型。
"""

__version__ = "0.2.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .server import main

__all__ = ["main", "__version__"]