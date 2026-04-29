# AGENTS.md

## Personalization
- When outputting Markdown (`md`) that contains math, always verify TeX rendering for both inline and block formulas before finalizing.
- Follow the local [`PRINCIPLES.md`](./PRINCIPLES.md) for collaboration and execution style, especially `Correctness > Speed > Aesthetics`, discussion depth by task risk, convergence discipline, and closeout expectations.

## Repo Role
- This folder is a Codex-native `agent coordination kit` and an `incubation + integration workspace` for central-nervous-system workflows, new techniques, and governance contracts.
- It is designed for ordinary Codex CLI or Codex GUI use inside this same workspace folder.
- It does not assume a persistent server, daemon, or separate orchestration UI.
- Its purpose is not to host all implementation work directly, but to validate, converge, and package new patterns here before promoting them globally.
- Protect existing canonical outputs, schemas, runner interfaces, and governance contracts by default; do not treat this repo as a casual scratchpad.

## Artifact Coordination Workflow
- Primary workflow:
  - `user mission -> Artifact Harness SPEC -> HR staffing -> Team Operating Packet -> Capability Access Packet -> runtime mapping -> verification/review`
- Artifact Harness SPEC owns only rules, contract, acceptance, and boundaries.
- `HR` owns staffing and role design only.
- `Team Architect` owns collaboration pattern, shared artifacts, task graph, convergence, and CAP generation.
- Capability Access Packet owns only skill, plugin, tool authorization, approval gates, and runtime allowlist.
- Runtime adapters are execution layers only; they do not become governance owners.
- Prefer agent-readable, template-first packet assembly. Auto-fill from the user mission and source packets only when the needed information is present; do not claim complete automation without executable evidence.
- Minimal same-folder entrypoint:
  - `./scripts/brain.sh artifact-harness "<mission>" --path <workspace-folder>`
  - `./scripts/brain.sh artifact-harness "<mission>" --path <workspace-folder> --json`
- Packet lifecycle/evidence entrypoints:
  - `./scripts/brain.sh artifact-harness status --path <workspace-folder> --id <packet-id>`
  - `./scripts/brain.sh artifact-harness resume --path <workspace-folder> --id <packet-id> --json`
  - `./scripts/brain.sh artifact-harness mark --path <workspace-folder> --id <packet-id> --status filled --note "packet fields filled" --json`
  - `./scripts/brain.sh artifact-harness replay --path <workspace-folder> --id <packet-id> --json`
  - `./scripts/brain.sh artifact-harness provenance --path <workspace-folder> --id <packet-id> --json`
  - `./scripts/brain.sh artifact-harness runtime-check --path <workspace-folder> --id <packet-id> --json`
  - `./scripts/brain.sh artifact-harness approval --path <workspace-folder> --id <packet-id> --gate runtime_execution --decision approved --approver "<label>" --json`
  - `./scripts/brain.sh artifact-harness runtime-invoke --path <workspace-folder> --id <packet-id> --adapter open-multi-agent --surface typescript-runTasks --dry-run --json`
  - `./scripts/brain.sh artifact-harness repair-plan --path <workspace-folder> --id <packet-id> --json`
  - `./scripts/brain.sh artifact-harness schema-check --path <workspace-folder> --id <packet-id> --json`
  - `./scripts/brain.sh artifact-harness migrate --path <workspace-folder> --id <packet-id> --json`
- Packet lifecycle status is continuity metadata only; it does not replace review, approval, CAP, runtime adapter policy, or artifact acceptance.
- Packet replay evidence is observation and continuity only; it does not accept artifacts, approve capabilities, select runtime, or execute adapters.
- Packet provenance ledger is source tracking only; it does not accept artifacts, approve capabilities, select runtime, verify output, or replace packet ownership.
- Packet runtime readiness report is preflight evidence only; it does not approve capabilities, authorize execution, accept artifacts, invoke runtime adapters, or make runtime adapters governance owners.
- Packet approval evidence records explicit gate decisions only; it does not replace CAP ownership, lifecycle status, artifact acceptance, runtime selection, or verification.
- Packet runtime invocation report is a guarded dry-run/export envelope only; it does not execute adapters, spawn agents, approve capabilities, accept artifacts, or make runtime adapters governance owners.
- Packet repair plan is advisory recovery evidence only; it does not rewrite packet Markdown, approve capabilities, change lifecycle status, execute adapters, or accept artifacts.
- Packet schema-check and migration are compatibility tools only; they do not rewrite filled packet Markdown, approve capabilities, accept artifacts, execute runtime adapters, or move ownership boundaries.
- Explicit keyword route check:
  - `./scripts/brain.sh packet-route "<utterance>" --path <workspace-folder>`
  - `./scripts/brain.sh packet-route "<utterance>" --path <workspace-folder> --create`
  - `./scripts/brain.sh packet-route "<utterance>" --path <workspace-folder> --json`
  - `./scripts/brain.sh packet-route "<utterance>" --path <workspace-folder> --id <packet-id> --json`
- Roster skill install / health check:
  - `./scripts/brain.sh roster-install --codex-home <codex-home> --json`
  - `./scripts/brain.sh roster-uninstall --codex-home <codex-home> --json`
  - `./scripts/brain.sh roster-health --codex-home <codex-home> --path <workspace-folder> --json`
- Roster preference memory is explicit and workspace-local only:
  - `./scripts/brain.sh roster-preferences remember "<preference>" --path <workspace-folder> --json`
  - `./scripts/brain.sh roster-preferences list --path <workspace-folder> --json`
  - `./scripts/brain.sh roster-preferences forget --id <preference-id> --path <workspace-folder> --json`
  - Preferences live at `<workspace-folder>/contexts/roster_preferences.json`.
  - Do not silently record ordinary task content; only write preferences when the user explicitly asks Roster to remember a recurring coordination default.
  - Preferences guide Roster defaults only and do not replace Artifact Harness SPEC acceptance, HR staffing boundaries, Team Architect planning, CAP authorization, runtime policy, verification, or final artifact acceptance.
- `--path <workspace-folder>` is the target workspace and packet output root; packet runs go under `<workspace-folder>/contexts/artifact_harness_runs/` with a sibling `<workspace-folder>/contexts/artifact_harness_registry.json`.
- `packet-route` uses deterministic repo keywords and must be called by Codex or the user; do not imply automatic interception of every free-form GUI/CLI phrase.
- `packet-route` also supports conservative natural artifact-mission intake. It may route ordinary phrases like `make a review-ready methods appendix` when deterministic deliverable plus action/quality cues are present, but vague hints such as `help with this artifact` must ask for clarification before creating packets.
- `packet-route` distinguishes registered front doors such as `Roster`, literal `@roster` text, artifact-context `PM`, `HR`, `Team Architect`, `CAP`, runtime mapping, and requirement-form language. `Roster`, literal `@roster` text, and unambiguous artifact-task `PM` route to the Artifact Harness workflow when the route helper is called. Do not imply `@roster` is a verified installed Codex mention. Artifact-production requests remain SPEC-first even when a downstream front door is named; HR-only staffing requests stay HR-only and must not create Artifact Harness packet runs.
- Smoke packet verification should run in a temporary workspace or clean up `smoke-artifact-harness` registry/run output before repo closeout.

## Stability Map
- `stable core`
  - memory routing
  - benchmark / policy / overlay contract
  - reconciliation / status / capability surfaces
- `active convergence`
  - skill lifecycle
  - bootstrap / session discipline
- `experimental`
  - quality-aware skill router
  - intent parsing
  - discovery / candidate-install orchestration

## Session Roles
- This repo is primarily a governance and convergence workspace, not a long-lived implementation worksite.
- Central coordination, policy shaping, and strategy convergence can happen in this session.
- Concrete project implementation, artifact correction, data processing, video repair, or document editing should usually happen in a separate functional session, with the result folded back here afterward.

## Memory Contract
- Memory is assistant-operated by default; the user should not need to manage it manually first.
- In this repo, prefer `overlay`, `closeout`, and `session-gate` for runtime continuity; use `memory-triage` as a governance and diagnostic surface rather than a default daily entrypoint.
- Do not force-resume stale sessions by default; if the governance threshold is crossed, prefer a new session with a curated brief or summary.
- Long-lived knowledge should be consolidated into canonical policy or context artifacts, not left only in transient conversation state.

## Skill Policy
- The skill router is a `quality-aware workflow planner`, not a flat skill list generator.
- Router usage is `user-attached, assistant-advised` by default:
  - fully engage it when the user explicitly asks for routing
  - proactively recommend it when there is workflow gap, skill uncertainty, or repeated high-friction process work
- For `existing artifact + correction / qa` tasks, `primary = none`, `gap = true`, and `discovery = true` are valid and preferred outcomes; do not force an incorrect skill just to avoid a gap.
- If skill discovery or installation is involved, default to a trusted-source candidate path only; do not promote unverified skills directly into active routing.

## Named Team Alias Policy
- Stable local team surfaces may define short natural-language aliases.
- `Roster` is the current user-facing Artifact Harness workflow alias. Literal `@roster` text is a route-helper alias and future mention target, not a verified installed Codex mention. `PM` is accepted only as an unambiguous artifact-task alias.
- Prefer a registered named team alias over an explicit skill call for daily chat invocation.
- Use explicit skills only as fallback adapters for automation, portability, or forced routing.
- Current alias routing policy lives in [`policy/NAMED_TEAM_ALIAS_ROUTING_V0.md`](./policy/NAMED_TEAM_ALIAS_ROUTING_V0.md).
- Current machine-readable alias registry lives in [`contexts/team_alias_registry.json`](./contexts/team_alias_registry.json).

## Multi-Agent Runtime Adapter Policy
- Runtime adapters execute local operating packets; they do not replace local role governance.
- Prefer `Team Architect` generated task graphs before using an external multi-agent runtime for governed work.
- External runtimes are optional execution layers and must remain usable from the Codex CLI/GUI workflow without adding a persistent local server requirement.
- Current runtime adapter policy lives in [`policy/MULTI_AGENT_RUNTIME_ADAPTERS_V0.md`](./policy/MULTI_AGENT_RUNTIME_ADAPTERS_V0.md).

## Promotion Rule
- Treat a pattern here as globally promotable only after local validation passes, canonical outputs are stable, and existing contracts remain intact.
- Any change that touches global defaults, benchmark schema, overlay contract, or memory routing should converge here first and leave auditable evidence behind.
- If a capability is still `experimental`, say so explicitly in documentation and closeout; do not imply it is already a global standard.
