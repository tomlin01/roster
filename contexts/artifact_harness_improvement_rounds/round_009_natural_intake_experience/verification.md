# Verification Evidence

## Round Metadata

- round: `round_009_natural_intake_experience`
- prompt file: `contexts/artifact_harness_improvement_rounds/round_009_natural_intake_experience/prompt.md`
- developer report: `contexts/artifact_harness_improvement_rounds/round_009_natural_intake_experience/developer_report.md`
- reviewer notes: `contexts/artifact_harness_improvement_rounds/round_009_natural_intake_experience/reviewer_notes.md`
- date: `2026-04-28`

## Reported Verification

Commands reported during implementation.

- command: `python3 -m py_compile scripts/system_hub.py scripts/test_system_hub.py`
  - cwd: `/Users/tom/Documents/PHD/codex-cns`
  - reported result: passed
  - evidence path or output summary: command exited `0`
- command: `python3 scripts/test_system_hub.py`
  - cwd: `/Users/tom/Documents/PHD/codex-cns`
  - reported result: passed
  - evidence path or output summary: `system hub test harness checks passed`
- command: natural Markdown smoke for `make a review-ready methods appendix`
  - cwd: `/Users/tom/Documents/PHD/codex-cns`
  - reported result: passed
  - evidence path or output summary: rendered `## Next Step`, `user_intent=artifact_production`, and did not write packet output without `--create`
- command: underspecified artifact `--create --json` smoke
  - cwd: `/Users/tom/Documents/PHD/codex-cns`
  - reported result: passed as refusal
  - evidence path or output summary: `reason=needs_clarification`; no registry/run output created
- command: Chinese natural route smoke for `幫我整理這個投影片任務`
  - cwd: `/Users/tom/Documents/PHD/codex-cns`
  - reported result: passed
  - evidence path or output summary: parseable JSON; `create_allowed=true`; `natural_triggers.deliverables` included `投影片`
- command: temp workspace natural `--create --json` smoke
  - cwd: `/Users/tom/Documents/PHD/codex-cns`
  - reported result: passed
  - evidence path or output summary: created packet output under temp target workspace only; temp directory removed
- command: Vis_Math Lecture1 natural route smoke
  - cwd: `/Users/tom/Documents/PHD/codex-cns`
  - reported result: passed
  - evidence path or output summary: parseable JSON; `recommended_route=artifact_harness_workflow`; `create=false`; no packet output written by the route command

## Reviewer Rerun Verification

Commands actually rerun by the reviewer after implementation.

- command: `python3 -m py_compile scripts/system_hub.py scripts/test_system_hub.py`
  - cwd: `/Users/tom/Documents/PHD/codex-cns`
  - rerun result: passed
  - evidence path or output summary: command exited `0`
- command: `python3 scripts/test_system_hub.py`
  - cwd: `/Users/tom/Documents/PHD/codex-cns`
  - rerun result: passed
  - evidence path or output summary: `system hub test harness checks passed`
- command: non-reference Markdown link check
  - cwd: `/Users/tom/Documents/PHD/codex-cns`
  - rerun result: passed
  - evidence path or output summary: `missing=0 files_checked=97`
- command: `find contexts -maxdepth 3 \( -path '*artifact_harness_runs*' -o -name 'artifact_harness_registry.json' \) -print`
  - cwd: `/Users/tom/Documents/PHD/codex-cns`
  - rerun result: passed
  - evidence path or output summary: command returned empty

## Artifact Inspection

- artifact: `scripts/system_hub.py`
  - expected state: deterministic natural artifact intake under `packet-route`
  - observed state: term-combination heuristics added; no LLM calls or dependencies
- artifact: `scripts/test_system_hub.py`
  - expected state: regression coverage for natural artifact route hits, underspecified refusal, HR-only preservation, and downstream-only runtime preservation
  - observed state: tests added and included in the main harness list
- artifact: `README.md`
  - expected state: documents natural intake without claiming automatic interception
  - observed state: updated near `packet-route` documentation
- artifact: `AGENTS.md`
  - expected state: captures local operating rule for natural intake and clarification behavior
  - observed state: updated in Artifact Coordination Workflow section
- artifact: `policy/NAMED_TEAM_ALIAS_ROUTING_V0.md`
  - expected state: defines deterministic natural artifact-mission heuristics and create refusal for vague hints
  - observed state: updated under Packet Route Front Door

## Not Run / Unable To Run

- command or check: Prompt 10
  - reason not run: explicitly out of scope for Prompt 9
  - residual risk: future workflow polish remains separate
- command or check: external runtime adapter execution
  - reason not run: out of scope and still forbidden by the runtime boundary
  - residual risk: no runtime execution behavior changed
- command or check: broad natural-language classifier evaluation
  - reason not run: Prompt 9 intentionally uses deterministic heuristics, not an LLM classifier
  - residual risk: real-world phrasing coverage needs ongoing examples

## Verification Summary

- Syntax checks and the full system hub test suite passed.
- Natural artifact-production phrases now route without internal keywords.
- Underspecified artifact references refuse creation and return clarification questions.
- HR-only and downstream-only routes keep their existing boundaries.
- Vis_Math Lecture1 natural route smoke wrote no packet output because `--create` was not used.
- No repo-local artifact-harness smoke packet output remains under `codex-cns/contexts/`.
