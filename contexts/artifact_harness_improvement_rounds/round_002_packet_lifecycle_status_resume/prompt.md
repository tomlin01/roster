# Prompt 2: Packet Lifecycle, Status, And Resume Surface

## Context

We are improving `codex-cns` as a Codex-native agent coordination kit:

> codex-cns does not assume a persistent server and does not require users to
> leave Codex CLI/GUI. It turns artifact-production quality contracts,
> staffing, capability authorization, and runtime mapping into agent-readable
> files and templates so Codex can assemble task forms and execution boundaries
> inside the same working folder.

Round 001 added an explicit `hr_staffing_packet` slot to the generated
Artifact Harness packet chain. Its follow-up reviewer gate is accepted:

- `contexts/artifact_harness_improvement_rounds/round_001_hr_packet_slot/reviewer_notes.md`
- `contexts/artifact_harness_improvement_rounds/round_001_hr_packet_slot/verification.md`

For this round, focus only on packet lifecycle/status/resume. Do not start the
other future-angle items.

## Problem

`artifact-harness` can now scaffold packets, guard reruns, write a manifest and
registry, and emit JSON. But after creation, the run directory is still mostly
static output. A later Codex session can see packet files, but there is no
repo-native way to answer:

- Is this packet run still a draft, partially filled, reviewed, blocked,
  approved, executed, verified, superseded, or archived?
- Which packet should a resumed session inspect first?
- What is the safe next command or next human action?
- How can a user or agent mark status without rewriting packet content?
- How can old runs stay trustworthy continuity evidence instead of being
  silently overwritten or treated as current forever?

## Goal

Add a minimal, CLI/GUI-friendly lifecycle/status/resume surface for Artifact
Harness packet runs, while preserving the current same-folder, no-server model.

The result should be useful from another workspace by absolute CLI path, and
should be parseable by Codex agents without scraping Markdown when `--json` is
used.

## Required Behavior

1. Define a small lifecycle vocabulary.
   - Suggested statuses: `draft`, `filled`, `reviewed`, `approved`, `blocked`,
     `executed`, `verified`, `superseded`, `archived`.
   - It is acceptable to choose a smaller set if the implementation clearly
     explains the tradeoff.
   - Status must not imply runtime execution or human approval unless explicitly
     marked by the user/agent.

2. Persist lifecycle metadata inside the target workspace.
   - Use the existing run directory:
     `<workspace>/contexts/artifact_harness_runs/<packet-id>/`.
   - Prefer a small JSON sidecar such as `packet_status.json` or an extension
     to `packet_manifest.json`; choose the least surprising option.
   - Preserve existing packet Markdown files; do not rewrite filled packet
     fields just to update status.
   - Update `<workspace>/contexts/artifact_harness_registry.json` enough for
     agents to find current status and resume targets.

3. Add a repo-native status/resume command surface.
   - Either extend `artifact-harness` or add focused commands such as:
     - `artifact-harness status --path <workspace> --id <packet-id> [--json]`
     - `artifact-harness resume --path <workspace> --id <packet-id> [--json]`
     - `artifact-harness mark --path <workspace> --id <packet-id> --status <status> [--note "..."] [--json]`
   - If you choose different command names, document them and keep them
     predictable for CLI/GUI use.
   - `resume` should not invoke an agent by itself. It should return the packet
     paths, current status, next recommended inspection/action, and safe command
     forms.
   - All commands that support `--json` must return structured stdout for both
     success and expected refusal/error paths.

4. Keep overwrite safety intact.
   - Existing rerun guard behavior must still prevent accidental packet content
     loss.
   - Lifecycle/status updates may modify only lifecycle metadata and registry
     fields, not the Markdown packets, unless an explicit force/overwrite path
     already exists and is intentionally used.

5. Keep governance boundaries intact.
   - Artifact Harness SPEC still owns rules, contract, acceptance, and boundary.
   - HR still owns staffing and role design only.
   - Team Architect still owns collaboration pattern, shared artifacts, task
     graph, convergence, and CAP generation.
   - CAP still owns skill/plugin/tool authorization, approval gates, and
     runtime allowlist only.
   - Runtime adapters remain execution layers only.
   - A lifecycle status must not become hidden approval authority or runtime
     governance.

6. Update documentation minimally.
   - Update `README.md`, `AGENTS.md`, and/or
     `policy/ARTIFACT_HARNESS_WORKFLOW_V0.md` only where needed to describe the
     new status/resume surface.
   - Do not rewrite the product positioning.

7. Preserve the improvement-round exchange.
   - Create or update:
     - `contexts/artifact_harness_improvement_rounds/round_002_packet_lifecycle_status_resume/developer_report.md`
     - `contexts/artifact_harness_improvement_rounds/round_002_packet_lifecycle_status_resume/verification.md`
   - Follow the Round 000 templates and include concrete verification evidence.

## Acceptance Criteria

- A packet run can be scaffolded in a temp workspace.
- The new lifecycle metadata is created with a clear initial status.
- Status can be read via CLI and JSON.
- Resume can return packet paths, status, next action, and safe command forms
  without changing packet Markdown.
- A status can be marked/updated without overwriting filled packet fields.
- Registry state is consistent with run-local lifecycle metadata.
- Existing rerun guard still fails fast for same mission/id unless force is
  explicit.
- Expected refusal/error cases in JSON mode emit parseable JSON rather than
  only stderr.
- No repo-local `contexts/artifact_harness_runs/` or
  `artifact_harness_registry.json` smoke output is left behind.

## Verification Requirements

Run at least:

- `python3 -m py_compile scripts/system_hub.py scripts/test_system_hub.py`
- `python3 scripts/test_system_hub.py`
- temp-workspace scaffold smoke:
  - `artifact-harness "<mission>" --path <temp-workspace> --id <id> --json`
- temp-workspace lifecycle/status smoke:
  - read status in human and JSON mode
  - mark a new allowed status with a note in JSON mode
  - resume in JSON mode
  - verify Markdown packet content is not changed by status/resume/mark
- rerun guard smoke:
  - same id without force still refuses and preserves a sentinel in a packet
- cleanup check:
  - `find contexts -maxdepth 3 \( -path '*artifact_harness_runs*' -o -name 'artifact_harness_registry.json' \) -print`

## Non-Goals

- Do not implement a persistent daemon, server, database, or orchestration UI.
- Do not implement full natural-language automation.
- Do not implement runtime execution.
- Do not make lifecycle status a substitute for review, approval, CAP, or
  runtime adapter policy.
- Do not start Prompt 3 or any replay/benchmark lane in this round.
