# Verification Evidence

## Round Metadata

- round: `round_003_replay_evidence_lane`
- prompt file: `contexts/artifact_harness_improvement_rounds/round_003_replay_evidence_lane/prompt.md`
- developer report: `contexts/artifact_harness_improvement_rounds/round_003_replay_evidence_lane/developer_report.md`
- reviewer notes: not yet created
- date: `2026-04-27`

## Reported Verification

Commands reported by the developer.

- command: `python3 -m py_compile scripts/system_hub.py scripts/test_system_hub.py`
  - cwd: `/Users/tom/Documents/PHD/codex-cns`
  - reported result: passed
  - evidence path or output summary: no stderr; compilation succeeded
- command: `python3 scripts/test_system_hub.py`
  - cwd: `/Users/tom/Documents/PHD/codex-cns`
  - reported result: passed
  - evidence path or output summary: output ended with `system hub test harness checks passed`
- command: `/Users/tom/Documents/PHD/codex-cns/scripts/brain.sh artifact-harness "Draft a replay smoke artifact" --path /tmp/codex-cns-round003.sbsQNQ/target --id round003-replay-smoke --json`
  - cwd: `/tmp/codex-cns-round003.sbsQNQ/cwd`
  - reported result: passed
  - evidence path or output summary: return code `0`; scaffolded packet run started as `draft`
- command: `/Users/tom/Documents/PHD/codex-cns/scripts/brain.sh artifact-harness replay --path /tmp/codex-cns-round003.sbsQNQ/target --id round003-replay-smoke --json | python3 -m json.tool`
  - cwd: `/tmp/codex-cns-round003.sbsQNQ/cwd`
  - reported result: passed
  - evidence path or output summary: JSON parsed; payload included mission, `status=draft`, `registry_status=draft`, packet summaries, heuristics, `evidence_path`, `refused=false`, and `reason=null`
- command: `test -f /tmp/codex-cns-round003.sbsQNQ/target/contexts/artifact_harness_runs/round003-replay-smoke/artifact_replay_evidence.json && rg -n "SENTINEL_ROUND003_REPLAY_NO_REWRITE" /tmp/codex-cns-round003.sbsQNQ/target/contexts/artifact_harness_runs/round003-replay-smoke/artifact_harness_spec.md`
  - cwd: `/Users/tom/Documents/PHD/codex-cns`
  - reported result: passed
  - evidence path or output summary: evidence file existed and sentinel was still present at line `84`
- command: `/Users/tom/Documents/PHD/codex-cns/scripts/brain.sh artifact-harness replay --path /tmp/codex-cns-round003.sbsQNQ/target --id missing-round003 --json`
  - cwd: `/tmp/codex-cns-round003.sbsQNQ/cwd`
  - reported result: passed
  - evidence path or output summary: return code `1`; JSON stdout reported `refused=true`, `reason=missing_packet_run`, and an attempted `evidence_path`
- command: `/Users/tom/Documents/PHD/codex-cns/scripts/brain.sh artifact-harness "Prepare a review-ready team operating packet for Lecture 1 visual math slide/video artifact production" --path /Users/tom/Documents/PHD/Vis_Math/Slides/Lecture1 --id vis-math-lecture1-team-smoke --json`
  - cwd: `/Users/tom/Documents/PHD/codex-cns`
  - reported result: passed
  - evidence path or output summary: return code `0`; created the real smoke packet run under the Vis_Math Lecture1 workspace with `status=draft`
- command: `/Users/tom/Documents/PHD/codex-cns/scripts/brain.sh artifact-harness replay --path /Users/tom/Documents/PHD/Vis_Math/Slides/Lecture1 --id vis-math-lecture1-team-smoke --json | python3 -m json.tool`
  - cwd: `/Users/tom/Documents/PHD/codex-cns`
  - reported result: passed
  - evidence path or output summary: JSON parsed; evidence reported `existing_packet_count=7`, `missing_packet_count=0`, and `heuristic_open_items_total=170`
- command: `python3 -m json.tool /Users/tom/Documents/PHD/Vis_Math/Slides/Lecture1/contexts/artifact_harness_runs/vis-math-lecture1-team-smoke/artifact_replay_evidence.json`
  - cwd: `/Users/tom/Documents/PHD/codex-cns`
  - reported result: passed
  - evidence path or output summary: persisted real smoke replay evidence is valid JSON
- command: non-reference Markdown link check
  - cwd: `/Users/tom/Documents/PHD/codex-cns`
  - reported result: passed
  - evidence path or output summary: `missing=0 files_checked=70`
- command: `find contexts -maxdepth 3 \( -path '*artifact_harness_runs*' -o -name 'artifact_harness_registry.json' \) -print`
  - cwd: `/Users/tom/Documents/PHD/codex-cns`
  - reported result: passed
  - evidence path or output summary: no repo-local artifact-harness packet output remained

## Reviewer Rerun Verification

Commands actually rerun by the reviewer.

- command: `python3 -m py_compile scripts/system_hub.py scripts/test_system_hub.py`
  - cwd: `/Users/tom/Documents/PHD/codex-cns`
  - rerun result: passed
  - evidence path or output summary: no stderr; compilation succeeded
- command: `python3 scripts/test_system_hub.py`
  - cwd: `/Users/tom/Documents/PHD/codex-cns`
  - rerun result: passed
  - evidence path or output summary: output ended with `system hub test harness checks passed`
- command: `find contexts -maxdepth 3 \( -path '*artifact_harness_runs*' -o -name 'artifact_harness_registry.json' \) -print`
  - cwd: `/Users/tom/Documents/PHD/codex-cns`
  - rerun result: passed
  - evidence path or output summary: empty output; no repo-local smoke packet registry or run remained
- command: `python3 -m json.tool /Users/tom/Documents/PHD/Vis_Math/Slides/Lecture1/contexts/artifact_harness_registry.json`
  - cwd: `/Users/tom/Documents/PHD/codex-cns`
  - rerun result: passed
  - evidence path or output summary: target-workspace registry is valid JSON
- command: `python3 -m json.tool /Users/tom/Documents/PHD/Vis_Math/Slides/Lecture1/contexts/artifact_harness_runs/vis-math-lecture1-team-smoke/artifact_replay_evidence.json`
  - cwd: `/Users/tom/Documents/PHD/codex-cns`
  - rerun result: passed
  - evidence path or output summary: target-workspace replay evidence is valid JSON
- command: independent temp reproduction for manifest-derived packet path boundary
  - cwd: `/Users/tom/Documents/PHD/codex-cns`
  - rerun result: passed
  - evidence path or output summary: created `/tmp/codex-cns-review-r003-boundary-post.Lh8dG9`, corrupted manifest SPEC path to `../outside_secret.md`, and confirmed replay/status returned non-zero parseable JSON with `refused=true`, `reason=manifest_packet_path_outside_target_workspace`, `offending_packet_key=artifact_harness_spec`, no outside file content in stdout, no `heuristic_open_items` in refusal stdout, and unchanged prior `artifact_replay_evidence.json`

## Artifact Inspection

Generated or claimed artifacts inspected by the reviewer.

- artifact: temp-workspace `artifact_replay_evidence.json`
  - expected state: replay evidence exists under the packet run directory and records packet presence plus simple open-field heuristics
  - observed state: developer-side smoke confirmed evidence file creation, packet presence counts, heuristic rules, and parseable JSON
  - reviewer note: external reviewer confirmed JSON validity and boundary-safe path placement
- artifact: temp-workspace `artifact_harness_spec.md`
  - expected state: replay must not rewrite packet Markdown
  - observed state: developer-side smoke preserved `SENTINEL_ROUND003_REPLAY_NO_REWRITE`
  - reviewer note: external reviewer confirmed replay/status now refuse manifest packet paths outside the target workspace before reading packet contents
- artifact: Vis_Math Lecture1 `vis-math-lecture1-team-smoke` packet run
  - expected state: real allowed smoke run exists under the target workspace `contexts/` directory
  - observed state: run directory exists and contains scaffold packets, manifest, lifecycle status, and replay evidence
  - reviewer note: external reviewer confirmed the real smoke run remains in the target workspace, not the `codex-cns` repo-local `contexts/`
- artifact: Vis_Math Lecture1 `artifact_replay_evidence.json`
  - expected state: evidence records mission, target path, packet id, packet files, lifecycle state, command forms, and heuristics
  - observed state: JSON parsed successfully and reported mission, `status=draft`, `registry_status=draft`, `existing_packet_count=7`, and `heuristic_open_items_total=170`
  - reviewer note: external reviewer confirmed the persisted evidence JSON parses after the follow-up changes

## Not Run / Unable To Run

- command or check: versioned replay evidence JSON schema validation
  - reason not run: no separate schema file exists yet
  - residual risk: replay JSON is tested as an implementation contract but not validated against a formal schema

## Verification Summary

- Developer-side verification passed for replay command implementation,
  parseable JSON, replay evidence persistence, Markdown preservation,
  missing-run structured refusal, real Vis_Math Lecture1 smoke, full regression
  tests, and repo-local smoke cleanup.
- External reviewer rerun evidence passed, including the follow-up manifest path
  boundary regression.
