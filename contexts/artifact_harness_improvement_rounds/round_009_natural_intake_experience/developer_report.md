# Developer Report

## Round Metadata

- round: `round_009_natural_intake_experience`
- prompt file: `contexts/artifact_harness_improvement_rounds/round_009_natural_intake_experience/prompt.md`
- developer: `Codex`
- date: `2026-04-28`
- branch or worktree: current dirty worktree, no staging
- related artifacts:
  - `contexts/artifact_harness_improvement_rounds/round_009_natural_intake_experience/verification.md`
  - `contexts/artifact_harness_improvement_rounds/round_009_natural_intake_experience/reviewer_notes.md`

## Findings Addressed

- Added a conservative natural artifact-mission intake layer to `packet-route`.
- Natural routing now recognizes deterministic deliverable plus action/quality/process cues without requiring internal keywords such as `Artifact Harness` or `requirement form`.
- Plain artifact-production phrases such as `make a review-ready methods appendix`, `make this lecture slide task organized`, and `幫我整理這個投影片任務` now route to `artifact_harness_workflow`.
- Underspecified references such as `can you help with this artifact?` are recognized as artifact hints but set `needs_clarification=true`, return clarification questions, refuse `--create`, and do not write packet output.
- JSON output preserves Round 006 keys and adds:
  - `user_intent`
  - `confidence`
  - `needs_clarification`
  - `clarifying_questions`
  - `natural_triggers`
  - `next_step_label`
  - `user_message`
  - `visible_next_action`
- Markdown output keeps `# Packet Route` for compatibility, but now presents a human-facing `## Next Step` section before internal route details.
- HR-only routing remains HR-only; downstream-only runtime mapping remains non-create-ready.
- Commands emitted by the route remain absolute `brain.sh` commands.
- README, AGENTS, and named-team routing policy now document natural intake as deterministic, explicit, and advisory unless `--create` writes forms.

## Changed Files

- `scripts/system_hub.py`
- `scripts/test_system_hub.py`
- `README.md`
- `AGENTS.md`
- `policy/NAMED_TEAM_ALIAS_ROUTING_V0.md`
- `contexts/artifact_harness_improvement_rounds/round_009_natural_intake_experience/prompt.md`
- `contexts/artifact_harness_improvement_rounds/round_009_natural_intake_experience/developer_report.md`
- `contexts/artifact_harness_improvement_rounds/round_009_natural_intake_experience/verification.md`
- `contexts/artifact_harness_improvement_rounds/round_009_natural_intake_experience/reviewer_notes.md`

## Generated Artifacts

- Temporary route smoke workspaces under `/var/folders/.../tmp.*`
  - used for natural route hit, underspecified refusal, Chinese route hit, and temp `--create` smoke
  - removed after the smoke commands
- No durable `codex-cns` repo-local artifact-harness packet runs were written.
- The Vis_Math Lecture1 smoke used `/Users/tom/Documents/PHD/Vis_Math/Slides/Lecture1` with `packet-route --json` only; it did not use `--create` and did not write packet output.

## Verification Commands

- command: `python3 -m py_compile scripts/system_hub.py scripts/test_system_hub.py`
  - cwd: `/Users/tom/Documents/PHD/codex-cns`
  - result: passed
- command: `python3 scripts/test_system_hub.py`
  - cwd: `/Users/tom/Documents/PHD/codex-cns`
  - result: passed
  - output summary: `system hub test harness checks passed`
- command: natural Markdown smoke for `make a review-ready methods appendix`
  - cwd: `/Users/tom/Documents/PHD/codex-cns`
  - result: passed
  - output summary: route matched, next step was user-facing, no packet output without `--create`
- command: underspecified artifact `--create --json` smoke
  - cwd: `/Users/tom/Documents/PHD/codex-cns`
  - result: passed as structured refusal
  - output summary: `reason=needs_clarification`, `recommended_command=null`, no packet output
- command: Chinese natural route smoke for `幫我整理這個投影片任務`
  - cwd: `/Users/tom/Documents/PHD/codex-cns`
  - result: passed
  - output summary: parseable JSON, `user_intent=artifact_production`, `create_allowed=true`
- command: temp workspace natural `--create --json` smoke
  - cwd: `/Users/tom/Documents/PHD/codex-cns`
  - result: passed
  - output summary: packet run created under the temp target workspace and removed with the temp directory
- command: Vis_Math Lecture1 natural route smoke
  - cwd: `/Users/tom/Documents/PHD/codex-cns`
  - result: passed
  - output summary: parseable JSON, `recommended_route=artifact_harness_workflow`, `create=false`
- command: non-reference Markdown link check
  - cwd: `/Users/tom/Documents/PHD/codex-cns`
  - result: passed
  - output summary: `missing=0 files_checked=97`
- command: `find contexts -maxdepth 3 \( -path '*artifact_harness_runs*' -o -name 'artifact_harness_registry.json' \) -print`
  - cwd: `/Users/tom/Documents/PHD/codex-cns`
  - result: passed
  - output summary: command returned empty

## Known Non-Goals

- did not start Prompt 10
- did not stage files
- did not add an LLM classifier or fuzzy semantic router
- did not implement automatic interception of arbitrary Codex GUI/CLI phrases
- did not add a server, daemon, database, orchestration UI, or dependency
- did not run external runtime adapters
- did not weaken rerun guards, path guards, schema-check/migrate behavior, approval evidence behavior, or runtime invocation dry-run behavior

## Remaining Risks

- Natural intake remains deterministic heuristics, not broad semantic understanding.
- The term lists are intentionally conservative and will need tuning as real artifact tasks expose misses or false positives.
- User-facing messages are more natural than before, but still reveal internal route details later in the Markdown output for reviewer/debug use.
