#!/usr/bin/env bash
set -euo pipefail

printf '\n===============================================\n'
printf 'MCP for Unity Development Deployment Script\n'
printf '===============================================\n\n'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BRIDGE_SOURCE="$SCRIPT_DIR/UnityMcpBridge"
SERVER_SOURCE="$SCRIPT_DIR/UnityMcpBridge/UnityMcpServer~/src"

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

printf '\n===============================================\n'
printf 'Validating paths...\n'
printf '===============================================\n'

for path in "$BRIDGE_SOURCE" "$SERVER_SOURCE" "$PACKAGE_CACHE_PATH" "$SERVER_PATH"; do
  if [[ ! -e "$path" ]]; then
    echo "Error: missing path $path" >&2
    exit 1
  fi
fi

mkdir -p "$BACKUP_DIR"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
BACKUP_SUBDIR="$BACKUP_DIR/backup_${TIMESTAMP}"
mkdir -p "$BACKUP_SUBDIR"

printf '\n===============================================\n'
printf 'Backing up existing installation...\n'
printf '===============================================\n'

if [[ -d "$PACKAGE_CACHE_PATH/Editor" ]]; then
  rsync -a "$PACKAGE_CACHE_PATH/Editor/" "$BACKUP_SUBDIR/UnityBridge/Editor/"
fi

if [[ -d "$SERVER_PATH" ]]; then
  rsync -a "$SERVER_PATH/" "$BACKUP_SUBDIR/PythonServer/"
fi

printf '\n===============================================\n'
printf 'Deploying repo sources...\n'
printf '===============================================\n'

rsync -a "$BRIDGE_SOURCE/Editor/" "$PACKAGE_CACHE_PATH/Editor/"
rsync -a "$SERVER_SOURCE/" "$SERVER_PATH/"

printf '\n===============================================\n'
printf 'Deployment complete!\n'
printf '===============================================\n'
printf 'Backup stored at: %s\n' "$BACKUP_SUBDIR"
printf 'Restart Unity and any MCP clients to pick up the changes.\n'
