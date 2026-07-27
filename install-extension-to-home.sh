#!/bin/sh
set -eu
SOURCE_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
TARGET_DIR="$HOME/hol-family-source-diagnostic-extension"
rm -rf "$TARGET_DIR"
cp -R "$SOURCE_DIR/chrome-extension" "$TARGET_DIR"
chmod -R u+rwX,go-rwx "$TARGET_DIR"
printf 'Chrome extension copied to: %s\n' "$TARGET_DIR"
printf 'Next open chrome://extensions, enable Developer mode, choose Load unpacked, and select that directory.\n'
