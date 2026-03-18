#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
GLOBAL_RUNNER="$CODEX_HOME/agent_policy/run_agent_benchmark.py"
SELF_RUNNER="$SCRIPT_DIR/run_agent_benchmark.py"
LOCAL_RUNNER="$ROOT_DIR/scripts/run_agent_benchmark.py"

if [[ -f "$GLOBAL_RUNNER" ]]; then
  python3 "$GLOBAL_RUNNER" "$@"
  exit 0
fi

if [[ -f "$SELF_RUNNER" ]]; then
  python3 "$SELF_RUNNER" "$@"
  exit 0
fi

python3 "$LOCAL_RUNNER" "$@"
