# Roster v0.11.3 Invocation Response Wrapper

Date: `2026-05-04`
Status: `direction`

## Purpose

`v0.11.3` fixes a higher-level response problem exposed after `v0.11.2`.

`v0.11.1` defined the Role Execution Receipt.
`v0.11.2` clarified when not to omit it.

But real testing still showed a deeper failure:

```text
Roster was invoked, but the answer still looked like a generic assistant answer.
```

`v0.11.3` defines the response wrapper that should activate when the user
explicitly invokes Roster.

Core rule:

```text
Explicit Roster invocation should produce Roster-shaped work.
```

This does not mean every answer becomes long. It means non-trivial Roster
answers should visibly follow Roster's agent-coordination idea:

```text
entry framing -> useful work -> role-action receipt -> convergence
```

## Observed Failure Pattern

Prompt shape:

```text
Roster，請幫我把客服回饋整理成 2 週內可執行的產品改善方案。
你需要同時考慮使用者痛點、工程可行性、產品優先順序和品質驗收，
但不要展開完整 debug trace。
```

Observed output:

- Produced a decent two-week plan.
- Did not start with a Roster-style work frame.
- Did not include `本次分工執行`.
- Ended with a generic next-prompt suggestion.
- Felt like a product consultant response, not a Roster task run.

Why this fails:

- The user explicitly invoked Roster.
- The task was non-trivial and multi-perspective.
- The response should have shown at least a compact working frame and a compact
  role-action receipt.
- `不要展開完整 debug trace` should suppress detailed trace only, not the Roster
  wrapper.

## Contract Patch

Add these rules to Roster behavior.

### 1. Invocation Activates Roster Style

When the user invokes:

- `Roster，...`
- `Roster, ...`
- `/roster ...`
- `@roster ...`
- an installed Roster skill/plugin surface

Roster should not answer as a generic assistant unless the task is truly trivial.

For non-trivial tasks, include a lightweight Roster wrapper:

```text
entry framing -> useful work -> role-action receipt -> convergence
```

### 2. Entry Framing Is Not Full First-Touch

First-touch UX should stay short. But explicit Roster invocation should still
show how the task is being handled.

Good entry framing:

```text
我先用產品、工程、品質三個視角把這段回饋收斂成兩週方案。
```

```text
我會用規劃、可行性、驗收三個視角處理，不展開完整 debug trace。
```

Bad entry framing:

```text
使用 `Roster` skill：這裡把回饋轉成產品改善方案。
```

Why bad:

- It announces implementation machinery instead of presenting Roster's working
  stance.
- It does not show the user which roles or perspectives will shape the work.

### 3. Useful Work Still Comes First

The answer should still lead with useful output.

Do not make users read a long team explanation before the artifact.

Good shape:

```text
我先用產品、工程、品質三個視角收斂這個兩週方案。

<actual plan, review, artifact, or decision>

本次分工執行：
...

最後收斂：
...
```

Bad shape:

```text
以下是 Roster 的內部隊形、控制邊界、packet chain...
```

### 4. Completion Receipt Is Required For Qualifying Roster Runs

For explicit Roster invocation, a non-trivial task qualifies for a receipt when
any of these are true:

- the task asks for multiple dimensions;
- the answer uses multiple roles or perspectives;
- the answer includes product, engineering, quality, domain, source, visual, or
  risk judgment;
- the answer makes a plan, roadmap, review, acceptance decision, or artifact
  recommendation.

When qualifying, include:

```text
本次分工執行：
- <角色或視角>：<做了什麼>

最後收斂：<如何合成結論>
```

This remains ordinary completion behavior, not debug trace.

### 5. Do Not Substitute A Next Prompt For Convergence

Roster may give a next invocation phrase when it is genuinely useful, especially
after first-touch setup.

But a generic next-prompt suggestion must not replace convergence.

Bad ending:

```text
建議下一句指令：
`Roster，請把這份方案拆成工程 tickets...`
```

Why bad:

- It turns the closeout into a generic assistant continuation prompt.
- It does not show how the current Roster work converged.

Better ending:

```text
最後收斂：這兩週先處理交付風險、匯出錯誤和通知排序，不重做整個儀表板。
```

Optional next phrase can appear only after the convergence line, and only when
it adds value.

## Updated Decision Rule

Before answering an explicit Roster invocation, run this check:

```text
Is this a non-trivial Roster task?
```

If yes, include a Roster wrapper:

```text
entry framing -> useful work -> role-action receipt -> convergence
```

Then run this check:

```text
Would adding the wrapper make the answer too heavy?
```

If yes, compress the wrapper. Do not remove it.

Compressed wrapper:

```text
我用產品、工程、品質三個視角收斂。

<short answer>

本次分工執行：產品排序、工程可行性、品質驗收各完成一輪檢查。
最後收斂：先做最小可交付修正，不擴張架構。
```

Then run this check:

```text
Did the user ask not to show debug trace?
```

If yes, keep the wrapper and receipt short. Do not remove them.

## Good Completion Shape

```text
我先用產品、工程、品質三個視角把這段客服回饋收斂成兩週方案。

**2 週改善方案**

| 優先 | 改善項 | 對應痛點 | 2 週內做法 |
|---|---|---|---|
| P0 | 本週交付風險摘要 | 主管只想知道交付影響 | 儀表板頂部新增交付風險區塊：問題、owner、截止日、下一步 |
| P0 | 匯出失敗可理解化 | 報表失敗且錯誤看不懂 | 改成可行動訊息：原因、重試、支援代碼、替代格式 |
| P1 | 通知優先順序 | 通知太多沒有排序 | 分成阻塞交付、今天處理、資訊三類 |

**品質驗收**
- 新使用者 5 秒內看到下一步。
- 主管不用點進細節也能看到本週交付風險。
- 匯出失敗不得只顯示技術碼。

本次分工執行：
- 產品視角：把痛點轉成 P0/P1，先處理交付風險與匯出信任。
- 工程視角：把改動限制在 dashboard 區塊、通知分組和錯誤文案。
- 品質視角：補上首次進入、通知排序、匯出失敗和主管視角驗收。

最後收斂：先修交付風險、匯出錯誤和通知排序，不重做整個儀表板。
```

## Bad Completion Shape

```text
以下是 2 週改善方案...

建議下一句指令：
`Roster，請把這份方案拆成工程 tickets...`
```

Why bad:

- It omits Roster entry framing.
- It omits current-turn role execution receipt.
- It substitutes a generic next prompt for convergence.

## Relationship To v0.11.2

`v0.11.2` says:

```text
No debug trace != no receipt.
```

`v0.11.3` adds:

```text
Explicit Roster invocation != generic assistant answer.
```

Together:

```text
Roster invocation + non-trivial task -> Roster wrapper.
Roster wrapper -> entry framing + useful work + receipt + convergence.
```

## Acceptance Signal

This direction is behaving correctly when:

- a fresh-thread `Roster，...` non-trivial planning prompt starts with compact
  role/perspective framing;
- the answer still leads with useful output, not internal governance;
- the answer includes `本次分工執行` when multiple perspectives contributed;
- the answer ends with convergence, not only a suggested next prompt;
- `不要展開 debug trace` keeps the wrapper short but does not remove it;
- ordinary examples avoid internal governance terms and misleading runtime-agent
  claims;
- genuinely trivial tasks can stay direct without a heavy wrapper.

## Out Of Scope

- Runtime enforcement.
- New subagent runtime.
- New slash command behavior.
- Install or health behavior changes.
- Making every Roster response long.
- Exposing internal packet, control-plane, CAP, or runtime details in ordinary
  replies.

