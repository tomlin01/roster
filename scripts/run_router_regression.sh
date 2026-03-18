#!/usr/bin/env bash
set -euo pipefail
CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
RUNNER="$CODEX_HOME/skills/requirement-skill-router/scripts/run_router_regression.py"
if [[ ! -f "$RUNNER" ]]; then
  echo "Runner not found: $RUNNER" >&2
  exit 2
fi
python3 "$RUNNER" "$@"
