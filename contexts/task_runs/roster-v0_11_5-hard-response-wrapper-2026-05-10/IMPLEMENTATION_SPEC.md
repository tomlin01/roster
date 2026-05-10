# Implementation Spec

Task ID: `roster-v0_11_5-hard-response-wrapper-2026-05-10`

## Required Behavior

For non-trivial explicit Roster invocation, ordinary replies must include:

```text
本次啟用：...
目前階段：...
useful work
本次分工執行：...
最後收斂：...
```

Before sending, Roster should silently check for those five parts. If any are
missing, rewrite the reply before sending.

## Internal Diagnostics Barrier

Ordinary replies must not mention:

- route check
- packet-route
- artifact-harness
- preference / roster_preferences
- registry
- routing score
- CAP
- runtime adapter
- control plane

Use these terms only in review, debug, implementation, or explicit routing
explanation mode.

## Files To Update

- `skills/roster/SKILL.md`
- `plugins/roster/commands/roster.md`
- `README.md`
- `contexts/artifact_harness_usage_experience/README.md`
- `contexts/artifact_harness_usage_experience/README.target-user-experience.draft.md`
- `contexts/artifact_harness_usage_experience/ROSTER_MILESTONE_ROADMAP.md`
- `contexts/artifact_harness_usage_experience/ROSTER_V0_11_5_HARD_RESPONSE_WRAPPER.md`
- focused tests or audits in `scripts/test_system_hub.py` if useful

## Verification

Run:

```sh
python3 -m py_compile scripts/system_hub.py scripts/test_system_hub.py
python3 scripts/test_system_hub.py
git diff --check
```

Text audit:

- v0.11.5 docs mention the hard response gate.
- examples include `本次啟用`, `目前階段`, `本次分工執行`, and `最後收斂`.
- ordinary-response examples do not expose internal route/preference/packet
  diagnostics.
