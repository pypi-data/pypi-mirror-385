"""
Logging infrastructure for Image MCP Server.

Provides structured logging with configurable levels and formats.
"""

import logging
import sys
from typing import Optional
from datetime import datetime
import json


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging."""

    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception information if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        # Add extra fields from record
        for key, value in record.__dict__.items():
            if key not in {
                "name", "msg", "args", "levelname", "levelno", "pathname",
                "filename", "module", "exc_info", "exc_text", "stack_info",
                "lineno", "funcName", "created", "msecs", "relativeCreated",
                "thread", "threadName", "processName", "process", "getMessage"
            }:
                log_entry[key] = value

        return json.dumps(log_entry)


class ColoredFormatter(logging.Formatter):
    """Colored formatter for console output."""

    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }

    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']

        # Format timestamp
        timestamp = datetime.fromtimestamp(record.created).strftime('%H:%M:%S.%f')[:-3]

        # Build log message
        formatted = (
            f"{log_color}[{timestamp}] "
            f"{record.levelname:8} "
            f"{record.name}: "
            f"{record.getMessage()}{reset}"
        )

        # Add exception if present
        if record.exc_info:
            formatted += f"\n{self.formatException(record.exc_info)}"

        return formatted


def setup_logging(
    level: str = "INFO",
    enable_debug: bool = False,
    use_json: bool = False,
    log_file: Optional[str] = None
) -> logging.Logger:
    """
    Set up logging configuration for the application.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        enable_debug: Enable debug mode with more verbose logging
        use_json: Use JSON formatting for logs
        log_file: Optional file to write logs to

    Returns:
        Configured logger instance
    """
    # Convert string level to logging constant
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    # Create root logger
    logger = logging.getLogger("image_mcp")
    logger.setLevel(numeric_level)

    # Clear existing handlers
    logger.handlers.clear()

    # Create formatters
    if use_json:
        formatter = JSONFormatter()
    else:
        console_format = (
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        formatter = logging.Formatter(
            fmt=console_format,
            datefmt="%Y-%m-%d %H:%M:%S"
        )

    # Console handler with colors for interactive use
    console_handler = logging.StreamHandler(sys.stderr)
    if use_json:
        console_handler.setFormatter(JSONFormatter())
    else:
        console_handler.setFormatter(ColoredFormatter())
    console_handler.setLevel(numeric_level)
    logger.addHandler(console_handler)

    # File handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(JSONFormatter() if use_json else formatter)
        file_handler.setLevel(numeric_level)
        logger.addHandler(file_handler)

    # Configure specific loggers
    if enable_debug:
        # Enable debug logging for external libraries
        logging.getLogger("httpx").setLevel(logging.DEBUG)
        logging.getLogger("openai").setLevel(logging.DEBUG)
    else:
        # Reduce noise from external libraries
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.getLogger("openai").setLevel(logging.WARNING)

    # Prevent propagation to avoid duplicate logs
    logger.propagate = False

    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the specified name."""
    return logging.getLogger(f"image_mcp.{name}")


class RequestLogger:
    """Logger for tracking request processing."""

    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.request_id: Optional[str] = None

    def start_request(self, request_id: str, **kwargs):
        """Log the start of request processing."""
        self.request_id = request_id
        self.logger.info(
            "Request started",
            extra={
                "request_id": request_id,
                "event": "request_start",
                **kwargs
            }
        )

    def log_step(self, step: str, **kwargs):
        """Log a processing step."""
        self.logger.info(
            f"Request step: {step}",
            extra={
                "request_id": self.request_id,
                "event": "request_step",
                "step": step,
                **kwargs
            }
        )

    def log_error(self, error: Exception, **kwargs):
        """Log an error during request processing."""
        self.logger.error(
            f"Request error: {error}",
            extra={
                "request_id": self.request_id,
                "event": "request_error",
                "error_type": type(error).__name__,
                "error_message": str(error),
                **kwargs
            },
            exc_info=True
        )

    def complete_request(self, **kwargs):
        """Log the completion of request processing."""
        self.logger.info(
            "Request completed",
            extra={
                "request_id": self.request_id,
                "event": "request_complete",
                **kwargs
            }
        )

    def fail_request(self, error: Exception, **kwargs):
        """Log request failure."""
        self.logger.error(
            f"Request failed: {error}",
            extra={
                "request_id": self.request_id,
                "event": "request_failed",
                "error_type": type(error).__name__,
                "error_message": str(error),
                **kwargs
            },
            exc_info=True
        )