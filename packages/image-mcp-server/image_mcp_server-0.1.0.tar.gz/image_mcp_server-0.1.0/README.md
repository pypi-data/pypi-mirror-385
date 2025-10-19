# Image MCP Server

A Model Context Protocol (MCP) server for image understanding using Alibaba Cloud's Qwen3-VL-Plus model.

## Quick Start

### Installation

```bash
uvx image-mcp-server
```

### Configuration

Set your DashScope API key:

```bash
export IMAGE_MCP_DASHSCOPE_API_KEY="your-api-key-here"
```

### Usage

The server provides an `analyze_image` tool that can analyze images from URLs or base64 data.

## Development

```bash
# Install in development mode
uv pip install -e .

# Run tests
pytest

# Lint code
ruff check .

# Format code
black .
isort .
```

## License

MIT