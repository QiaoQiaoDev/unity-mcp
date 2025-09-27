"""Lightweight command line interface for the Unity MCP server."""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path
from typing import Any, Iterable

import typer

from logging_utils import setup_logging
from unity_connection import get_unity_connection, send_command_with_retry

setup_logging()

app = typer.Typer(add_completion=False, help="Utility commands for the Unity MCP bridge")


def _build_mcp_server():
    from mcp.server.fastmcp import FastMCP
    from tools import register_all_tools

    mcp = FastMCP("unity-mcp-cli")
    register_all_tools(mcp)
    return mcp


def _serialize(obj: Any) -> Any:
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    if isinstance(obj, dict):
        return {key: _serialize(value) for key, value in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_serialize(value) for value in obj]
    return obj


@app.command()
def health(timeout: float = typer.Option(5.0, help="Timeout for the health ping in seconds")) -> None:
    """Ping the Unity bridge to verify connectivity."""
    try:
        conn = get_unity_connection()
        response = send_command_with_retry(
            "ping",
            {},
            max_retries=1,
            retry_ms=250,
            timeout=timeout,
        )
        typer.echo(json.dumps({"status": "ok", "response": response}))
    except Exception as exc:  # pragma: no cover - exercised via CLI integration tests
        typer.secho(f"Unity MCP health check failed: {exc}", fg=typer.colors.RED)
        raise typer.Exit(code=1) from exc


@app.command("list-tools")
def list_tools(show_details: bool = typer.Option(False, "--details", help="Show full tool metadata")) -> None:
    """List registered MCP tools."""

    async def _run() -> Iterable[Any]:
        mcp = _build_mcp_server()
        tools = await mcp.list_tools()
        if show_details:
            return [_serialize(tool) for tool in tools]
        return [tool.name for tool in tools]

    result = asyncio.run(_run())
    typer.echo(json.dumps(result, indent=2 if show_details else None))


@app.command("run-sample")
def run_sample(path: Path) -> None:
    """Execute a sample tool invocation described by a JSON file."""
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        typer.secho(f"Could not read sample file: {exc}", fg=typer.colors.RED)
        raise typer.Exit(code=1) from exc

    tool = payload.get("tool")
    params = payload.get("params") or {}
    if not tool or not isinstance(params, dict):
        typer.secho("Sample file must contain 'tool' (str) and 'params' (object)", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    async def _run() -> Any:
        mcp = _build_mcp_server()
        return await mcp.call_tool(tool, params)

    try:
        result = asyncio.run(_run())
    except Exception as exc:  # pragma: no cover - depends on Unity state
        typer.secho(f"Tool execution failed: {exc}", fg=typer.colors.RED)
        raise typer.Exit(code=1) from exc

    typer.echo(json.dumps(_serialize(result), indent=2))


def main() -> None:
    app()


if __name__ == "__main__":  # pragma: no cover
    main()
