#!/bin/sh
set -eu
SOURCE_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
mkdir -p /tmp/datediag /tmp/sensitiveinf22
for file in hol-family-source-investigator.py README.md LICENSE .gitignore; do
    [ ! -f "$SOURCE_DIR/$file" ] || cp "$SOURCE_DIR/$file" /tmp/datediag/
done
chmod +x /tmp/datediag/hol-family-source-investigator.py
exec python3 /tmp/datediag/hol-family-source-investigator.py
