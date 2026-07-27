#!/bin/sh
set -eu
PROJECT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$PROJECT_DIR"
exec /usr/bin/python3 "$PROJECT_DIR/hol-reddit-ollama-bridge.py"
