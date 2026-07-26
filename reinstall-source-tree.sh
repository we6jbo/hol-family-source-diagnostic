#!/bin/sh
# Reinstall this reviewed source tree at the original source location.
set -eu
SOURCE_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
TARGET_DIR=/tmp/to-github/hol-family-source-diagnostic
PARENT_DIR=$(dirname "$TARGET_DIR")
BACKUP_DIR="${TARGET_DIR}.backup-$(date +%Y%m%d-%H%M%S)"

mkdir -p "$PARENT_DIR"
if [ -e "$TARGET_DIR" ]; then
    mv "$TARGET_DIR" "$BACKUP_DIR"
    printf 'Existing tree moved to %s\n' "$BACKUP_DIR"
fi
cp -a "$SOURCE_DIR" "$TARGET_DIR"
rm -rf "$TARGET_DIR/.git"
chmod 755 "$TARGET_DIR"
find "$TARGET_DIR" -type d -exec chmod 755 {} +
find "$TARGET_DIR" -type f -exec chmod 644 {} +
chmod 755 "$TARGET_DIR"/*.sh "$TARGET_DIR"/*.py 2>/dev/null || true
printf 'Installed reviewed project at %s\n' "$TARGET_DIR"
printf 'Current owner: '
stat -c '%U:%G' "$TARGET_DIR"
printf 'Expected owner from supplied metadata: we6jbo:we6jbo\n'
