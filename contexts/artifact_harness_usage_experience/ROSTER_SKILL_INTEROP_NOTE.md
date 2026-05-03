# Roster Skill Interop Note

Date: `2026-05-03`
Status: `future validation note`

## Purpose

Record a future validation direction:

```text
Confirm how Roster works together with other installed skills.
```

This is not a v0.10.0 implementation spec yet. It is a continuity note for the
next exploration stage after v0.9.0 Role Interaction Patterns.

## Working Hypothesis

Roster should be the coordination layer, not the specialist production skill.

Expected split:

- Roster shapes the team, work lines, interaction patterns, Quality loop, and
  capability boundary.
- Domain or artifact skills perform specialized production or inspection work
  when they are a better fit.
- Roster decides when a specialist skill should be invoked, what role it serves,
  what artifact it receives, and what output or review result should return to
  the roster.

In short:

```text
Roster coordinates the work; specialist skills do the specialized parts.
```

## Questions To Validate

- Does Roster naturally select or recommend the right specialist skill for an
  artifact without making the user manage skill names?
- Can Roster keep its own role/interaction model while delegating production to
  another skill?
- Does a specialist skill output return cleanly into the Roster Quality loop?
- Can Roster distinguish skill use from role ownership?
- Can Roster avoid exposing internal governance terms while still using skills
  correctly?
- Does using another skill improve artifact quality, or does it add unnecessary
  coordination cost?
- Can Roster review another skill or workflow as a small review team instead of
  falling into a single-reviewer findings-first mode?

## Candidate Interop Cases

### Skill Or Workflow Review

Roster role:

- form a small review team around the target skill or workflow;
- keep the first response human-facing rather than opening with code-review
  findings;
- separate user experience, coordination, delivery Quality, and implementation
  evidence as distinct review perspectives;
- converge the perspectives into a short diagnosis and next repair direction.

Potential review team:

- User Experience Reviewer: checks whether the first-touch response feels
  natural and actionable.
- Resource Coordinator: checks whether resources, skills, or tools become a
  usable execution chain.
- Delivery QA: checks handoff, fallback, verification, and recheck conditions.
- Implementation Reviewer: produces file/line findings only when the user asks
  for engineering review, patch detail, or PR-style evidence.

Expected first-touch shape:

```text
我會用一個小 review team 看這個 skill：

- 使用者體驗：看它是否讓人自然知道下一步
- 協調流程：看資源是否能接成可執行流程
- 交付品質：看失敗時誰修、怎麼驗收、何時 fallback

初步判斷：問題不是缺資源，而是缺把資源轉成 handoff / recheck 的協作層。
```

Boundary:

- Team Review Mode is not the same as code review.
- Do not start with `P1/P2` findings, `::code-comment`, or file-line reports
  unless the user explicitly asks for review findings, patch detail, PR review,
  or implementation evidence.
- Roster should first explain the team judgment in plain language, then offer
  deeper findings or a fix prompt if needed.

### Meeting Notes To Executive Slides

Roster role:

- define content line, slide line, and Quality line;
- decide whether a presentation/deck skill should handle slide production;
- route visual Quality findings back to slide production or content owners.

Potential specialist capability:

- presentation or slide-generation skill;
- document summarization or meeting-insights skill;
- screenshot, render, OCR, or visual QA capability.

### BCQ_III Questionnaire APP

Roster role:

- coordinate Chinese medicine content, statistics/scoring, user-facing report,
  physician-facing details, privacy/legal review, and Quality.

Potential specialist capability:

- statistical analysis skill for scoring validation;
- clinical or medical-writing skill for safe wording;
- frontend/app planning skill for user and physician interfaces.

### Spreadsheet Or Data Report

Roster role:

- separate data cleaning, analysis, interpretation, stakeholder narrative, and
  Quality checks.

Potential specialist capability:

- spreadsheet, Python/statistics, plotting, or report-writing skill.

### Visual Or Presentation Artifact

Roster role:

- decide when visual evidence is required;
- attach a Quality loop for occlusion, readability, layout, contrast, and
  export mismatch;
- return findings to the responsible producer.

Potential specialist capability:

- presentation, screenshot, browser, image inspection, OCR, or CV review skill.

## Boundary Rules

- Skill invocation is a capability choice, not a new governance owner.
- A skill can serve a role, but it does not replace the role's responsibility.
- Roster may recommend a skill, but tool/plugin/model access still follows the
  Capability Access Packet boundary when governed execution is needed.
- Specialist skill output should return as an artifact, finding, or handoff
  input inside the Roster task graph.
- Roster should not overuse skills for small tasks where one agent can handle
  all layers cleanly.

## Success Criteria

A successful interop pass should show:

- one ordinary user prompt;
- Roster identifies the useful team shape;
- Roster invokes or recommends a specialist skill only where it adds value;
- the specialist output maps back to a role, work card, or interaction edge;
- Quality can inspect or challenge that output;
- final user-facing explanation stays short and natural.

## Risk

The main risk is turning Roster into a visible skill router. That would make the
user manage machinery again.

The intended behavior is quieter:

```text
Roster should make skill use feel like part of the team doing its job.
```
