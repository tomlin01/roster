# Target README Instruction

This instruction defines the target shape for the final user-facing
`Roster` README.

It is not a claim that the current implementation already satisfies every item.
It is the product target that future implementation and documentation work
should converge toward.

## Core Direction

`Roster` is a local Codex-native staffing-and-project-planning surface.

It should feel like Codex is helping the user organize artifact work, not like
the user is operating a packet system manually.

The README must lead with the human experience:

- what the kit helps with
- what the user types
- where the work is written
- how to resume
- how install works on another machine
- how reviewers can inspect evidence

Internal vocabulary such as Artifact Harness SPEC, Team Operating Packet,
Capability Access Packet, runtime mapping, packet id, and adapter commands
should appear only after the user-facing path is clear.

## Required README Structure

The final README should use this order:

1. One-screen value statement
2. Primary user invocation
3. Workspace and output behavior
4. Typical Codex response
5. Resume and active-run discovery
6. Permission and tool-access summary
7. Install on another machine
8. Reviewer/debug evidence
9. Formal ownership boundaries
10. Current status, if the implementation is still partial

The draft warning or implementation-status warning must not occupy the first
screen. If needed, move it into `Current Status`.

## Primary Invocation Requirement

The README must tell a human user exactly what to type.

It cannot only list possible surfaces such as skill, mention, plugin, or slash
command. It must choose one primary path and mark others as optional.

Target wording shape:

```text
Primary path:
In Codex, type: Roster, <your artifact task>

Then say the artifact task in ordinary language.
```

Current evidence says `@roster` is not a working installed Codex mention. Do
not publish `@roster` as the primary path until a Codex mention/plugin/app layer
proves it in the actual CLI or GUI. If a future verified primary path is not
plain `Roster, ...`, replace this section with the real installed surface.

Specialized aliases may remain supported, but they are secondary convenience
paths and should not appear on the first screen unless the user asks for review,
staffing, debug, or implementation details. The user should not have to include
a keyword in the message body if they intentionally invoked the kit.

## Basic Use Requirement

The README must show ordinary user language first.

Good examples:

```text
Roster, 幫我把這個 slide 任務安排好。
```

```text
Roster, organize the task boundary and handoff for this artifact.
```

```text
Roster, 這個任務現在卡在哪裡？
```

The README should not make `brain.sh`, `packet-route`, or `artifact-harness` the
basic usage path.

## First-Touch Response Requirement

For ordinary first-touch Roster replies, keep the response short and
action-oriented:

- show the useful working team/roles
- keep role descriptions concrete
- provide one next invocation phrase
- add at most one durable file link if a file was written

Do not mention `HR`, `Team Architect`, `Artifact Harness`, `Capability Access
Packet`, `CAP`, runtime adapter, control plane, or continuity receipt in the
first response unless the user explicitly asks for governance, review, debug, or
implementation details.

Do not describe current-turn scope as a capability limit. If this turn only
prepared the roster, say that directly and make clear that future Roster runs can
assign scene, render, video, QA, or other artifact work to the relevant roles.

## Quality Response Requirement

Quality must read as a built-in Roster behavior, not as another layer the user
has to operate manually.

For prompts such as:

```text
Roster，幫我看 Lecture1 的 Quality 要怎麼設定
```

The README and skill instructions should show a short response that separates:

- short-term checks for whether the current artifact, unit, scene, render,
  table, draft, or output can be delivered now
- long-term improvements for recurring team, workflow, checklist, or template
  issues

If an Artifact Harness SPEC exists, its acceptance checks remain the source of
truth internally, but the first user-facing Quality answer should not expose
`HR`, `Team Architect`, `CAP`, runtime adapter, control plane, or packet-chain
terms.

## Workspace Selection Requirement

The README must state how Codex chooses the output workspace.

Target rule:

- The active Codex workspace is the default output root.
- Packet files are written under that workspace, not under the `Roster` kit
  repo by default.
- If the active workspace is ambiguous, Codex should ask one short location
  question before writing files.

Target output path:

```text
<active-workspace>/contexts/artifact_harness_runs/<packet-id>/
<active-workspace>/contexts/artifact_harness_registry.json
```

## Cross-Machine Install Requirement

The README must provide executable user steps for a fresh machine.

It should cover:

1. install or register the Codex-native invocation surface
2. provide local credentials or auth for LLM/provider access
3. run a health check
4. interpret success or missing-auth / missing-provider failure

Target wording shape:

```text
On a new machine:

1. Clone or copy the kit.
2. Install the `roster` skill from the kit root.
3. Use the current natural-language invocation surface: `Roster, ...`.
4. Configure local LLM credentials.
5. Run `roster-health` with the same Codex home and target workspace.
6. Confirm that the skill surface, packet output, and LLM path work.
```

Do not imply that local auth, API keys, personal memory, model caches, or
machine-local overlays are portable repo content.

## Reviewer And Debug Command Requirement

Debug commands may remain in the README, but they must be clearly marked as
reviewer/debug evidence, not basic usage.

If commands use `./scripts/brain.sh`, the README must say they are run from the
`Roster` kit root.

Better final options:

- show the installed invocation path first
- use an absolute or resolved kit command only in generated diagnostics
- keep repo-root commands inside a reviewer/debug section

## Human-Friendly Response Requirement

The README should model the expected Codex response in plain language.

Good response shape:

```text
I set up the task brief, role plan, tool-access note, and review checklist.
The files are in your workspace under contexts/artifact_harness_runs/...
```

Formal packet names should appear as audit links after the plain-language
summary.

## Resume Requirement

The README must make clear that the user should not need to remember packet ids
for normal recovery.

Target behavior:

- Codex inspects the current workspace registry and recent packet runs.
- If there is one likely active run, Codex summarizes status, blocker, and next
  action.
- If there are several likely runs, Codex asks one short disambiguation question
  using mission titles or artifact names.

## Permission Summary Requirement

The README should show concise permission summaries:

```text
No external tools needed.
```

```text
Needs filesystem writes only.
```

```text
Needs LLM/provider access; no external runtime.
```

```text
Needs approval before network/plugin/runtime execution.
```

The formal allowlist and gates remain in the Capability Access Packet.

## Boundary Requirement

The final README must preserve these ownership boundaries:

- Artifact Harness owns rules, contract, acceptance, and boundary.
- HR owns staffing and role design only.
- PM remains an optional natural alias for project-planning language, not the
  primary product name.
- Team Architect owns collaboration pattern, shared artifacts, task graph,
  convergence, and CAP generation.
- Capability Access Packet owns skill, plugin, tool authorization, approval
  gates, and runtime allowlist.
- Runtime adapters execute; they do not become governance owners.

## Acceptance Checklist

The final README is acceptable when:

- a human knows what to type within the first screen
- a human knows where files will be written
- a human can understand basic use without knowing packet vocabulary
- a new-machine user sees concrete install and health-check steps
- reviewer/debug commands are clearly separated from normal use
- shell commands are not presented as the primary interface
- the README does not claim unverified `@`, `/`, plugin, skill, LLM, or install
  behavior as already working
