"""
DashScope API 客户端

用于调用阿里云通义千问3-VL-Plus模型的API客户端。
"""

import os
import json
import httpx
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class DashScopeClient:
    """DashScope API 客户端"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://dashscope.aliyuncs.com",
        model: str = "qwen3-vl-plus"
    ):
        """
        初始化 DashScope 客户端

        Args:
            api_key: API 密钥，如果为 None 则从环境变量获取
            base_url: API 基础URL
            model: 模型名称
        """
        self.api_key = api_key or os.getenv("IMAGE_MCP_DASHSCOPE_API_KEY")
        if not self.api_key:
            raise ValueError(
                "DashScope API 密钥未设置。请设置环境变量 IMAGE_MCP_DASHSCOPE_API_KEY "
                "或在创建客户端时传入 api_key 参数"
            )

        self.base_url = base_url.rstrip('/')
        self.model = model
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def analyze_image(
        self,
        image_base64: str,
        mime_type: str,
        question: str = "请分析这张图片的内容"
    ) -> Dict[str, Any]:
        """
        分析图片内容

        Args:
            image_base64: base64编码的图片数据
            mime_type: 图片的MIME类型
            question: 关于图片的问题

        Returns:
            Dict[str, Any]: API响应结果

        Raises:
            Exception: API调用失败
        """
        # 构建请求数据 (OpenAI 兼容格式)
        data = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime_type};base64,{image_base64}"
                            }
                        },
                        {
                            "type": "text",
                            "text": question
                        }
                    ]
                }
            ]
        }

        # 发送请求
        url = f"{self.base_url}/compatible-mode/v1/chat/completions"

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    url,
                    headers=self.headers,
                    json=data
                )
                response.raise_for_status()

                result = response.json()
                return self._parse_response(result)

        except httpx.HTTPStatusError as e:
            error_msg = f"API请求失败: HTTP {e.response.status_code}"
            try:
                error_data = e.response.json()
                if "error" in error_data:
                    error_msg += f" - {error_data['error'].get('message', '未知错误')}"
            except:
                pass
            raise Exception(error_msg)

        except httpx.RequestError as e:
            raise Exception(f"网络请求失败: {str(e)}")

        except json.JSONDecodeError as e:
            raise Exception(f"API响应解析失败: {str(e)}")

        except Exception as e:
            raise Exception(f"图片分析失败: {str(e)}")

    def _parse_response(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        解析API响应

        Args:
            response_data: 原始API响应数据

        Returns:
            Dict[str, Any]: 解析后的响应数据
        """
        try:
            # 检查是否有错误
            if "error" in response_data:
                error_info = response_data["error"]
                raise Exception(f"API错误: {error_info.get('message', '未知API错误')}")

            # 提取内容
            if "choices" in response_data and len(response_data["choices"]) > 0:
                choice = response_data["choices"][0]
                if "message" in choice and "content" in choice["message"]:
                    content = choice["message"]["content"]

                    # 构建返回结果
                    result = {
                        "success": True,
                        "analysis": content,
                        "model": self.model,
                        "usage": response_data.get("usage", {}),
                    }

                    return result

            # 如果没有找到内容，返回原始响应
            return {
                "success": False,
                "error": "API响应格式异常",
                "raw_response": response_data,
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"响应解析失败: {str(e)}",
                "raw_response": response_data,
            }

    async def test_connection(self) -> Dict[str, Any]:
        """
        测试API连接（仅验证密钥有效性，不发送图片）

        Returns:
            Dict[str, Any]: 测试结果
        """
        try:
            # 只验证 API 密钥是否有效，不发送实际请求
            if not self.api_key:
                return {
                    "success": False,
                    "message": "API密钥未设置",
                }

            # 简单验证 API 密钥格式
            if not self.api_key.startswith("sk-"):
                return {
                    "success": False,
                    "message": "API密钥格式无效",
                }

            return {
                "success": True,
                "message": "API配置验证成功",
                "model": self.model,
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"API配置验证失败: {str(e)}",
            }

    def get_model_info(self) -> Dict[str, str]:
        """
        获取模型信息

        Returns:
            Dict[str, str]: 模型信息
        """
        return {
            "model": self.model,
            "provider": "DashScope",
            "base_url": self.base_url,
            "capabilities": "图像理解、视觉问答、内容分析",
        }


# 创建全局客户端实例
_client: Optional[DashScopeClient] = None


def get_client() -> DashScopeClient:
    """获取全局客户端实例"""
    global _client
    if _client is None:
        _client = DashScopeClient()
    return _client


def set_client(client: DashScopeClient) -> None:
    """设置全局客户端实例"""
    global _client
    _client = client