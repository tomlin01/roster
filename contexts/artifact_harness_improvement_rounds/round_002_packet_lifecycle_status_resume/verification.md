# Verification Evidence

## Round Metadata

- round: `round_002_packet_lifecycle_status_resume`
- prompt file: `contexts/artifact_harness_improvement_rounds/round_002_packet_lifecycle_status_resume/prompt.md`
- developer report: `contexts/artifact_harness_improvement_rounds/round_002_packet_lifecycle_status_resume/developer_report.md`
- reviewer notes: `contexts/artifact_harness_improvement_rounds/round_002_packet_lifecycle_status_resume/reviewer_notes.md`
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
- command: `/Users/tom/Documents/PHD/codex-cns/scripts/brain.sh artifact-harness "Draft a lifecycle smoke artifact" --path /tmp/codex-cns-round002.yIwWgK/target --id round002-smoke --json`
  - cwd: `/tmp/codex-cns-round002.yIwWgK/cwd`
  - reported result: passed
  - evidence path or output summary: return code `0`; JSON reported `created=true`, `status=draft`, and `status_path=/private/tmp/codex-cns-round002.yIwWgK/target/contexts/artifact_harness_runs/round002-smoke/packet_status.json`
- command: `/Users/tom/Documents/PHD/codex-cns/scripts/brain.sh artifact-harness status --path /tmp/codex-cns-round002.yIwWgK/target --id round002-smoke`
  - cwd: `/tmp/codex-cns-round002.yIwWgK/cwd`
  - reported result: passed
  - evidence path or output summary: human Markdown reported `Status: draft` and `Next inspection: artifact_harness_spec`
- command: `/Users/tom/Documents/PHD/codex-cns/scripts/brain.sh artifact-harness status --path /tmp/codex-cns-round002.yIwWgK/target --id round002-smoke --json`
  - cwd: `/tmp/codex-cns-round002.yIwWgK/cwd`
  - reported result: passed
  - evidence path or output summary: JSON parsed successfully; payload reported `status=draft`, `registry_status=draft`, `next_inspection=artifact_harness_spec`, and absolute safe command forms
- command: `/Users/tom/Documents/PHD/codex-cns/scripts/brain.sh artifact-harness mark --path /tmp/codex-cns-round002.yIwWgK/target --id round002-smoke --status filled --note "smoke lifecycle note" --json`
  - cwd: `/tmp/codex-cns-round002.yIwWgK/cwd`
  - reported result: passed
  - evidence path or output summary: JSON parsed successfully; payload reported `status=filled`, `status_note=smoke lifecycle note`, and history containing the draft and filled events
- command: `/Users/tom/Documents/PHD/codex-cns/scripts/brain.sh artifact-harness resume --path /tmp/codex-cns-round002.yIwWgK/target --id round002-smoke --json`
  - cwd: `/tmp/codex-cns-round002.yIwWgK/cwd`
  - reported result: passed
  - evidence path or output summary: JSON parsed successfully; payload reported `status=filled`, `next_inspection=team_operating_packet`, packet paths, and safe command forms
- command: lifecycle JSON parse checks with `python3 -m json.tool`
  - cwd: `/tmp/codex-cns-round002.yIwWgK/cwd`
  - reported result: passed
  - evidence path or output summary: `artifact-harness status --json` and `artifact-harness resume --json` both parsed successfully
- command: rerun guard after appending `SENTINEL_ROUND002_NO_OVERWRITE`
  - cwd: `/tmp/codex-cns-round002.yIwWgK/cwd`
  - reported result: passed
  - evidence path or output summary: same id rerun returned code `1`, JSON reported `refused=true` and `reason=existing_packet_run`, stderr listed `packet_status.json`, and `rg` confirmed sentinel remained in `artifact_harness_spec.md`
- command: non-reference Markdown link check
  - cwd: `/Users/tom/Documents/PHD/codex-cns`
  - reported result: passed
  - evidence path or output summary: `missing=0 files_checked=66`
- command: `find contexts -maxdepth 3 \( -path '*artifact_harness_runs*' -o -name 'artifact_harness_registry.json' \) -print`
  - cwd: `/Users/tom/Documents/PHD/codex-cns`
  - reported result: passed
  - evidence path or output summary: no repo `contexts/` artifact-harness output remained

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
- command: independent temp-workspace lifecycle smoke
  - cwd: `/tmp/codex-cns-review-r002.UOtap7/cwd`
  - rerun result: passed
  - evidence path or output summary: create/status/mark/resume JSON parsed; status sidecar and registry agreed; packet Markdown sentinel was preserved; same-id rerun returned `reason=existing_packet_run`; invalid mark returned `reason=invalid_status`
- command: matching `packet-route --create --json` smoke
  - cwd: `/Users/tom/Documents/PHD/codex-cns`
  - rerun result: passed
  - evidence path or output summary: route matched `artifact_harness_workflow`, created a packet chain, and returned nested artifact-harness `status=draft` plus a real `status_path`
- command: non-reference Markdown link check
  - cwd: `/Users/tom/Documents/PHD/codex-cns`
  - rerun result: passed
  - evidence path or output summary: `missing=0 files_checked=90`
- command: `find contexts -maxdepth 3 \( -path '*artifact_harness_runs*' -o -name 'artifact_harness_registry.json' \) -print`
  - cwd: `/Users/tom/Documents/PHD/codex-cns`
  - rerun result: passed
  - evidence path or output summary: no repo-local artifact-harness packet output was present

## Artifact Inspection

Generated or claimed artifacts inspected by the reviewer.

- artifact: temp-workspace `packet_status.json`
  - expected state: status sidecar exists with initial `draft`, allowed statuses, boundary note, and history
  - observed state: reviewer smoke confirmed `draft` creation, `filled` mark, boundary note, and history
  - reviewer note: passed
- artifact: temp-workspace `artifact_harness_registry.json`
  - expected state: registry mirrors lifecycle status and update timestamp
  - observed state: reviewer smoke confirmed registry status changed to `filled` and matched sidecar `updated_at`
  - reviewer note: passed
- artifact: temp-workspace `artifact_harness_spec.md`
  - expected state: lifecycle status/resume/mark must not rewrite packet Markdown
  - observed state: reviewer smoke preserved `REVIEWER_R002_SENTINEL` across mark, resume, and same-id rerun refusal
  - reviewer note: passed
- artifact: `README.md`, `AGENTS.md`, and `policy/ARTIFACT_HARNESS_WORKFLOW_V0.md`
  - expected state: lifecycle/status/resume commands documented without changing artifact workflow ownership
  - observed state: reviewer inspection confirmed lifecycle status is documented as metadata-only and below review, approval, CAP, runtime authority, and artifact acceptance
  - reviewer note: passed

## Not Run / Unable To Run

- command or check: full real-world packet lifecycle over an already-filled production packet chain
  - reason not run: this round was verified with temp smoke workspaces only
  - residual risk: production use may reveal UX gaps around status vocabulary, exact keyword phrasing, or old-run migration needs

## Verification Summary

- Developer-side verification passed for scaffold creation, lifecycle metadata
  creation, human and JSON status reads, mark, resume, Markdown preservation,
  registry consistency, rerun guard, parseable refusal JSON, and repo smoke
  cleanup.
- Reviewer-side verification also passed for the Prompt 2 acceptance surface.
