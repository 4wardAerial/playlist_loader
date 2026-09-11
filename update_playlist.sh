#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="$SCRIPT_DIR/.venv/bin/activate"
CODE="$SCRIPT_DIR/main.py"

cd "$SCRIPT_DIR" || exit 1
source "$VENV"
python3 "$CODE"

echo ""
read -p "Press [Enter] to close terminal."