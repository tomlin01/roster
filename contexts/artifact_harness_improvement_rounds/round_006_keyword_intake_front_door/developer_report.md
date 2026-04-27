# Developer Report

## Round Metadata

- round: `round_006_keyword_intake_front_door`
- prompt file: `contexts/artifact_harness_improvement_rounds/round_006_keyword_intake_front_door/prompt.md`
- developer: `Codex`
- date: `2026-04-27`
- branch or worktree: current dirty worktree, no staging
- related artifacts:
  - `contexts/artifact_harness_improvement_rounds/round_006_keyword_intake_front_door/verification.md`

## Findings Addressed

- Upgraded `packet-route` from a single Artifact Harness keyword matcher into a deterministic front-door router.
- `packet-route` now reads registered `aliases` and all `keyword_families` from `contexts/team_alias_registry.json`; TOML Artifact Harness keywords remain config-level additions.
- Added optional `packet-route --id <packet-id>` for existing-run downstream routing.
- JSON output now includes `recognized_front_doors`, `candidate_routes`, `recommended_route`, `recommended_command`, `create_allowed`, `chain_start`, `handoff_target`, `refused`, `reason`, and explicit boundary notes while preserving legacy `route`, `matched_keywords`, and `command` fields.
- Artifact-production requests remain SPEC-first even when the utterance names `HR`, `Team Architect`, `CAP`, or runtime mapping.
- HR-only staffing or role-design requests route to `human_resources`, set `create_allowed=false`, emit no Artifact Harness create command, and do not write packet runs.
- Direct downstream requests without an existing packet id route back to the SPEC-first chain and do not allow `--create` unless there is artifact-production intent.
- Existing-run downstream requests with `--id` route to safe inspection commands:
  - CAP / Team Architect: `artifact-harness resume ... --json`
  - runtime mapping: `artifact-harness runtime-check ... --json`
- `--create` now writes a packet chain only when the recommended route is `artifact_harness_workflow` and `create_allowed=true`; otherwise it returns parseable refusal JSON.
- Commands emitted in JSON/Markdown use absolute `brain.sh` paths.
- Route output explicitly states that routing is advisory unless `--create` writes a packet chain, and that it does not approve capabilities, execute runtime adapters, accept artifacts, or move ownership boundaries.
- Follow-up review fix: keyword and alias matching is now boundary-aware, so short aliases such as `HR` match standalone phrases like `HR, ...` and `ask HR ...` but do not match inside ordinary words such as `through`.
- Added regression coverage for `walk me through runtime mapping` and `walk through the requirement form`; both avoid the false `human_resources` front door, while preserving runtime-mapping and requirement-form routing.

## Changed Files

- `scripts/system_hub.py`
- `scripts/test_system_hub.py`
- `README.md`
- `AGENTS.md`
- `policy/NAMED_TEAM_ALIAS_ROUTING_V0.md`
- `contexts/artifact_harness_improvement_rounds/round_006_keyword_intake_front_door/developer_report.md`
- `contexts/artifact_harness_improvement_rounds/round_006_keyword_intake_front_door/verification.md`

## Generated Artifacts

- `/var/folders/_s/p_gdfcgs2_s4dd0rgz1sk1wc0000gn/T/codex-cns-r006-routes-9ui1fdgt/`
  - temporary
  - ignore
  - temp route smoke workspace with one created Artifact Harness packet run for `fill requirement form for methods appendix`
- `/var/folders/_s/p_gdfcgs2_s4dd0rgz1sk1wc0000gn/T/codex-cns-r006-boundary-smoke-7kt5suxk/`
  - temporary
  - ignore
  - temp route smoke workspace for the follow-up HR false-positive regression
- `contexts/artifact_harness_improvement_rounds/round_006_keyword_intake_front_door/developer_report.md`
  - durable
  - review
- `contexts/artifact_harness_improvement_rounds/round_006_keyword_intake_front_door/verification.md`
  - durable
  - review

No durable artifact-harness packet runs were left under the `codex-cns` repo-local `contexts/` directory.

## Verification Commands

- command: `python3 -m py_compile scripts/system_hub.py scripts/test_system_hub.py`
  - cwd: `/Users/tom/Documents/PHD/codex-cns`
  - result: passed
  - notes: syntax check for route implementation and tests
- command: `python3 scripts/test_system_hub.py`
  - cwd: `/Users/tom/Documents/PHD/codex-cns`
  - result: passed
  - notes: output ended with `system hub test harness checks passed`; includes the follow-up boundary regression tests
- command: temp workspace Prompt6 route smoke
  - cwd: `/Users/tom/Documents/PHD/codex-cns`
  - result: passed
  - notes: covered HR artifact, HR-only, requirement-form create, Team Architect artifact, CAP artifact, runtime mapping downstream-only, unmatched utterance, HR-only `--create` refusal, and absolute command shape
- command: temp workspace follow-up boundary smoke
  - cwd: `/Users/tom/Documents/PHD/codex-cns`
  - result: passed
  - notes: `walk me through runtime mapping` recognized only `runtime_mapping` with `create_allowed=false`; `walk through the requirement form` recognized `artifact_harness_workflow` with `create_allowed=true`; neither recognized `human_resources`
- command: `find contexts -maxdepth 3 \( -path '*artifact_harness_runs*' -o -name 'artifact_harness_registry.json' \) -print`
  - cwd: `/Users/tom/Documents/PHD/codex-cns`
  - result: passed
  - notes: no repo-local artifact-harness packet output was found

## Known Non-Goals

- did not start Prompt 7
- did not implement automatic global CLI/GUI phrase interception
- did not add a server, daemon, database, orchestration UI, or dependency
- did not run external runtime adapters or implement runtime execution
- did not rename packet files
- did not make HR, Team Architect, CAP, or runtime mapping own upstream/downstream responsibilities

## Remaining Risks

- Routing remains deterministic keyword matching. It is stable and agent-readable, but it is not a natural-language classifier.
- TOML-level Artifact Harness keywords can still add broad hints; downstream-family keyword collisions are filtered when matching config additions, but future config edits should keep front-door specificity in mind.
- HR route output remains advisory because this repo does not yet expose a separate executable HR packet command.
- Existing-run downstream routing checks the run exists and emits safe commands, but does not inspect whether downstream packet fields are complete.
- Boundary-aware matching is still deterministic keyword matching, not semantic routing; future aliases should avoid overly broad registered phrases.

## Notes For Reviewer

- Review the diff directly; do not rely only on this report.
- Rerun the necessary tests when possible.
- Inspect JSON output for the Prompt6 route cases, especially HR-only `--create` refusal, runtime mapping downstream-only behavior, and the `HR`/`through` false-positive regression.
