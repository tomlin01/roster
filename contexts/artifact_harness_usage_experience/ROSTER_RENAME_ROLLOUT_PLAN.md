# Roster Rename Rollout Plan

This plan defines how to move the user-facing surface from the internal
`codex-cns` name toward `Roster` without breaking existing policy, paths, tests,
or historical evidence.

## Rename Goal

`Roster` should become the user-facing name for the staffing-and-coordination
surface.

Target public surfaces:

- display name: `Roster`
- current primary invocation: `Roster, ...`
- installable skill name: `roster`
- future mention target: `@roster`
- natural aliases: `Roster`, `PM`
- retained staffing alias: `HR`

The internal repo path and historical workspace identity may remain
`codex-cns` during migration.

## Safety Rule

Do not perform a global mechanical rename from `codex-cns` to `Roster`.

Separate every occurrence into one of three buckets:

- `internal identity`: repo path, owner workspace id, historical reports,
  verification logs, temporary paths, committed evidence
- `user-facing surface`: README language, invocation examples, install docs,
  usage examples, alias names
- `adapter compatibility`: CLI command names, JSON fields, config keys, route
  registries, tests

Only `user-facing surface` should move first.

`adapter compatibility` should add `Roster` aliases while keeping old names
working until a migration is explicitly accepted.

`internal identity` should not be renamed unless there is a separate repository
rename plan.

## Phases

### Phase 0: Inventory

Goal: classify naming occurrences before editing.

Required actions:

- Run `rg` for `codex-cns`, `codex`, `Project Office`, `@project-office`,
  `@roster`, `Roster`, `PM`, and `HR`.
- Label each occurrence as internal identity, user-facing surface, adapter
  compatibility, or historical evidence.
- Do not modify historical improvement-round reports except to add new notes.

Acceptance:

- There is an inventory table or summary that explains what will and will not be
  renamed.
- No code or docs are changed in this phase unless the inventory document itself
  is updated.

### Phase 1: User-Facing Docs

Goal: make human-facing docs consistently describe `Roster`.

Required actions:

- Update target README draft to use `Roster, ...` as the current path and
  `@roster` as a future install target only.
- Update target README instruction to use `Roster, ...` as the current path and
  `@roster` as a future install target only.
- Keep historical `codex-cns` references only where they describe the current
  repo or past evidence.
- Keep CLI commands in reviewer/debug sections, not basic usage.

Acceptance:

- A human can tell within the first screen that they should type `Roster,
  <task>` in ordinary Codex chat.
- No `@codex-*` or `@project-*` invocation remains in target user-facing docs,
  except rejected-candidate notes.

### Phase 2: Alias And Routing Surface

Goal: make `Roster` executable without breaking existing routes.

Required actions:

- Add `Roster`, `@roster`, and `PM` keyword families to alias/routing config.
- Preserve `HR` as staffing-only.
- Preserve Artifact Harness / Team Architect / CAP / runtime mapping routing.
- Ensure `Roster` routes to the artifact-production front door only when the
  request is artifact-production oriented.
- Ensure `HR` alone does not become a project-management owner.

Acceptance:

- `Roster` / `@roster` route checks work.
- `HR` staffing-only route still works and does not generate a packet chain
  unless artifact-production intent is present.
- Tests cover Chinese and English examples.

### Phase 3: Install And Invocation Layer

Goal: make `roster` skill install/register semantics real while keeping
`@roster` as a future target until Codex mention registration is verified.

Required actions:

- Define the smallest install/register mechanism supported by current Codex
  CLI/GUI.
- Do not claim custom `@` or `/` behavior until verified.
- If a skill/plugin/app mention is used, document the exact installed name.
- Current minimum accepted install surface is the repo-owned `roster` skill.
- Keep `brain.sh` and JSON commands as internal adapters.
- Do not add a persistent server, daemon, database, or hidden control plane.

Acceptance:

- A fresh Codex thread can intentionally call the surface without embedding
  `HR`, `CAP`, or another keyword in the message body.
- If `@roster` is not the verified invocation name, docs use the verified name
  and keep `@roster` as the future target only.

### Phase 4: Cross-Machine Health Check

Goal: make portability and LLM attachment verifiable.

Required actions:

- Add or document a health check that verifies:
  - invocation surface visibility
  - packet output under the target workspace
  - LLM/provider path or structured missing-auth / missing-provider diagnostics
  - no server/daemon/control-plane dependency
- Keep secrets out of repo artifacts.
- State which setup is repo-portable and which setup is machine-local.

Acceptance:

- A fresh-machine simulation or real second-machine run proves the setup can be
  reconstructed from repo artifacts plus local credentials.
- Missing credentials fail with actionable diagnostics.

### Phase 5: Root README Promotion

Goal: turn the target README draft into the live root README only after the
surface is real enough.

Required actions:

- Compare root `README.md` against
  `contexts/artifact_harness_usage_experience/README.target-user-experience.draft.md`.
- Promote the target shape only after the primary invocation and install/health
  checks are implemented or clearly marked as current-status limitations.
- Keep reviewer/debug commands separate from basic use.
- Link policy/template details after the human-facing path.

Acceptance:

- The root README does not advertise unverified `@`, `/`, plugin, skill, LLM, or
  install behavior as complete.
- The first screen tells a human what to type, where files go, and what outcome
  Codex should produce.

## Verification Baseline

At minimum, each implementation phase should run:

```bash
python3 -m py_compile scripts/system_hub.py scripts/test_system_hub.py
python3 scripts/test_system_hub.py
python3 scripts/test_overlay_policy.py
python3 scripts/test_run_agent_benchmark.py
```

Markdown link checks should report:

```text
missing=0
```

Smoke packet runs should use a temporary target workspace and must not leave
`contexts/artifact_harness_registry.json` or
`contexts/artifact_harness_runs/smoke-*` under the kit repo.

## Non-Goals

- no full repo rename in the first pass
- no rewrite of historical improvement-round evidence
- no server or daemon
- no hidden LLM credentials in repo files
- no collapse of HR, Team Architect, CAP, or runtime adapter ownership
