#!/usr/bin/env python3
"""Generate JSON Schemas for Unity MCP tool requests."""

from __future__ import annotations

import json
from pathlib import Path

SCHEMA_BASE = Path("protocol/schemas/v1/tools")
SCHEMA_BASE.mkdir(parents=True, exist_ok=True)

def request_schema_path(tool: str) -> Path:
    return SCHEMA_BASE / f"{tool}-request.json"


def response_schema_path(tool: str) -> Path:
    return SCHEMA_BASE / f"{tool}-response.json"

TOOL_SCHEMAS = {
    "manage_scene": {
        "required": ["action"],
        "properties": {
            "action": {"type": "string"},
            "name": {"type": ["string", "null"]},
            "path": {"type": ["string", "null"]},
            "build_index": {"type": ["integer", "string", "null"]},
            "buildIndex": {"type": ["integer", "string", "null"]},
        },
    },
    "manage_asset": {
        "required": ["action", "path"],
        "properties": {
            "action": {"type": "string"},
            "path": {"type": "string"},
            "asset_type": {"type": ["string", "null"]},
            "assetType": {"type": ["string", "null"]},
            "properties": {"type": ["object", "null"]},
            "destination": {"type": ["string", "null"]},
            "search_pattern": {"type": ["string", "null"]},
            "searchPattern": {"type": ["string", "null"]},
            "filter_type": {"type": ["string", "null"]},
            "filterType": {"type": ["string", "null"]},
            "filter_date_after": {"type": ["string", "null"]},
            "filterDateAfter": {"type": ["string", "null"]},
            "page_size": {"type": ["integer", "string", "null"]},
            "pageSize": {"type": ["integer", "string", "null"]},
            "page_number": {"type": ["integer", "string", "null"]},
            "pageNumber": {"type": ["integer", "string", "null"]},
            "generate_preview": {"type": ["boolean", "null"]},
            "generatePreview": {"type": ["boolean", "null"]},
        },
    },
    "manage_script": {
        "required": ["action", "name", "path"],
        "properties": {
            "action": {"type": "string"},
            "name": {"type": "string"},
            "path": {"type": "string"},
            "contents": {"type": ["string", "null"]},
            "encodedContents": {"type": ["string", "null"]},
            "contentsEncoded": {"type": ["boolean", "null"]},
            "script_type": {"type": ["string", "null"]},
            "scriptType": {"type": ["string", "null"]},
            "namespace": {"type": ["string", "null"]},
        },
    },
    "apply_text_edits": {
        "required": ["uri", "edits"],
        "properties": {
            "uri": {"type": "string"},
            "edits": {"type": "array"},
            "precondition_sha256": {"type": ["string", "null"]},
            "preconditionSha256": {"type": ["string", "null"]},
            "strict": {"type": ["boolean", "null"]},
            "options": {"type": ["object", "null"]},
        },
    },
    "create_script": {
        "required": ["path"],
        "properties": {
            "path": {"type": "string"},
            "contents": {"type": ["string", "null"]},
            "script_type": {"type": ["string", "null"]},
            "scriptType": {"type": ["string", "null"]},
            "namespace": {"type": ["string", "null"]},
        },
    },
    "delete_script": {
        "required": ["uri"],
        "properties": {
            "uri": {"type": "string"},
        },
    },
    "validate_script": {
        "required": ["uri"],
        "properties": {
            "uri": {"type": "string"},
            "level": {"type": ["string", "null"]},
            "include_diagnostics": {"type": ["boolean", "null"]},
            "includeDiagnostics": {"type": ["boolean", "null"]},
        },
    },
    "manage_script_capabilities": {
        "required": [],
        "properties": {},
    },
    "get_sha": {
        "required": ["uri"],
        "properties": {
            "uri": {"type": "string"},
        },
    },
    "script_apply_edits": {
        "required": ["name", "path", "edits"],
        "properties": {
            "name": {"type": "string"},
            "path": {"type": "string"},
            "edits": {"type": "array"},
            "options": {"type": ["object", "null"]},
            "script_type": {"type": ["string", "null"]},
            "scriptType": {"type": ["string", "null"]},
            "namespace": {"type": ["string", "null"]},
        },
    },
    "manage_editor": {
        "required": ["action"],
        "properties": {
            "action": {"type": "string"},
            "wait_for_completion": {"type": ["boolean", "null"]},
            "waitForCompletion": {"type": ["boolean", "null"]},
            "tool_name": {"type": ["string", "null"]},
            "toolName": {"type": ["string", "null"]},
            "tag_name": {"type": ["string", "null"]},
            "tagName": {"type": ["string", "null"]},
            "layer_name": {"type": ["string", "null"]},
            "layerName": {"type": ["string", "null"]},
        },
    },
    "manage_gameobject": {
        "required": ["action"],
        "properties": {
            "action": {"type": "string"},
            "target": {"type": ["string", "null"]},
            "search_method": {"type": ["string", "null"]},
            "searchMethod": {"type": ["string", "null"]},
            "name": {"type": ["string", "null"]},
            "tag": {"type": ["string", "null"]},
            "parent": {"type": ["string", "null"]},
            "position": {"type": ["array", "null"]},
            "rotation": {"type": ["array", "null"]},
            "scale": {"type": ["array", "null"]},
            "components_to_add": {"type": ["array", "null"]},
            "componentsToAdd": {"type": ["array", "null"]},
            "primitive_type": {"type": ["string", "null"]},
            "primitiveType": {"type": ["string", "null"]},
            "save_as_prefab": {"type": ["boolean", "null"]},
            "saveAsPrefab": {"type": ["boolean", "null"]},
            "prefab_path": {"type": ["string", "null"]},
            "prefabPath": {"type": ["string", "null"]},
            "prefab_folder": {"type": ["string", "null"]},
            "prefabFolder": {"type": ["string", "null"]},
            "set_active": {"type": ["boolean", "null"]},
            "setActive": {"type": ["boolean", "null"]},
            "layer": {"type": ["string", "null"]},
            "components_to_remove": {"type": ["array", "null"]},
            "componentsToRemove": {"type": ["array", "null"]},
            "component_properties": {"type": ["object", "null"]},
            "componentProperties": {"type": ["object", "null"]},
            "search_term": {"type": ["string", "null"]},
            "searchTerm": {"type": ["string", "null"]},
            "find_all": {"type": ["boolean", "null"]},
            "findAll": {"type": ["boolean", "null"]},
            "search_in_children": {"type": ["boolean", "null"]},
            "searchInChildren": {"type": ["boolean", "null"]},
            "search_inactive": {"type": ["boolean", "null"]},
            "searchInactive": {"type": ["boolean", "null"]},
            "component_name": {"type": ["string", "null"]},
            "componentName": {"type": ["string", "null"]},
            "includeNonPublicSerialized": {"type": ["boolean", "null"]},
        },
    },
    "manage_menu_item": {
        "required": ["action"],
        "properties": {
            "action": {"type": "string"},
            "menu_path": {"type": ["string", "null"]},
            "menuPath": {"type": ["string", "null"]},
            "search": {"type": ["string", "null"]},
            "refresh": {"type": ["boolean", "null"]},
        },
    },
    "manage_prefabs": {
        "required": ["action"],
        "properties": {
            "action": {"type": "string"},
            "prefab_path": {"type": ["string", "null"]},
            "prefabPath": {"type": ["string", "null"]},
            "mode": {"type": ["string", "null"]},
            "save_before_close": {"type": ["boolean", "null"]},
            "saveBeforeClose": {"type": ["boolean", "null"]},
            "target": {"type": ["string", "null"]},
            "allow_overwrite": {"type": ["boolean", "null"]},
            "allowOverwrite": {"type": ["boolean", "null"]},
            "search_inactive": {"type": ["boolean", "null"]},
            "searchInactive": {"type": ["boolean", "null"]},
        },
    },
    "manage_shader": {
        "required": ["action", "name", "path"],
        "properties": {
            "action": {"type": "string"},
            "name": {"type": "string"},
            "path": {"type": "string"},
            "contents": {"type": ["string", "null"]},
            "encodedContents": {"type": ["string", "null"]},
            "contentsEncoded": {"type": ["boolean", "null"]},
        },
    },
    "read_console": {
        "required": [],
        "properties": {
            "action": {"type": ["string", "null"]},
            "types": {"type": ["array", "null"]},
            "count": {"type": ["integer", "string", "null"]},
            "filter_text": {"type": ["string", "null"]},
            "filterText": {"type": ["string", "null"]},
            "since_timestamp": {"type": ["string", "null"]},
            "sinceTimestamp": {"type": ["string", "null"]},
            "format": {"type": ["string", "null"]},
            "include_stacktrace": {"type": ["boolean", "null"]},
            "includeStacktrace": {"type": ["boolean", "null"]},
        },
    },
    "list_resources": {
        "required": [],
        "properties": {
            "pattern": {"type": ["string", "null"]},
            "under": {"type": ["string", "null"]},
            "limit": {"type": ["integer", "string", "null"]},
            "project_root": {"type": ["string", "null"]},
            "projectRoot": {"type": ["string", "null"]},
        },
    },
    "read_resource": {
        "required": ["uri"],
        "properties": {
            "uri": {"type": "string"},
            "start_line": {"type": ["integer", "string", "null"]},
            "startLine": {"type": ["integer", "string", "null"]},
            "line_count": {"type": ["integer", "string", "null"]},
            "lineCount": {"type": ["integer", "string", "null"]},
            "head_bytes": {"type": ["integer", "string", "null"]},
            "headBytes": {"type": ["integer", "string", "null"]},
            "tail_lines": {"type": ["integer", "string", "null"]},
            "tailLines": {"type": ["integer", "string", "null"]},
            "project_root": {"type": ["string", "null"]},
            "projectRoot": {"type": ["string", "null"]},
            "request": {"type": ["string", "null"]},
        },
    },
    "find_in_file": {
        "required": ["uri", "pattern"],
        "properties": {
            "uri": {"type": "string"},
            "pattern": {"type": "string"},
            "ignore_case": {"type": ["boolean", "null"]},
            "ignoreCase": {"type": ["boolean", "null"]},
            "project_root": {"type": ["string", "null"]},
            "projectRoot": {"type": ["string", "null"]},
            "max_results": {"type": ["integer", "string", "null"]},
            "maxResults": {"type": ["integer", "string", "null"]},
        },
    },
}

SCHEMA_TEMPLATE = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "additionalProperties": True,
}

for tool, info in TOOL_SCHEMAS.items():
    payload = SCHEMA_TEMPLATE | {
        "$id": f"https://unity-mcp.dev/schemas/v1/{tool}-request.json",
        "title": f"{tool} request",
        "required": info.get("required", []),
        "properties": info.get("properties", {}),
    }
    with request_schema_path(tool).open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2)
        fh.write("\n")

    response_payload = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": f"https://unity-mcp.dev/schemas/v1/{tool}-response.json",
        "title": f"{tool} response",
        "allOf": [{"$ref": "tool-response.json"}],
    }
    with response_schema_path(tool).open("w", encoding="utf-8") as fh:
        json.dump(response_payload, fh, indent=2)
        fh.write("\n")

print(f"Wrote {len(TOOL_SCHEMAS)} tool request/response schemas to {SCHEMA_BASE}")
