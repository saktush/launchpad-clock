#!/bin/bash
# Install (or `--uninstall`) a LaunchAgent that runs the clock at login.
set -euo pipefail
LABEL=com.user.launchpad-clock
PLIST=~/Library/LaunchAgents/$LABEL.plist
DOMAIN=gui/$(id -u)
ROOT=$(cd "$(dirname "$0")/.." && pwd)

launchctl bootout "$DOMAIN/$LABEL" 2>/dev/null || true
while launchctl print "$DOMAIN/$LABEL" >/dev/null 2>&1; do sleep 0.5; done  # bootout is async
if [ "${1:-}" = "--uninstall" ]; then rm -f "$PLIST"; echo "Removed $LABEL"; exit 0; fi

mkdir -p ~/Library/LaunchAgents ~/Library/Logs
cat > "$PLIST" <<PL
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>$LABEL</string>
  <key>ProgramArguments</key><array>
    <string>$ROOT/.venv/bin/python</string><string>-u</string><string>-m</string><string>launchpad_clock</string>
  </array>
  <key>WorkingDirectory</key><string>$ROOT</string>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><true/>
  <key>StandardOutPath</key><string>$HOME/Library/Logs/launchpad-clock.log</string>
  <key>StandardErrorPath</key><string>$HOME/Library/Logs/launchpad-clock.log</string>
</dict></plist>
PL
launchctl bootstrap "$DOMAIN" "$PLIST"
echo "Installed $LABEL (log: ~/Library/Logs/launchpad-clock.log)"
