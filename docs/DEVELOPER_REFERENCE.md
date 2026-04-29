# Roster Developer Reference

This document keeps implementation and reviewer references out of the public
README.

## Current User Surface

- Primary invocation: `Roster, <task>`
- Install command: `./scripts/brain.sh roster-install --codex-home <codex-home> --json`
- Uninstall command: `./scripts/brain.sh roster-uninstall --codex-home <codex-home> --json`
- Health command: `./scripts/brain.sh roster-health --codex-home <codex-home> --path <workspace-folder> --json`

`@roster` remains a future product target. Do not claim it is a verified Codex
mention, slash command, plugin/app mention, or automatic GUI/CLI interception
surface.

## Packet Workflow

The internal packet chain is:

```text
user mission
-> Artifact Harness SPEC
-> HR staffing packet
-> Team Operating Packet
-> Capability Access Packet
-> optional runtime mapping
-> verification / review
```

Ownership boundaries:

- Artifact Harness SPEC owns rules, contract, acceptance, and boundaries.
- HR owns staffing and role design only.
- Team Architect owns collaboration pattern, shared artifacts, task graph,
  convergence, and CAP generation.
- Capability Access Packet owns skill, plugin, tool authorization, approval
  gates, and runtime allowlist.
- Runtime adapters are execution layers only.

## Core Commands

```bash
./scripts/brain.sh packet-route "<utterance>" --path <workspace-folder> --json
./scripts/brain.sh packet-route "<utterance>" --path <workspace-folder> --create --json
./scripts/brain.sh artifact-harness "<mission>" --path <workspace-folder> --json
./scripts/brain.sh artifact-harness status --path <workspace-folder> --id <packet-id>
./scripts/brain.sh artifact-harness resume --path <workspace-folder> --id <packet-id> --json
./scripts/brain.sh artifact-harness runtime-check --path <workspace-folder> --id <packet-id> --json
./scripts/brain.sh artifact-harness approval --path <workspace-folder> --id <packet-id> --gate runtime_execution --decision approved --approver "<label>" --json
./scripts/brain.sh artifact-harness runtime-invoke --path <workspace-folder> --id <packet-id> --adapter open-multi-agent --surface typescript-runTasks --dry-run --json
./scripts/brain.sh roster-preferences remember "<preference>" --path <workspace-folder> --json
./scripts/brain.sh roster-preferences list --path <workspace-folder> --json
./scripts/brain.sh roster-preferences forget --id <preference-id> --path <workspace-folder> --json
```

## Key Files

- [AGENTS.md](../AGENTS.md)
- [policy/ARTIFACT_HARNESS_WORKFLOW_V0.md](../policy/ARTIFACT_HARNESS_WORKFLOW_V0.md)
- [policy/ARTIFACT_HARNESS_SCHEMA_V0.md](../policy/ARTIFACT_HARNESS_SCHEMA_V0.md)
- [policy/NAMED_TEAM_ALIAS_ROUTING_V0.md](../policy/NAMED_TEAM_ALIAS_ROUTING_V0.md)
- [policy/MULTI_AGENT_RUNTIME_ADAPTERS_V0.md](../policy/MULTI_AGENT_RUNTIME_ADAPTERS_V0.md)
- [policy/ROLE_LIBRARY_ADOPTION_WORKFLOW_V0.md](../policy/ROLE_LIBRARY_ADOPTION_WORKFLOW_V0.md)
- [contexts/team_alias_registry.json](../contexts/team_alias_registry.json)
- [skills/roster/SKILL.md](../skills/roster/SKILL.md)
- [templates/artifact_harness/artifact_harness_spec.template.md](../templates/artifact_harness/artifact_harness_spec.template.md)
- [templates/human_resources/hr_staffing_packet.template.md](../templates/human_resources/hr_staffing_packet.template.md)
- [templates/team_architect/team_operating_packet.template.md](../templates/team_architect/team_operating_packet.template.md)
- [templates/team_architect/capability_access_packet.template.md](../templates/team_architect/capability_access_packet.template.md)
- [templates/team_architect/open_multi_agent_runtasks_mapping.template.md](../templates/team_architect/open_multi_agent_runtasks_mapping.template.md)
- [THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md)

## Third-Party Reference Boundary

Third-party snapshots under `references/third_party/` are read-only reference
material unless explicitly adapted into local-owned files.

Do not install an upstream role library wholesale into active skill or agent
directories. Adapt roles through
[policy/ROLE_LIBRARY_ADOPTION_WORKFLOW_V0.md](../policy/ROLE_LIBRARY_ADOPTION_WORKFLOW_V0.md).

## Verification

Before release-oriented changes, run:

```bash
python3 -m py_compile scripts/system_hub.py scripts/test_system_hub.py
python3 scripts/test_system_hub.py
python3 scripts/test_overlay_policy.py
python3 scripts/test_run_agent_benchmark.py
python3 -m json.tool contexts/team_alias_registry.json
git diff --check
```
