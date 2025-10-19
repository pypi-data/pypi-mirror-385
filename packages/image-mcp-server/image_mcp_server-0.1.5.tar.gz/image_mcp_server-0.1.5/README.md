# Image MCP Server

A Model Context Protocol (MCP) server for image understanding using Alibaba Cloud's Qwen3-VL-Plus model.

[![PyPI version](https://badge.fury.io/py/image-mcp-server.svg)](https://badge.fury.io/py/image-mcp-server)
![Python versions](https://img.shields.io/pypi/pyversions/image-mcp-server.svg)
![License](https://img.shields.io/pypi/l/image-mcp-server.svg)

## 🚀 Quick Start

### Installation

#### Option 1: Using uvx (Recommended)
```bash
uvx image-mcp-server
```

#### Option 2: Using pip
```bash
pip install image-mcp-server
```

#### Option 3: Using uv
```bash
uv pip install image-mcp-server
```

## 🔧 MCP Configuration

### Claude Desktop Configuration

1. **Locate your Claude Desktop config file**:
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
   - **Linux**: `~/.config/claude/claude_desktop_config.json`

2. **Add the MCP server configuration**:

```json
{
  "mcpServers": {
    "image-mcp-server": {
      "command": "uvx",
      "args": ["image-mcp-server@latest"],
      "env": {
        "IMAGE_MCP_DASHSCOPE_API_KEY": "your-dashscope-api-key-here"
      }
    }
  }
}
```

**Configuration Notes:**
- Replace `your-dashscope-api-key-here` with your actual DashScope API key
- Using `@latest` ensures you always get the newest version
- The server will automatically download and run when first used by Claude

3. **Restart Claude Desktop** to load the new configuration.

### API Key Setup

1. Visit [Alibaba Cloud DashScope Console](https://dashscope.console.aliyun.com/)
2. Sign up or log in to your account
3. Navigate to **API Keys** section
4. Create a new API key
5. Copy the key for use in your MCP configuration

## 🎯 Usage Examples

Once configured, you can use the image analysis capabilities directly in Claude:

### Basic Image Analysis
```
Please analyze this image: [upload image]
```

### Detailed Analysis Request
```
Describe this image in detail, including the main objects, colors, and overall scene. Also provide confidence scores for your observations.
```

### Technical Analysis
```
What type of objects are visible in this image? Please provide a list with confidence scores.
```

### URL-based Analysis
```
Please analyze the image at this URL: https://example.com/image.jpg
```

## 📋 Features

- **Multi-format Support**: JPEG, PNG, GIF, WebP
- **Dual Input Methods**: Direct upload or URL-based analysis
- **Confidence Scoring**: Provides confidence levels and scores for detected objects
- **Structured Output**: JSON-formatted analysis results
- **Environment Configuration**: Secure API key management
- **Automatic Updates**: Using `@latest` ensures latest features

## 🔧 Configuration Options

The server supports various configuration options via environment variables:

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `IMAGE_MCP_DASHSCOPE_API_KEY` | Required | Your DashScope API key |
| `IMAGE_MCP_DASHSCOPE_BASE_URL` | `https://dashscope.aliyuncs.com/compatible-mode/v1` | API endpoint URL |
| `IMAGE_MCP_MODEL_NAME` | `qwen3-vl-plus` | Model to use for analysis |
| `IMAGE_MCP_MAX_IMAGE_SIZE_MB` | `10` | Maximum image size in MB |
| `IMAGE_MCP_REQUEST_TIMEOUT` | `30` | Request timeout in seconds |
| `IMAGE_MCP_MAX_RETRIES` | `3` | Maximum retry attempts |
| `IMAGE_MCP_LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) |
| `IMAGE_MCP_ENABLE_DEBUG` | `false` | Enable debug logging |

## 🛠️ Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/your-repo/image-mcp-server.git
cd image-mcp-server

# Install in development mode
uv pip install -e .

# Run tests
pytest

# Run tests with coverage
pytest --cov=image_mcp

# Lint code
ruff check .

# Format code
black .
isort .
```

### Build Package

```bash
# Build for distribution
python -m build

# Upload to PyPI (requires credentials)
twine upload dist/*
```

## 📚 API Documentation

### MCP Tools

The server provides the following MCP tools:

#### `analyze_image`
Analyzes an image and returns detailed information about its contents.

**Parameters:**
- `image_data` (optional): Base64-encoded image data
- `image_url` (optional): URL to an image file
- `prompt` (optional): Custom prompt for analysis

**Example:**
```json
{
  "image_url": "https://example.com/image.jpg",
  "prompt": "Describe what you see in this image"
}
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [Full Documentation](https://github.com/your-repo/image-mcp-server/docs)
- **Issues**: [GitHub Issues](https://github.com/your-repo/image-mcp-server/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-repo/image-mcp-server/discussions)

## 🔗 Related Links

- [Alibaba Cloud DashScope](https://dashscope.console.aliyun.com/)
- [Qwen3-VL-Plus Documentation](https://help.aliyun.com/zh/dashscope/developer-reference/qwen-vl-plus)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Claude Desktop](https://claude.ai/download)

---

**Happy image analyzing! 🚀**