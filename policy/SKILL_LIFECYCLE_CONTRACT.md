# Skill Lifecycle Contract

## Purpose

This document defines how skills should be discovered, trialed, reviewed, and promoted in this workspace.
It exists to separate `skill trust` from `skill routing`.

## Core Principle

The router decides what may fit a task.
The lifecycle decides what is trustworthy enough to be routed confidently.

These are related, but they are not the same system.

## Lifecycle Stages

### 1. Discovery

A skill enters the lifecycle when one of these is true:

- there is a workflow gap
- an installed skill family is unclear or incomplete
- repeated friction suggests a missing reusable method

Discovery may surface:

- local existing skills
- remote candidates
- trusted-source install options

### 2. Candidate

A newly installed or newly adopted skill should enter as `candidate`, not `active`.

Candidate means:

- allowed for controlled use
- not yet globally trusted
- still expected to prove fit through real work

### 3. Trial

A skill should be trialed through a real task, not only through abstract inspection.

The important outputs are:

- whether it helped
- whether it reduced workaround effort
- whether it is likely to be reused
- whether it created new failure or ambiguity

### 4. Learning via closeout

Closeout is the main learning surface for lifecycle evidence.

It should capture at least:

- used skills
- outcome
- reuse intent
- helpful or failed skills when known
- workarounds or missing capability when relevant

This is how skill trust accumulates.

### 5. Review

Promotion should not be automatic merely because a skill was used once.

Review asks:

- did the skill succeed in a real task
- is the behavior reproducible
- did it fit the workflow better than generic fallback
- does it belong in active or only fallback routing

### 6. Promotion or rejection

Possible outcomes:

- promote to `active`
- promote to `fallback`
- keep as `candidate`
- reject or quarantine

Trusted-source installation is not the same as trusted routing.

## Router Relationship

The current router is a quality-aware workflow planner.

Important implications:

- `gap = true` is a valid answer
- `primary = none` is valid when no skill truly fits
- discovery is preferable to forced wrong routing

The lifecycle should support this honesty, not pressure the router to pretend coverage exists.

## Trusted Install Discipline

If installation is involved:

- prefer trusted sources only
- install into `candidate`
- do not jump directly into `active`
- require real-task evidence before stronger routing trust

## Promotion Evidence

A pattern is a strong promotion candidate when:

- it worked on a real task
- the result passed local validation
- reuse is likely
- it reduced manual workaround burden
- it did not break existing contracts

## What This Contract Does Not Cover

This document does not define:

- the full router scoring model
- domain-specific skill prompts
- every skill inventory entry
- multi-agent role design

Those belong elsewhere.

## Current Maturity Statement

In this workspace:

- skill lifecycle is in active convergence
- it is more mature than the router
- it should be treated as a managed subsystem, but not yet as a finished global standard
