"""
Telemetry decorator for Unity MCP tools
"""

import functools
import time
import inspect
import logging
from typing import Callable, Any
from telemetry import record_tool_usage, record_milestone, MilestoneType
from request_context import activate_request_context, annotate_response
from schema_validator import validate_tool_request, validate_tool_response


def _extract_ctx(args: tuple, kwargs: dict):
    """Best-effort extraction of the MCP Context from positional/keyword args."""
    for value in args:
        if hasattr(value, "request_id"):
            return value
    return kwargs.get("ctx")


def _extract_payload(func, args, kwargs) -> dict:
    try:
        sig = inspect.signature(func)
        bound = sig.bind_partial(*args, **kwargs)
        bound.apply_defaults()
        return {k: v for k, v in bound.arguments.items() if k != "ctx"}
    except Exception:
        return {}

_log = logging.getLogger("unity-mcp-telemetry")
_decorator_log_count = 0

def telemetry_tool(tool_name: str):
    """Decorator to add telemetry tracking to MCP tools"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def _sync_wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            success = False
            error = None
            # Extract sub-action (e.g., 'get_hierarchy') from bound args when available
            sub_action = None
            payload = {}
            try:
                sig = inspect.signature(func)
                bound = sig.bind_partial(*args, **kwargs)
                bound.apply_defaults()
                sub_action = bound.arguments.get("action")
                payload = {k: v for k, v in bound.arguments.items() if k != "ctx"}
            except Exception:
                sub_action = None
                payload = _extract_payload(func, args, kwargs)
            ctx = _extract_ctx(args, kwargs)
            try:
                with activate_request_context(ctx):
                    validate_tool_request(tool_name, payload)
                    global _decorator_log_count
                    if _decorator_log_count < 10:
                        _log.info(f"telemetry_decorator sync: tool={tool_name}")
                        _decorator_log_count += 1
                    result = func(*args, **kwargs)
                    success = True
                    action_val = sub_action or kwargs.get("action")
                    try:
                        if tool_name == "manage_script" and action_val == "create":
                            record_milestone(MilestoneType.FIRST_SCRIPT_CREATION)
                        elif tool_name.startswith("manage_scene"):
                            record_milestone(MilestoneType.FIRST_SCENE_MODIFICATION)
                        record_milestone(MilestoneType.FIRST_TOOL_USAGE)
                    except Exception:
                        _log.debug("milestone emit failed", exc_info=True)
                    annotated = annotate_response(result)
                    if isinstance(annotated, dict):
                        validate_tool_response(tool_name, annotated)
                    return annotated
            except Exception as e:
                error = str(e)
                raise
            finally:
                duration_ms = (time.time() - start_time) * 1000
                try:
                    record_tool_usage(tool_name, success, duration_ms, error, sub_action=sub_action)
                except Exception:
                    _log.debug("record_tool_usage failed", exc_info=True)

        @functools.wraps(func)
        async def _async_wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            success = False
            error = None
            # Extract sub-action (e.g., 'get_hierarchy') from bound args when available
            sub_action = None
            payload = {}
            try:
                sig = inspect.signature(func)
                bound = sig.bind_partial(*args, **kwargs)
                bound.apply_defaults()
                sub_action = bound.arguments.get("action")
                payload = {k: v for k, v in bound.arguments.items() if k != "ctx"}
            except Exception:
                sub_action = None
                payload = _extract_payload(func, args, kwargs)
            ctx = _extract_ctx(args, kwargs)
            try:
                with activate_request_context(ctx):
                    validate_tool_request(tool_name, payload)
                    global _decorator_log_count
                    if _decorator_log_count < 10:
                        _log.info(f"telemetry_decorator async: tool={tool_name}")
                        _decorator_log_count += 1
                    result = await func(*args, **kwargs)
                    success = True
                    action_val = sub_action or kwargs.get("action")
                    try:
                        if tool_name == "manage_script" and action_val == "create":
                            record_milestone(MilestoneType.FIRST_SCRIPT_CREATION)
                        elif tool_name.startswith("manage_scene"):
                            record_milestone(MilestoneType.FIRST_SCENE_MODIFICATION)
                        record_milestone(MilestoneType.FIRST_TOOL_USAGE)
                    except Exception:
                        _log.debug("milestone emit failed", exc_info=True)
                    annotated = annotate_response(result)
                    if isinstance(annotated, dict):
                        validate_tool_response(tool_name, annotated)
                    return annotated
            except Exception as e:
                error = str(e)
                raise
            finally:
                duration_ms = (time.time() - start_time) * 1000
                try:
                    record_tool_usage(tool_name, success, duration_ms, error, sub_action=sub_action)
                except Exception:
                    _log.debug("record_tool_usage failed", exc_info=True)

        return _async_wrapper if inspect.iscoroutinefunction(func) else _sync_wrapper
    return decorator
