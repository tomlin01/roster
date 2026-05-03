# Intent Record

Task ID: `roster-v0_10-capability-aware-role-execution-2026-05-03`
Date: `2026-05-03`
Workspace: `/Users/tom/Documents/PHD/codex-cns`
Main Thread: `Roster v0.10 planning`
Source: `chat`

## Purpose

Preserve the user's intent and context for the next Roster milestone after
`v0.9.0`. This file is evidence for translation. It is not the implementation
contract.

## Original User Language

```text
所以應該說v0.10.0是讓AGENT更好的規劃使用LLM 平台的工具
```

```text
OK，那方向定下來就可以開始寫文件了
```

```text
應該可以開branch交付v0.10.0的工作
```

## User Outcome

What the user wants to be true after the work:

- Roster v0.10.0 is framed as planning how roles use LLM platform
  capabilities, not just subagents.
- Roster can express that roles may need web search, browser, visual capture,
  CV, filesystem/code execution, specialist skills, plugins/connectors, or
  subagents.
- The implementation remains honest about what Roster owns versus what the
  active host/runtime provides.
- The work is delegated as a bounded branch/task packet, following the existing
  main-thread -> developer-thread -> reviewer-thread workflow.

## Why It Matters

What problem this solves for the user's workflow:

- The user expects to delegate to Roster without manually deciding which role
  should use which LLM platform tool.
- Roster's role model now needs execution awareness: roles should carry
  capability needs and fallbacks, not only names, work cards, and interaction
  edges.
- This prevents overclaiming that every role can automatically use web search,
  browser, CV, plugins, or subagents on every host.

## Main-Thread Interpretation

Translate the user's language into practical engineering meaning:

- `v0.10.0` should be named `Capability-Aware Role Execution`.
- Subagent policy should be a subsection, not the headline.
- The planning chain is:
  `role -> work -> interaction -> capability need -> availability -> fallback`.
- The first implementation should update Roster docs/templates and add a
  conservative runtime/capability report where practical.

## Ambiguities

Items that are not yet fully specified:

- How much capability availability can be detected reliably from a local Codex
  repo command versus what remains host/UI-dependent.
- Whether capability availability should later be recorded in packet artifacts
  or remain a health/runtime diagnostic.
- Whether low-risk public web lookup should be silently usable by a role or
  disclosed in user-facing text only after it is used.

## Constraints From User

Hard constraints:

- Do not drift into a Rust rewrite, new runtime architecture, persistent server,
  automatic connector login, or external action system.
- Do not make every role a separate subagent.
- Do not make Roster replace CAP authorization or runtime adapter boundaries.

Soft preferences:

- Keep ordinary first-touch UX natural and not tool-mechanical.
- Make the model practical enough that later real roles can use current host
  capabilities such as web, browser, CV, filesystem/code execution, and skills.
- Preserve the current v0.7-v0.9 UX improvements.

## Parent Spec Check

Is this too broad for one developer pass?

- Parent spec: `yes`
- Child spec for this pass: implement the smallest useful `v0.10.0`
  capability-aware role execution surface in docs/templates and conservative
  health/capability reporting. Do not implement new adapters or automatic
  runtime delegation.

## Do Not Infer

Things the developer/reviewer must not assume:

- Do not assume Roster ships its own web-search adapter.
- Do not assume every Codex/Claude/other host exposes the same capabilities.
- Do not assume `@roster` or `/roster` UI visibility is proof of every platform
  capability.
- Do not treat capability need as authorization.
- Do not expose capability matrices in ordinary first-touch replies.
