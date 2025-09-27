"""Runtime guardrails (allowlist, dry-run, confirmation, rate limits)."""

from __future__ import annotations

import logging
import os
import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Callable, Dict, Optional, Tuple

_logger = logging.getLogger("mcp-for-unity-server")

ConfirmationCallback = Callable[[str, Optional[str], Dict[str, object]], bool]


@dataclass
class RateLimitConfig:
    max_hits: int
    window_seconds: float


class GuardrailManager:
    """Evaluates guardrail policies for outbound Unity tool calls."""

    _HIGH_RISK_DEFAULT = {
        "manage_asset:delete",
        "manage_asset:remove",
        "manage_asset:destroy",
        "manage_asset:move",
        "manage_asset:rename",
        "manage_gameobject:delete",
        "manage_gameobject:remove",
        "manage_scene:close",
        "manage_scene:unload",
        "manage_scene:save",
        "manage_menu_item:execute",
    }

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._hits: Dict[str, deque[float]] = defaultdict(deque)
        self._confirmation_callback: ConfirmationCallback | None = None
        self.reload()

    # ------------------------------------------------------------------
    # Configuration helpers
    # ------------------------------------------------------------------
    def reload(self) -> None:
        """Re-evaluate configuration from environment variables."""
        self.enabled = _env_flag("MCP_GUARD_ENABLE", False)
        self.dry_run = _env_flag("MCP_GUARD_DRY_RUN", False)
        allowlist_raw = os.getenv("MCP_GUARD_ALLOWLIST", "")
        self.allowlist = {
            _normalize_guard_key(entry)
            for entry in allowlist_raw.split(",")
            if entry.strip()
        }
        # include default allowlist entries specified in env (if provided we interpret as allow). defaults to empty.
        self.high_risk = set(self._HIGH_RISK_DEFAULT)

        rate_raw = os.getenv("MCP_GUARD_RATE_LIMITS", "")
        window = _env_float("MCP_GUARD_RATE_WINDOW", 60.0)
        self.rate_limits: Dict[str, RateLimitConfig] = {}
        for token in rate_raw.split(","):
            token = token.strip()
            if not token or "=" not in token:
                continue
            key, value = token.split("=", 1)
            key = _normalize_guard_key(key)
            try:
                limit = int(value.strip())
            except ValueError:
                _logger.warning("Ignoring invalid rate limit value for %s: %s", key, value)
                continue
            if limit <= 0:
                continue
            self.rate_limits[key] = RateLimitConfig(max_hits=limit, window_seconds=window)

        require_confirmation = _env_flag("MCP_GUARD_REQUIRE_CONFIRMATION", False)
        self.require_confirmation = require_confirmation
        with self._lock:
            self._hits.clear()

    def register_confirmation_callback(self, callback: ConfirmationCallback | None) -> None:
        self._confirmation_callback = callback

    # ------------------------------------------------------------------
    # Evaluation
    # ------------------------------------------------------------------
    def evaluate(self, tool: str, payload: Dict[str, object]) -> Optional[Dict[str, object]]:
        if not self.enabled:
            return None

        action = _extract_action(payload)
        guard_key = _normalize_guard_key(f"{tool}:{action or ''}")
        log_suffix = f"tool={tool} action={action or 'n/a'}"

        # Allowlist enforcement for high-risk operations
        if guard_key in self.high_risk and guard_key not in self.allowlist:
            _logger.warning("Guardrail block (allowlist) %s", log_suffix)
            return {
                "success": False,
                "state": "guardrail_blocked",
                "error": "Operation requires explicit allowlist entry",
                "details": {
                    "tool": tool,
                    "action": action,
                },
            }

        # Confirmation hook
        if self.require_confirmation and guard_key in self.high_risk:
            confirmed = False
            if self._confirmation_callback:
                try:
                    confirmed = self._confirmation_callback(tool, action, payload)
                except Exception as exc:  # pragma: no cover - defensive
                    _logger.warning("Confirmation callback failed: %s", exc)
            if not confirmed:
                _logger.warning("Guardrail block (confirmation) %s", log_suffix)
                return {
                    "success": False,
                    "state": "confirmation_required",
                    "error": "Operation requires confirmation",
                    "details": {
                        "tool": tool,
                        "action": action,
                    },
                }

        # Rate limiting (tool-level and tool+action)
        now = time.monotonic()
        for key in (_normalize_guard_key(tool), guard_key):
            limit = self.rate_limits.get(key)
            if not limit:
                continue
            with self._lock:
                hits = self._hits[key]
                while hits and now - hits[0] > limit.window_seconds:
                    hits.popleft()
                if len(hits) >= limit.max_hits:
                    retry_after = max(0.0, limit.window_seconds - (now - hits[0]))
                    _logger.warning("Guardrail block (rate) %s hits=%d limit=%d", log_suffix, len(hits), limit.max_hits)
                    return {
                        "success": False,
                        "state": "rate_limited",
                        "error": "Request rate exceeded",
                        "retry_after_s": round(retry_after, 2),
                        "details": {
                            "tool": tool,
                            "action": action,
                        },
                    }
                hits.append(now)

        if self.dry_run:
            _logger.info("Guardrail dry-run %s", log_suffix)
            return {
                "success": True,
                "state": "dry_run",
                "message": "Dry-run enabled: operation not sent to Unity",
                "details": {
                    "tool": tool,
                    "action": action,
                },
            }

        return None


def _normalize_guard_key(value: str) -> str:
    return value.strip().lower().replace(" ", "")


def _extract_action(payload: Dict[str, object]) -> Optional[str]:
    for key in ("action", "Action", "operation", "mode"):
        if key in payload and isinstance(payload[key], str):
            return payload[key]
    return None


def _env_flag(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _env_float(name: str, default: float) -> float:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return float(raw)
    except ValueError:
        _logger.warning("Invalid float value for %s: %s", name, raw)
        return default


_manager = GuardrailManager()


def evaluate(tool: str, payload: Dict[str, object]) -> Optional[Dict[str, object]]:
    return _manager.evaluate(tool, payload)


def reload() -> None:
    _manager.reload()


def register_confirmation_callback(callback: ConfirmationCallback | None) -> None:
    _manager.register_confirmation_callback(callback)


__all__ = ["evaluate", "reload", "register_confirmation_callback", "GuardrailManager"]
