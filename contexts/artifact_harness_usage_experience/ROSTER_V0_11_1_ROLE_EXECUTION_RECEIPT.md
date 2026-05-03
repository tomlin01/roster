# Roster v0.11.1 Role Execution Receipt

Date: `2026-05-03`
Status: `direction`

## Purpose

`v0.11.1` defines the user-visible evidence layer after Roster has already
chosen a team shape and completed a non-trivial task.

The goal is not to make ordinary replies longer or expose the full internal
packet chain. The goal is to let the user judge whether the declared roles
actually did work.

This is also a style contract. After the first-touch reply, Roster should still
sound like an agent coordination system: roles do work, exchange checks, surface
evidence, and converge. It should not collapse back into a generic single-agent
summary unless the task was actually handled that way.

Core question:

```text
Did the roles Roster named actually contribute, and what did each one do?
```

## Problem

The current first-touch direction works well when the user is just starting a
task. It keeps Roster natural and avoids forcing the user to understand internal
governance.

But after a task is completed, a response that only gives the final answer can
hide whether the multi-role plan was real or decorative.

The user needs enough evidence to judge:

- whether the named roles actually executed their responsibilities;
- whether any role was only a label;
- which role produced or checked which conclusion;
- whether external lookup, local file inspection, code execution, visual review,
  or another capability was actually used;
- whether Roster simulated multiple roles in one agent or used separate runtime
  agents.

## Response Layers

Roster should use three presentation layers.

### 1. First-Touch Reply

Use when the user first asks Roster to organize or start a task.

Behavior:

- keep it short;
- show the smallest useful team shape;
- avoid internal governance terms;
- give a natural way to proceed when useful.

First-touch replies do not need a receipt unless the user asks for one.

### 2. Ordinary Completion Reply

Use after a non-trivial task is completed or a roadmap, review, plan, report,
or artifact decision has been produced.

Behavior:

- lead with the user-facing outcome;
- include a short `本次分工執行` section;
- list only roles that actually contributed;
- describe actions, not just titles;
- keep each line concrete enough that the user can judge whether the role did
  real work;
- preserve the agent-coordination style by showing role behavior, handoff,
  evidence, or convergence when those happened;
- do not include full capability matrices, packet names, CAP, runtime adapters,
  or internal control-plane terms.

Example:

```text
我已經把 v0.11.0 收斂成第一次使用體驗版本。

本次分工執行：

- 產品規劃：把需求收斂成 install/onboarding/invocation 的 5 點 roadmap。
- 安裝體驗：檢查 `/roster`、`@roster`、`Roster, ...` 的入口差異。
- 外部參考：比對 gstack 的 workflow 設計，抽出可借鑑的 stage 概念。
- 品質檢查：確認範圍沒有膨脹到 marketplace、daemon 或完整 runtime。

結論是：v0.11.0 應先把「裝得上、叫得起、第一次知道怎麼用」做好。
```

### 3. Review / Debug / Verification Reply

Use when the user asks for review, debug, verification, implementation detail,
or multi-agent evidence.

Behavior:

- include role trace;
- include capability trace;
- include source trace when external or local evidence was used;
- include assumptions and unverified items;
- identify whether work was done by separate runtime agents or simulated role
  perspectives inside one agent.

This layer can expose internal names when they are needed for review, but it
should still separate user-facing conclusions from governance details.

## Role Execution Receipt

An ordinary completion reply should include a lightweight receipt when the task
used more than one meaningful role or perspective.

Recommended label:

```text
本次分工執行
```

Receipt rules:

- `list only executed roles`
  - Do not list a role that did not contribute.
- `describe behavior`
  - Say what the role checked, produced, compared, or decided.
- `keep the agent idea visible`
  - The reply should make it clear that Roster coordinated roles or
    perspectives, not merely rewrote the final answer.
- `show convergence`
  - When useful, include how the role outputs were combined into the final
    decision, artifact, or next state.
- `avoid title theater`
  - Do not write `Reviewer participated` without saying what was reviewed.
- `separate role from runtime`
  - If no separate subagent was spawned, say `角色分工` or `視角分工`, not
    `多個 agent 已並行執行`.
- `surface missing capability`
  - If a role needed web, browser, CV, plugin, connector, or subagent capability
    but could not use it, mark that limitation briefly.
- `attach evidence only when useful`
  - External lookup, local file inspection, code execution, tests, or visual
    checks should point to a source, file, or result when that evidence matters.

## When To Include The Receipt

Include the receipt by default for:

- multi-role roadmap or project planning;
- artifact reviews;
- quality-direction tasks;
- external reference comparisons;
- tasks using web, filesystem, code execution, CV, browser, plugin, connector,
  specialist skill, or subagent capability;
- tasks where the user needs to know whether a declared role did real work.

Do not include the receipt by default for:

- trivial one-step answers;
- pure discussion or brainstorming before execution;
- first-touch team proposals before work has actually been done;
- cases where the receipt would be longer than the useful answer.

## Style Boundary

First-touch UX should remain minimal. Later Roster replies can be more explicit,
but they should still avoid becoming either:

- a generic assistant summary with no visible role execution; or
- an internal audit log full of governance and runtime mechanics.

The target style is:

```text
outcome -> role actions -> convergence
```

Good later-response shape:

```text
我已經把方案收斂成三個可執行方向。

本次分工執行：

- 需求整理：把你的目標拆成安裝、呼叫、第一次成功任務三個問題。
- 技術檢查：確認目前入口和健康檢查能支撐這三個問題。
- 品質檢查：刪掉超出這版範圍的 marketplace、daemon 和完整 runtime。

最後收斂：這版先補 onboarding 和 role-action receipt，不擴張底層架構。
```

Bad later-response shape:

```text
以下是三點建議...
```

This may be a useful answer, but it does not preserve Roster's agent
coordination identity when a multi-role task was declared.

## Relationship To v0.10.0

`v0.10.0` makes capability needs explicit inside role planning.

`v0.11.1` makes completed role behavior visible enough for the user to judge.

The relationship is:

```text
v0.10.0: role -> work -> interaction -> capability need -> availability -> fallback
v0.11.1: completed role -> action taken -> evidence or limitation -> contribution
```

`v0.11.1` does not require every role to spawn a separate runtime agent. It does
require Roster to be honest about whether work was done as:

- a separate runtime agent;
- a delegated subagent;
- an installed skill or plugin;
- a local tool call;
- or a simulated perspective inside the coordinating agent.

## Acceptance Signal

This direction is behaving correctly when:

- ordinary completion replies show who did what without exposing the full
  governance stack;
- users can tell whether a named role actually contributed;
- source-backed roles can point to their evidence when needed;
- missing capabilities are visible instead of silently hidden;
- first-touch replies remain short and natural;
- review/debug replies can expand into a full role, capability, source, and
  assumption trace.

## Out Of Scope

- Forcing every role into a separate subagent.
- Building a new runtime or message bus.
- Replacing Artifact Harness, Team Architect, CAP, runtime mapping, or
  verification ownership.
- Adding a persistent memory database.
- Making ordinary replies into full audit logs.
