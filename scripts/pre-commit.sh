#!/bin/bash
# Run pre-commit checks and formatting

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

"$SCRIPT_DIR/dependencies-upgrade.sh"
"$SCRIPT_DIR/ruff-format.sh"
"$SCRIPT_DIR/code-check.sh"
"$SCRIPT_DIR/run-tests.sh"