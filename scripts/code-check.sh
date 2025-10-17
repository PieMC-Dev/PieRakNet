#!/bin/bash
# Code quality checks

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "Running syntax checker"
"$PROJECT_ROOT/.venv/bin/ruff" check

echo "Running type checker"
"$PROJECT_ROOT/.venv/bin/ty" check