#!/bin/sh
# Install the runnable project copy while preserving the existing localhost port.
set -eu
SOURCE_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
TARGET_DIR=/tmp/datediag
SENSITIVE_DIR=/tmp/sensitiveinf22

mkdir -p "$TARGET_DIR" "$SENSITIVE_DIR"
for file in \
    hol-family-source-diagnostic.py \
    hol-family-source-investigator.py \
    hol-reddit-ollama-bridge.py \
    run-hol-family-source-investigator.sh \
    run-reddit-ollama-bridge.sh \
    README.md LICENSE .gitignore install.sh publish-to-github.sh reinstall-source-tree.sh token439873.touch
do
    [ ! -f "$SOURCE_DIR/$file" ] || cp "$SOURCE_DIR/$file" "$TARGET_DIR/$file"
done
if [ -d "$SOURCE_DIR/chrome-extension" ]; then
    rm -rf "$TARGET_DIR/chrome-extension"
    cp -R "$SOURCE_DIR/chrome-extension" "$TARGET_DIR/chrome-extension"
fi
chmod 755 "$TARGET_DIR"/*.py "$TARGET_DIR"/*.sh 2>/dev/null || true
exec python3 "$TARGET_DIR/hol-family-source-diagnostic.py"
