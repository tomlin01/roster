**Findings**

**P0:** None.

**P1:** `@roster`, `Roster`, and `PM` are target names but not executable yet. The target docs name `@roster` as the primary invocation, but the live alias registry only registers `HR`/`Human Resources`, and routing code reads aliases/keyword families from that registry/config. See [README target draft](/Users/tom/Documents/PHD/codex-cns/contexts/artifact_harness_usage_experience/README.target-user-experience.draft.md:14), [TARGET_README_INSTRUCTION.md](/Users/tom/Documents/PHD/codex-cns/contexts/artifact_harness_usage_experience/TARGET_README_INSTRUCTION.md:48), [team_alias_registry.json](/Users/tom/Documents/PHD/codex-cns/contexts/team_alias_registry.json:10), [system_hub.py](/Users/tom/Documents/PHD/codex-cns/scripts/system_hub.py:8880). Read-only route checks confirmed `@roster` and `Roster, do we have the right roles?` return `matched: false`, while `HR, do we have the right roles?` routes to `human_resources`.

**P2:** The root README is still `codex-cns` / command-first. That is acceptable as current internal state, but unsafe to promote as the renamed user-facing surface. See [README.md](/Users/tom/Documents/PHD/codex-cns/README.md:1) and command-first usage at [README.md](/Users/tom/Documents/PHD/codex-cns/README.md:33).

**P2:** `HR` is inconsistently framed as both a Roster alias and a retained staffing-only sub-surface. The safer model is: `Roster`/`@roster`/`PM` as coordination surface; `HR` retained as staffing-only. Compare [NAMING_DECISION_DRAFT.md](/Users/tom/Documents/PHD/codex-cns/contexts/artifact_harness_usage_experience/NAMING_DECISION_DRAFT.md:72) with [NAMING_DECISION_DRAFT.md](/Users/tom/Documents/PHD/codex-cns/contexts/artifact_harness_usage_experience/NAMING_DECISION_DRAFT.md:167).

**P3:** `Project Office` / `@project-office` only appears as rejected-candidate context, not an active target. Leave it as historical decision evidence. See [NAMING_DECISION_DRAFT.md](/Users/tom/Documents/PHD/codex-cns/contexts/artifact_harness_usage_experience/NAMING_DECISION_DRAFT.md:141).

**Rename Inventory**

| Occurrence group | Classification | Evidence | Rename action |
|---|---|---|---|
| `codex-cns` repo title/current workspace identity | internal identity | [README.md](/Users/tom/Documents/PHD/codex-cns/README.md:1), [team_alias_registry.json](/Users/tom/Documents/PHD/codex-cns/contexts/team_alias_registry.json:3) | Do not globally replace. |
| `central-nervous-system` governance wording | internal identity | [AGENTS.md](/Users/tom/Documents/PHD/codex-cns/AGENTS.md:8) | Leave unless a later governance-doc pass explicitly renames framing. |
| `Roster`, `@roster`, `PM` target | user-facing surface | [ROSTER_RENAME_ROLLOUT_PLAN.md](/Users/tom/Documents/PHD/codex-cns/contexts/artifact_harness_usage_experience/ROSTER_RENAME_ROLLOUT_PLAN.md:12), [README target draft](/Users/tom/Documents/PHD/codex-cns/contexts/artifact_harness_usage_experience/README.target-user-experience.draft.md:1) | Add as user-facing route/invocation surface first. |
| `HR` / `Human Resources` | user-facing sub-surface | [team_alias_registry.json](/Users/tom/Documents/PHD/codex-cns/contexts/team_alias_registry.json:14), [AGENTS.md](/Users/tom/Documents/PHD/codex-cns/AGENTS.md:18) | Preserve as staffing-only. Do not merge into Roster ownership. |
| `Artifact Harness`, `Team Architect`, `CAP` | adapter/governance compatibility | [AGENTS.md](/Users/tom/Documents/PHD/codex-cns/AGENTS.md:16), [team_alias_registry.json](/Users/tom/Documents/PHD/codex-cns/contexts/team_alias_registry.json:49) | Keep formal packet names. Surface them after human-facing Roster path. |
| `artifact-harness`, `packet-route`, packet JSON keys | adapter compatibility | [system_hub.py](/Users/tom/Documents/PHD/codex-cns/scripts/system_hub.py:546), [system_hub.py](/Users/tom/Documents/PHD/codex-cns/scripts/system_hub.py:561) | Keep existing commands/fields; add aliases rather than rename. |
| `open-multi-agent`, `runTasks` | adapter compatibility | [policy/system_hub.toml](/Users/tom/Documents/PHD/codex-cns/policy/system_hub.toml:39), [system_hub.py](/Users/tom/Documents/PHD/codex-cns/scripts/system_hub.py:91) | No rename. Runtime remains execution layer only. |
| `.codex`, `codex_home`, `codex_ckpt`, Codex CLI/Desktop | internal platform/runtime naming | [policy/system_hub.toml](/Users/tom/Documents/PHD/codex-cns/policy/system_hub.toml:8), [system_hub.py](/Users/tom/Documents/PHD/codex-cns/scripts/system_hub.py:441) | Do not rename; these refer to Codex runtime, not product branding. |
| `Project Office`, `@project-office` | historical evidence / rejected candidate | [NAMING_DECISION_DRAFT.md](/Users/tom/Documents/PHD/codex-cns/contexts/artifact_harness_usage_experience/NAMING_DECISION_DRAFT.md:141) | Leave as decision history. |
| Rename rollout docs themselves | historical/current planning evidence | [ROSTER_RENAME_ROLLOUT_PLAN.md](/Users/tom/Documents/PHD/codex-cns/contexts/artifact_harness_usage_experience/ROSTER_RENAME_ROLLOUT_PLAN.md:22) | Do not rewrite as if migration already happened. |

**Recommended Edit Order**

1. Add routing support for `Roster`, `@roster`, and `PM` without removing `HR`.
2. Extend `packet-route` semantics so Roster can be an explicit coordination front door, while artifact-production requests still start SPEC-first.
3. Add tests for `@roster`, `Roster`, `PM`, English/Chinese artifact examples, and HR-only no-create behavior.
4. Only then update target user-facing docs and eventually root `README.md`.
5. Keep `artifact-harness`, `packet-route`, packet keys, and runtime adapter names as compatibility surfaces.

**No-Touch Zones**

- Repo path `/Users/tom/Documents/PHD/codex-cns`.
- Historical improvement-round reports and committed evidence.
- Existing packet-run evidence and registries unless a specific migration is approved.
- `codex_home`, `.codex`, `codex_ckpt`, Codex CLI/Desktop runtime references.
- `artifact-harness`, `packet-route`, JSON packet keys, and `open-multi-agent` / `runTasks` adapter names.

No files were modified.

