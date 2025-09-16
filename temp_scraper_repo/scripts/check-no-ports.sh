#!/usr/bin/env bash
set -euo pipefail

# Check staged app files for disallowed port usage in URLs.
# Allowed: config files (web.config*, *.ps1) and docs are ignored by default.

shopt -s nullglob

echo "[check-no-ports] Scanning staged files for ported URLs..."
STRICT_DOCS=${STRICT_DOCS:-1}

# Get staged files; if none, check tracked files
STAGED_FILES=$(git diff --cached --name-only || true)
if [[ -z "$STAGED_FILES" ]]; then
  FILES=$(git ls-files)
else
  FILES="$STAGED_FILES"
fi

EXIT=0
FOUND=()

while IFS= read -r file; do
  # Only scan app/source files
  case "$file" in
    *.py|*.js|*.ts|*.jsx|*.tsx|*.html|templates/*)
      # Skip known config files
      [[ "$file" == web.config* || "$file" == *.ps1 ]] && continue
      if rg -n "http://localhost:\d{2,5}|http://127\.0\.0\.1:\d{2,5}" "$file" -S > /dev/null; then
        while IFS= read -r line; do
          FOUND+=("$file:$line")
        done < <(rg -n "http://localhost:\d{2,5}|http://127\.0\.0\.1:\d{2,5}" "$file" -S)
        EXIT=1
      fi
      ;;
    *) ;;
  esac
done < <(printf "%s\n" $FILES)

if [[ $EXIT -ne 0 ]]; then
  echo "\n❌ Disallowed ported URLs detected (see CRITICAL_NO_PORTS_RULE.md):"
  for hit in "${FOUND[@]}"; do
    echo "  - $hit"
  done
  echo "\nFix: use relative paths or '/scraper' base, e.g., '/scraper/api/...'."
  exit 1
fi

# Optionally scan docs for guidance issues
DOC_HITS=()
for doc in $(git ls-files "*.md" "*.html"); do
  [[ "$doc" == web.config* ]] && continue
  # Skip matches inside fenced code blocks (``` ... ```)
  awk -v file="$doc" '
    BEGIN { inblock=0 }
    {
      line=$0
      if (match(line,/^```/)) { inblock = !inblock }
      if (!inblock) {
        if (match(line,/http:\/\/localhost:(5000|5050)/)) {
          printf("%s:%d:%s\n", file, NR, line)
        }
      }
    }
  ' "$doc" | while IFS= read -r hit; do DOC_HITS+=("$hit"); done
done

if [[ ${#DOC_HITS[@]} -gt 0 ]]; then
  echo "\n⚠️ Docs contain ported localhost URLs (advice may be outdated):"
  for hit in "${DOC_HITS[@]}"; do
    echo "  - $hit"
  done
  if [[ "$STRICT_DOCS" == "1" ]]; then
    echo "\nSTRICT_DOCS=1 set — failing commit. Update docs to use http://localhost/scraper."
    exit 1
  fi
fi

echo "[check-no-ports] OK — no ported URLs in app files."
exit 0
