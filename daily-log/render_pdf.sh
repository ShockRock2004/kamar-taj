#!/usr/bin/env bash
# Render a daily-log markdown file to a phone-friendly PDF.
#   markdown --(marked)--> styled HTML --(headless Chrome)--> PDF
#
# Needs Node/npx (for `marked`) and a Chrome-like browser (for print-to-pdf).
# Both are common on macOS. SAFE NO-OP (exit 0) if either is missing, so the
# skill never breaks and stays shareable.
#
# Usage:  render_pdf.sh "/path/to/<file>.md"
#         -> creates "/path/to/<file>.pdf" and prints its path.

MD="${1:-}"
if [ -z "$MD" ] || [ ! -f "$MD" ]; then
  echo "[daily-log pdf] no markdown file given — skipping PDF"
  exit 0
fi

# Find a Chromium-based browser that can print to PDF.
CHROME=""
for b in \
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser" \
  "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge" \
  "/Applications/Chromium.app/Contents/MacOS/Chromium"; do
  [ -x "$b" ] && { CHROME="$b"; break; }
done

if ! command -v npx >/dev/null 2>&1; then
  echo "[daily-log pdf] node/npx not found — skipping PDF (install Node to enable)"
  exit 0
fi
if [ -z "$CHROME" ]; then
  echo "[daily-log pdf] no Chrome-like browser found — skipping PDF"
  exit 0
fi

PDF="${MD%.md}.pdf"
TMPHTML="$(mktemp -t daily-log-XXXX).html"
TMPPROFILE="$(mktemp -d -t daily-log-prof-XXXX)"

# 1) markdown -> HTML fragment (marked enables GitHub-flavored markdown by default:
#    fenced code blocks, tables, etc.). First run downloads marked into the npx cache.
BODY="$(npx -y marked -i "$MD" 2>/dev/null)"
if [ -z "$BODY" ]; then
  echo "[daily-log pdf] markdown->HTML conversion failed — skipping PDF"
  rm -rf "$TMPHTML" "$TMPPROFILE"
  exit 0
fi

# 2) Wrap in a phone-friendly styled HTML document. Narrow page + wrapping code
#    blocks so it reads comfortably on a phone with minimal pinch-zooming.
cat > "$TMPHTML" <<HTMLDOC
<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
  /* Dark theme (Tailwind slate), small type for phone reading. margin:0 + body
     padding so the dark background fills the whole page edge to edge. */
  @page { size: 6in 9in; margin: 0; }
  html, body { background: #0f172a; }  /* slate-900 */
  html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  body { font-family: -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
         font-size: 9.5pt; line-height: 1.55; color: #cbd5e1; /* slate-300 */
         padding: 12mm 11mm; word-wrap: break-word; }
  h1 { font-size: 16pt; color: #f8fafc; border-bottom: 1px solid #334155; padding-bottom: .2em; line-height: 1.25; }
  h2 { font-size: 12.5pt; color: #f1f5f9; margin-top: 1.4em; border-bottom: 1px solid #1e293b; padding-bottom: .15em; }
  h3 { font-size: 10.5pt; color: #e2e8f0; margin-top: 1.1em; }
  p, li { font-size: 9.5pt; }
  strong { color: #f1f5f9; }
  a { color: #38bdf8; text-decoration: none; word-break: break-all; }  /* sky-400 */
  code { font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
         background: #1e293b; color: #e2e8f0; padding: .1em .35em; border-radius: 4px; font-size: 86%; }
  pre { background: #020617; border: 1px solid #334155; border-radius: 8px; padding: 10px;
        white-space: pre-wrap; word-break: break-word; overflow-wrap: anywhere; font-size: 8pt; line-height: 1.45; }
  pre code { background: none; color: #e2e8f0; padding: 0; font-size: inherit; }
  blockquote { margin: .8em 0; padding: .4em .9em; border-left: 3px solid #6366f1;
               background: #1e293b; color: #cbd5e1; border-radius: 0 6px 6px 0; }
  hr { border: none; border-top: 1px solid #334155; margin: 1.5em 0; }
  table { border-collapse: collapse; width: 100%; font-size: 8.5pt; }
  th, td { border: 1px solid #334155; padding: 5px 7px; text-align: left; }
  th { background: #1e293b; color: #f1f5f9; }
  img { max-width: 100%; }
</style></head><body>
$BODY
</body></html>
HTMLDOC

# 3) HTML -> PDF via headless Chrome (own temp profile to avoid clashing with an
#    already-open Chrome window).
"$CHROME" --headless=new --disable-gpu --no-pdf-header-footer \
  --user-data-dir="$TMPPROFILE" \
  --print-to-pdf="$PDF" "file://$TMPHTML" >/dev/null 2>&1

rm -rf "$TMPHTML" "$TMPPROFILE"

if [ -f "$PDF" ]; then
  echo "[daily-log pdf] rendered $PDF"
else
  echo "[daily-log pdf] PDF render failed — skipping (markdown is unaffected)"
fi
exit 0
