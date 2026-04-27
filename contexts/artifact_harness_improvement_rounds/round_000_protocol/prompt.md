# Round 000 Protocol Prompt

## Original Prompt

```text
我們要開始 artifact-harness improvement rounds。請先建立一個輕量文件交換區，不要先修功能。

目標：
建立穩定的 prompt -> developer report -> reviewer notes -> verification evidence 交換格式，讓後續每輪改動都能被外部 reviewer 重播與審查。

請新增：
- contexts/artifact_harness_improvement_rounds/README.md
- contexts/artifact_harness_improvement_rounds/round_000_protocol/prompt.md
- contexts/artifact_harness_improvement_rounds/round_000_protocol/developer_report.template.md
- contexts/artifact_harness_improvement_rounds/round_000_protocol/reviewer_notes.template.md
- contexts/artifact_harness_improvement_rounds/round_000_protocol/verification.template.md

交換區要求：
- 每輪都保留原始 prompt。
- developer report 必須包含：
  - Findings Addressed
  - Changed Files
  - Generated Artifacts
  - Verification Commands
  - Known Non-Goals
  - Remaining Risks
- reviewer notes 必須 findings-first，含 P0/P1/P2/P3、檔案與行號。
- verification 必須區分：
  - reported verification
  - reviewer rerun verification
  - not run / unable to run
- 不要把這個交換區變成 governance owner；它只是工作證據與 review handoff surface。
- 不要引入 server、daemon、database，保持 same-folder Markdown/JSON。
- 更新 README 或 AGENTS 只需要簡短提到這個 improvement-rounds 交換區即可，不要大幅重寫定位。

驗收：
- 新增文件能清楚支援後續 Prompt 1-5 的工作報告與 review。
- 文件內要明確寫出 reviewer 不只讀 developer report，還要查 diff、重跑必要 tests、檢查 artifacts。
- 不修改 artifact-harness 功能程式碼。
```

## Protocol Round Scope

This round establishes the exchange format only. It does not change
artifact-harness runtime behavior, packet generation, routing, or policy
ownership.

