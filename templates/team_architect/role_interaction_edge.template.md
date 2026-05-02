# Role Interaction Edge

## Metadata

- source_team_operating_packet:
- status: draft/reviewed/closed

## Interaction Edge

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

## Fill Notes

- Use this template when the team plan needs to record how roles interact, not
  only who they are or what each role owns.
- Role lists identify responsibilities. Group expansion identifies members.
  Agent Work Cards identify ownership, inputs, outputs, completion, and next
  receiver. Role Interaction Edges identify coordination behavior between
  roles.
- Interaction edges alter task graph behavior, not governance ownership.
- Capability implication is an input to the Capability Access Packet only. It is
  not authorization for tools, plugins, models, screenshots, OCR, filesystem, or
  runtime access.
- Interaction edges do not automatically spawn subagents.
- `approval_signoff` blocks delivery only when the user, task policy, or an
  explicit approval boundary grants blocking authority. Without that authority,
  record the role as `review_challenge` or reviewer-only advice.
- Runtime adapters execute only; they do not own the interaction edge.

## Pattern Definitions

- `handoff`: one-way transfer of a prepared or completed artifact from source
  role to target role.
- `dialogue_friction_loop`: two-way loop where a counter-perspective challenges
  a primary role's clarity, assumptions, audience fit, or comprehension before
  production.
- `peer_alignment`: two-way alignment between same-level roles before handoff,
  usually around definitions, assumptions, interfaces, or boundaries.
- `review_challenge`: review loop where one role checks another role's output
  and may request revision without blocking by default.
- `approval_signoff`: sign-off gate where one role may approve or block the
  next step only when authority is explicitly granted.
- `parallel_contribution`: parallel work where roles produce separate parts
  that later integrate.
- `quality_loop`: correction loop where Quality findings return to the
  responsible producer or upstream owner for revision and recheck.

## Example Edges

- source_role: Teacher
  - target_roles: Student
  - interaction_type: dialogue_friction_loop
  - direction: loop
  - shared_artifact: explanation draft
  - authority_boundary: challenges
  - fallback_owner: Teacher

- source_role: Engineering Technical Staff
  - target_roles: Financial Technical Staff
  - interaction_type: peer_alignment
  - direction: two-way
  - shared_artifact: metric definition and processing interface
  - authority_boundary: advises
  - fallback_owner: Project Lead

- source_role: Producer
  - target_roles: Quality Reviewer
  - interaction_type: quality_loop
  - direction: loop
  - shared_artifact: draft artifact and Quality findings
  - authority_boundary: requests_revision
  - fallback_owner: Producer
