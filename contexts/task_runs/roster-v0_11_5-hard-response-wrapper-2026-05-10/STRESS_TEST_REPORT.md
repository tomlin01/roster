# Stress Test Report

Task ID: `roster-v0_11_5-hard-response-wrapper-2026-05-10`

## Summary

The v0.11.5 response contract needed multiple loops before it became stable
enough for a fresh CLI start.

Final accepted evidence:

- `cli_stress_outputs_round3/`: five independent fresh `codex exec
  --ephemeral` sessions all passed the final-answer gate.
- `cli_stress_outputs_round6/prompt1.md`: a repeated high-risk creative
  planning prompt passed after the repo-level visible-response guard and
  literal `role-agents` wording were added.

## Initial Failures

Round 1/2 failures showed that ordinary Roster answers were still behaving like
generic assistant replies:

- missing `本次啟用`
- missing `本次分工執行`
- missing `最後收斂`
- occasional visible leakage of route/packet/preference diagnostics
- `未來` / `之後` artifact wording was too easy to treat as preference memory

## Fixes From The Loop

- Moved the hard response wrapper to the top of the Roster skill and plugin
  command.
- Added metadata-level wording so the installed skill/plugin advertise that
  ordinary Roster replies begin with `本次啟用` and do not expose internals.
- Added a repo-level `Roster v0.11.5 Visible Response Guard` in `AGENTS.md` so
  fresh starts in this repo know the visible pre-tool status must also avoid
  internal diagnostics.
- Tightened preference-memory detection so ordinary future-artifact wording
  such as `未來可能` or `之後可能` does not route to preference memory.
- Required the first line to use literal `agent` or `role-agents`, not only
  generic `角色`, `小組`, `視角`, or `流程`.

## Accepted Gate

For the final accepted fresh-output scan, the saved answer had:

- first line: `本次啟用：4 個 role-agents...`
- `目前階段`
- useful planning work
- `本次分工執行`
- `最後收斂`
- no saved-final matches for `route check`, `packet-route`, `artifact-harness`,
  `preference`, `roster_preferences`, `registry`, `CAP`, `runtime adapter`,
  `control plane`, `路由檢查`, `不建 packet`, `偏好記憶`, `任務表單`, or `控制面`

## Commands

```sh
python3 -m py_compile scripts/system_hub.py scripts/test_system_hub.py
git diff --check
python3 scripts/test_system_hub.py
./scripts/brain.sh roster-install --codex-home /Users/tom/.codex --force --json
codex exec --ephemeral -C /Users/tom/Documents/PHD/codex-cns -s read-only --output-last-message <round-output> '<stress prompt>'
```

Observed CLI:

```text
codex-cli 0.125.0
```

The CLI emitted `unknown feature key in config: goals`; that is an environment
warning and not a Roster behavior failure.

## Remaining Risk

This is still instruction-level behavior, not a runtime formatter. The tested
fresh starts now pass the saved-final response gate, and the repo-level guard
reduced visible pre-tool leakage in this repo. A host or workspace that does not
load the repo `AGENTS.md` may still depend on the installed skill/plugin
metadata and body.
