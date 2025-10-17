#!/bin/bash
# Upgrade dependencies

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "Updating dependencies..."
"$PROJECT_ROOT/.venv/bin/uv" sync

"$SCRIPT_DIR/export-requirements.sh"