import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from cli import app

runner = CliRunner()


def test_list_tools_outputs_json():
    result = runner.invoke(app, ["list-tools"])
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

    monkeypatch.setattr("cli.send_command_with_retry", _send_command)
    monkeypatch.setattr("cli.get_unity_connection", lambda: object())
    result = runner.invoke(app, ["health"])
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

    result = runner.invoke(app, ["run-sample", str(sample_path)])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert isinstance(payload, dict)
    assert "data" in payload or isinstance(payload, list)
