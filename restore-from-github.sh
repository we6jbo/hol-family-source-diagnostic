#!/bin/sh
set -eu
TARGET=/tmp/to-github/hol-family-source-diagnostic
TMP=$(mktemp -d /tmp/hol-github-restore.XXXXXX)
trap 'rm -rf "$TMP"' EXIT
git clone https://github.com/we6jbo/hol-family-source-diagnostic.git "$TMP/repo"
python3 -m py_compile "$TMP/repo/hol-reddit-ollama-bridge.py"
if [ -d "$TARGET" ]; then mv "$TARGET" "$TARGET.backup-$(date +%Y%m%d-%H%M%S)"; fi
mkdir -p /tmp/to-github
mv "$TMP/repo" "$TARGET"
"$TARGET/install-extension-to-home.sh"
printf 'Restored from GitHub. Start with: %s/run-reddit-ollama-bridge.sh\n' "$TARGET"
