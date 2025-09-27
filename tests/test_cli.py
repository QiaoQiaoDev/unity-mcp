import importlib
import json
import sys
from pathlib import Path

from typer.testing import CliRunner

runner = CliRunner()


def _invoke_cli(args):
    for key in list(sys.modules.keys()):
        if key == "cli" or key.startswith("cli."):
            sys.modules.pop(key, None)
            continue
        if key.startswith("mcp"):
            sys.modules.pop(key, None)
            continue
        if key.startswith("tools.") or key == "tools":
            sys.modules.pop(key, None)
            continue
        if key.startswith("UnityMcpBridge.UnityMcpServer~.src.tools"):
            sys.modules.pop(key, None)
            continue
    cli = importlib.import_module("cli")
    return runner.invoke(cli.app, args)


def test_list_tools_outputs_json():
    result = _invoke_cli(["list-tools"])
    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert isinstance(data, list)
    assert any(name == "manage_asset" for name in data)


def test_health_uses_stub(monkeypatch):
    monkeypatch.setenv("MCP_GUARD_ENABLE", "0")
    monkeypatch.setenv("LOG_PLAIN_TEXT", "1")
    monkeypatch.setenv("MCP_JSON_LOGS", "0")
    monkeypatch.setenv("MCP_VALIDATE_SCHEMAS", "0")

    def _send_command(name, params, **kwargs):
        assert name == "ping"
        return {"message": "pong"}

    for key in list(sys.modules.keys()):
        if key == "cli" or key.startswith("mcp"):
            sys.modules.pop(key, None)
    import cli

    monkeypatch.setattr(cli, "send_command_with_retry", _send_command)
    monkeypatch.setattr(cli, "get_unity_connection", lambda: object())
    result = runner.invoke(cli.app, ["health"])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["status"] == "ok"


def test_run_sample_returns_output(tmp_path: Path, monkeypatch):
    sample = {
        "tool": "list_resources",
        "params": {
            "pattern": "*.py",
            "under": "UnityMcpBridge/UnityMcpServer~/src",
            "project_root": ".",
            "limit": 1,
        },
    }
    sample_path = tmp_path / "sample.json"
    sample_path.write_text(json.dumps(sample), encoding="utf-8")

    result = _invoke_cli(["run-sample", str(sample_path), "--preview"])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["tool"] == "list_resources"
    assert "params" in payload
