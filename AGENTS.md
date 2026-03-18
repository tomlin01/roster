# AGENTS.md

## Personalization
- When outputting Markdown (`md`) that contains math, always verify TeX rendering for both inline and block formulas before finalizing.
- Follow the local [`PRINCIPLES.md`](./PRINCIPLES.md) for collaboration and execution style, especially `Correctness > Speed > Aesthetics`, discussion depth by task risk, convergence discipline, and closeout expectations.

## Repo Role
- This folder is an `incubation + integration workspace` for central-nervous-system workflows, new techniques, and governance contracts.
- Its purpose is not to host all implementation work directly, but to validate, converge, and package new patterns here before promoting them globally.
- Protect existing canonical outputs, schemas, runner interfaces, and governance contracts by default; do not treat this repo as a casual scratchpad.

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

## Promotion Rule
- Treat a pattern here as globally promotable only after local validation passes, canonical outputs are stable, and existing contracts remain intact.
- Any change that touches global defaults, benchmark schema, overlay contract, or memory routing should converge here first and leave auditable evidence behind.
- If a capability is still `experimental`, say so explicitly in documentation and closeout; do not imply it is already a global standard.
