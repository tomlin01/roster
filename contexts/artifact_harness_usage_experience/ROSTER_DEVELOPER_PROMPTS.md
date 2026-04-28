# Roster Developer Prompts

These prompts are intended for developer implementation threads. Use them in
order. Each prompt should produce a developer report with changed files,
verification commands, and remaining risks.

Do not ask a developer to perform a global rename. The migration is staged.

## Prompt 0: Rename Inventory

```text
Review the repo from the Roster rename safety angle.

Context:
The user-facing name is moving from the internal `codex-cns` framing toward
`Roster`, with target invocation `@roster`. `Roster` should preserve the HR /
human-staffing advantage while also covering project boundary, collaboration,
tool-access, and review coordination. Do not rename the repo path or historical
evidence.

Goal:
Create a naming inventory that classifies every relevant occurrence into:
- internal identity
- user-facing surface
- adapter compatibility
- historical evidence

Files to read:
- README.md
- AGENTS.md
- contexts/team_alias_registry.json
- policy/system_hub.toml
- scripts/system_hub.py
- scripts/test_system_hub.py
- contexts/artifact_harness_usage_experience/NAMING_DECISION_DRAFT.md
- contexts/artifact_harness_usage_experience/ROSTER_RENAME_ROLLOUT_PLAN.md
- contexts/artifact_harness_usage_experience/README.target-user-experience.draft.md
- contexts/artifact_harness_usage_experience/TARGET_README_INSTRUCTION.md

Constraints:
- Do not edit code in this prompt.
- Do not rewrite historical improvement-round reports.
- Do not replace `codex-cns` globally.

Output:
- Findings first, P0/P1/P2/P3.
- A rename inventory table.
- A recommended edit order.
- Explicit no-touch zones.
```

## Prompt 1: User-Facing Docs To Roster

```text
Implement the first safe rename phase: user-facing docs only.

Goal:
Make the target user-facing docs consistently present `Roster, ...` as the
current primary surface, while preserving `codex-cns` only as the internal repo /
historical name and treating `@roster` as a future install target.

Files in scope:
- contexts/artifact_harness_usage_experience/README.target-user-experience.draft.md
- contexts/artifact_harness_usage_experience/TARGET_README_INSTRUCTION.md
- contexts/artifact_harness_usage_experience/NAMING_DECISION_DRAFT.md
- contexts/artifact_harness_usage_experience/README.md
- README.md only if you can avoid claiming unverified `@roster` behavior as
  already implemented
- AGENTS.md only if the wording is explicitly target-state or current-status
  accurate

Requirements:
- First screen tells a human to type `Roster, <task>` in ordinary Codex chat.
- State that `@roster` was tested and is not currently a working installed
  Codex mention; do not publish it as the primary path until registration is
  verified.
- Keep `HR` as staffing-only.
- Keep `PM` as an optional natural alias, not the primary name.
- Remove `@codex-*` and `@project-*` from target user-facing examples except in
  rejected-candidate history.
- Do not make shell commands the basic usage path.
- Keep reviewer/debug commands in a separate section.
- Add current-status wording wherever the implementation is not yet verified.

Verification:
- Markdown link check: missing=0.
- rg confirms no live target example uses `@codex-*` or `@project-*`.
- No code behavior changes in this phase.
```

## Prompt 2: Roster Alias And Route Execution

```text
Implement executable Roster routing while preserving existing behavior.

Goal:
Add `Roster` / `@roster` / `PM` as user-facing route aliases that can reach the
artifact-production front door, without making HR own project coordination or
tool authorization.

Files likely in scope:
- contexts/team_alias_registry.json
- policy/system_hub.toml
- scripts/system_hub.py
- scripts/test_system_hub.py
- README.md / AGENTS.md only for current accurate usage notes

Requirements:
- `Roster` and `@roster` route to the same high-level artifact coordination
  surface.
- `PM` is accepted as a natural alias if unambiguous.
- `HR` remains staffing/role-design only.
- Artifact-production requests remain SPEC-first.
- CAP remains tool/plugin/approval/runtime allowlist only.
- Runtime adapter remains execution layer only.
- Routing should work from another workspace and write packets under the target
  workspace.
- JSON output should be parseable for route hit, miss, create, and refusal.

Tests:
- route hit: `@roster 幫我把這個 slide 任務安排好`
- route hit: `Roster, set up the team and task boundary for this artifact`
- route hit: `PM, organize this artifact task`
- HR-only request does not create artifact packet chain
- CAP request does not become a project owner
- miss/refusal remains structured JSON

Verification:
- python3 -m py_compile scripts/system_hub.py scripts/test_system_hub.py
- python3 scripts/test_system_hub.py
- existing overlay/benchmark tests if touched
- no durable smoke output left under repo contexts/
```

## Prompt 3: Install/Register Surface And Health Check

```text
Design and implement the smallest install/register and health-check path for
Roster.

Goal:
Make it possible to reconstruct Roster on a fresh machine from repo artifacts
plus local credentials, without a server, daemon, database, or separate UI.

Requirements:
- Define the verified invocation mechanism supported by the current Codex
  CLI/GUI. Do not claim `@roster` works until verified.
- If the real mechanism is a skill, plugin, app mention, or slash command, name
  it exactly.
- Keep `@roster` as the product target if exact current support is not yet
  available.
- Add a health check that verifies:
  - invocation surface visibility or structured unavailable status
  - packet output under the target workspace
  - LLM/provider path success or structured missing-auth / missing-provider
    diagnostics
  - no persistent server/daemon/control-plane dependency
- Do not commit secrets or local auth.

Documentation:
- Update target README and root README only with current-status-accurate
  language.
- Separate repo-portable setup from machine-local state.

Verification:
- fresh temp workspace packet-output smoke
- missing-auth/provider simulation if possible
- JSON parse checks for health-check output
- no repo-local smoke artifacts
```

## Prompt 4: Root README Promotion Plan

```text
Review the current root README against the target user experience README and
promote only the parts that are true today.

Inputs:
- README.md
- contexts/artifact_harness_usage_experience/README.target-user-experience.draft.md
- contexts/artifact_harness_usage_experience/TARGET_README_INSTRUCTION.md
- contexts/artifact_harness_usage_experience/ROSTER_RENAME_ROLLOUT_PLAN.md

Goal:
Make root README human-facing without overstating unfinished install or
invocation behavior.

Requirements:
- First screen leads with Roster / human staffing-and-coordination value.
- Basic use shows natural Codex interaction first.
- If `@roster` is not verified, mark it clearly as target invocation and show
  the current verified fallback separately.
- Workspace/output semantics are clear.
- Cross-machine install has executable steps or current-status caveat.
- Debug CLI commands are not the basic usage path.
- Formal governance documents are linked after the human usage path.

Verification:
- Markdown link check.
- Review for overclaiming unverified `@`, `/`, plugin, skill, LLM, or install
  behavior.
- Existing tests if code/config changed.
```

## Prompt 5: External Review

```text
Review the Roster rename and README/user-experience changes as an external
reviewer.

Review goals:
- The name `Roster` preserves the human-staffing advantage.
- `HR` remains staffing/role design only.
- Roster does not own tool authorization; CAP still owns capability access.
- Roster does not own runtime execution; runtime adapters remain execution
  layers.
- User-facing docs do not overclaim unverified invocation/install behavior.
- Basic usage does not require bash.
- Fresh-machine install and LLM attachment are concrete or clearly marked as not
  implemented.
- No historical evidence was rewritten misleadingly.

Output format:
- Findings first, ordered P0/P1/P2/P3.
- File and line references for every finding.
- Say explicitly if there are no blocking findings.
- End with Review Summary, Verification, Remaining Risks.
```
