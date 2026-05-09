# Implementation Spec

Task ID: `roster-v0_11_4-stable-team-status-receipt-2026-05-05`

## Goal

Implement Roster `v0.11.4` documentation and response-contract updates so
ordinary explicit Roster responses consistently declare:

- how many agents or role-agents are active;
- the current workflow stage;
- the useful output;
- current-turn role actions;
- convergence.

## Required Behavior

For explicit Roster invocation:

- `Roster，...`
- `Roster, ...`
- `/roster ...`
- `@roster ...`
- installed Roster surfaces

When the task is non-trivial, Roster should use:

```text
agent count + workflow state -> useful work -> 本次分工執行 -> convergence
```

## Agent Count Requirement

Roster must declare active agent count.

Examples:

```text
本次啟用：1 個 agent（單一整合流程）
```

```text
本次啟用：5 個 agent（使用者研究、客服分析、產品排序、工程評估、品質驗收）
```

Do not force every task to be multi-agent.

If one agent is enough, declare the one-agent workflow.

## Workflow State Requirement

Roster must declare the current stage when useful:

```text
目前階段：初步規劃
```

For future-artifact prompts where the user asks not to produce the artifact yet:

```text
目前階段：初步規劃；正式 artifact 這輪先不產出。
```

This must be framed as current-turn stage, not capability limitation.

## Runtime Honesty

Agent count does not imply actual parallel runtime execution.

Use neutral wording such as:

```text
本次啟用：5 個 role-agents（單一回覆中分工處理）
```

Do not claim:

```text
5 個 agent 已並行執行。
```

unless actual subagents were spawned.

## Likely Files To Update

- `skills/roster/SKILL.md`
- `plugins/roster/commands/roster.md`
- `README.md`
- `contexts/artifact_harness_usage_experience/README.md`
- `contexts/artifact_harness_usage_experience/README.target-user-experience.draft.md`
- `contexts/artifact_harness_usage_experience/ROSTER_MILESTONE_ROADMAP.md`
- `contexts/artifact_harness_usage_experience/ROSTER_V0_11_4_STABLE_TEAM_STATUS_RECEIPT.md`

## Must Preserve

- Do not expose internal governance terms in ordinary replies.
- Do not make first-touch responses long.
- Do not require runtime subagent spawning.
- Do not change install, health, packet-route, artifact-harness, slash, or
  plugin routing behavior unless absolutely necessary.
- Do not make every task use a fixed team size.

## Examples To Add Or Update

Add at least:

1. A fuzzy future-artifact planning prompt that naturally uses 5 agents.
2. A one-agent Roster prompt showing one-agent workflow.
3. A bad example where useful perspectives are listed but agent count and
   workflow state are missing.

## Verification

Run:

```sh
python3 -m py_compile scripts/system_hub.py scripts/test_system_hub.py
python3 scripts/test_system_hub.py
git diff --check
```

Also run a text audit:

- `v0.11.4` examples include `本次啟用`.
- one-agent examples include `1 個 agent`.
- future-artifact examples say current stage, not capability limit.
- ordinary examples do not claim parallel runtime execution.

