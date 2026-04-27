# Developer Report

## Round Metadata

- round: `round_004_provenance_ledger`
- prompt file: `contexts/artifact_harness_improvement_rounds/round_004_provenance_ledger/prompt.md`
- developer: `Codex`
- date: `2026-04-27`
- branch or worktree: current dirty worktree, no staging
- related artifacts:
  - `contexts/artifact_harness_improvement_rounds/round_004_provenance_ledger/verification.md`
  - `/Users/tom/Documents/PHD/Vis_Math/Slides/Lecture1/contexts/artifact_harness_runs/vis-math-lecture1-team-smoke/packet_provenance_ledger.json`

## Findings Addressed

- Added `artifact-harness provenance --path <workspace> --id <packet-id> [--json]`.
- Provenance inspects an existing packet run, manifest, lifecycle status, registry, packet files, and replay evidence when present.
- Provenance writes `packet_provenance_ledger.json` inside the target workspace packet run directory.
- JSON output includes `id`, `target_path`, `run_dir`, `manifest`, `status`, `provenance_ledger_path`, `source_categories`, `packet_chain_provenance`, `refused`, and `reason`.
- The ledger records the accepted coarse source categories:
  `user_mission`, `template_default`, `generated_scaffold`, `packet_reference`, `repo_evidence`, `agent_inference`, `runtime_output`, `test_result`, `human_approval`, `approval_required`, `unresolved`, and `unknown`.
- Packet-chain provenance now distinguishes:
  SPEC mission/contract/acceptance/boundary source, HR source SPEC and staffing boundary, TOP source SPEC and HR packet, CAP source TOP and approval gates, runtime mapping source TOP/CAP, lifecycle status, and replay evidence when present.
- Provenance reuses the lifecycle loader, so manifest-derived packet paths are validated before packet contents are read.
- Missing packet runs and manifest path boundary violations return parseable JSON under `--json`.
- Provenance does not rewrite packet Markdown, lifecycle metadata, manifest, or registry.
- The ledger explicitly states that it is source tracking only, not acceptance, approval, runtime selection, verification, or execution.

## Changed Files

- `scripts/system_hub.py`
- `scripts/test_system_hub.py`
- `README.md`
- `AGENTS.md`
- `policy/ARTIFACT_HARNESS_WORKFLOW_V0.md`
- `contexts/artifact_harness_improvement_rounds/round_004_provenance_ledger/developer_report.md`
- `contexts/artifact_harness_improvement_rounds/round_004_provenance_ledger/verification.md`

## Generated Artifacts

- `/Users/tom/Documents/PHD/Vis_Math/Slides/Lecture1/contexts/artifact_harness_runs/vis-math-lecture1-team-smoke/packet_provenance_ledger.json`
  - durable
  - review
  - allowed by the Round 004 prompt as real Vis_Math continuity smoke output
- `/var/folders/_s/p_gdfcgs2_s4dd0rgz1sk1wc0000gn/T/codex-cns-r004-provenance-n99rhlkl/target/contexts/artifact_harness_runs/r004-provenance-smoke/packet_provenance_ledger.json`
  - temporary
  - ignore
  - temp-workspace smoke output
- `contexts/artifact_harness_improvement_rounds/round_004_provenance_ledger/developer_report.md`
  - durable
  - review
- `contexts/artifact_harness_improvement_rounds/round_004_provenance_ledger/verification.md`
  - durable
  - review

No durable artifact-harness packet runs were left under the `codex-cns` repo-local `contexts/` directory.

## Verification Commands

- command: `python3 -m py_compile scripts/system_hub.py scripts/test_system_hub.py`
  - cwd: `/Users/tom/Documents/PHD/codex-cns`
  - result: passed
  - notes: syntax check for provenance implementation and tests
- command: `python3 scripts/test_system_hub.py`
  - cwd: `/Users/tom/Documents/PHD/codex-cns`
  - result: passed
  - notes: output ended with `system hub test harness checks passed`
- command: temp workspace absolute `brain.sh artifact-harness provenance ... --json`
  - cwd: temp cwd under `/var/folders/_s/p_gdfcgs2_s4dd0rgz1sk1wc0000gn/T/codex-cns-r004-provenance-n99rhlkl`
  - result: passed
  - notes: JSON parsed, ledger was written under the temp target run directory, and sentinel packet Markdown text was preserved
- command: Vis_Math Lecture1 provenance smoke
  - cwd: `/Users/tom/Documents/PHD/codex-cns`
  - result: passed
  - notes: wrote and parsed `/Users/tom/Documents/PHD/Vis_Math/Slides/Lecture1/contexts/artifact_harness_runs/vis-math-lecture1-team-smoke/packet_provenance_ledger.json`
- command: `python3 -m json.tool /Users/tom/Documents/PHD/Vis_Math/Slides/Lecture1/contexts/artifact_harness_runs/vis-math-lecture1-team-smoke/packet_provenance_ledger.json`
  - cwd: `/Users/tom/Documents/PHD/codex-cns`
  - result: passed
  - notes: persisted real smoke ledger is valid JSON
- command: `find contexts -maxdepth 3 \( -path '*artifact_harness_runs*' -o -name 'artifact_harness_registry.json' \) -print`
  - cwd: `/Users/tom/Documents/PHD/codex-cns`
  - result: passed
  - notes: no repo-local artifact-harness packet output was found

## Known Non-Goals

- did not start Prompt 5
- did not implement runtime execution proof
- did not implement schema migration for old packet runs
- did not expand security policy beyond existing read-boundary checks
- did not redesign failure recovery workflow
- did not make provenance a substitute for SPEC, HR, Team Architect, CAP, runtime mapping, or verification/review
- did not add a server, daemon, database, or orchestration UI

## Remaining Risks

- Provenance categories are coarse and conservative; they are useful for agent-readable source tracking but not a formal schema migration system.
- Field provenance does not parse every Markdown field. It records important packet-chain facts and uses shallow packet heuristics for unresolved/open items.
- `test_result` and `human_approval` categories are available but normally remain count `0` until external evidence or explicit approval artifacts exist.
- The real Vis_Math ledger overwrites the latest provenance snapshot for that run; it does not preserve ledger revision history.

## Notes For Reviewer

- Review the diff directly; do not rely only on this report.
- Rerun the necessary tests when possible.
- Inspect the Vis_Math provenance ledger, packet manifest, status sidecar, registry entry, replay evidence, and packet Markdown files before accepting this round.
