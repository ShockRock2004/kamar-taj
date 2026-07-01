#!/usr/bin/env bash
# Installer for the Kamar-Taj skills repo.
# Copies each skill into your Claude Code skills folder (~/.claude/skills/).
#
# Usage:  bash install.sh
set -e

SRC="$(cd "$(dirname "$0")" && pwd)"
DEST="$HOME/.claude/skills"
mkdir -p "$DEST"

for skill in wong dormammu agamotto; do
  mkdir -p "$DEST/$skill"
  cp -R "$SRC/$skill/." "$DEST/$skill/"
  chmod +x "$DEST/$skill/"*.sh 2>/dev/null || true
  echo "installed: $skill -> $DEST/$skill"
done

echo
echo "Done. Restart Claude Code (or start a new session), then use:"
echo "   /wong     /dormammu     /agamotto"
echo
echo "Optional for wong: Node.js + Google Chrome (PDF), rclone (Google Drive)."
