#!/bin/bash
# Run tests using pytest

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "Running tests..."
"$PROJECT_ROOT/.venv/bin/pytest" -v