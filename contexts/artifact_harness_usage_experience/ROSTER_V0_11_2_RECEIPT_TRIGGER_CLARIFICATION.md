# Roster v0.11.2 Receipt Trigger Clarification

Date: `2026-05-03`
Status: `direction`

## Purpose

`v0.11.2` tightens the `v0.11.1` Role Execution Receipt contract.

The problem is not the idea of receipts. The problem is that the current
contract can still be misread as:

- debug trace;
- a future product feature to plan;
- optional when the task feels simple;
- something to omit when the user says not to expand debug details.

`v0.11.2` makes the trigger rule explicit:

```text
Role Execution Receipt is part of the ordinary completion reply.
It is not debug trace.
```

## Observed Failure Pattern

Prompt shape:

```text
Roster，請幫我把使用者回饋整理成 2 週內可執行的產品改善方案。
需要同時考慮使用者痛點、工程可行性、產品優先順序和品質驗收。
不要展開完整 debug trace。
```

Observed output:

- Produced a useful two-week plan.
- Included role-summary as a future feature inside the plan.
- Did not include a current-turn `本次分工執行` receipt.

Why this fails:

- The answer handled the task through multiple perspectives.
- The task itself asked for product, engineering, priority, and quality
  judgment.
- The answer should have shown what those perspectives did in the current turn.
- `不要展開完整 debug trace` should suppress full trace, not suppress the ordinary
  receipt.

## Contract Patch

Add these rules to Roster behavior:

### 1. Receipt Is Not Debug Trace

`本次分工執行` is ordinary completion evidence.

It is not:

- full debug trace;
- reviewer trace;
- capability matrix;
- source audit;
- internal packet chain;
- runtime log.

Therefore:

```text
If the user says "不要展開 debug trace", still include a short receipt when the
task qualifies for one.
```

### 2. Receipt Is About The Current Answer

If the task asks Roster to design or improve a future role-summary feature, the
answer may discuss that feature as a product item.

But the answer itself must still include its own current-turn receipt when the
current task used multiple roles or perspectives.

Bad:

```text
未來應在任務完成後加入角色貢獻摘要...
```

Good:

```text
未來應在任務完成後加入角色貢獻摘要...

本次分工執行：
- 使用者體驗：整理首次使用卡點。
- 工程檢查：確認兩週內可落地的修改面。
- 品質檢查：確認不展開完整 debug trace，也不暴露內部控制層。

最後收斂：先修 onboarding、health wording、completion receipt 三個信任缺口。
```

### 3. Simplicity Does Not Remove The Receipt

Task simplicity changes receipt length, not the trigger.

Use a receipt when the task is non-trivial and any of these are true:

- the user asks Roster to consider multiple dimensions;
- the response uses multiple roles, perspectives, or checks;
- the result includes product, engineering, quality, domain, source, visual, or
  risk judgment;
- the user needs to judge whether declared roles actually did work.

For a small qualifying task, the receipt can be two or three lines.

### 4. Do Not Over-Formalize

The receipt should remain lightweight.

It should not turn into:

- a table unless a table is genuinely clearer;
- full debug trace;
- capability/source/assumption trace;
- a long audit report;
- internal governance explanation.

The default shape remains:

```text
本次分工執行：
- <角色或視角>：<做了什麼>
- <角色或視角>：<做了什麼>

最後收斂：<怎麼合成最後結論>
```

## Updated Decision Rule

Before finalizing a non-trivial Roster completion reply, run this check:

```text
Did I use more than one role, perspective, or quality check to produce this
answer?
```

If yes, include `本次分工執行`.

Then run this check:

```text
Did the user ask not to show debug trace?
```

If yes, keep the receipt short, but do not remove it.

Then run this check:

```text
Am I talking about role summaries as a future product feature?
```

If yes, also include a current-turn receipt for this answer.

## Good Completion Shape

```text
我把回饋收斂成三個兩週內可交付的改善項：入口指引、health 語意、任務完成摘要。

優先順序：
1. P0：入口指引統一。
2. P0：health check 拆成核心可用與選配能力。
3. P1：完成回覆加入角色貢獻摘要。

本次分工執行：
- 使用者體驗：把卡點整理成第一次叫用、安裝信心、完成可解釋性。
- 工程檢查：把可行改動限制在 help、README、health summary 和完成回覆格式。
- 產品排序：把直接影響第一次成功的項目排在 P0。
- 品質檢查：確認不展開完整 debug trace，也不新增大型架構。

最後收斂：這兩週先修新手信任與完成可解釋性，不碰大型 runtime 或 UI。
```

## Bad Completion Shape

```text
以下是 2 週方案...

P1：未來任務完成後加入角色貢獻摘要。
```

Why bad:

- The answer describes the future feature but does not prove this answer's own
  roles or perspectives did work.

## Relationship To v0.11.1

`v0.11.1` defines the receipt.

`v0.11.2` defines when not to omit it.

The practical rule:

```text
No debug trace != no receipt.
Future role-summary feature != current-turn receipt.
Simple qualifying task != no receipt.
```

## Acceptance Signal

This direction is behaving correctly when:

- a two-week product plan with UX, engineering, priority, and quality judgment
  includes a short `本次分工執行`;
- the receipt still appears when the user says not to expand debug trace;
- role-summary can appear as a product item, but the answer also includes its
  own current-turn receipt;
- receipts remain short and do not expose internal governance terms;
- first-touch replies remain unaffected.

## Out Of Scope

- Implementing runtime enforcement.
- Adding a new subagent runtime.
- Building debug/source/capability trace UI.
- Making every response include a receipt.
- Changing install, health, or slash invocation behavior in this direction note.

