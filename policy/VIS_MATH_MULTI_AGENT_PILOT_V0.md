# Vis_Math Multi-Agent Pilot v0

## Purpose
- This pilot is a small, controlled experiment for a `multi-agent system`, not a general replacement for the current native subagent feature.
- The goal is to validate a clearer collaboration loop for Vis_Math teaching artifacts before considering wider adoption.
- The pilot is intentionally small: one lesson chunk, one storyboard or short video draft, one student review pass, and one revision pass.

## System Definition
- `subagent` is only the execution primitive.
- `multi-agent` in this pilot means:
  - fixed role boundaries,
  - shared artifacts,
  - explicit interaction protocol,
  - convergence rules.
- The pilot should be able to run manually first. Native subagents may carry the roles later, but they are not the definition of the system.

## Pilot Scope
- Workspace family: `Vis_Math`
- Initial test topic: a single chunk from probability axioms or a similarly short lecture concept
- Initial deliverable:
  - one `lesson_brief`,
  - one `storyboard_draft`,
  - one `student_review`,
  - one `revision_log`
- Out of scope for v0:
  - full-course production,
  - generalized multi-agent orchestration for all folders,
  - automatic role spawning,
  - persistent cross-session command-and-control

## Roles

### 1. Teacher
- Owns concept correctness, learning objectives, and pedagogical order.
- Publishes the lesson brief and decides whether a reported issue is conceptual or pedagogical.
- May revise:
  - learning goals,
  - explanation order,
  - example choice,
  - wording for clarity
- Must not:
  - micromanage visual layout details,
  - ignore repeated student confusion,
  - trade correctness away for superficial simplicity

### 2. Video Producer
- Owns presentation design, pacing, timing, on-screen readability, annotations, and transitions.
- Publishes the storyboard or video draft.
- May revise:
  - sequence timing,
  - text density,
  - transition timing,
  - highlights,
  - layout and animation choices
- Must not:
  - redefine the underlying concept,
  - silently change mathematical meaning,
  - decide pedagogical tradeoffs alone when the issue is conceptual

### 3. Student
- Represents a constrained target learner, not a caricature.
- Assumed profile:
  - limited working memory,
  - partial prerequisite intuition,
  - no firm mastery of the current concept,
  - vulnerable to pacing, notation overload, and visual overlap
- Publishes the student review.
- May report:
  - what is unclear,
  - what feels too fast,
  - what is unreadable,
  - what appears contradictory
- Must not:
  - rewrite the lesson directly,
  - dictate implementation details,
  - pretend to know a fix when only confusion is observed

## Shared Artifacts
- `lesson_brief.md`
  - the teaching contract for one chunk
- `storyboard_draft.md`
  - the current production plan for that chunk
- `student_review.md`
  - structured learner feedback
- `revision_log.md`
  - the authoritative change record for each loop

## Artifact Metadata Minimum
- Every published artifact should carry:
  - `owner`,
  - `status`,
  - `intent`,
  - `open questions`
- The exact field layout may differ by artifact type, but these four items should be recoverable from the document without guessing.

## Interaction Protocol

### 1. Publish
- A role publishes a stable artifact that another role can consume.
- Publish requires:
  - artifact path,
  - current status,
  - short intent statement,
  - open questions or none

### 2. Request
- A role requests clarification or revision from another role.
- Requests must be specific.
- Good request examples:
  - `Teacher`: clarify whether the example should show impossibility before additivity
  - `Producer`: reduce text density in scene 3 because the learner cannot read it in time
  - `Student`: explain what changed between scene 2 and scene 3

### 3. Promote
- A draft is promoted only when it becomes reusable by the next role without hidden assumptions.
- Promotion criteria:
  - internally coherent,
  - artifact is readable,
  - next owner can act on it directly,
  - unresolved issues are explicitly listed
- Promotion is blocked if:
  - a higher-priority issue class is still unresolved,
  - the current owner still has an explicit decision gate,
  - the next owner would need to infer missing rationale

### 4. Closeout
- Each loop ends with a short receipt:
  - what changed,
  - why it changed,
  - what remains open,
  - who acts next

## Issue Classes
- `conceptual`
  - the learner does not understand the underlying idea
  - owner: `Teacher`
- `pedagogical`
  - the explanation sequence, example order, or pacing of ideas is poor
  - owner: `Teacher`, then `Video Producer` if the content order is settled
- `visual`
  - the learner cannot read or track the screen state
  - owner: `Video Producer`

## Loop
1. `Teacher` publishes `lesson_brief.md`
2. `Video Producer` publishes `storyboard_draft.md`
3. `Student` publishes `student_review.md`
4. Issues are classified as `conceptual`, `pedagogical`, or `visual`
5. The single owning role revises and records the change in `revision_log.md`
6. The updated artifact is promoted to the next loop

## Convergence Rules
- Work on one lesson chunk at a time.
- Each loop should modify one dominant issue family first.
- Other issue families may be noted as deferred, but should not be revised in the same loop unless they are purely mechanical consequences of the dominant owner decision.
- Priority order:
  1. conceptual
  2. pedagogical
  3. visual
- If the same issue appears twice, escalate from micro-editing to structural revision.
- Default cap:
  - 2 to 3 loops per chunk
- If the chunk still fails after loop 3, treat it as a lesson-design problem, not a polishing problem.

## Stop Conditions
- The learner can restate the core point in plain language.
- On-screen content remains readable through the whole chunk.
- The pacing allows the learner to follow the transitions.
- The teacher confirms that simplification did not distort the concept.

## Execution Modes

### Manual-First
- A single session can simulate the three roles by producing the four artifacts in order.
- This is the default for v0.

### Native-Subagent-Assisted
- Native subagents may later carry one or more roles.
- If used, keep the same artifact protocol.
- Do not replace the protocol with free-form multi-agent chat.

## Evaluation
- The pilot is successful if it improves:
  - concept clarity,
  - visual readability,
  - revision discipline,
  - traceability of why a change happened
- The pilot is not successful if it only creates more role chatter without clearer artifacts or cleaner revision decisions.

## Audit Expectation
- `revision_log.md` should make role ownership auditable.
- Each recorded change should show:
  - issue class,
  - owning role,
  - changed artifact,
  - change summary,
  - reason

## Promotion Guidance
- Do not generalize this pilot to global policy after one successful run.
- Promote outward only if the loop works on more than one Vis_Math chunk and the artifact protocol remains stable.
