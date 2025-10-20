"""
MCP 服务器主逻辑

实现 MCP 协议的服务器，提供图片分析工具。
"""

import asyncio
import sys
import json
import logging
from typing import Any, Dict, List, Optional

try:
    from mcp.server import Server
    from mcp.server.models import InitializationOptions
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent, ImageContent
except ImportError:
    raise ImportError("MCP is required. Install with: pip install mcp>=1.0.0")

from .image_handler import image_handler
from .api_client import get_client, DashScopeClient

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("image-mcp-server")


class ImageMCPServer:
    """Image MCP 服务器类"""

    def __init__(self):
        """初始化 MCP 服务器"""
        self.server = Server("image-mcp-server")
        self._setup_handlers()
        self._client: Optional[DashScopeClient] = None

    def _setup_handlers(self):
        """设置 MCP 处理器"""

        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            """列出可用工具"""
            return [
                Tool(
                    name="analyze_image",
                    description="分析图片内容，支持本地文件和剪贴板图片。基于通义千问3-VL-Plus模型进行视觉理解。",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "image": {
                                "type": "string",
                                "description": "图片来源：本地文件路径（如./image.jpg）或'clipboard'表示剪贴板图片"
                            },
                            "question": {
                                "type": "string",
                                "description": "关于图片的问题（可选）",
                                "default": "请分析这张图片的内容"
                            }
                        },
                        "required": ["image"]
                    }
                )
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """调用工具"""
            if name == "analyze_image":
                return await self._handle_analyze_image(arguments)
            else:
                raise ValueError(f"未知工具: {name}")

        @self.server.list_prompts()
        async def list_prompts():
            """列出可用提示（空列表，因为只有工具）"""
            return []

        @self.server.get_prompt()
        async def get_prompt(name: str, arguments: Optional[Dict[str, str]] = None):
            """获取提示（不支持）"""
            raise ValueError("不支持提示功能")

    async def _handle_analyze_image(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """
        处理图片分析请求

        Args:
            arguments: 工具参数

        Returns:
            List[TextContent]: 分析结果
        """
        try:
            # 解析参数
            image_input = arguments.get("image", "")
            question = arguments.get("question", "请分析这张图片的内容")

            if not image_input:
                return [TextContent(
                    type="text",
                    text="错误: 缺少图片参数。请提供图片文件路径或使用 'clipboard' 来分析剪贴板图片。"
                )]

            logger.info(f"开始分析图片: {image_input}")

            # 处理图片
            try:
                base64_data, mime_type = image_handler.process_image_input(image_input)
                logger.info(f"图片处理成功，格式: {mime_type}")
            except Exception as e:
                error_msg = f"图片处理失败: {str(e)}"
                logger.error(error_msg)
                return [TextContent(type="text", text=error_msg)]

            # 调用 API 分析图片
            try:
                client = get_client()
                result = await client.analyze_image(base64_data, mime_type, question)

                if result.get("success", False):
                    analysis = result.get("analysis", "分析完成但没有返回内容")
                    logger.info("图片分析成功")
                    return [TextContent(type="text", text=analysis)]
                else:
                    error_msg = result.get("error", "图片分析失败")
                    logger.error(f"API分析失败: {error_msg}")
                    return [TextContent(type="text", text=f"分析失败: {error_msg}")]

            except Exception as e:
                error_msg = f"API调用失败: {str(e)}"
                logger.error(error_msg)
                return [TextContent(type="text", text=error_msg)]

        except Exception as e:
            error_msg = f"处理请求时发生错误: {str(e)}"
            logger.error(error_msg)
            return [TextContent(type="text", text=error_msg)]

    async def run(self):
        """运行 MCP 服务器"""
        # 验证 API 连接
        try:
            client = get_client()
            test_result = await client.test_connection()
            if not test_result.get("success", False):
                logger.warning(f"API连接测试失败: {test_result.get('message')}")
            else:
                logger.info("API连接测试成功")
        except Exception as e:
            logger.error(f"API连接测试异常: {str(e)}")

        # 启动服务器
        logger.info("Image MCP Server 启动...")
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="image-mcp-server",
                    server_version="0.2.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=None,
                        experimental_capabilities=None
                    )
                )
            )


# 全局服务器实例
_server_instance: Optional[ImageMCPServer] = None


def get_server() -> ImageMCPServer:
    """获取服务器实例"""
    global _server_instance
    if _server_instance is None:
        _server_instance = ImageMCPServer()
    return _server_instance


async def main():
    """主函数"""
    try:
        server = get_server()
        await server.run()
    except KeyboardInterrupt:
        logger.info("收到中断信号，正在关闭服务器...")
    except Exception as e:
        logger.error(f"服务器运行错误: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())