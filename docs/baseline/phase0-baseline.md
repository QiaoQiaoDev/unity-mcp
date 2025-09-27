# Phase 0 Baseline Checklist

This document captures the baseline verification state prior to hardening changes. It should be updated whenever the baseline is re-run.

## Metadata
- Tag: `v0-baseline`
- Branch: `feature/hardening-phased`
- Date: $(date -u)
- Unity Version: Unity 6.1 (Editor)
- Python Version: 3.13.5

## How to Capture a Fresh Baseline
1. Ensure the Unity Editor project is open and the MCP Bridge is running.
2. Launch the Python bridge via `uv run python -m unity_mcp_server` (or the current entrypoint).
3. Set environment variables before launching:
   ```bash
   export UNITY_MCP_SKIP_STARTUP_CONNECT=0
   export MCP_JSON_LOGS=false
   export LOG_PLAIN_TEXT=true
   export UNITY_MCP_TELEMETRY_ENABLED=false
   ```
4. Start a new terminal for the MCP client (Cursor/IDE or CLI) and execute the prompts in the table below.
5. Collect server logs from `~/Library/Application Support/UnityMCP/Logs/unity_mcp_server.log` and Unity Editor logs from `~/Library/Logs/Unity/Editor.log`.
6. Archive logs under `logs/baseline/YYYYMMDD/` with filenames `python-bridge.log` and `unity-editor.log`.

## Baseline Prompts and Outcomes
Record the exact prompt issued, observed output, and whether it matched expectations. Include Unity console excerpts if needed.

| Flow | Prompt / Script | Expected Outcome | Observed Outcome | Pass? |
| ---- | --------------- | ---------------- | ---------------- | ----- |
| manage_scene | | Hierarchy listed, scene load/save succeeds | | |
| manage_asset | | Asset lifecycle completes (create/import/delete) | | |
| manage_script | | Script create/edit/validate with clean domain reload | | |
| manage_gameobject | | GameObject operations succeed | | |
| manage_menu_item | | `File/Save Project` executes without error | | |
| read_console | | Logs readable, clear leaves console empty | | |
| Long-running op | | Moderate import/shader compile finishes without timeout | | |
| Multi-request burst | | 10 quick script edits processed in order | | |

> **Note:** Populate the “Prompt / Script” column with the exact text used. Save any supporting JSON payloads or CLI invocations under `logs/baseline/YYYYMMDD/prompts/`.

## Log Archival Checklist
- [ ] `logs/baseline/YYYYMMDD/python-bridge.log`
- [ ] `logs/baseline/YYYYMMDD/unity-editor.log`
- [ ] `logs/baseline/YYYYMMDD/prompts/*.md`
- [ ] `logs/baseline/YYYYMMDD/diff-notes.md` (record notable differences once phases progress)

## Exit Criteria
- All rows in the table above marked as Pass.
- Logs archived and paths recorded here.
- Any anomalies documented prior to proceeding to Phase 1.
