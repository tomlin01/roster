## Prompt 2: Roster Alias And Route Execution

```text
Implement executable Roster routing while preserving existing behavior.

Goal:
Add `Roster` / `@roster` / `PM` as user-facing route aliases that can reach the
artifact-production front door, without making HR own project coordination or
tool authorization.

Files likely in scope:
- contexts/team_alias_registry.json
- policy/system_hub.toml
- scripts/system_hub.py
- scripts/test_system_hub.py
- README.md / AGENTS.md only for current accurate usage notes

Requirements:
- `Roster` and `@roster` route to the same high-level artifact coordination
  surface.
- `PM` is accepted as a natural alias if unambiguous.
- `HR` remains staffing/role-design only.
- Artifact-production requests remain SPEC-first.
- CAP remains tool/plugin/approval/runtime allowlist only.
- Runtime adapter remains execution layer only.
- Routing should work from another workspace and write packets under the target
  workspace.
- JSON output should be parseable for route hit, miss, create, and refusal.

Tests:
- route hit: `@roster 幫我把這個 slide 任務安排好`
- route hit: `Roster, set up the team and task boundary for this artifact`
- route hit: `PM, organize this artifact task`
- HR-only request does not create artifact packet chain
- CAP request does not become a project owner
- miss/refusal remains structured JSON

Verification:
- python3 -m py_compile scripts/system_hub.py scripts/test_system_hub.py
- python3 scripts/test_system_hub.py
- existing overlay/benchmark tests if touched
- no durable smoke output left under repo contexts/
```
