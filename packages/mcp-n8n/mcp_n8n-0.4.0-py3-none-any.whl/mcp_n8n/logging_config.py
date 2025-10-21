"""Structured logging configuration for mcp-n8n gateway.

Provides JSON-structured logging for better observability and debugging.
Supports trace context propagation for cross-service correlation.
"""
# mypy: disable-error-code="type-arg,override"

import json
import logging
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


class StructuredFormatter(logging.Formatter):
    """JSON-structured log formatter with trace context.

    Formats log records as JSON objects with:
    - Standardized timestamp (ISO 8601 UTC)
    - Log level and logger name
    - Source location (module, function, line)
    - Trace ID for cross-service correlation
    - Exception details if present
    """

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON.

        Args:
            record: Log record to format

        Returns:
            JSON-formatted log string
        """
        log_data: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add trace_id if present (for event correlation)
        if hasattr(record, "trace_id"):
            log_data["trace_id"] = record.trace_id

        # Add backend context if present
        if hasattr(record, "backend"):
            log_data["backend"] = record.backend

        # Add tool_name if present
        if hasattr(record, "tool_name"):
            log_data["tool_name"] = record.tool_name

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": self.formatException(record.exc_info),
            }

        # Add any extra fields from LoggerAdapter
        for key, value in record.__dict__.items():
            if key not in [
                "name",
                "msg",
                "args",
                "created",
                "msecs",
                "levelname",
                "levelno",
                "pathname",
                "filename",
                "module",
                "exc_info",
                "exc_text",
                "stack_info",
                "lineno",
                "funcName",
                "process",
                "processName",
                "thread",
                "threadName",
                "taskName",
                "trace_id",
                "backend",
                "tool_name",
            ] and not key.startswith("_"):
                log_data[key] = value

        return json.dumps(log_data)


def setup_structured_logging(
    log_level: str = "INFO",
    log_file: str = "logs/mcp-n8n.log",
    debug: bool = False,
) -> logging.Logger:
    """Configure structured JSON logging.

    Args:
        log_level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file for JSON output
        debug: Enable debug mode (forces DEBUG level)

    Returns:
        Configured root logger
    """
    # Create logs directory if it doesn't exist
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # Determine log level
    level = (
        logging.DEBUG if debug else getattr(logging, log_level.upper(), logging.INFO)
    )

    # Clear existing handlers
    root_logger = logging.getLogger()
    root_logger.handlers.clear()

    # File handler with JSON formatting
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(StructuredFormatter())
    file_handler.setLevel(level)
    root_logger.addHandler(file_handler)

    # Console handler with human-readable formatting (for development)
    console_handler = logging.StreamHandler(sys.stderr)
    console_format = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    console_handler.setFormatter(logging.Formatter(console_format))
    console_handler.setLevel(level)
    root_logger.addHandler(console_handler)

    # Set root logger level
    root_logger.setLevel(level)

    return root_logger


class TraceLogger(logging.LoggerAdapter):
    """Logger adapter that adds trace context to all log records.

    Usage:
        logger = TraceLogger(logging.getLogger(__name__), {"trace_id": "abc123"})
        logger.info("Processing request")  # trace_id automatically included
    """

    def process(self, msg: str, kwargs: dict[str, Any]) -> tuple[str, dict[str, Any]]:
        """Add trace context to log record.

        Args:
            msg: Log message
            kwargs: Additional log arguments

        Returns:
            Tuple of (message, kwargs with extra context)
        """
        extra = kwargs.get("extra", {})
        extra.update(self.extra)
        kwargs["extra"] = extra
        return msg, kwargs
