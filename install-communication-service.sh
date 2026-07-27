#!/bin/sh
set -eu
HOME_DIR=/home/we6jbo
PROJECT_DIR=/tmp/to-github/hol-family-source-diagnostic
PERSIST_DIR="$HOME_DIR/.local/lib/hol-family-source-diagnostic"
CONFIG_DIR="$HOME_DIR/.config/hol-family-source-diagnostic"
SERVICE_DIR="$HOME_DIR/.config/systemd/user"
mkdir -p "$PERSIST_DIR" "$CONFIG_DIR" "$SERVICE_DIR"
cp "$PROJECT_DIR/communication.py" "$PERSIST_DIR/communication.py"
chmod 600 "$PERSIST_DIR/communication.py"
if [ ! -s "$CONFIG_DIR/communication_password" ]; then
    printf 'Enter the localhost communication password: ' >&2
    stty -echo
    IFS= read -r password
    stty echo
    printf '\n' >&2
    [ -n "$password" ] || { echo 'Password cannot be empty.' >&2; exit 1; }
    printf '%s\n' "$password" > "$CONFIG_DIR/communication_password"
fi
chmod 600 "$CONFIG_DIR/communication_password"
cat > "$SERVICE_DIR/hol-qvix-communication.service" <<EOF
[Unit]
Description=HOL QVIX localhost communication console
After=graphical-session.target

[Service]
Type=simple
ExecStartPre=/bin/cp $PERSIST_DIR/communication.py /tmp/communication.py
ExecStartPre=/bin/chmod 700 /tmp/communication.py
ExecStart=/usr/bin/python3 /tmp/communication.py
Restart=on-failure
RestartSec=3

[Install]
WantedBy=default.target
EOF
systemctl --user daemon-reload
systemctl --user enable --now hol-qvix-communication.service
echo 'QVIX communication service installed. Connect with: telnet 127.0.0.1 2323'
