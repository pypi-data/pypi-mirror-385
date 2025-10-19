"""
Main MCP server implementation for Image MCP Server.

Provides the FastMCP server setup, tool registration, and server lifecycle
management for image understanding functionality.
"""

import asyncio
import signal
import sys
from typing import Optional

import typer
from fastmcp import FastMCP

from image_mcp.config import APIConfiguration
from image_mcp.client import DashScopeClient
from image_mcp.tools import ImageAnalyzer
from image_mcp.logging import setup_logging, get_logger
from image_mcp.exceptions import ConfigurationError, ImageMCPError


class ImageMCPServer:
    """
    Main MCP server for image analysis.

    Manages server lifecycle, tool registration, and provides the main
    entry point for running the image analysis MCP server.
    """

    def __init__(
        self,
        config: Optional[APIConfiguration] = None,
        client: Optional[DashScopeClient] = None
    ):
        """
        Initialize the Image MCP server.

        Args:
            config: Optional configuration (will load from environment if not provided)
            client: Optional pre-configured API client
        """
        # Load configuration
        self.config = config or APIConfiguration()

        # Setup logging
        self.logger = setup_logging(
            level=self.config.log_level,
            enable_debug=self.config.enable_debug_logging,
            use_json=False,  # Use human-readable logs for server
            log_file="image_mcp.log" if self.config.enable_debug_logging else None
        )

        self.logger.info(
            "Initializing Image MCP Server",
            extra={
                "version": "0.1.0",
                "model": self.config.model_name,
                "log_level": self.config.log_level
            }
        )

        # Validate configuration
        self._validate_configuration()

        # Initialize FastMCP server
        self.mcp_server = FastMCP(
            name="image-mcp-server",
            version="0.1.0"
        )

        # Initialize components
        self.client = client or DashScopeClient(self.config)
        self.analyzer = ImageAnalyzer(self.config, self.client)

        # Register tools
        self._register_tools()

        # Setup signal handlers for graceful shutdown
        self._setup_signal_handlers()

        self.logger.info(
            "Image MCP Server initialized successfully",
            extra={
                "supported_formats": self.config.supported_formats,
                "max_image_size_mb": self.config.max_image_size_mb,
                "api_timeout": self.config.request_timeout
            }
        )

    def _validate_configuration(self) -> None:
        """
        Validate server configuration using enhanced validation methods.

        Raises:
            ConfigurationError: If configuration is invalid
        """
        try:
            # Use the comprehensive validation from configuration
            self.config.validate_configuration()

            self.logger.info(
                "Configuration validation completed",
                extra={
                    "region": self.config.get_region_config()["region"],
                    "model": self.config.model_name,
                    "timeout": self.config.request_timeout,
                    "max_retries": self.config.max_retries
                }
            )

        except ConfigurationError:
            raise
        except Exception as e:
            raise ConfigurationError(f"Configuration validation failed: {e}")

    def _register_tools(self) -> None:
        """Register all tools with the MCP server."""
        try:
            self.analyzer.register_tools(self.mcp_server)
            self.logger.info("Tools registered successfully")
        except Exception as e:
            self.logger.error(f"Failed to register tools: {e}")
            raise ConfigurationError(f"Tool registration failed: {e}")

    def _setup_signal_handlers(self) -> None:
        """Setup signal handlers for graceful shutdown."""
        def signal_handler(signum, frame):
            self.logger.info(f"Received signal {signum}, initiating graceful shutdown")
            asyncio.create_task(self.shutdown())

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

    async def start(self, host: str = "localhost", port: int = 8000) -> None:
        """
        Start the MCP server.

        Args:
            host: Server host
            port: Server port
        """
        try:
            self.logger.info(
                "Starting Image MCP Server",
                extra={
                    "host": host,
                    "port": port,
                    "transport": "stdio"  # FastMCP default
                }
            )

            # Test API connection before starting
            api_healthy = await self.client.test_connection()
            if not api_healthy:
                self.logger.warning(
                    "API connection test failed, but starting server anyway"
                )

            # Start the MCP server (stdio transport by default)
            await self.mcp_server.run()

        except Exception as e:
            self.logger.error(f"Failed to start server: {e}")
            raise

    async def shutdown(self) -> None:
        """Gracefully shutdown the server."""
        try:
            self.logger.info("Shutting down Image MCP Server")

            # Close components
            await self.analyzer.close()
            await self.client.close()

            self.logger.info("Server shutdown completed")

        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")

    async def health_check(self) -> dict:
        """
        Perform health check of the server.

        Returns:
            Dictionary with health status information
        """
        try:
            # Check analyzer health
            analyzer_health = await self.analyzer.health_check()

            # Check server configuration
            config_health = {
                "status": "healthy",
                "model": self.config.model_name,
                "max_image_size_mb": self.config.max_image_size_mb,
                "supported_formats": self.config.supported_formats
            }

            return {
                "status": "healthy" if analyzer_health["status"] == "healthy" else "unhealthy",
                "server": {
                    "version": "0.1.0",
                    "status": "healthy"
                },
                "analyzer": analyzer_health,
                "configuration": config_health
            }

        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }


# CLI application
app = typer.Typer(
    name="image-mcp-server",
    help="MCP server for image understanding using Qwen3-VL-Plus model"
)


@app.command()
def main(
    host: str = typer.Option(
        "localhost",
        "--host",
        "-h",
        help="Server host"
    ),
    port: int = typer.Option(
        8000,
        "--port",
        "-p",
        help="Server port"
    ),
    debug: bool = typer.Option(
        False,
        "--debug",
        "-d",
        help="Enable debug logging"
    ),
    log_file: Optional[str] = typer.Option(
        None,
        "--log-file",
        "-l",
        help="Log file path"
    )
) -> None:
    """
    Start the Image MCP server.

    The server provides image analysis capabilities through the Model Context Protocol,
    using Alibaba Cloud's Qwen3-VL-Plus model for understanding images.
    """
    try:
        # Setup logging first
        setup_logging(
            level="DEBUG" if debug else "INFO",
            enable_debug=debug,
            use_json=False,
            log_file=str(log_file) if log_file else None
        )

        logger = get_logger("server")
        logger.info("Starting Image MCP Server")

        # Create and run server
        server = ImageMCPServer()

        # Run the server
        asyncio.run(server.start(host, port))

    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except ConfigurationError as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)


@app.command()
def health(
    format: str = typer.Option(
        "text",
        "--format",
        "-f",
        help="Output format (text or json)"
    )
) -> None:
    """
    Check the health of the Image MCP server and its dependencies.
    """
    async def run_health_check():
        try:
            server = ImageMCPServer()
            health_status = await server.health_check()

            if format == "json":
                import json
                print(json.dumps(health_status, indent=2))
            else:
                print("Image MCP Server Health Status")
                print("=" * 35)
                print(f"Overall Status: {health_status['status'].upper()}")
                print(f"Server Version: 0.1.0")
                print(f"Model: {health_status['configuration']['model']}")
                print(f"Max Image Size: {health_status['configuration']['max_image_size_mb']}MB")
                print(f"Supported Formats: {', '.join(health_status['configuration']['supported_formats'])}")

                if health_status['analyzer']['status'] != 'healthy':
                    print(f"Analyzer Status: {health_status['analyzer']['status']}")
                    if 'error' in health_status['analyzer']:
                        print(f"Analyzer Error: {health_status['analyzer']['error']}")

            await server.shutdown()

        except Exception as e:
            logger = get_logger("server")
            logger.error(f"Health check failed: {e}")
            if format == "json":
                import json
                print(json.dumps({"status": "error", "error": str(e)}, indent=2))
            else:
                print(f"Health check failed: {e}")
            sys.exit(1)

    asyncio.run(run_health_check())


@app.command()
def config() -> None:
    """
    Display current configuration settings.
    """
    try:
        config = APIConfiguration()

        print("Image MCP Server Configuration")
        print("=" * 35)
        print(f"Model: {config.model_name}")
        print(f"API Base URL: {config.dashscope_base_url}")
        print(f"Request Timeout: {config.request_timeout}s")
        print(f"Max Retries: {config.max_retries}")
        print(f"Max Image Size: {config.max_image_size_mb}MB")
        print(f"Supported Formats: {', '.join(config.supported_formats)}")
        print(f"Log Level: {config.log_level}")
        print(f"Debug Logging: {config.enable_debug_logging}")

        region_config = config.get_region_config()
        print(f"Region: {region_config['region']}")
        print(f"Endpoint: {region_config['endpoint_notes']}")

    except ConfigurationError as e:
        print(f"Configuration error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    app()