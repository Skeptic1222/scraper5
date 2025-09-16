#!/usr/bin/env bash
set -euo pipefail

# Safe cleanup helper for common dev/test artifacts.
# Dry-run by default: shows what would be removed. Use --apply to delete.

ROOT_PATTERNS=(
  "*.log"
  "test_results.json"
  "test_report.json"
  "accessibility_tree.json"
  "files.zip" "files2.zip"
  "*_screenshot.png"
  "actual_*.png" "actual_*.html" "actual_served.html"
  "current_splash.png" "final_splash.png" "new_splash.png" "splash_*"
  "dropdown_*.png" "verified_fix.png" "debug_screenshot.png"
)

APPLY=false
if [[ "${1:-}" == "--apply" ]]; then
  APPLY=true
fi

echo "[cleanup-artifacts] Scanning for removable artifacts in repo root..."

TO_REMOVE=()
for pat in "${ROOT_PATTERNS[@]}"; do
  while IFS= read -r -d '' f; do
    TO_REMOVE+=("$f")
  done < <(find . -maxdepth 1 -type f -name "$pat" -print0)
done

if [[ ${#TO_REMOVE[@]} -eq 0 ]]; then
  echo "No matching artifacts found."
  exit 0
fi

echo "Found ${#TO_REMOVE[@]} file(s):"
for f in "${TO_REMOVE[@]}"; do
  echo "  - $f"
done

if $APPLY; then
  echo "\nDeleting files..."
  for f in "${TO_REMOVE[@]}"; do
    rm -f -- "$f"
  done
  echo "Done."
else
  echo "\nDry run. Pass --apply to delete."
fi

