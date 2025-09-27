#!/usr/bin/env bash
set -euo pipefail

printf '\n===============================================\n'
printf 'MCP for Unity Development Restore Script\n'
printf '===============================================\n\n'

if [[ "$OSTYPE" == darwin* ]]; then
  DEFAULT_SERVER_PATH="$HOME/Library/Application Support/UnityMCP/UnityMcpServer/src"
else
  DEFAULT_SERVER_PATH="$HOME/.local/share/UnityMCP/UnityMcpServer/src"
fi
DEFAULT_BACKUP_DIR="$HOME/Desktop/unity-mcp-backup"

read -rp $'Unity Package Cache path (e.g. /path/to/Library/PackageCache/com.coplaydev.unity-mcp@1.0.0):\n> ' PACKAGE_CACHE_PATH
if [[ -z "${PACKAGE_CACHE_PATH}" ]]; then
  echo "Error: package cache path is required." >&2
  exit 1
fi

read -rp $'Server installation path (press enter for default):\n> ' SERVER_PATH
SERVER_PATH=${SERVER_PATH:-$DEFAULT_SERVER_PATH}

read -rp $'Backup directory (press enter for default):\n> ' BACKUP_DIR
BACKUP_DIR=${BACKUP_DIR:-$DEFAULT_BACKUP_DIR}

if [[ ! -d "$BACKUP_DIR" ]]; then
  echo "No backups found in $BACKUP_DIR" >&2
  exit 1
fi

mapfile -t BACKUPS < <(find "$BACKUP_DIR" -maxdepth 1 -type d -name 'backup_*' | sort)
if [[ ${#BACKUPS[@]} -eq 0 ]]; then
  echo "No backups found in $BACKUP_DIR" >&2
  exit 1
fi

echo "Available backups:"
for idx in "${!BACKUPS[@]}"; do
  printf '  %d) %s\n' $((idx + 1)) "${BACKUPS[$idx]##*/}"
fi

read -rp "Select backup to restore (1-${#BACKUPS[@]}): " choice
if [[ -z "$choice" || ! "$choice" =~ ^[0-9]+$ || $choice -lt 1 || $choice -gt ${#BACKUPS[@]} ]]; then
  echo "Invalid selection" >&2
  exit 1
fi

SELECTED_BACKUP="${BACKUPS[$((choice - 1))]}"

echo
printf 'Restoring from: %s\n' "$SELECTED_BACKUP"
read -rp "This will overwrite files. Continue? (y/N): " confirm
if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
  echo "Restore cancelled."
  exit 0
fi

printf '\n===============================================\n'
printf 'Restoring backup...\n'
printf '===============================================\n'

if [[ -d "$SELECTED_BACKUP/UnityBridge/Editor" ]]; then
  rm -rf "$PACKAGE_CACHE_PATH/Editor"
  rsync -a "$SELECTED_BACKUP/UnityBridge/Editor/" "$PACKAGE_CACHE_PATH/Editor/"
else
  echo "Warning: Unity bridge backup not found, skipping" >&2
fi

if [[ -d "$SELECTED_BACKUP/PythonServer" ]]; then
  rm -rf "$SERVER_PATH"
  mkdir -p "$SERVER_PATH"
  rsync -a "$SELECTED_BACKUP/PythonServer/" "$SERVER_PATH/"
else
  echo "Warning: Python server backup not found, skipping" >&2
fi

printf '\nRestore complete. Restart Unity and MCP clients to apply restored files.\n'
