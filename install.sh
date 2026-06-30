#!/usr/bin/env bash
# Installer for the Kamar-Taj skills repo.
# Copies each skill into your Claude Code skills folder (~/.claude/skills/).
#
# Usage:  bash install.sh
set -e

SRC="$(cd "$(dirname "$0")" && pwd)"
DEST="$HOME/.claude/skills"
mkdir -p "$DEST"

for skill in daily-log dormammu; do
  mkdir -p "$DEST/$skill"
  cp -R "$SRC/$skill/." "$DEST/$skill/"
  chmod +x "$DEST/$skill/"*.sh 2>/dev/null || true
  echo "installed: $skill -> $DEST/$skill"
done

echo
echo "Done. Restart Claude Code (or start a new session), then use:"
echo "   /daily-log     and     /dormammu"
echo
echo "Optional for daily-log: Node.js + Google Chrome (PDF), rclone (Google Drive)."
