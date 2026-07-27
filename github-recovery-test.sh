#!/bin/sh
set -eu
TMP=$(mktemp -d /tmp/hol-github-test.XXXXXX)
trap 'rm -rf "$TMP"' EXIT
git clone --depth 1 https://github.com/we6jbo/hol-family-source-diagnostic.git "$TMP/repo"
python3 -m py_compile "$TMP/repo/hol-reddit-ollama-bridge.py"
python3 - <<PY
import json
from pathlib import Path
p=Path('$TMP/repo/chrome-extension/manifest.json')
d=json.loads(p.read_text())
for n in ['background.js','content.js','popup.js','popup.html']:
 assert (p.parent/n).is_file(), n
print('GitHub recovery test passed for version', d['version'])
PY
