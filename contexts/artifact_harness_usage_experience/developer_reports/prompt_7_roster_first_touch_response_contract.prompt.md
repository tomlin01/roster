# Prompt 7: Roster First-Touch Response Contract

## Context

Roster now has a repo-owned `roster` skill and install/health commands, but a
real user test in `/Users/tom/Documents/PHD/Vis_Math/Slides/Lecture1` showed the
first user-facing response still feels too much like an internal governance
closeout.

Example problematic response shape:

```text
I created a roster...
Daily team:
- Codex orchestrator
- Student
- Teacher
- Video Production
- Quality Management

Control-plane roles:
- HR...
- Team Architect...

This did not modify scene/render/video files...
continuity receipt...
```

User feedback:

- Ordinary users should not need to think about `HR`, `Team Architect`,
  `Capability Access Packet`, runtime mapping, control plane, continuity receipt,
  or Harness terminology in the first response.
- Roster can still use those layers internally.
- The response should not say or imply Roster cannot modify scene/render/video
  files. If this turn only prepared a roster, say that as current-turn scope,
  not as a capability limit.
- The first response should be short. Too much explanation makes the user think
  for too long.

## Goal

Make Roster's first-touch response behavior feel like a natural human-facing
staffing/project coordination surface:

- short
- useful
- plain language
- no internal control-plane leakage
- clear next invocation phrase
- optional file link at the end

## Required Changes

Update the repo-owned Roster behavior docs and target README/UX docs so ordinary
Roster replies follow this contract.

Likely files:

- `skills/roster/SKILL.md`
- `README.md`
- `contexts/artifact_harness_usage_experience/README.target-user-experience.draft.md`
- `contexts/artifact_harness_usage_experience/TARGET_README_INSTRUCTION.md`
- `contexts/artifact_harness_usage_experience/README.md`
- optionally `contexts/artifact_harness_usage_experience/ROSTER_DEVELOPER_PROMPTS.md`

Do not modify `/Users/tom/Documents/PHD/Vis_Math/Slides/Lecture1`; use it only
as the motivating example.

## Response Contract

For ordinary first-touch Roster replies:

1. Lead with the user-facing outcome.
2. Show only the working team/roles relevant to the user's task.
3. Keep role descriptions short and concrete.
4. Provide one next invocation phrase.
5. Add at most one durable file link if a file was written.
6. Do not explain internal design, governance boundaries, packet chain, or why
   roles are separated.
7. Do not mention `HR`, `Team Architect`, `Artifact Harness`, `Capability Access
   Packet`, `CAP`, runtime adapter, control plane, or continuity receipt unless
   the user explicitly asks for governance, review, debug, or implementation
   details.
8. Do not describe current-turn scope as a capability limit.

Good first-touch response shape:

```text
我已經把 Lecture1 的工作隊形整理好了：

- Student：看懂不懂、哪裡會卡
- Teacher：決定講解順序和例題
- Video Production：處理畫面、旁白和輸出
- Quality Management：做播放檢查和成品驗收

之後你可以直接說：
`用 Lecture1 team 跑下一個 unit`

我會照這個隊形把任務分下去，該改 slide、scene、render 或影片時再進到對應步驟。

文件在：`LECTURE1_TEAM_ROSTER.md`
```

Bad patterns:

- Saying `HR` and `Team Architect` are part of the user's day-to-day team.
- Saying "Roster only handles staffing and QA, not scene/render/video changes."
- Listing the full packet chain in the first response.
- Using `continuity receipt` in a normal user-facing closeout.
- Explaining "control plane" separation unless the user asks for review/debug.

## Internal Boundary

Preserve the actual workflow internally:

- Artifact Harness SPEC still owns rule / contract / acceptance / boundary.
- HR still owns staffing and role design only.
- Team Architect still owns collaboration pattern, shared artifacts, task graph,
  convergence, and CAP generation.
- CAP still owns skill/plugin/tool authorization, approval gates, and runtime
  allowlist.
- Runtime adapters remain execution layers only.

The change is presentation behavior, not governance ownership.

## Verification

Run:

- `python3 -m py_compile scripts/system_hub.py scripts/test_system_hub.py`
- `python3 scripts/test_system_hub.py`
- `git diff --check`

Also do a text audit:

- Roster first-touch examples should not expose `HR`, `Team Architect`,
  `Artifact Harness`, `CAP`, runtime adapter, control plane, or continuity
  receipt.
- Internal governance docs may still contain those terms.
- The good example should not imply Roster cannot execute future
  scene/render/video work.

Write a report to:

`contexts/artifact_harness_usage_experience/developer_reports/prompt_7_roster_first_touch_response_contract.report.md`

