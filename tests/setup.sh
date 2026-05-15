#!/usr/bin/env bash
# Creates an isolated venv and installs pinned test dependencies.
# Run from anywhere — the script locates itself and uses absolute paths.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"

echo "Creating venv at $VENV_DIR ..."
python3 -m venv "$VENV_DIR"

echo "Installing pinned test dependencies ..."
"$VENV_DIR/bin/pip" install --quiet --upgrade pip
"$VENV_DIR/bin/pip" install --quiet -r "$SCRIPT_DIR/requirements-dev.txt"

echo ""
echo "Done. To run the tests:"
echo "  cd $SCRIPT_DIR"
echo "  .venv/bin/pytest -v"
