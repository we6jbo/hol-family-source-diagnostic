#!/bin/sh
set -eu
SOURCE_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
mkdir -p /tmp/datediag /tmp/sensitiveinf22
cp "$SOURCE_DIR/hol-reddit-ollama-bridge.py" /tmp/datediag/
cp "$SOURCE_DIR/run-reddit-ollama-bridge.sh" /tmp/datediag/
rm -rf /tmp/datediag/chrome-extension
cp -R "$SOURCE_DIR/chrome-extension" /tmp/datediag/chrome-extension
[ ! -f "$SOURCE_DIR/README.md" ] || cp "$SOURCE_DIR/README.md" /tmp/datediag/
[ ! -f "$SOURCE_DIR/LICENSE" ] || cp "$SOURCE_DIR/LICENSE" /tmp/datediag/
[ ! -f "$SOURCE_DIR/.gitignore" ] || cp "$SOURCE_DIR/.gitignore" /tmp/datediag/
chmod +x /tmp/datediag/hol-reddit-ollama-bridge.py
exec python3 /tmp/datediag/hol-reddit-ollama-bridge.py
