# Developer Report

## Round Metadata

- round: `round_003_replay_evidence_lane`
- prompt file: `contexts/artifact_harness_improvement_rounds/round_003_replay_evidence_lane/prompt.md`
- developer: `Codex`
- date: `2026-04-27`
- branch or worktree: current dirty worktree, no staging
- related artifacts:
  - `contexts/artifact_harness_improvement_rounds/round_003_replay_evidence_lane/verification.md`
  - `/Users/tom/Documents/PHD/Vis_Math/Slides/Lecture1/contexts/artifact_harness_runs/vis-math-lecture1-team-smoke/artifact_replay_evidence.json`

## Findings Addressed

- Added `artifact-harness replay --path <workspace> --id <packet-id> [--json]`.
- Replay inspects an existing packet run, lifecycle sidecar, manifest, registry,
  and packet files without invoking an agent, executing runtime, approving
  capabilities, or accepting the artifact.
- Replay writes
  `contexts/artifact_harness_runs/<packet-id>/artifact_replay_evidence.json`
  inside the target workspace packet run directory.
- Replay JSON includes `id`, mission, `target_path`, `run_dir`, `manifest`,
  `status`, registry lifecycle status, packet summaries, `evidence_path`,
  `refused`, and `reason`.
- Evidence records practical completion heuristics:
  packet presence, line/byte counts, visible open-question markers, empty
  Markdown bullet fields, placeholder marker counts, and a heuristic completion
  state.
- Missing packet runs return non-zero with structured JSON under `--json`.
- Replay does not rewrite packet Markdown; regression and smoke checks preserve
  explicit sentinel text.
- A real Vis_Math Lecture1 smoke run was created and replayed at the prompt's
  target workspace using packet id `vis-math-lecture1-team-smoke`.
- Follow-up review found and fixed a P1 manifest read boundary issue:
  lifecycle commands now refuse manifest-derived packet paths outside the
  target workspace before replay/status/resume expose or read them.
- The structured refusal reason is
  `manifest_packet_path_outside_target_workspace`, with
  `offending_packet_key` and `attempted_path`; replay does not rewrite existing
  evidence on this refusal path.

## Changed Files

- `scripts/system_hub.py`
- `scripts/test_system_hub.py`
- `README.md`
- `AGENTS.md`
- `policy/ARTIFACT_HARNESS_WORKFLOW_V0.md`
- `contexts/artifact_harness_improvement_rounds/round_003_replay_evidence_lane/developer_report.md`
- `contexts/artifact_harness_improvement_rounds/round_003_replay_evidence_lane/verification.md`

## Generated Artifacts

- `/Users/tom/Documents/PHD/Vis_Math/Slides/Lecture1/contexts/artifact_harness_runs/vis-math-lecture1-team-smoke/`
  - durable
  - review
  - allowed by the Round 003 prompt as the real replay smoke target
- `/Users/tom/Documents/PHD/Vis_Math/Slides/Lecture1/contexts/artifact_harness_runs/vis-math-lecture1-team-smoke/artifact_replay_evidence.json`
  - durable
  - review
  - replay evidence for the real Vis_Math smoke
- `/Users/tom/Documents/PHD/Vis_Math/Slides/Lecture1/contexts/artifact_harness_registry.json`
  - durable
  - review
  - updated with the new `vis-math-lecture1-team-smoke` packet run
- `contexts/artifact_harness_improvement_rounds/round_003_replay_evidence_lane/developer_report.md`
  - durable
  - review
- `contexts/artifact_harness_improvement_rounds/round_003_replay_evidence_lane/verification.md`
  - durable
  - review
- temp artifact-harness smoke workspace:
  - `/tmp/codex-cns-round003.sbsQNQ/target`
  - temporary
  - can be ignored or removed

No durable artifact-harness packet runs were left under the `codex-cns`
repo-local `contexts/` directory.

## Verification Commands

- command: `python3 -m py_compile scripts/system_hub.py scripts/test_system_hub.py`
  - cwd: `/Users/tom/Documents/PHD/codex-cns`
  - result: passed
  - notes: syntax check for replay implementation and regression tests
- command: `python3 scripts/test_system_hub.py`
  - cwd: `/Users/tom/Documents/PHD/codex-cns`
  - result: passed
  - notes: output ended with `system hub test harness checks passed`
- command: regression for manifest packet path boundary
  - cwd: `/Users/tom/Documents/PHD/codex-cns`
  - result: passed
  - notes: corrupting manifest `artifact_harness_spec` to `../outside_secret.md` makes replay and status fail non-zero with `reason=manifest_packet_path_outside_target_workspace`, without leaking outside file content or rewriting existing replay evidence
- command: independent reviewer temp reproduction for manifest packet path boundary
  - cwd: `/Users/tom/Documents/PHD/codex-cns`
  - result: passed
  - notes: `boundary_refusal_ok`; temp workspace `/tmp/codex-cns-review-r003-boundary-post.Lh8dG9`
- command: temp-workspace `artifact-harness replay --json | python3 -m json.tool`
  - cwd: `/tmp/codex-cns-round003.sbsQNQ/cwd`
  - result: passed
  - notes: replay JSON parsed, wrote `artifact_replay_evidence.json`, and reported `status=draft`, `registry_status=draft`, mission, packet presence, and open-field heuristics
- command: temp-workspace sentinel preservation check
  - cwd: `/Users/tom/Documents/PHD/codex-cns`
  - result: passed
  - notes: `SENTINEL_ROUND003_REPLAY_NO_REWRITE` remained in `artifact_harness_spec.md` after replay
- command: temp-workspace missing-run replay refusal
  - cwd: `/tmp/codex-cns-round003.sbsQNQ/cwd`
  - result: passed
  - notes: command returned code `1`; JSON stdout was parseable and reported `refused=true`, `reason=missing_packet_run`, and an attempted `evidence_path`
- command: Vis_Math Lecture1 scaffold smoke
  - cwd: `/Users/tom/Documents/PHD/codex-cns`
  - result: passed
  - notes: created `vis-math-lecture1-team-smoke` under `/Users/tom/Documents/PHD/Vis_Math/Slides/Lecture1/contexts/artifact_harness_runs/`
- command: Vis_Math Lecture1 replay smoke
  - cwd: `/Users/tom/Documents/PHD/codex-cns`
  - result: passed
  - notes: replay wrote `artifact_replay_evidence.json`; JSON parsed with `status=draft`, `registry_status=draft`, `existing_packet_count=7`, and `heuristic_open_items_total=170`
- command: `python3 -m json.tool /Users/tom/Documents/PHD/Vis_Math/Slides/Lecture1/contexts/artifact_harness_runs/vis-math-lecture1-team-smoke/artifact_replay_evidence.json`
  - cwd: `/Users/tom/Documents/PHD/codex-cns`
  - result: passed
  - notes: persisted real smoke evidence is valid JSON
- command: non-reference Markdown link check
  - cwd: `/Users/tom/Documents/PHD/codex-cns`
  - result: passed
  - notes: `missing=0 files_checked=70`
- command: `find contexts -maxdepth 3 \( -path '*artifact_harness_runs*' -o -name 'artifact_harness_registry.json' \) -print`
  - cwd: `/Users/tom/Documents/PHD/codex-cns`
  - result: passed
  - notes: no repo-local artifact-harness packet output remained

## Known Non-Goals

- did not start Prompt 4
- did not implement runtime execution
- did not implement full artifact verification or benchmark replay
- did not make replay evidence a substitute for SPEC, HR, Team Architect, CAP,
  runtime mapping, or verification/review
- did not add a server, daemon, database, or orchestration UI
- did not overwrite any existing Vis_Math packet run

## Remaining Risks

- Replay completion heuristics are intentionally simple and may overcount
  scaffold fields as open items. The evidence records the heuristic rules so
  reviewers can interpret the counts.
- Replay evidence JSON is implemented and tested but not yet a separately
  versioned schema.
- Existing older packet runs without `packet_status.json` will still fail fast
  through the lifecycle loader instead of being silently migrated.
- Replay evidence currently overwrites the latest evidence snapshot for a run;
  it does not preserve evidence revision history.

## Notes For Reviewer

- Review the diff directly; do not rely only on this report.
- Rerun the necessary tests when possible.
- Inspect the Vis_Math replay evidence, packet manifest, status sidecar,
  registry entry, and packet Markdown files before accepting this round.
