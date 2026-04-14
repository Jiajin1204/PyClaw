#!/bin/bash
# run.sh - Run PyClaw (activates venv and runs main.py)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [ ! -d "venv" ]; then
    bash setup.sh
fi

source venv/bin/activate
python main.py "$@"
