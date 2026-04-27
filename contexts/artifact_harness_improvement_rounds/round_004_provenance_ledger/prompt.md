# Prompt 4: Artifact Harness Provenance Ledger

## Context

We are continuing `codex-cns` Artifact Harness improvement rounds.

`codex-cns` is a Codex-native agent coordination kit. It does not assume a
persistent server and does not require users to leave Codex CLI/GUI. It turns
artifact-production quality contracts, staffing, capability authorization, and
runtime mapping into agent-readable files and templates so Codex can assemble
task forms and execution boundaries inside the same working folder.

Completed rounds:

- Round 000 established the improvement-round evidence exchange.
- Round 001 added the missing `hr_staffing_packet` slot.
- Round 002 added lifecycle/status/resume metadata and commands.
- Round 003 added replay evidence and fixed the manifest-derived packet path
  read boundary.

For this round, focus only on provenance/evidence source tracking. Do not start
runtime execution proof, schema migration, security policy expansion, or
failure-recovery workflow redesign.

## Problem

Replay evidence now records packet presence and open-field heuristics, but it
does not tell a future Codex agent where important packet claims came from.

Without a small provenance ledger, future auto-fill still has to infer whether
a packet field came from:

- the user mission
- a template default
- a source packet reference
- repo evidence
- agent inference
- runtime output
- test result
- explicit human approval
- an unresolved question

That makes the kit look operational but brittle: a later agent can see packet
files, but not which values are grounded, which are only scaffold defaults, and
which require approval before execution.

## Goal

Add a minimal, same-folder, agent-readable provenance ledger for Artifact
Harness packet runs.

The ledger should help future Codex sessions understand the source class and
confidence of important packet facts without scraping chat history or treating
all Markdown text as equally authoritative.

## Required Behavior

1. Add a repo-native provenance command or subcommand.
   - Suggested form:
     - `./scripts/brain.sh artifact-harness provenance --path <workspace> --id <packet-id> --json`
   - Another predictable command name is acceptable if documented.
   - It must inspect an existing packet run, manifest, lifecycle status,
     registry, and packet files.
   - It must not invoke an agent, execute a runtime adapter, approve
     capabilities, or accept the artifact.
   - It must return structured JSON when `--json` is supplied.

2. Persist a provenance ledger inside the target workspace.
   - Use the existing packet run directory:
     `<workspace>/contexts/artifact_harness_runs/<packet-id>/`.
   - Suggested file:
     - `packet_provenance_ledger.json`
   - The ledger must not rewrite packet Markdown forms.
   - The ledger must be safe to regenerate; if it overwrites itself, it should
     not overwrite packet content or lifecycle metadata.

3. Record provenance at a practical, coarse field level.
   - Minimal accepted categories:
     - `user_mission`
     - `template_default`
     - `generated_scaffold`
     - `packet_reference`
     - `repo_evidence`
     - `agent_inference`
     - `runtime_output`
     - `test_result`
     - `human_approval`
     - `approval_required`
     - `unresolved`
     - `unknown`
   - It is acceptable if the first implementation records a conservative
     source map for important fields rather than fully parsing every Markdown
     field.
   - It must clearly distinguish grounded facts from scaffold defaults and open
     questions.

4. Include the packet-chain source model.
   - The ledger should identify at least:
     - Artifact Harness SPEC mission / contract / acceptance / boundary source
     - HR staffing packet source SPEC and staffing-only boundary
     - Team Operating Packet source SPEC and HR packet references
     - Capability Access Packet source TOP and authorization-only boundary
     - Runtime mapping source TOP and source CAP references
     - lifecycle status source
     - replay evidence source, if present
   - Do not make the ledger the owner of these responsibilities. It only records
     source and confidence.

5. Keep same-workspace and read-boundary guarantees.
   - All generated ledger paths must stay under the target workspace.
   - Manifest-derived packet paths must continue to be validated before reading.
   - Expected refusal/error cases in `--json` mode must emit parseable JSON.

6. Use the Vis_Math Lecture1 packet run as a real continuity smoke.
   - Target workspace:
     `/Users/tom/Documents/PHD/Vis_Math/Slides/Lecture1`
   - Prefer the existing packet id:
     `vis-math-lecture1-team-smoke`
   - Do not overwrite packet Markdown.
   - Writing `packet_provenance_ledger.json` under that existing target
     workspace run is allowed.
   - If the run is missing or blocked, report a structured refusal rather than
     forcing creation.

7. Update docs minimally.
   - README / AGENTS / workflow policy should mention provenance ledger only
     where needed.
   - Do not market this as complete automation.
   - Do not introduce a server, daemon, database, or orchestration UI.

## Constraints

- Do not start Prompt 5.
- Do not stage files.
- Do not revert unrelated worktree changes.
- Do not write durable smoke packet output under the `codex-cns` repo
  `contexts/` directory.
- Temp workspace smoke output is fine.
- The real Vis_Math provenance ledger is allowed because this prompt names that
  target workspace explicitly.

## Exchange Artifacts

Create or update:

- `contexts/artifact_harness_improvement_rounds/round_004_provenance_ledger/developer_report.md`
- `contexts/artifact_harness_improvement_rounds/round_004_provenance_ledger/verification.md`

Use the round 000 protocol spirit:

- Findings Addressed
- Changed Files
- Generated Artifacts
- Verification Commands
- Known Non-Goals
- Remaining Risks

## Verification

Run at minimum:

```bash
python3 -m py_compile scripts/system_hub.py scripts/test_system_hub.py
python3 scripts/test_system_hub.py
```

Also verify:

- temp workspace provenance command returns parseable JSON
- provenance ledger is written under the target workspace packet run directory
- provenance does not rewrite packet Markdown
- missing packet run returns structured refusal JSON under `--json`
- corrupted manifest packet path outside the target workspace still refuses
  before reading packet contents
- Vis_Math Lecture1 provenance smoke succeeds or fails fast with a structured
  reason
- `find contexts -maxdepth 3 \( -path '*artifact_harness_runs*' -o -name 'artifact_harness_registry.json' \) -print` returns no `codex-cns` repo smoke output

## Acceptance

- There is a repeatable CLI path from an existing packet run to a provenance
  ledger.
- JSON output includes at least:
  - `id`
  - `target_path`
  - `run_dir`
  - `manifest`
  - `status`
  - `provenance_ledger_path`
  - `source_categories`
  - `packet_chain_provenance`
  - `refused`
  - `reason`
- The ledger distinguishes user mission, template defaults, generated scaffold,
  packet references, approval-required fields, and unresolved fields.
- The ledger is explicitly observation/provenance only, not acceptance,
  approval, runtime selection, or verification ownership.
- Round 004 has developer report and verification evidence.
