# Agent Benchmark Baseline

- Timestamp: `2026-03-14T07:11:57+00:00`
- Benchmark kind: `parsed_overlay`
- Scope: `workspace`
- Workspace: `per-case`
- Passed: `8`
- Failed: `4`
- task_success_rate: `0.666667`
- route_match_rate: `1.0`
- manual_intervention_rate: `0.333333`
- median_wall_time_sec: `1e-06`
- avg_tool_calls: `3.5`

## Overlay Summary
| workspace | has_agents_md | has_principles_md | overlay_depth | strictness_score | parsed_signals |
| --- | --- | --- | --- | --- | --- |
| `/Users/tom/Documents/PHD/codex_updat` | `True` | `True` | `2` | `7` | `discussion_before_high_impact_changes, non_trivial_task_locking, visual_first_verification, closeout_definition_of_done, correctness_priority` |
| `/Users/tom/Documents/PHD/Vis_Math` | `True` | `False` | `1` | `0` | `none` |
| `/Users/tom/Documents/GitHub/obsidian_tom` | `False` | `False` | `0` | `0` | `none` |

## Failure Reasons
- `manual_intervention_required:local_overlay_requires_discussion_for_high_impact_changes+local_overlay_requires_task_lock_before_execution`: `4`

## Case Summary
| id | category | global_success | overlay_success | delta_success | delta_manual_intervention |
| --- | --- | --- | --- | --- | --- |
| `meta_contract_refresh` | `meta-workspace` | `True` | `False` | `True` | `True` |
| `meta_router_regression` | `meta-workspace` | `True` | `True` | `False` | `False` |
| `meta_taxonomy_update` | `meta-workspace` | `True` | `False` | `True` | `True` |
| `vismath_bugfix_scene` | `coding` | `True` | `True` | `False` | `False` |
| `vismath_refactor_small` | `coding` | `True` | `True` | `False` | `False` |
| `vismath_quick_query` | `coding` | `True` | `True` | `False` | `False` |
| `obsidian_memory_review` | `research-writing` | `True` | `True` | `False` | `False` |
| `obsidian_pipeline_checkpoint` | `research-writing` | `True` | `True` | `False` | `False` |
| `obsidian_style_normalization` | `research-writing` | `True` | `True` | `False` | `False` |
| `cross_workspace_policy_read` | `cross-workspace` | `True` | `False` | `True` | `True` |
| `cross_workspace_overlay_guard` | `cross-workspace` | `True` | `False` | `True` | `True` |
| `cross_workspace_trivial_time` | `cross-workspace` | `True` | `True` | `False` | `False` |
