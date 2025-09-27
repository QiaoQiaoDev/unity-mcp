"""Warn-only JSON Schema validation for Unity MCP payloads."""

from __future__ import annotations

import json
import logging
import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict

from jsonschema import Draft202012Validator, ValidationError

from request_context import current_request_id

_logger = logging.getLogger("mcp-for-unity-server")


def _env_flag(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


SCHEMA_ROOT = Path(__file__).resolve().parents[3] / "protocol" / "schemas" / "v1"


def _schema_path(kind: str, tool: str | None = None) -> Path:
    if kind in {"request", "response"} and tool:
        return SCHEMA_ROOT / "tools" / f"{tool}-{kind}.json"
    if kind in {"request-envelope", "response-envelope"}:
        return SCHEMA_ROOT / "envelopes" / ("request.json" if kind == "request-envelope" else "response.json")
    raise ValueError(f"Unknown schema kind: {kind}")


@lru_cache(maxsize=None)
def _load_validator(kind: str, tool: str | None = None) -> Draft202012Validator | None:
    try:
        schema_file = _schema_path(kind, tool)
        with schema_file.open("r", encoding="utf-8") as fh:
            schema = json.load(fh)
        return Draft202012Validator(schema)
    except FileNotFoundError:
        _logger.debug("Schema file missing for kind=%s tool=%s", kind, tool)
    except Exception:
        _logger.exception("Failed to load schema for kind=%s tool=%s", kind, tool)
    return None


def _warn(errors: list[ValidationError], *, context: str, tool: str | None = None) -> None:
    rid = current_request_id()
    for err in errors:
        data_path = ".".join([str(part) for part in err.absolute_path]) or "<root>"
        _logger.warning(
            "Schema validation warning (%s%s): %s [path=%s]",
            tool or "envelope",
            f"/{context}",
            err.message,
            data_path,
            extra={"request_id": rid} if rid else None,
        )


def _should_validate() -> bool:
    return _env_flag("MCP_VALIDATE_SCHEMAS", True)


def validate_tool_request(tool: str, payload: Dict[str, Any] | None) -> None:
    if not _should_validate() or payload is None:
        return
    validator = _load_validator("request", tool)
    if validator is None:
        return
    errors = list(validator.iter_errors(payload))
    if errors:
        _warn(errors, context="request", tool=tool)


def validate_tool_response(tool: str, payload: Dict[str, Any] | None) -> None:
    if not _should_validate() or payload is None:
        return
    validator = _load_validator("response", tool)
    if validator is None:
        return
    errors = list(validator.iter_errors(payload))
    if errors:
        _warn(errors, context="response", tool=tool)


def validate_envelope(kind: str, payload: Dict[str, Any] | None) -> None:
    if not _should_validate() or payload is None:
        return
    if kind not in {"request", "response"}:
        raise ValueError(f"Envelope kind must be 'request' or 'response', got {kind}")
    validator = _load_validator(f"{kind}-envelope")
    if validator is None:
        return
    errors = list(validator.iter_errors(payload))
    if errors:
        _warn(errors, context="envelope")
