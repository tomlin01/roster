# Artifact Harness Usage Experience Log

## Purpose

This folder records real usage experience for the Artifact Harness workflow.

It is not a policy owner, runtime owner, approval surface, or packet output
root. It is an experience notebook for deciding which parts of the
Codex-native staffing-and-coordination surface feel natural in ordinary Codex CLI/GUI use and
which parts still leak implementation details to the user.

Current verified user invocation:

```text
Roster, 幫我把這個 slide 任務安排好。
```

Current status: `@roster` was tested and did not work as an installed Codex
mention in this phase. Treat it as a future install target only. The current
usable surface is natural-language invocation through `Roster, ...`, backed by
repo-local route checks when Codex or a reviewer needs deterministic evidence.

Current target artifacts:

- [`README.target-user-experience.draft.md`](./README.target-user-experience.draft.md)
  drafts the final user-facing README shape.
- [`TARGET_README_INSTRUCTION.md`](./TARGET_README_INSTRUCTION.md)
  records the review-derived instruction that the final README should satisfy.
- [`NAMING_DECISION_DRAFT.md`](./NAMING_DECISION_DRAFT.md)
  records the current move away from `codex-cns` toward a human-role surface,
  with `Roster` as the current recommendation and `@roster` as a future install
  target only.
- [`ROSTER_RENAME_ROLLOUT_PLAN.md`](./ROSTER_RENAME_ROLLOUT_PLAN.md)
  defines the staged, safe rename plan and no-touch zones.
- [`ROSTER_DEVELOPER_PROMPTS.md`](./ROSTER_DEVELOPER_PROMPTS.md)
  contains phased prompts for developer implementation and external review.

## Core UX Principle

The user should not need to remember or type `brain.sh`, `packet-route`, or
`artifact-harness` commands during ordinary work.

The intended user-facing interaction is natural Codex CLI/GUI language, for
example:

- `Roster, 幫我把這個 slide 任務安排好。`
- `Roster, organize the task boundary and handoff for this artifact`
- `HR, help me confirm the staffing roles for this artifact`
- `CAP, what tool access does this task need?`
- `Roster, make this lecture slide task organized`

`PM` is an optional natural alias for project-planning language. `HR` remains
staffing-only; it should not become the project-coordination or tool-access
owner.

The command-line surfaces are implementation adapters for Codex, reviewers, and
debugging. They are allowed to exist, but they should normally be invoked by the
agent in the background, not by the user as the primary workflow.

## Human-Centered UX Lens

The user should experience this kit as help organizing work, not as a new system
they must learn.

Important human factors:

- Plain language first: say `task brief`, `team`, `tool access`, `next step`,
  and `review checklist` before exposing names like SPEC, TOP, CAP, or runtime
  mapping.
- Progressive disclosure: show the simple outcome first, then link packet files
  for audit. Do not dump the full packet chain unless the user asks or the risk
  justifies it.
- Location confidence: before writing files, Codex should know the target
  workspace. If the active folder is ambiguous, ask one short location question
  rather than guessing.
- Recovery without memory burden: the user should not need to remember packet
  ids. Codex should find the likely active run from the current workspace,
  registry, and recent files.
- Minimal interruption: ask approval only for real ambiguity, destructive
  action, external access, tool escalation, or budget/time risk. Do not turn
  every packet field into a question.
- Right-sized scaffolding: small one-step work should not trigger a heavy packet
  chain. The kit should recognize when a lightweight note or direct action is
  enough.
- Quality as normal coordination: when the user asks how Quality should be set,
  answer with immediate delivery checks and durable improvement checks before
  exposing internal packet names.
- Visual artifact quality loop: for slide, scene, render, video, screenshot,
  image, UI, or presentation production, Roster should plan 2-3 bounded
  inspect-and-correct passes before delivery. The loop checks visible output for
  occlusion, overlap, readability, contrast, missing expected content, and
  slide/render/video mismatch; CV inspection can request screenshot capture,
  playback or frame sampling, OCR/readability review, and vision-model review.
  These remain tool capabilities governed by CAP, not Quality-owned governance.
- Bilingual tolerance: English aliases and Chinese task phrases should both
  feel native. The user should not need to switch language to activate the
  workflow.
- Failure clarity: errors should say what failed, whether anything was written,
  and the next concrete recovery action.
- Reversibility: generated coordination files should be auditable and safe to
  remove or regenerate with explicit overwrite rules.
- User ownership: the kit proposes structure and boundaries; it should not make
  the user feel locked into an invented process.

## Install Semantics

`Install` should not mean deploying a server, daemon, database, or separate
orchestration UI.

For this kit, `install` should mean registering a Codex-native invocation
surface that can reach the existing packet engine:

- user-facing surface: current `Roster, ...` natural-language invocation backed
  by an installable `roster` skill, with `@roster`, plugin/app mention, or
  slash-accessible command reserved for a future verified install layer
- agent-facing adapter: the existing deterministic CLI and JSON outputs
- output location: the target workspace, not the kit repo by default
- governance boundary: unchanged Artifact Harness / HR / Team Architect / CAP /
  runtime-adapter layering
- portability contract: a fresh machine can reconstruct the invocation surface
  and LLM attachment from repo artifacts plus explicit local credentials
- health check: install success is not just files copied; it must verify that
  Codex can invoke the surface and that LLM-dependent paths either work or fail
  with an actionable missing-auth / missing-provider message

The current repo has the packet engine, repo-local instructions, and a
repo-owned `roster` skill install path. The installation story is still
incomplete only for custom `@`, `/`, plugin, or app-mention affordances.

Machine-specific state should stay out of the repo:

- local Codex auth/session state
- API keys and provider credentials
- personal accumulated memory
- local model caches
- machine-local overlays that have not been artifactized

Repo-portable state should be artifactized:

- install manifest and expected file layout
- `skills/roster` source and skill install manifest
- skill/plugin/slash registration instructions or package metadata
- `.codex` project configuration when needed
- hook/MCP/runtime attachment skeletons when needed
- LLM provider requirements and environment variable names
- smoke-test commands or agent-facing checks that prove the installation works

## Initial Experience Finding

### UX-001: Bash-first instructions are the wrong primary interface

- date: `2026-04-28`
- source: user feedback after Prompt 10 closeout
- severity: P1 for user experience, not a workflow-safety blocker

Current risk:

- Documentation and closeout examples show direct shell commands as the basic
  use path.
- This makes the kit feel like a CLI tool the user must operate manually.
- That contradicts the desired Codex-native model where the user uses `Roster,
  ...` or another supported natural alias in Codex CLI/GUI and the agent handles
  routing.

Desired behavior:

- User says a natural phrase or a named team alias.
- Codex recognizes the front door from repo instructions and alias policy.
- Codex invokes `packet-route`, `artifact-harness`, `resume`, or `repair-plan`
  internally only when useful.
- Codex reports the result in normal language and links the generated packet
  files.
- The user sees shell commands only when debugging, reviewing, or explicitly
  asking for reproducible CLI evidence.

Acceptance signal:

- A user can start from `Roster, ...` or a supported natural artifact-production
  alias without being told to copy-paste a bash command.
- `HR` continues to work only as a staffing and role-design surface.
- Generated packets still land in the target workspace.
- No persistent server, daemon, database, or separate UI is introduced.
- Agent behavior remains explicit and auditable through generated packet files
  and optional JSON evidence.

### UX-002: Invocation should be install-like, mentionable, or slash-accessible

- date: `2026-04-28`
- source: user feedback after opening this usage log
- severity: P1 for user experience, not a workflow-safety blocker

Current risk:

- The workflow is repo-local and executable, and now has an installable
  repo-owned `roster` Codex skill source. It is still not verified as a custom
  `@roster` mention, slash command, plugin/app mention, or globally distributed
  package.
- If the user must remember exact paths or shell commands during ordinary work,
  the kit is still too manual; the current human path should remain `Roster, ...`
  after install, with shell commands reserved for setup and diagnostics.
- The user reasonably expects a reusable coordination surface to be easy to
  call through Codex-native affordances such as a mention, skill invocation,
  plugin/app entry, or slash-accessible command.
- Repo-local keyword routing only works when the active assistant recognizes
  the phrase and follows the local instructions. It does not solve explicit
  invocation when the user wants to call the kit without embedding `HR`, `CAP`,
  or another configured keyword in the message body.

Desired behavior:

- The user can call the staffing-and-coordination surface without typing bash.
- The current primary call is `Roster, ...`; `PM` may remain an optional natural
  alias for project-planning language.
- `@roster` remains the desired future install target, but it is not current
  verified behavior.
- Natural aliases such as `HR` should still work when they appear in ordinary
  language, but `HR` stays staffing-only.
- Explicit invocation should also exist for cases where the user does not want
  to rely on keywords, for example:
  - a mentionable surface for the staffing-and-coordination surface or team
  - a skill-style invocation for Artifact Harness / HR / Team Architect
  - a slash-accessible command if the active Codex surface supports custom or
    plugin-provided commands
- The explicit invocation should still land packet files in the target
  workspace and preserve the same governance boundaries.

Candidate packaging directions:

- `Codex skill`: good for reusable workflow instructions and implicit/explicit
  activation. The skill should call repo scripts as internal adapters and hide
  bash from ordinary user-facing text.
- `Codex plugin`: good if the kit should be installable, mentionable, or shared
  beyond this local repo; package one or more skills plus optional metadata.
- `Slash command wrapper`: useful only if the current Codex CLI/GUI surface
  supports a custom command path for local workflows. Treat this as a UX
  adapter, not the governance owner.
- `Shell alias`: not sufficient as the basic interface. It may help debugging,
  but it still forces the user to operate the implementation adapter directly.

Acceptance signal:

- A new thread can invoke the kit through an explicit Codex-native surface
  without the user typing the absolute `brain.sh` path.
- A user can type an explicit affordance such as `@...` or `/...`, where
  supported by the current Codex surface, and reach the coordination workflow
  without also adding a keyword like `HR`.
- The surface works in both routine natural-language mode and explicit
  invocation mode.
- The surface does not introduce a persistent server, daemon, database, or
  separate orchestration UI.
- The surface keeps shell/JSON evidence available for review, but not as the
  default user experience.

Open question for implementation:

- Verify the exact supported mechanism in the current Codex CLI/GUI version.
  Skills are the likely first packaging layer for a reusable workflow; `/`
  currently has strong built-in command semantics in Codex CLI, so any custom
  slash path needs explicit support rather than assumption.

### UX-003: `@roster` is not currently a working Codex mention

- date: `2026-04-28`
- source: user manual test of `@` invocation
- severity: P1 for invocation experience, not a workflow-safety blocker

Observed result:

- The user tested `@roster` and it did not activate as a Codex mention.
- Repo-local `packet-route` can still match the literal text `@roster`, but that
  is not the same thing as an installed mention, skill, plugin/app mention, or
  slash command.

Current documentation rule:

- Current primary user-facing invocation is `Roster, ...`.
- `@roster` must be described only as a future install target until a real
  registration layer proves it in Codex CLI/GUI.
- Any future README that puts `@roster` in the first-screen primary path must
  include concrete verification evidence for the installed surface.

### UX-003: Cross-machine install must include LLM attachment

- date: `2026-04-28`
- source: user feedback after invocation-layer discussion
- severity: P1 for portability and trust

Current risk:

- A repo-local workflow can look complete on the original machine because the
  user's Codex auth, API keys, MCP setup, hooks, and local memory already exist.
- Moving to another machine can silently break the workflow if those
  dependencies are not declared and checked.
- LLM-dependent paths are especially vulnerable: a copied skill or plugin may be
  present, but actual model access may be missing, expired, or pointed at the
  wrong provider.

Desired behavior:

- A fresh machine can install or register the invocation layer from repo-local
  artifacts.
- The install flow asks only for machine-specific secrets or auth that cannot be
  committed.
- The kit records which LLM path is expected, for example Codex built-in model
  access, OpenAI API key, MCP-backed docs access, or another configured provider.
- The health check verifies:
  - invocation surface is visible to Codex
  - packet engine can run in a target workspace
  - LLM-dependent path can make a minimal call or returns structured missing-auth
    diagnostics
  - no server, daemon, or hidden control plane is introduced

Acceptance signal:

- On a second machine, the user can clone/copy the kit, run the documented
  install/register step, provide local credentials, and invoke the workflow from
  Codex without manually rediscovering scripts.
- If credentials or provider setup are missing, the failure message identifies
  exactly what must be configured and does not pretend the install succeeded.
- The repo distinguishes portable setup from machine-local state rather than
  relying on memory from the original machine.

### UX-004: Internal packet vocabulary should not dominate the user surface

- date: `2026-04-28`
- source: human-centered UX review
- severity: P2 for adoption and daily usability

Current risk:

- The workflow is structurally sound, but the visible vocabulary can become too
  system-internal.
- Users may not know whether they need `Artifact Harness`, `Team Operating
  Packet`, `CAP`, `runtime mapping`, or `repair-plan`.
- If every interaction starts by naming these layers, the kit feels like
  bureaucracy instead of assistance.

Desired behavior:

- Use human task language first:
  - `I set up the task brief.`
  - `I mapped the roles.`
  - `I listed the tool access and approvals.`
  - `I left the execution boundary here.`
- Link the formal packet names as audit artifacts, not as the primary
  explanation.
- Introduce formal names only when the user is reviewing, debugging, or asking
  about the architecture.

Acceptance signal:

- A new user can understand what Codex did without learning the packet taxonomy.
- A reviewer can still inspect exact SPEC/TOP/CAP/runtime files when needed.

### UX-005: The kit needs resume and active-run discovery

- date: `2026-04-28`
- source: human-centered UX review
- severity: P1 for continuity

Current risk:

- The workflow creates durable files, but a human will not reliably remember the
  packet id, exact run directory, or which packet is current.
- If the user says `這個任務現在卡在哪裡？`, a poor implementation may ask for
  internal ids instead of inspecting local state.

Desired behavior:

- Codex should locate likely active packet runs from:
  - current workspace path
  - `contexts/artifact_harness_registry.json`
  - recent packet run directories
  - open or recently edited artifacts when available
- If multiple candidates exist, ask one short disambiguation question with
  human-readable mission titles.
- The response should summarize status, blocker, and next action before listing
  file paths.

Acceptance signal:

- A user can resume a packetized task from ordinary language without copying a
  packet id.

### UX-006: The workflow needs a lightweight path

- date: `2026-04-28`
- source: human-centered UX review
- severity: P2 for friction

Current risk:

- A full SPEC -> HR -> TOP -> CAP -> runtime mapping chain is valuable for
  artifact-production work, but too heavy for quick questions or small edits.
- If the system over-scaffolds every request, the user will stop trusting the
  route.

Desired behavior:

- Detect when the request only needs direct execution, a short note, or a simple
  staffing check.
- Use full packet assembly when there is real artifact-production risk:
  multi-step work, roles, tool authorization, review criteria, external runtime,
  or future resumption.
- Explain the choice briefly when it matters:
  - `This is small enough to handle directly.`
  - `This should get a task brief because it has roles, deliverables, and tool
    access.`

Acceptance signal:

- The kit improves high-friction work without adding ceremony to low-friction
  work.

### UX-007: Permission and tool access should feel visible but not scary

- date: `2026-04-28`
- source: human-centered UX review
- severity: P2 for trust

Current risk:

- CAP is meant to make tool authorization explicit, but visible approval language
  can feel intimidating if presented as governance jargon.
- Conversely, hiding tool/runtime choices makes the system feel opaque.

Desired behavior:

- Show concise human-facing permission summaries:
  - `No external tools needed.`
  - `Needs filesystem writes only.`
  - `Needs LLM/provider access; no external runtime.`
  - `Needs approval before network/plugin/runtime execution.`
- Keep formal allowlists and gates in CAP for audit.
- Ask for approval only at real gates and explain why the gate exists.

Acceptance signal:

- The user understands what access is needed without reading the whole CAP.

### UX-008: First-touch replies should feel like a working interface

- date: `2026-04-28`
- source: user feedback after a Lecture1 team-roster test
- severity: P1 for daily usability

Current risk:

- Roster can route and scaffold correctly, but the first response can still read
  like an internal closeout if it exposes `HR`, `Team Architect`, packet names,
  control-plane language, or continuity receipts.
- Telling the user what was not modified can sound like a capability limit if it
  is not framed as current-turn scope.
- A long explanatory first response makes the user think about the system
  instead of using it.

Desired behavior:

- First-touch replies show only the useful working team, short role descriptions,
  one next invocation phrase, and at most one file link.
- Internal governance terms remain available in generated files, review/debug
  replies, and later explanations, but they do not lead the ordinary response.
- If this turn only prepared a roster, say that as current-turn scope and make
  clear that future Roster runs can assign slide, scene, render, video, QA, or
  other artifact work to the relevant roles.

## Experience Probes

Use these as real-world checks before the next implementation round.

### Probe 1: HR Alias Front Door

User phrase:

```text
HR, help me set up the right team for this artifact
```

Expected agent behavior:

- Treat `HR` as a named team alias.
- If the request is artifact-production oriented, start SPEC-first and route HR
  as the staffing stage.
- Do not ask the user to run `brain.sh`.
- Link the generated or relevant packet paths.

### Probe 2: HR-Only Staffing

User phrase:

```text
HR, do we have the right roles?
```

Expected agent behavior:

- Stay on the Human Resources team surface.
- Do not create an Artifact Harness packet chain unless an artifact-production
  mission is actually present.
- Preserve HR as staffing and role-design only.

### Probe 3: Natural Artifact Mission

User phrase:

```text
幫我整理這個投影片任務
```

Expected agent behavior:

- Recognize artifact-production intent.
- Use Artifact Harness packet assembly internally if useful.
- Explain the next step in ordinary language.
- Avoid exposing internal route IDs first.

### Probe 4: Recovery Without Bash

User phrase:

```text
這個 packet 現在卡在哪裡？
```

Expected agent behavior:

- Locate the active packet run when possible.
- Run or read `repair-plan` internally if useful.
- Summarize blockers and next actions in normal language.
- Do not require the user to know the packet id unless it is ambiguous.

### Probe 5: Explicit Invocation Without Keywords

User intent:

```text
I want to call the staffing-and-coordination surface directly without saying HR, CAP, or runtime mapping.
```

Expected agent behavior:

- Provide a Codex-native invocation path such as a skill, plugin/app mention, or
  slash-accessible command.
- Do not require the user to type a bash command.
- Route to the same Artifact Harness / HR / Team Architect / CAP workflow after
  invocation.
- Keep generated packet evidence file-grounded in the target workspace.

### Probe 6: Fresh-Machine Install With LLM Check

Scenario:

```text
I moved to a new machine and want this staffing-and-coordination surface to work there.
```

Expected agent behavior:

- Reconstruct the invocation surface from repo artifacts rather than relying on
  the original machine's local state.
- Identify required machine-local credentials or auth without committing them.
- Verify the LLM path with a minimal health check or return a structured
  missing-auth / missing-provider diagnostic.
- Confirm that packet output still lands in the target workspace.

### Probe 7: Human-Friendly Resume

User phrase:

```text
這個任務現在卡在哪裡？
```

Expected agent behavior:

- Search the current workspace for active packet runs.
- If one likely run exists, summarize its status without asking for a packet id.
- If several likely runs exist, ask one short disambiguation question using
  mission titles or artifact names.
- Link the relevant packet files only after the human-readable status.

### Probe 8: Lightweight Direct Path

User phrase:

```text
HR, 這個小修正需要什麼角色？
```

Expected agent behavior:

- Treat this as a staffing check, not a full artifact-production chain, unless
  the surrounding context shows a larger artifact mission.
- Give the staffing answer directly.
- Avoid generating a packet run just because `HR` appeared.

### Probe 9: Plain-Language Outcome

User phrase:

```text
幫我把這個 slide 任務安排好
```

Expected agent behavior:

- Start with a plain-language result such as:
  `I set up a task brief, role plan, tool-access note, and review checklist.`
- Then link the generated SPEC/TOP/CAP/runtime packet files.
- Do not make the formal packet names the first thing the user must parse.

## Improvement Backlog

- Treat the invocation layer as the next product milestone: turn the working
  packet engine into a packageable Codex surface the user can call without bash.
- Reword README and AGENTS so shell commands are documented as reproducible
  internals, not the primary user flow.
- Add an "Agent-facing usage" section: when Codex sees `Roster`, optional `PM`
  language, staffing-only `HR`, `Team Architect`, `CAP`, `runtime mapping`, or
  artifact-production language, it should call the route/check commands itself.
- Add an "End-user usage" section that shows only natural phrases and expected
  Codex behavior.
- Decide whether `packet-route` should be described as an internal adapter
  rather than an explicit user command in ordinary docs.
- Design a packageable invocation layer:
  - repo-local skill first
  - plugin packaging if sharing/installing is needed
  - slash-accessible adapter only after verifying the current Codex surface
    supports the intended command shape
- Add a portability/install manifest that separates repo-portable artifacts from
  machine-specific auth, API keys, local memory, and caches.
- Add a health check for LLM attachment and invocation visibility on a fresh
  machine.
- Add active-run discovery and human-friendly resume behavior.
- Add a lightweight path so trivial tasks are not over-scaffolded.
- Rework user-facing language so formal packet names appear as audit links, not
  the first explanation.
- Collect at least three real tasks where Codex starts from natural language
  and produces or resumes packet files without asking the user to type bash.

## Prompt Candidate: Invocation Layer

Use this when handing the next implementation round to a developer thread:

```text
Review and improve Roster from the user-facing invocation angle.

Core product direction:
Roster is a Codex-native agent staffing-and-coordination surface. It should not require a
persistent server or a separate orchestration UI. The packet engine may use CLI
adapters internally, but the basic user experience should not require the user
to type bash commands.

Goal:
Design and implement the smallest install-like invocation layer that lets a
user call the Artifact Harness / HR / Team Architect / CAP workflow from Codex
CLI or GUI through a natural Codex-native affordance such as a skill invocation,
plugin/app mention, or slash-accessible command where supported.

Requirements:
- Do not replace the existing packet engine; reuse it as the internal adapter.
- Preserve same-folder output semantics:
  packets go under <target-workspace>/contexts/artifact_harness_runs/.
- Preserve governance boundaries:
  Artifact Harness owns rule/contract/acceptance/boundary;
  HR owns staffing/role design only;
  Team Architect owns collaboration pattern/task graph/shared artifacts/CAP;
  CAP owns skill/plugin/tool authorization and approval gates only;
  runtime adapters remain execution layers only.
- The user-facing docs should show natural invocation first, not `brain.sh`.
- Shell commands and JSON output should remain available as review/debug
  evidence, but not be the basic use path.
- Verify the exact current Codex support for reusable skills, plugin/app
  mentions, and slash commands before claiming a surface works.

Acceptance:
- From a fresh Codex thread, the user can intentionally call the coordination
  kit without embedding keywords like HR or CAP in the natural-language body.
- The implementation does not add a persistent server, daemon, database, or
  always-on external control plane.
- A smoke test shows the invocation layer reaches the same packet output path
  and produces reviewable evidence.
- Documentation clearly distinguishes end-user invocation from agent-facing
  internal adapter commands.
```

## Prompt Candidate: Portable Install And LLM Attachment

Use this after or alongside the invocation-layer implementation:

```text
Review and improve Roster from the cross-machine install and LLM-attachment
angle.

Core product direction:
Roster should be usable on a fresh machine without a persistent server or
separate orchestration UI. The repo should carry the portable setup artifacts;
local auth, API keys, personal memory, model caches, and other machine-specific
state must remain outside the repo.

Goal:
Create the smallest install/register + health-check path that proves the
staffing-and-coordination surface can be reconstructed on another machine and can reach its LLM
dependency intentionally.

Requirements:
- Define what is repo-portable vs machine-specific.
- Add or document an install/register path for the Codex-native invocation
  surface.
- Record required LLM/provider inputs without committing secrets.
- Include a health check that verifies:
  - Codex can see or invoke the coordination surface;
  - the packet engine can write to <target-workspace>/contexts/;
  - LLM-dependent behavior succeeds or returns structured missing-auth /
    missing-provider diagnostics;
  - no server, daemon, database, or hidden always-on control plane is added.
- Preserve existing workflow boundaries:
  Artifact Harness, HR, Team Architect, CAP, and runtime adapter roles must not
  be collapsed into the installer.

Acceptance:
- A fresh-machine smoke test, or a documented reproducible simulation, shows the
  setup can be reconstructed from repo artifacts plus local credentials.
- Missing credential/provider cases fail fast with actionable messages.
- User-facing docs explain install in Codex terms, not as manual bash-first
  operation.
- Review/debug shell commands remain available but are not the primary usage
  path.
```

## Prompt Candidate: Human-Centered Usage Pass

Use this when the invocation and portability layers exist but the workflow still
feels too mechanical:

```text
Review and improve Roster from the human usage experience angle.

Core product direction:
Roster is a Codex-native agent staffing-and-coordination surface. It should feel like Codex is
helping the user organize artifact work, not like the user is operating a packet
system manually.

Goal:
Make the daily interaction natural, recoverable, and right-sized while
preserving the existing Artifact Harness / HR / Team Architect / CAP / runtime
boundaries.

Requirements:
- Use plain language before internal packet vocabulary in user-facing docs and
  closeout messages.
- Add or document active-run discovery so the user can resume with ordinary
  phrases such as `這個任務現在卡在哪裡？` without remembering packet ids.
- Add a lightweight path for small tasks that should not generate the full
  packet chain.
- Add location-confidence behavior: if the target workspace is ambiguous, ask
  one short question before writing files.
- Keep formal packet paths available as audit evidence after the plain-language
  summary.
- Keep permission/tool-access summaries human-readable while preserving formal
  CAP allowlists and gates.
- Support Chinese and English invocation phrases in the examples and tests.

Acceptance:
- A human can understand what Codex did without learning SPEC/TOP/CAP/runtime
  terminology first.
- A reviewer can still inspect the exact generated packet files.
- Resume works from current workspace context without requiring a packet id when
  there is only one likely active run.
- Small tasks are handled directly or with a lightweight note instead of forced
  full packet assembly.
- Ambiguous target workspaces are not guessed silently.
```

## Non-Goals

- no server
- no daemon
- no database
- no always-on text interception outside Codex agent behavior
- no hidden approval system
- no replacement for file-grounded packet evidence
