# Team Operating Packet

## Metadata

- owner:
- status: draft/reviewed/approved
- target_mission:
- generated_by:
- source_artifact_harness_spec:
- source_hr_staffing_packet:

## Fill Notes

- Fill this template from the Artifact Harness SPEC, HR staffing packet, and
  coordination baseline.
- Keep this file agent-readable Markdown in the same workspace folder.
- This packet owns collaboration structure, not staffing or capability
  authorization.
- Generate or link a Capability Access Packet when skills, plugins, tools, or
  runtime approval gates are needed.
- Capability-Aware Role Execution uses:
  `role -> work -> interaction -> capability need -> availability -> fallback`.
- Roster plans capability needs; CAP authorizes access; runtime executes.

## Team Shape

- team name:
- task shape:
- chosen collaboration pattern:
- why this pattern fits:

## Groups

- group:
  - purpose:
  - when_to_expand:
  - members:
    - member:
      - responsibility:
      - perspective:
      - deliverable:
      - agent_instance: merged/single/peer/reviewer/approver/counter_perspective

Fill notes:

- Broad first-touch replies may show groups first and defer member expansion.
- Expand groups when the user asks, implementation planning begins, or risk
  requires explicit responsibility and perspective.
- Expanded members do not automatically become separate agents.
- Group/member expansion is not the same as full role interaction-edge
  modeling.
- When expanded members need execution clarity, fill Agent Work Cards or link
  `templates/team_architect/agent_work_card.template.md`.

## Agent Work Cards

- work_card:
  - role_name:
  - group:
  - responsibility:
  - perspective:
  - inputs:
  - outputs_or_deliverables:
  - done_condition:
  - handoff_target:
  - tool_or_capability_need:
  - capability_needs:
    - capability: reasoning_only/filesystem_read/filesystem_write/code_execution/web_search/browser/visual_capture/vision_review/specialist_skill/plugin_or_connector/subagent_execution
      purpose:
      availability: available/available_after_reload/available_if_approved/unknown/unavailable
      evidence_expected:
      fallback:
  - agent_assignment: separate_agent/merged_with/simulated_perspective/reviewer_only/approval_gate_candidate
  - open_questions:

Fill notes:

- Work cards are actionable handoff units for expanded roles and members.
- Do not fill work cards for ordinary short first-touch previews unless risk or
  authority clarity requires it.
- `agent_assignment` records the handling mode; it does not spawn runtime
  agents by itself.
- `tool_or_capability_need` is a short summary for older packets; use
  `capability_needs` when the role needs explicit capability planning.
- Capability need is not authorization. Capability authorization stays with CAP
  and approval gates.
- Use `unknown` when local packet evidence cannot prove the active host/runtime
  exposes a capability such as web search, browser, visual capture, vision
  review, plugins/connectors, or subagent execution.
- Preserve perspective separation even when one agent carries several work
  cards or simulates a role rather than spawning a subagent.
- `approval_gate_candidate` records possible gate authority only; it does not
  approve or block delivery without user or policy authority.
- `handoff_target` is the next receiver, not full role interaction-edge
  modeling.

Example capability needs:

- Research Reviewer: `web_search`, `browser`; evidence expected is URLs, dates,
  and source summaries; fallback is user-provided sources or local files only.
- Visual QA: `visual_capture`, `vision_review`, `browser`; evidence expected is
  screenshot/render/frame/OCR/CV findings; fallback is visual acceptance marked
  limited until evidence exists.
- Slide Producer: `specialist_skill`, `plugin_or_connector`,
  `filesystem_write`; evidence expected is a generated deck or slide artifact
  plus verification result; fallback is outline or HTML draft.
- Skill Reviewer: `filesystem_read`, optionally `filesystem_write`; evidence
  expected is diagnosis, file-line findings, and optional patch; fallback is
  plain-language diagnosis without patch.
- Statistical Reviewer: `code_execution`, `specialist_skill`; evidence expected
  is a reproducible check, test cases, and assumption notes; fallback is
  conceptual review only.

## Role Interaction Edges

- interaction_edge:
  - source_role:
  - target_roles:
  - interaction_type: handoff/dialogue_friction_loop/peer_alignment/review_challenge/approval_signoff/parallel_contribution/quality_loop
  - direction: one-way/two-way/parallel/loop
  - trigger:
  - shared_artifact:
  - expected_output_or_decision:
  - done_condition:
  - revision_or_escalation_rule:
  - authority_boundary: advises/challenges/requests_revision/blocks/signs_off
  - capability_implication:
  - fallback_owner:

Fill notes:

- Fill this section after roles, groups, or work cards need explicit
  role-to-role coordination. For a standalone edge file, use
  `templates/team_architect/role_interaction_edge.template.md`.
- Role interaction edges are task-graph edges. They do not change governance
  ownership, grant capability authorization, approve work, or execute runtime
  adapters.
- Capability implications feed the Capability Access Packet only; they are not
  tool, plugin, model, screenshot, OCR, filesystem, or runtime authorization.
- Interaction edges do not automatically spawn subagents.
- `approval_signoff` blocks delivery only when user wording, task policy, or an
  explicit approval boundary grants blocking authority. Otherwise use
  `review_challenge` or reviewer-only advice.
- `handoff_target` in an Agent Work Card records the next receiver only; this
  section records how roles coordinate, revise, align, review, integrate, sign
  off, or fall back.
- Pattern definitions:
  - `handoff`: one role passes a prepared artifact to the next role.
  - `dialogue_friction_loop`: a counter-perspective role creates productive
    friction before production.
  - `peer_alignment`: same-level roles align assumptions, definitions, or
    boundaries before handoff.
  - `review_challenge`: one role checks another role's output and may request
    revision without blocking by default.
  - `approval_signoff`: one role can approve or block only when authority is
    explicitly granted.
  - `parallel_contribution`: multiple roles produce separate parts that later
    integrate.
  - `quality_loop`: Quality findings return to the responsible producer or
    upstream owner for correction and recheck.

## Roles

- role:
  - mission:
  - perspective:
  - layer: planning/production/domain_judgment/quality
  - agent_instance: merged/single/peer/reviewer/approver/counter_perspective
  - workflow_position:
  - authority_boundary: advises/challenges/requests_revision/blocks/signs_off
  - capability_implication:
  - owns:
  - must_produce:
  - must_not_do:

## Role Context Notes

- role_context_rule: domain_extension/peer_domain_role/reviewer_approver/counter_perspective/other
- merged_roles:
- split_roles:
- peer_alignment_needed: yes/no
- review_or_signoff_needed: yes/no
- user_wording_that_set_authority:
- ambiguity_to_confirm:

Fill notes:

- A user-added role is not automatically a new agent instance.
- The default four-role shape is layer compression, not a maximum team size.
- Peer roles add alignment by default; they become approvers only when user
  wording, task risk, or approval boundaries require it.
- Capability implications should feed the Capability Access Packet when they
  require skills, plugins, tools, model/provider access, filesystem access,
  screenshots, playback, OCR, or runtime exposure.

## Inputs From Staffing

- reused roles:
- adapted roles:
- new roles:
- unresolved role gaps:

## Shared Artifacts

- artifact:
  - owner:
  - purpose:
  - handoff target:
  - promotion rule:

## Capability Access

- source Artifact Harness SPEC:
- capability access packet:
- required: yes/no
- reason required:
- authorized capability summary:
- approval gate summary:
- access boundaries:

## Interaction Protocol

1. publish:
2. request:
3. revise:
4. promote:
5. closeout:

## Escalation And Convergence

- escalation triggers:
- dominant issue owner rule:
- stop conditions:
- fallback if the pattern stalls:

## Authority Envelope

- what this team may decide:
- what requires user approval:
- what must not be changed silently:

## Invocation Guidance

- how to call the team:
- when to use this team:
- when not to use this team:

## Execution Runtime Mapping

- runtime adapter:
- runtime mode:
- why this mode fits:
- task graph source:
- mapping artifact:
- source capability access packet:
- approval gate locations:
- expected runtime byproducts:

## Open Questions

- 
