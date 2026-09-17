#!/usr/bin/env bash
# Abort commit if any staged (added/copied/modified) file contains an OpenRouter key.
cd "$(git rev-parse --show-toplevel)"
files=$(git diff --cached --name-only --diff-filter=ACM)
[ -z "$files" ] && exit 0
hits=$(echo "$files" | while IFS= read -r f; do [ -f "$f" ] && grep -lE 'sk-or-v1-[0-9a-f]{20,}' "$f"; done)
if [ -n "$hits" ]; then echo "$hits"; echo "SECRET FOUND in staged files above — aborting" >&2; exit 1; fi
exit 0
