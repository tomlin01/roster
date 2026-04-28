Prompt 6 已完成。

新增了 repo-owned Roster skill install surface：[`skills/roster/SKILL.md`](/Users/tom/Documents/PHD/codex-cns/skills/roster/SKILL.md)，並新增 `roster-install` / 擴充 `roster-health`。現在可用的安裝路徑是：

```bash
./scripts/brain.sh roster-install --codex-home ~/.codex --json
```

會安裝到：

```text
~/.codex/skills/roster/
```

目前對人類最誠實的呼叫方式仍是：

```text
Roster, <your artifact task>
```

不是 `@roster`。`@roster` 目前只保留為未來 mention/plugin/app/slash surface 目標；文件也已改掉避免誤導。

主要改動：
- 新增 [`skills/roster/SKILL.md`](/Users/tom/Documents/PHD/codex-cns/skills/roster/SKILL.md)
- 更新 [`scripts/system_hub.py`](/Users/tom/Documents/PHD/codex-cns/scripts/system_hub.py)
- 更新 [`scripts/test_system_hub.py`](/Users/tom/Documents/PHD/codex-cns/scripts/test_system_hub.py)
- 更新 [`README.md`](/Users/tom/Documents/PHD/codex-cns/README.md)
- 更新 [`AGENTS.md`](/Users/tom/Documents/PHD/codex-cns/AGENTS.md)
- 更新 UX docs 與 Prompt 6 report：[`prompt_6_roster_skill_install_surface.report.md`](/Users/tom/Documents/PHD/codex-cns/contexts/artifact_harness_usage_experience/developer_reports/prompt_6_roster_skill_install_surface.report.md)

驗證已通過：
- `python3 -m py_compile scripts/system_hub.py scripts/test_system_hub.py`
- `python3 scripts/test_system_hub.py`
- `python3 scripts/test_overlay_policy.py`
- `python3 scripts/test_run_agent_benchmark.py`
- `python3 -m json.tool contexts/team_alias_registry.json`
- `git diff --check`
- `./scripts/brain.sh capabilities | rg 'roster-install|roster-health|Available commands'`
- repo-local smoke cleanup check：沒有殘留 `contexts/artifact_harness_registry.json` 或 `contexts/artifact_harness_runs/`

剩餘風險很明確：安裝 skill 後可能需要新 Codex session 才會被 runtime 發現；`@roster`、`/roster`、plugin/app mention 都還沒有被證明可用；provider auth 目前仍只是本機 presence check，沒有做 remote LLM call。

