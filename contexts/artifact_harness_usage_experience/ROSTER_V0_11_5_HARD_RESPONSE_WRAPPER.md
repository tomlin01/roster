# Roster v0.11.5 Hard Response Wrapper

Date: `2026-05-10`
Status: `direction`

## Purpose

`v0.11.4` made Roster declare active role-agents and workflow stage, but real
testing still showed response drift:

```text
Roster produced a useful planning answer, but it skipped the team-status
header, skipped the role-action receipt, and leaked internal route diagnostics.
```

The content quality can be acceptable while the Roster behavior is still wrong.
For Roster, the user should be able to tell:

- how many role-agents were used;
- what stage the work is in;
- which roles actually contributed;
- what the current answer converged to.

Core rule:

```text
Non-trivial explicit Roster invocation must pass the response wrapper before
the answer is sent.
```

This is a presentation and behavior contract. It does not require actual
runtime subagent spawning.

## Observed Failure

Test prompt shape:

```text
Roster，我想做一個有點奇怪的東西：一個「漂浮城市的夜市導覽」...

它未來可能變成簡報、互動網頁、遊戲規則或展示原型，但現在先不要產出任何正式內容...
```

Observed response:

- correctly treated the task as early planning;
- correctly avoided producing formal content;
- gave useful decomposition;
- did not declare active role-agent count;
- did not include a current-turn role-action receipt;
- did not end with a stable convergence line;
- exposed `route check`, `preference`, and `packet` language in an ordinary
  user-facing reply.

Why this fails:

- the user explicitly invoked Roster;
- the task was non-trivial and multi-perspective;
- the user intentionally did not mention agents or workflow;
- the test was whether Roster still behaves like Roster without being prompted;
- internal diagnostics leaked into a normal reply.

## Hard Gate

Before sending any ordinary non-trivial Roster reply, silently verify that the
answer contains all five parts:

```text
本次啟用：...
目前階段：...
useful work for the user's actual request
本次分工執行：...
最後收斂：...
```

If one part is missing, rewrite the answer before sending.

Do not tell the user that this gate ran.

## Response Before Routing

For ordinary planning-only turns, Roster should answer before adapter mechanics.

If the user says the formal artifact, PRD, review, file, or content draft should
not be produced this turn, do not run routing merely to decide whether Roster can
answer. Apply the wrapper and produce the planning answer.

Treat words such as `未來`, `之後`, `later`, and `future` as artifact-direction
words unless they are paired with an explicit memory/default request:

- remember / save / record / memorize;
- `記住` / `記錄`;
- default / prefer / always;
- `預設` / `每次` / `以後都`.

The phrase `之後可能變成...` is not preference memory.

## Trigger

Apply the gate when all are true:

- the user explicitly invokes Roster through `Roster`, `/roster`, `@roster`, or
  the installed Roster surface;
- the task is not a trivial one-line answer;
- the answer uses or should use multiple dimensions, roles, perspectives,
  checks, risks, sources, domains, artifacts, or future execution paths.

The gate still applies if the user says:

- `先不要產出正式內容`;
- `不要展開 debug trace`;
- `先看初步規劃`;
- `不用建立檔案`;
- `簡短就好`.

Those phrases reduce verbosity. They do not remove team-status visibility.

## Internal Diagnostics Barrier

Ordinary replies must not mention:

- `route check`
- `packet-route`
- `artifact-harness`
- `preference`
- `roster_preferences`
- `registry`
- `routing score`
- `CAP`
- `runtime adapter`
- `control plane`

Use those terms only in review, debug, implementation, or explicit routing
explanation mode.

If background routing evidence matters, translate it:

Bad:

```text
我做了 route check，因為 preference route 誤判，所以沒有建立 packet。
```

Good:

```text
目前階段：初步規劃；這輪不建立正式檔案。
```

## Good Response Shape

```text
本次啟用：4 個 role-agents（體驗規劃、互動設計、資料紀錄、品質檢查；單一回覆中分工處理）
目前階段：初步規劃；正式 artifact 這輪先不產出。

我先把它拆成「3 分鐘決策體驗」，不是先拆成簡報、網頁、遊戲或原型。

**第一輪先確認**
1. 使用者 3 分鐘後要理解什麼、比較什麼、留下什麼紀錄。
2. 攤位之間是否有真正取捨，而不是只有視覺風格差異。
3. 選擇紀錄未來要服務展示回放、個人化續接、研究分析，還是互動證明。
4. 未來載體需要哪些條件才值得選。

**容易走偏**
- 太早選媒介，把體驗問題誤解成版型問題。
- 世界觀太多，3 分鐘內使用者只記得設定但不知道怎麼選。
- 攤位只有風格差異，沒有風險、收益、路線或情緒代價。

本次分工執行：
- 體驗規劃：把任務收斂成理解、比較、選擇、紀錄四段。
- 互動設計：檢查攤位選項是否形成真正取捨。
- 資料紀錄：判斷選擇紀錄要支撐哪種後續用途。
- 品質檢查：找出太早選媒介、世界觀過量、選擇無取捨三個偏移風險。

最後收斂：這輪只固定判斷框架；下一輪才決定是否進入正式內容、原型或規則。
```

## Bad Response Shape

```text
我會先把它拆成「3 分鐘決策體驗」...

建議拆法：
1. ...

另外我做了 route check...
```

Why bad:

- useful planning exists, but Roster team state is invisible;
- role actions are not auditable;
- internal diagnostics are exposed;
- there is no stable convergence line.

## Acceptance Signal

This release behaves correctly when:

- fuzzy non-trivial Roster prompts include `本次啟用`;
- future-artifact prompts include `目前階段` and say formal output is not
  produced in the current turn;
- `本次分工執行` appears when multiple roles or checks contributed;
- the closeout starts with `最後收斂`;
- ordinary replies do not mention route checks, packet-route, preferences,
  registries, CAP, runtime adapters, or control plane.
- future-artifact wording such as `未來可能` or `之後可能` is not routed as
  preference memory.

## Out Of Scope

- Runtime enforcement.
- Required actual subagent spawning.
- New route, install, health, or packet engine behavior.
- Making every small answer long.
- Full debug trace in ordinary replies.
