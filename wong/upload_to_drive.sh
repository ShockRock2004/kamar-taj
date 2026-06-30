#!/usr/bin/env bash
# Upload a wong markdown file to Google Drive via rclone.
#
# ONE-TIME SETUP (run by you, once):
#   brew install rclone
#   rclone config          # create a remote named "gdrive" (type: drive), browser login
#
# After that, the /wong skill calls this automatically on every run.
#
# Usage:  upload_to_drive.sh "/path/to/<file>.md"
#
# Designed to be a SAFE NO-OP (exit 0) when rclone or the remote isn't set up,
# so the skill never breaks and the skill stays shareable with people who haven't
# configured Drive.

# --- config (edit these to taste) ---
REMOTE="gdrive"            # the rclone remote name you create in `rclone config`
DRIVE_FOLDER="Daily Log"   # destination folder inside your Google Drive
UPLOAD_MD=false            # Drive gets the PDF only. Set true to also upload the .md.
KEEP_LOCAL_PDF=false       # keep only the .md on disk: delete the local PDF after a successful upload.

FILE="${1:-}"

if [ -z "$FILE" ] || [ ! -f "$FILE" ]; then
  echo "[wong upload] no file given or file missing — skipping upload"
  exit 0
fi

if ! command -v rclone >/dev/null 2>&1; then
  echo "[wong upload] rclone not installed — skipping upload."
  echo "                   To enable: brew install rclone && rclone config (remote name: ${REMOTE})"
  exit 0
fi

if ! rclone listremotes 2>/dev/null | grep -q "^${REMOTE}:"; then
  echo "[wong upload] rclone remote '${REMOTE}' not configured — skipping upload."
  echo "                   To enable: run 'rclone config' and create a Google Drive remote named '${REMOTE}'."
  exit 0
fi

# `rclone copy` re-uploads when the local file is newer, so re-running the skill
# (the additive/append flow) keeps the Drive copy in sync without duplicates.
_upload() {
  if rclone copy "$1" "${REMOTE}:${DRIVE_FOLDER}"; then
    echo "[wong upload] uploaded ${REMOTE}:${DRIVE_FOLDER}/$(basename "$1")"
    return 0
  else
    echo "[wong upload] upload failed for $(basename "$1") (rclone error above) — local file unaffected"
    return 1
  fi
}

# The phone-readable PDF (rendered next to the .md by render_pdf.sh), if present.
PDF="${FILE%.md}.pdf"
pdf_uploaded=false
if [ -f "$PDF" ]; then
  _upload "$PDF" && pdf_uploaded=true
fi

# The raw markdown source — only if explicitly enabled (default: PDF only on Drive).
if [ "$UPLOAD_MD" = true ]; then
  _upload "$FILE"
fi

# Keep only the .md locally: remove the PDF once it's safely on Drive.
if [ "$KEEP_LOCAL_PDF" != true ] && [ "$pdf_uploaded" = true ]; then
  rm -f "$PDF" && echo "[wong upload] removed local PDF (kept the .md only)"
fi
exit 0
