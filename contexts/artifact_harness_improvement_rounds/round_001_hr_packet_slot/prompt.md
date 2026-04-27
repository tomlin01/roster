# Round 001 Prompt: HR Packet Slot

## Original Prompt

```text
請 review 並修正 artifact-harness packet generator：目前 workflow 聲稱是
user mission -> SPEC -> HR staffing -> TOP -> CAP -> runtime mapping -> verification，
但 generator 沒有產生 HR staffing packet，導致 Vis_Math / Lecture1 實測時需要手動補。

請先閱讀：
- contexts/artifact_harness_improvement_rounds/README.md
- contexts/artifact_harness_improvement_rounds/round_000_protocol/developer_report.template.md
- contexts/artifact_harness_improvement_rounds/round_000_protocol/verification.template.md
- policy/ARTIFACT_HARNESS_WORKFLOW_V0.md
- templates/artifact_harness/artifact_harness_spec.template.md
- templates/team_architect/team_operating_packet.template.md
- templates/team_architect/capability_access_packet.template.md
- templates/team_architect/open_multi_agent_runtasks_mapping.template.md
- agents/native/hr.md
- agents/native/team-architect.md
- teams/human-resources/TEAM.md

目標：
- 新增 HR staffing packet template 或 generator output。
- artifact-harness generated packet chain 必須包含 HR staffing packet。
- manifest / registry 必須包含 hr_staffing_packet。
- TOP 的 source_hr_staffing_packet 不應再是 "to be filled by HR"。
- README / AGENTS / workflow policy 如有提到 packet chain，必須與實際 generator output 一致。

邊界：
- HR packet 只能記錄 staffing / role reuse / role boundaries / Team Architect handoff。
- 不得讓 HR packet 授權 tools、skills、plugins。
- 不得讓 HR packet 選 runtime adapter。
- 不得讓 HR packet own artifact acceptance 或 verification。
- 不要做 Prompt 2 lifecycle/status/resume；這輪只處理 HR packet slot。
- 不要引入 server、daemon、database，保持 Codex-native、same-folder、CLI/GUI friendly。

交換區要求：
- 使用 round_001_hr_packet_slot 這個 round。
- 若你修改或新增 developer_report / verification，請放在：
  - contexts/artifact_harness_improvement_rounds/round_001_hr_packet_slot/developer_report.md
  - contexts/artifact_harness_improvement_rounds/round_001_hr_packet_slot/verification.md
- developer_report 必須使用 round_000_protocol 的格式精神，至少包含：
  - Findings Addressed
  - Changed Files
  - Generated Artifacts
  - Verification Commands
  - Known Non-Goals
  - Remaining Risks

驗收：
- `./scripts/brain.sh artifact-harness "<mission>" --path <temp-workspace> --id <id> --json`
  會產生 artifact_harness_spec、hr_staffing_packet、team_operating_packet、
  capability_access_packet、runtime_mapping、manifest。
- manifest JSON 與 registry JSON 都有 hr_staffing_packet。
- generated TOP 正確 link source_hr_staffing_packet。
- rerun guard 仍保護既有 packet，不因 HR packet 加入而回歸覆寫。
- `packet-route --create --json` 也能產生同樣完整 packet chain。
- smoke tests 使用 temp workspace，不要污染 repo contexts。
- 更新或新增 tests，至少覆蓋 artifact-harness create、packet-route create、manifest/registry linkage、rerun guard。
```

## Round Scope

This round fixes only the missing HR staffing packet slot in the generated
Artifact Harness packet chain. It does not implement packet lifecycle/status,
evidence ledger, replay benchmark, or failure recovery.
