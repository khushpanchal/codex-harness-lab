#!/usr/bin/env bash
# Abort commit if any staged file contains an OpenRouter key.
cd "$(git rev-parse --show-toplevel)"
if git diff --cached --name-only -z --diff-filter=ACM | xargs -0 grep -lE 'sk-or-v1-[0-9a-f]{20,}' 2>/dev/null; then
  echo "SECRET FOUND in staged files above — aborting" >&2; exit 1
fi
exit 0
