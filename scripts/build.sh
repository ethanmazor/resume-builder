#!/usr/bin/env bash
# build.sh — compile a resume .tex with Tectonic and verify it is one page.
#
# Usage: scripts/build.sh resumes/{slug}/resume.tex
#
# Compiles the given .tex into the same folder and prints the page count.
# Exits non-zero (and warns) if the PDF is not exactly one page, so the agent
# knows it must trim and recompile.

set -euo pipefail

TEX="${1:-}"
if [[ -z "$TEX" ]]; then
  echo "Usage: $0 path/to/resume.tex" >&2
  exit 2
fi
if [[ ! -f "$TEX" ]]; then
  echo "Error: file not found: $TEX" >&2
  exit 2
fi

# Preflight
for tool in tectonic pdfinfo; do
  if ! command -v "$tool" >/dev/null 2>&1; then
    echo "Error: '$tool' not found. Install with: brew install tectonic poppler" >&2
    exit 3
  fi
done

OUTDIR="$(dirname "$TEX")"

echo ">> Compiling $TEX with Tectonic..."
tectonic --keep-logs --outdir "$OUTDIR" "$TEX"

PDF="${OUTDIR}/$(basename "${TEX%.tex}").pdf"
if [[ ! -f "$PDF" ]]; then
  echo "Error: expected PDF not produced: $PDF" >&2
  exit 4
fi

PAGES="$(pdfinfo "$PDF" | awk '/^Pages:/ {print $2}')"
echo ">> Output: $PDF"
echo ">> Pages: $PAGES"

if [[ "$PAGES" != "1" ]]; then
  echo "!! NOT ONE PAGE ($PAGES). Trim content per the style guide and recompile." >&2
  exit 1
fi

echo ">> OK: one page."
