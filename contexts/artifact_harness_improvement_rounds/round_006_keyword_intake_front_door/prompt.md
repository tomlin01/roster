# Prompt 6: Keyword Intake Front Door UX

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
- Round 004 added provenance/source tracking for existing packet runs.
- Round 005 added runtime readiness preflight evidence.

For this round, focus on the user-facing keyword intake front door. Do not run
external runtime adapters. Do not implement runtime execution. Do not add a
server, daemon, database, or orchestration UI.

## Problem

The current routing surface is still too shallow for the intended user
experience.

`contexts/team_alias_registry.json` contains keyword families for Artifact
Harness, Team Architect, Capability Access Packet, and runtime mapping, but
`packet-route` effectively consumes only the Artifact Harness keyword set and
collapses all matched artifact-related language into one route:

```text
artifact_harness_workflow
```

This is useful as a scaffold command, but not enough for the core UX:

- a user should be able to say `HR`, `Team Architect`, `CAP`, `runtime mapping`,
  `requirement form`, or similar natural phrases
- Codex should explain which front door was recognized
- artifact-production requests should still start SPEC-first, even when the user
  names HR or a downstream packet
- HR-only staffing questions should stay HR-only and not create an Artifact
  Harness run
- direct downstream packet requests should not silently bypass upstream packet
  boundaries
- the JSON output should be stable enough for another Codex agent to consume
  without scraping Markdown

This is not automatic interception of every CLI/GUI phrase. The route command
must remain explicit and CLI-friendly.

## Goal

Upgrade the keyword intake model from a single Artifact Harness keyword matcher
into a small, deterministic front-door router.

Keep the existing command unless there is a strong reason to add a new one:

```bash
./scripts/brain.sh packet-route "<utterance>" --path <workspace-folder> --json
./scripts/brain.sh packet-route "<utterance>" --path <workspace-folder> --create --json
```

It is acceptable to add optional flags if they make the route safer, for
example:

```bash
--id <packet-id>
--stage <artifact-harness-spec|hr|team-operating-packet|cap|runtime-mapping>
```

But avoid a large redesign. The goal is a better front door, not a new
orchestration system.

## Required Behavior

1. Consume the full registry, not only the Artifact Harness family.
   - Read `aliases` and all `keyword_families` from
     `contexts/team_alias_registry.json`.
   - Keep TOML keywords as config-level additions, not the only source of truth.
   - Preserve the existing HR alias as a stable team surface.

2. Return structured route candidates.
   - JSON output should include at least:
     - `utterance`
     - `target_path`
     - `matched`
     - `route`
     - `recognized_front_doors`
     - `matched_keywords`
     - `candidate_routes`
     - `recommended_route`
     - `recommended_command`
     - `create`
     - `force`
     - `refused`
     - `reason`
   - Candidate routes should identify the matched alias or keyword family, the
     workflow stage, and why it is or is not directly executable.

3. Respect SPEC-first artifact-production flow.
   - If the utterance looks like an artifact-production mission and mentions
     `HR`, `Team Architect`, `CAP`, `runtime mapping`, or `requirement form`,
     recommend the Artifact Harness workflow as the chain start.
   - Record the mentioned front door separately, for example:
     - `recognized_front_doors=["human_resources"]`
     - `recommended_route="artifact_harness_workflow"`
     - `chain_start="Artifact Harness SPEC"`
     - `handoff_target="HR staffing"` when HR was the named front door
   - Do not let HR own SPEC, CAP, runtime mapping, or runtime execution.

4. Keep HR-only routing distinct.
   - If the utterance is a staffing or role-design request with no artifact
     production intent, route to the HR team surface and do not create an
     Artifact Harness packet run.
   - The JSON should make this explicit:
     - `recommended_route="human_resources"`
     - `create_allowed=false`
     - `recommended_command` may be `null` or a documented HR handoff surface
   - Do not force an Artifact Harness run just because the user says `HR`.

5. Make downstream packet references safe.
   - If the utterance asks for `Team Architect`, `CAP`, or `runtime mapping`
     without an existing packet id, recommend the SPEC-first packet chain rather
     than silently creating only the downstream packet.
   - If `--id <packet-id>` is supplied for an existing run, route to the safest
     existing packet command:
     - Team Architect request: `artifact-harness resume/status` plus path to
       `team_operating_packet.md`
     - CAP request: `artifact-harness resume/status` plus path to
       `capability_access_packet.md`
     - runtime mapping request: `artifact-harness runtime-check` or
       `artifact-harness resume/status`, depending on phrasing
   - Do not bypass missing upstream packets.

6. Make `--create` predictable.
   - `--create` should create an Artifact Harness packet chain only when the
     recommended route is `artifact_harness_workflow`.
   - For HR-only or downstream-only requests without a SPEC-first artifact
     mission, `--create` should refuse or no-op with parseable JSON rather than
     writing a misleading packet chain.
   - Existing overwrite protection must still apply.

7. Keep commands copy-paste safe.
   - Any command in JSON or Markdown must use an absolute `brain.sh` path or an
     otherwise executable command from a temp cwd.
   - `--path <workspace-folder>` must remain the target workspace and packet
     output root.

8. Keep boundaries visible.
   - Generated JSON and Markdown should make clear:
     - routing is advisory unless `--create` writes a packet chain
     - route output does not approve capabilities
     - route output does not execute runtime adapters
     - route output does not accept artifacts
     - route output does not make HR, Team Architect, CAP, or runtime adapter
       own each other's responsibilities

9. Update docs minimally.
   - README / AGENTS / routing policy should document the front-door semantics.
   - Avoid claiming automatic interception of every free-form CLI/GUI phrase.
   - Describe this as explicit CLI/agent-called routing.

## Suggested Route Semantics

Use deterministic rules before adding any fuzzy inference.

Examples:

| Utterance shape | Expected recommendation |
| --- | --- |
| `HR, help me design roles for this artifact` | Artifact Harness workflow, chain starts at SPEC, HR is named downstream front door |
| `HR, do we have the right roles?` | HR team surface only, no packet chain creation |
| `fill requirement form for methods appendix` | Artifact Harness workflow |
| `Team Architect for this artifact production task` | Artifact Harness workflow, then Team Operating Packet handoff |
| `create CAP for this artifact task` | Artifact Harness workflow unless `--id` points to an existing packet run |
| `runtime mapping for packet <id>` | existing-run route, recommend resume/status/runtime-check; no new chain unless explicit artifact mission |
| no registered keyword | no match, ordinary intake fallback |

## Constraints

- Do not start Prompt 7.
- Do not stage files.
- Do not revert unrelated worktree changes.
- Do not write durable smoke packet output under the `codex-cns` repo
  `contexts/` directory.
- Temp workspace smoke output is fine.
- Do not add a server, daemon, database, orchestration UI, or new dependency.
- Do not rename existing packet files unless there is a hard compatibility
  reason.

## Exchange Artifacts

Create or update:

- `contexts/artifact_harness_improvement_rounds/round_006_keyword_intake_front_door/developer_report.md`
- `contexts/artifact_harness_improvement_rounds/round_006_keyword_intake_front_door/verification.md`

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

Also verify in temp workspaces:

- `packet-route "HR, help me design roles for this artifact" --json`
  recommends Artifact Harness workflow but records HR as the recognized front
  door
- `packet-route "HR, do we have the right roles?" --json` routes to HR only and
  does not create packets
- `packet-route "fill requirement form for methods appendix" --create --json`
  creates a packet run under the target workspace
- `packet-route "Team Architect for this artifact production task" --json`
  recommends SPEC-first chain and does not pretend Team Architect owns SPEC
- `packet-route "create CAP for this artifact task" --json` recommends
  SPEC-first chain unless `--id` points to an existing run
- `packet-route "runtime mapping for this packet" --json` does not silently
  execute a runtime
- unmatched utterance returns parseable JSON with `matched=false`
- commands emitted from a temp cwd are copy-paste executable
- repo-local artifact-harness output check stays empty:

```bash
find contexts -maxdepth 3 \( -path '*artifact_harness_runs*' -o -name 'artifact_harness_registry.json' \) -print
```

## Acceptance

- Keyword UX is a real executable route surface, not only registry metadata.
- HR, Team Architect, CAP, runtime mapping, and requirement-form language can be
  distinguished in JSON output.
- Artifact-production requests remain SPEC-first even when the user names a
  downstream role or packet.
- HR-only staffing requests do not create Artifact Harness packet runs.
- `--create` behavior is predictable and guarded.
- JSON output is stable enough for another Codex agent to consume.
- Documentation says explicit CLI/agent-called route, not automatic global
  interception.
