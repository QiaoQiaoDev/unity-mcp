"""Helpers for configuring logging for the MCP for Unity server."""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler

from config import config
from request_context import RequestIdFilter


def _env_flag(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


class JsonFormatter(logging.Formatter):
    """Minimal JSON formatter that preserves extras like request ids."""

    def format(self, record: logging.LogRecord) -> str:  # pragma: no cover - exercised via logging
        payload = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        request_id = getattr(record, "request_id", None)
        if request_id:
            payload["request_id"] = request_id
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        if record.stack_info:
            payload["stack"] = self.formatStack(record.stack_info)
        return json.dumps(payload, ensure_ascii=False)


def _build_stream_handler(use_json: bool) -> logging.Handler:
    handler = logging.StreamHandler()
    handler.addFilter(RequestIdFilter())
    if use_json:
        handler.setFormatter(JsonFormatter())
    else:
        handler.setFormatter(logging.Formatter(config.log_format))
    return handler


def _build_file_handler(use_json: bool) -> RotatingFileHandler:
    log_dir = os.path.join(
        os.path.expanduser("~/Library/Application Support/UnityMCP"),
        "Logs",
    )
    os.makedirs(log_dir, exist_ok=True)
    file_path = os.path.join(log_dir, "unity_mcp_server.log")
    handler = RotatingFileHandler(
        file_path,
        maxBytes=512 * 1024,
        backupCount=2,
        encoding="utf-8",
    )
    handler.addFilter(RequestIdFilter())
    if use_json:
        handler.setFormatter(JsonFormatter())
    else:
        handler.setFormatter(logging.Formatter(config.log_format))
    handler.setLevel(getattr(logging, config.log_level, logging.INFO))
    return handler


def setup_logging() -> None:
    """Configure root logging according to environment toggles."""
    plain_text = _env_flag("LOG_PLAIN_TEXT", False)
    use_json_logs = _env_flag("MCP_JSON_LOGS", True)
    use_json = False if plain_text else use_json_logs

    root = logging.getLogger()
    root.setLevel(getattr(logging, config.log_level, logging.INFO))
    root.handlers.clear()
    root.addHandler(_build_stream_handler(use_json))

    # Add rotating file handler for durability
    try:
        root.addHandler(_build_file_handler(use_json))
    except Exception:  # pragma: no cover - best effort for read-only environments
        root.debug("Skipping rotating file handler setup", exc_info=True)

    telemetry_logger = logging.getLogger("unity-mcp-telemetry")
    telemetry_logger.setLevel(getattr(logging, config.log_level, logging.INFO))
    telemetry_logger.handlers.clear()
    telemetry_logger.propagate = True

    # Silence overly verbose third-party loggers unless explicitly enabled
    for noisy in ("httpx", "urllib3"):
        logging.getLogger(noisy).setLevel(
            max(logging.WARNING, getattr(logging, config.log_level, logging.INFO))
        )
