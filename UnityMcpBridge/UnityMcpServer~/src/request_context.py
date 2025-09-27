"""Utilities for managing request-scoped metadata such as request IDs."""

from __future__ import annotations

import contextlib
import contextvars
import logging
import os
import typing as t
import uuid

_logger = logging.getLogger("mcp-for-unity-server")

_request_id_var: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "unity_mcp_request_id",
    default=None,
)


def _normalize_request_id(value: t.Any) -> str | None:
    """Coerce a request identifier into the canonical string form."""
    if value is None:
        return None
    if isinstance(value, str):
        value = value.strip()
        return value or None
    try:
        return str(value)
    except Exception:  # pragma: no cover - defensive only
        return None


def current_request_id() -> str | None:
    """Return the active request id, if one has been established."""
    return _request_id_var.get()


@contextlib.contextmanager
def activate_request_context(ctx: t.Any | None = None, request_id: str | None = None):
    """Context manager that ensures a request id for the active scope.

    Args:
        ctx: Optional MCP Context object carrying request metadata.
        request_id: Explicit request id provided by upstream caller.
    """
    incoming = request_id
    # Attribute-based extraction from Context if available
    if incoming is None and ctx is not None:
        incoming = _normalize_request_id(getattr(ctx, "request_id", None))
        if incoming is None:
            try:
                request_ctx = getattr(ctx, "request_context", None)
                if isinstance(request_ctx, dict):
                    incoming = _normalize_request_id(request_ctx.get("request_id"))
            except Exception:  # pragma: no cover - defensive only
                pass
    rid = incoming or os.getenv("MCP_FORCE_REQUEST_ID") or str(uuid.uuid4())

    # Attempt to push onto the context object so downstream code can see it
    if ctx is not None:
        try:
            setattr(ctx, "request_id", rid)
        except Exception:  # pragma: no cover - defensive only
            _logger.debug("Could not set request_id on context", exc_info=True)

    token = _request_id_var.set(rid)
    try:
        yield rid
    finally:
        _request_id_var.reset(token)


def annotate_response(payload: t.Any) -> t.Any:
    """Attach the current request id to tool responses where applicable."""
    rid = current_request_id()
    if rid is None:
        return payload
    if isinstance(payload, dict):
        if "request_id" not in payload:
            payload = dict(payload)
            payload["request_id"] = rid
        return payload
    # Avoid mutating arbitrary payload types; return as-is
    return payload


class RequestIdFilter(logging.Filter):
    """Inject the active request id into log records for JSON logging."""

    def filter(self, record: logging.LogRecord) -> bool:  # pragma: no cover - exercised via logging
        rid = current_request_id()
        if rid is not None:
            setattr(record, "request_id", rid)
        return True
