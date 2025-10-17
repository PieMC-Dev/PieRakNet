#!/bin/bash
# Export requirements to requirements.txt and requirements-dev.txt

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "Exporting requirements..."
"$PROJECT_ROOT/.venv/bin/uv" export --format requirements.txt --no-hashes -o requirements.txt -qq
"$PROJECT_ROOT/.venv/bin/uv" export --format requirements.txt --no-hashes -o requirements-dev.txt -qq
