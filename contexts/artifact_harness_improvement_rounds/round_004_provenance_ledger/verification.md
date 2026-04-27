# Verification Evidence

## Round Metadata

- round: `round_004_provenance_ledger`
- prompt file: `contexts/artifact_harness_improvement_rounds/round_004_provenance_ledger/prompt.md`
- developer report: `contexts/artifact_harness_improvement_rounds/round_004_provenance_ledger/developer_report.md`
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
  - evidence path or output summary: `system hub test harness checks passed`
- command: temp workspace absolute `brain.sh artifact-harness provenance ... --json`
  - cwd: `/var/folders/_s/p_gdfcgs2_s4dd0rgz1sk1wc0000gn/T/codex-cns-r004-provenance-n99rhlkl/cwd`
  - reported result: passed
  - evidence path or output summary: JSON parsed; ledger path `/private/var/folders/_s/p_gdfcgs2_s4dd0rgz1sk1wc0000gn/T/codex-cns-r004-provenance-n99rhlkl/target/contexts/artifact_harness_runs/r004-provenance-smoke/packet_provenance_ledger.json`; status `draft`; source category count `12`; sentinel packet Markdown text preserved
- command: Vis_Math Lecture1 provenance smoke
  - cwd: `/Users/tom/Documents/PHD/codex-cns`
  - reported result: passed
  - evidence path or output summary: `artifact-harness provenance --path /Users/tom/Documents/PHD/Vis_Math/Slides/Lecture1 --id vis-math-lecture1-team-smoke --json` returned `refused=false`, `reason=null`, `status=draft`, and wrote `/Users/tom/Documents/PHD/Vis_Math/Slides/Lecture1/contexts/artifact_harness_runs/vis-math-lecture1-team-smoke/packet_provenance_ledger.json`
- command: `python3 -m json.tool /Users/tom/Documents/PHD/Vis_Math/Slides/Lecture1/contexts/artifact_harness_runs/vis-math-lecture1-team-smoke/packet_provenance_ledger.json`
  - cwd: `/Users/tom/Documents/PHD/codex-cns`
  - reported result: passed
  - evidence path or output summary: persisted Vis_Math provenance ledger parsed as valid JSON
- command: `find contexts -maxdepth 3 \( -path '*artifact_harness_runs*' -o -name 'artifact_harness_registry.json' \) -print`
  - cwd: `/Users/tom/Documents/PHD/codex-cns`
  - reported result: passed
  - evidence path or output summary: command returned no repo-local artifact-harness packet output

## Reviewer Rerun Verification

Commands actually rerun by the reviewer.

- command: `python3 -m py_compile scripts/system_hub.py scripts/test_system_hub.py`
  - cwd: `/Users/tom/Documents/PHD/codex-cns`
  - rerun result: passed
  - evidence path or output summary: command exited `0`
- command: `python3 scripts/test_system_hub.py`
  - cwd: `/Users/tom/Documents/PHD/codex-cns`
  - rerun result: passed
  - evidence path or output summary: `system hub test harness checks passed`
- command: independent temp workspace provenance smoke
  - cwd: temp cwd under `/tmp`
  - rerun result: passed
  - evidence path or output summary: created packet chain, added `REVIEW_SENTINEL_R004`, ran `artifact-harness provenance --json`, parsed JSON, verified ledger location, verified runtime mapping provenance traces to CAP, and verified packet Markdown was not rewritten
- command: independent missing-run refusal smoke
  - cwd: temp cwd under `/tmp`
  - rerun result: passed
  - evidence path or output summary: non-zero exit, parseable JSON refusal, `reason=missing_packet_run`, and no attempted provenance ledger was written
- command: independent manifest-boundary smoke
  - cwd: temp cwd under `/tmp`
  - rerun result: passed
  - evidence path or output summary: corrupted manifest packet path refused with `reason=manifest_packet_path_outside_target_workspace`, outside sentinel content was not leaked, and the prior ledger snapshot was not rewritten
- command: Vis_Math Lecture1 provenance smoke
  - cwd: `/Users/tom/Documents/PHD/codex-cns`
  - rerun result: passed
  - evidence path or output summary: reran `artifact-harness provenance --path /Users/tom/Documents/PHD/Vis_Math/Slides/Lecture1 --id vis-math-lecture1-team-smoke --json`, parsed JSON output, and parsed the persisted ledger with `json.loads`
- command: `find contexts -maxdepth 3 \( -path '*artifact_harness_runs*' -o -name 'artifact_harness_registry.json' \) -print`
  - cwd: `/Users/tom/Documents/PHD/codex-cns`
  - rerun result: passed
  - evidence path or output summary: command returned no repo-local artifact-harness packet output

## Artifact Inspection

Generated or claimed artifacts inspected by the developer before handoff.

- artifact: `/Users/tom/Documents/PHD/Vis_Math/Slides/Lecture1/contexts/artifact_harness_runs/vis-math-lecture1-team-smoke/packet_provenance_ledger.json`
  - expected state: durable real-workspace provenance ledger allowed by Prompt 4
  - observed state: exists, parses as JSON, includes `ledger_type=artifact_harness_provenance_ledger`, `status=draft`, 12 source categories, packet-chain provenance, and source category summary
  - reviewer note: inspect this file directly before accepting the round
- artifact: temp workspace provenance ledger under `/var/folders/_s/p_gdfcgs2_s4dd0rgz1sk1wc0000gn/T/codex-cns-r004-provenance-n99rhlkl/target/contexts/artifact_harness_runs/r004-provenance-smoke/`
  - expected state: temporary smoke output
  - observed state: exists during verification and can be ignored
  - reviewer note: not repo content
- artifact: `contexts/artifact_harness_improvement_rounds/round_004_provenance_ledger/developer_report.md`
  - expected state: durable round handoff report
  - observed state: created
  - reviewer note: report is not a substitute for diff/test/artifact inspection
- artifact: `contexts/artifact_harness_improvement_rounds/round_004_provenance_ledger/verification.md`
  - expected state: durable verification evidence
  - observed state: created
  - reviewer note: contains reported verification only; reviewer rerun is pending

## Not Run / Unable To Run

- command or check: Prompt 5
  - reason not run: explicitly out of scope for Round 004
  - residual risk: runtime execution proof and later workflow improvements remain future work

## Verification Summary

- Round 004 implementation passed syntax checks and the full system hub test suite.
- Regression coverage now includes provenance success, missing-run JSON refusal, manifest packet path boundary refusal, and packet Markdown sentinel preservation.
- A real Vis_Math Lecture1 provenance ledger was written in the prompt-approved target workspace.
- No repo-local artifact-harness smoke packet output remains under `codex-cns/contexts/`.
