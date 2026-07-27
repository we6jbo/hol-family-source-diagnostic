#!/bin/sh
set -eu
SRC=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PERSIST="$HOME/.local/lib/hol-family-source-diagnostic"
UNIT="$HOME/.config/systemd/user/hol-family-source-updater.service"
mkdir -p "$PERSIST" "$(dirname "$UNIT")" "$HOME/.local/state/hol-family-source-diagnostic"
cp "$SRC/hol-update-watcher.py" "$PERSIST/"
cp "$SRC/github-recovery-test.sh" "$PERSIST/"
cp "$SRC/restore-from-github.sh" "$PERSIST/"
chmod u+x "$PERSIST"/*.py "$PERSIST"/*.sh
cat > "$UNIT" <<EOF
[Unit]
Description=HOL Family Source Diagnostic update watcher
After=graphical-session.target network-online.target
Wants=network-online.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 $PERSIST/hol-update-watcher.py
Restart=on-failure
RestartSec=5

[Install]
WantedBy=default.target
EOF
systemctl --user daemon-reload
systemctl --user enable --now hol-family-source-updater.service
printf 'Updater enabled and stored persistently in %s\n' "$PERSIST"
printf 'Status: systemctl --user status hol-family-source-updater.service\n'
