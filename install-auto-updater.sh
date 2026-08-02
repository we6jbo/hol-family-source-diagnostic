#!/bin/sh
set -eu
SRC=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PERSIST="$HOME/.local/lib/hol-family-source-diagnostic"
UNIT="$HOME/.config/systemd/user/hol-family-source-updater.service"
AUTOSTART="$HOME/.config/autostart/hol-family-source-session.desktop"
CACHE="$HOME/.local/share/hol-family-source-diagnostic/recovery-project"
mkdir -p "$PERSIST" "$(dirname "$UNIT")" "$(dirname "$AUTOSTART")" "$HOME/.local/state/hol-family-source-diagnostic" "$(dirname "$CACHE")"
cp "$SRC/hol-update-watcher.py" "$PERSIST/"
cp "$SRC/hol-graphical-session-start.sh" "$PERSIST/"
for f in github-recovery-test.sh restore-from-github.sh; do
    [ ! -f "$SRC/$f" ] || cp "$SRC/$f" "$PERSIST/"
done
chmod 755 "$PERSIST/hol-update-watcher.py" "$PERSIST/hol-graphical-session-start.sh"
chmod u+x "$PERSIST"/*.sh 2>/dev/null || true

# Keep a persistent, private recovery copy outside /tmp.
rm -rf "$CACHE.new"
cp -a "$SRC" "$CACHE.new"
rm -rf "$CACHE"
mv "$CACHE.new" "$CACHE"
chmod -R u+rwX,go-rwx "$CACHE" 2>/dev/null || true
cat > "$UNIT" <<EOF2
[Unit]
Description=HOL Family Source Diagnostic update watcher
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 $PERSIST/hol-update-watcher.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=default.target
EOF2
cat > "$AUTOSTART" <<EOF2
[Desktop Entry]
Type=Application
Name=HOL Family Source Diagnostic Session Recovery
Comment=Import the graphical session, restore the project, and start the newest HOL version
Exec=/bin/sh $PERSIST/hol-graphical-session-start.sh
Terminal=false
StartupNotify=false
X-GNOME-Autostart-enabled=true
EOF2
chmod 644 "$AUTOSTART"
if [ -f "$SRC/setup-pf2f5qtt-private-recovery.sh" ]; then
    /bin/sh "$SRC/setup-pf2f5qtt-private-recovery.sh" || printf 'Warning: private PF2F5QTT package setup failed.\n' >&2
fi
systemctl --user daemon-reload
systemctl --user enable --now hol-family-source-updater.service
# Import the current environment too, when this installer is run from a terminal in the desktop.
systemctl --user import-environment DISPLAY WAYLAND_DISPLAY XAUTHORITY DBUS_SESSION_BUS_ADDRESS 2>/dev/null || true
systemctl --user restart hol-family-source-updater.service
printf 'Updater enabled at %s\n' "$PERSIST"
printf 'Graphical-login helper installed at %s\n' "$AUTOSTART"
printf 'Persistent recovery copy stored at %s\n' "$CACHE"
