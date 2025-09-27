import importlib
import os
from contextlib import contextmanager

import pytest

from guardrails import evaluate, reload as reload_guardrails


@contextmanager
def guard_env(**env):
    old = {key: os.environ.get(key) for key in env}
    try:
        for key, value in env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        reload_guardrails()
        yield
    finally:
        for key, value in old.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        reload_guardrails()


def make_payload(action: str = "delete"):
    return {"action": action}


def test_guardrails_disabled_allows_operations():
    with guard_env(MCP_GUARD_ENABLE="0"):
        result = evaluate("manage_asset", make_payload("delete"))
        assert result is None


def test_guardrails_allowlist_blocks_when_missing():
    with guard_env(MCP_GUARD_ENABLE="1", MCP_GUARD_ALLOWLIST=""):
        result = evaluate("manage_asset", make_payload("delete"))
        assert result is not None
        assert result["state"] == "guardrail_blocked"


def test_guardrails_allowlist_allows_when_listed():
    with guard_env(MCP_GUARD_ENABLE="1", MCP_GUARD_ALLOWLIST="manage_asset:delete"):
        result = evaluate("manage_asset", make_payload("delete"))
        assert result is None


def test_guardrails_dry_run_returns_message():
    with guard_env(
        MCP_GUARD_ENABLE="1",
        MCP_GUARD_ALLOWLIST="manage_asset:delete",
        MCP_GUARD_DRY_RUN="1",
    ):
        result = evaluate("manage_asset", make_payload("delete"))
        assert result is not None
        assert result["state"] == "dry_run"
        assert result["success"] is True


def test_guardrails_rate_limit_blocks_after_threshold():
    with guard_env(
        MCP_GUARD_ENABLE="1",
        MCP_GUARD_ALLOWLIST="manage_asset:delete",
        MCP_GUARD_RATE_LIMITS="manage_asset=2",
        MCP_GUARD_RATE_WINDOW="3600",
    ):
        assert evaluate("manage_asset", make_payload("delete")) is None
        assert evaluate("manage_asset", make_payload("delete")) is None
        result = evaluate("manage_asset", make_payload("delete"))
        assert result is not None
        assert result["state"] == "rate_limited"
        assert result["success"] is False


def test_guardrails_confirmation_requires_callback():
    from guardrails import register_confirmation_callback

    def _confirm(tool, action, payload):
        return action == "delete"

    try:
        with guard_env(
            MCP_GUARD_ENABLE="1",
            MCP_GUARD_ALLOWLIST="manage_asset:delete",
            MCP_GUARD_REQUIRE_CONFIRMATION="1",
        ):
            register_confirmation_callback(_confirm)
            result = evaluate("manage_asset", make_payload("delete"))
            assert result is None
            register_confirmation_callback(lambda *_: False)
            blocked = evaluate("manage_asset", make_payload("delete"))
            assert blocked is not None
            assert blocked["state"] == "confirmation_required"
    finally:
        register_confirmation_callback(None)
