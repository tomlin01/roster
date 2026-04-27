# Verification Evidence

## Round Metadata

- round: `round_006_keyword_intake_front_door`
- prompt file: `contexts/artifact_harness_improvement_rounds/round_006_keyword_intake_front_door/prompt.md`
- developer report: `contexts/artifact_harness_improvement_rounds/round_006_keyword_intake_front_door/developer_report.md`
- reviewer notes: not created yet
- date: `2026-04-27`

## Reported Verification

Commands reported by the developer.

- command: `python3 -m py_compile scripts/system_hub.py scripts/test_system_hub.py`
  - cwd: `/Users/tom/Documents/PHD/codex-cns`
  - reported result: passed
  - evidence path or output summary: command exited `0`
- command: `python3 scripts/test_system_hub.py`
  - cwd: `/Users/tom/Documents/PHD/codex-cns`
  - reported result: passed
  - evidence path or output summary: `system hub test harness checks passed`; includes follow-up boundary regression coverage for short aliases
- command: temp workspace Prompt6 route smoke
  - cwd: `/Users/tom/Documents/PHD/codex-cns`
  - reported result: passed
  - evidence path or output summary: JSON parsed for all specified route examples; requirement-form `--create` wrote a packet run under the temp target workspace; HR-only `--create` refused with parseable JSON; emitted command used `/Users/tom/Documents/PHD/codex-cns/scripts/brain.sh`
- command: temp workspace follow-up boundary smoke
  - cwd: `/Users/tom/Documents/PHD/codex-cns`
  - reported result: passed
  - evidence path or output summary: `walk me through runtime mapping` recognized only `runtime_mapping` with `create_allowed=false`; `walk through the requirement form` recognized `artifact_harness_workflow` with `create_allowed=true`; neither recognized `human_resources`
- command: `find contexts -maxdepth 3 \( -path '*artifact_harness_runs*' -o -name 'artifact_harness_registry.json' \) -print`
  - cwd: `/Users/tom/Documents/PHD/codex-cns`
  - reported result: passed
  - evidence path or output summary: command returned no repo-local artifact-harness packet output

## Reviewer Rerun Verification

Commands actually rerun by the reviewer.

- command: not run yet
  - cwd: not applicable
  - rerun result: pending external reviewer
  - evidence path or output summary: no independent reviewer rerun evidence has been produced for Round 006 yet

## Artifact Inspection

Generated or claimed artifacts inspected by the developer before handoff.

- artifact: temp route smoke workspace `/var/folders/_s/p_gdfcgs2_s4dd0rgz1sk1wc0000gn/T/codex-cns-r006-routes-9ui1fdgt/`
  - expected state: temporary smoke output only
  - observed state: contained temp target packet output for the requirement-form create smoke
  - reviewer note: not repo content
- artifact: temp route boundary smoke workspace `/var/folders/_s/p_gdfcgs2_s4dd0rgz1sk1wc0000gn/T/codex-cns-r006-boundary-smoke-7kt5suxk/`
  - expected state: temporary smoke output only
  - observed state: contained no created packet run; route JSON was parsed for both false-positive examples
  - reviewer note: not repo content
- artifact: `contexts/artifact_harness_improvement_rounds/round_006_keyword_intake_front_door/developer_report.md`
  - expected state: durable round handoff report
  - observed state: created
  - reviewer note: report is not a substitute for diff/test/artifact inspection
- artifact: `contexts/artifact_harness_improvement_rounds/round_006_keyword_intake_front_door/verification.md`
  - expected state: durable verification evidence
  - observed state: created
  - reviewer note: contains reported verification only; reviewer rerun is pending

## Not Run / Unable To Run

- command or check: external reviewer rerun
  - reason not run: this implementation pass produced developer-side evidence only
  - residual risk: independent reviewer still needs to inspect the diff and rerun route cases
- command or check: Prompt 7
  - reason not run: explicitly out of scope for Round 006
  - residual risk: later workflow improvements remain future work
- command or check: external runtime adapter execution
  - reason not run: explicitly out of scope for Prompt 6
  - residual risk: no runtime execution behavior is proven or changed

## Verification Summary

- Round 006 implementation passed syntax checks and the full system hub test suite.
- Regression coverage now distinguishes HR artifact requests, HR-only requests, requirement-form packet creation, Team Architect/CAP/runtime mapping front doors, existing `--id` downstream routing, unmatched utterances, absolute command emission, and guarded `--create`.
- Follow-up regression coverage now verifies short aliases such as `HR` do not match inside ordinary words such as `through`.
- Temp workspace route smoke matched the Prompt6 examples.
- No repo-local artifact-harness smoke packet output remains under `codex-cns/contexts/`.
