# CLI Behavior Test

Task ID: `roster-v0_11_3-invocation-response-wrapper-2026-05-04`
Date: `2026-05-04`
Status: `pass`

## Purpose

Run a branch-local CLI behavior test for the `v0.11.3` Invocation Response
Wrapper before merge/install.

This test checks whether a fresh CLI agent can use the current branch docs to
produce a Roster-shaped answer for a non-trivial explicit Roster invocation.

## Test Mode

`branch-local contract test`

The CLI test should read the repo-local Roster contract files from this branch
instead of relying only on the installed Codex skill copy. This avoids confusing
branch behavior with the currently installed Roster version.

## Required Reads

- `skills/roster/SKILL.md`
- `contexts/artifact_harness_usage_experience/ROSTER_V0_11_3_INVOCATION_RESPONSE_WRAPPER.md`
- `contexts/artifact_harness_usage_experience/ROSTER_V0_11_2_RECEIPT_TRIGGER_CLARIFICATION.md`

## Test Prompt

```text
Roster，請幫我把客服回饋整理成 2 週內可執行的產品改善方案。你需要同時考慮使用者痛點、工程可行性、產品優先順序和品質驗收，但不要展開完整 debug trace。

回饋：
新使用者說，第一次進到儀表板時不知道下一步該做什麼。通知太多但沒有優先順序。匯出報表有時會失敗，但錯誤訊息看不懂。主管只想知道哪些問題會影響本週交付。
```

## Acceptance Criteria

Pass when the answer:

- starts with compact Roster entry framing, for example
  `我先用產品、工程、品質三個視角...`;
- provides the useful two-week plan before any detailed trace;
- includes `本次分工執行`;
- lists concrete role/perspective actions, not empty role titles;
- includes a convergence line such as `最後收斂：...`;
- does not replace convergence with only a generic next-prompt suggestion;
- does not expose internal governance terms in the ordinary answer;
- does not claim separate runtime/subagent execution.

Fail when the answer:

- starts directly as a generic product plan with no Roster entry framing;
- omits `本次分工執行`;
- treats role contribution only as a future product feature;
- ends only with a suggested next prompt;
- exposes internal packet/control-plane terms in the ordinary answer.

## CLI Command

```sh
codex exec -C /Users/tom/Documents/PHD/codex-cns -s read-only '<prompt>'
```

## Result

- `pass`

CLI output satisfied the branch-local v0.11.3 response contract:

- Started with compact Roster entry framing:
  `我用產品、工程、品質四個視角把回饋收斂成兩週方案，不展開完整 debug trace。`
- Produced the useful two-week plan before role receipt.
- Included `本次分工執行`.
- Listed concrete role/perspective actions:
  - 使用者體驗：整理痛點類型。
  - 產品排序：把交付與主管判斷排為 P0。
  - 工程可行性：限制到兩週內可做的 UI、文案、分類規則與流程修正。
  - 品質驗收：為每個改善項設定可觀察完成條件。
- Ended with a convergence line:
  `最後收斂：這兩週先讓使用者知道「現在該做什麼、哪些事最急、匯出失敗怎麼處理、主管該看哪裡」，不擴張成大型儀表板重構。`
- Did not expose internal governance, packet, CAP, runtime, or control-plane terms.
- Did not claim separate runtime/subagent execution.

CLI notes:

- Command ran through `codex exec` in read-only mode from the repo root.
- Local CLI reported `codex-cli 0.125.0`.
- CLI emitted non-blocking environment warnings after the answer
  (`legacy_notify`, rollout record, MCP shutdown warnings). These did not affect
  the generated Roster response.
