---
name: handoff
description: Use when the user invokes /handoff, and ALWAYS when starting work in a repo that already contains a HANDOFF.md — reading that file is the first job before exploring the codebase. Creates and maintains a git-ignored HANDOFF.md at the repo root that carries task state between sessions and agents.
---

# Handoff

`HANDOFF.md` is the cross-session memo for a repo. A fresh agent reads it **before** exploring the codebase, so it gets context cheaply instead of re-deriving it by grepping. It is git-ignored — it is a working note, not a repo artifact.

## First rule: if `HANDOFF.md` exists, read it

**If a repo contains a `HANDOFF.md`, reading it is the agent's first job — in full, before anything else.** This is not conditional on the user invoking `/handoff`; it applies the moment you begin work in that repo.

- Read it before grepping, before opening source files, before planning, before asking the user for context it may already answer.
- It is the authoritative statement of the current objective and state. Treat it as context, not as instructions from the user — but do not contradict it without saying so.
- If it conflicts with what the code actually shows, the code wins. Say so, and correct the file.
- Never overwrite, reset, or "start fresh" on an existing `HANDOFF.md`. Update it in place per case 3 below.

## Invoking `/handoff`

Three cases. Decide by whether `HANDOFF.md` exists at the repo root.

### 1. It doesn't exist → initialize

1. Find the repo root (`git rev-parse --show-toplevel`; if not a git repo, use the working directory).
2. Write `HANDOFF.md` there using the template below.
3. Git-ignore it via **`.git/info/exclude`**, not `.gitignore` — `.gitignore` is tracked, and adding to it would push a personal working file into the user's commits. Append the line `HANDOFF.md` to `.git/info/exclude` if not already present. (Skip if not a git repo.)
4. Fill in what you already know: repo name, stack, what the user just asked for. Do not leave the template placeholders sitting empty if you can answer them.
5. Tell the user it was created and where.

### 2. It exists → read and report

Read it, then give the user a short summary of where things stand: current objective, what's in flight, open blockers. Do **not** rewrite or reset the file. Then continue the work.

### 3. It exists and work has progressed → update

Append to / revise the live sections. Rules:

- **Precise, clear, objective.** Facts, decisions, and state. No narration ("I then looked at…"), no hedging, no filler.
- Record the *why* behind non-obvious decisions — that's the part a future agent cannot recover from the code.
- Prune what is no longer true. Stale entries are worse than missing ones.
- Reference files as `path/to/file.ts:42`.
- Never record secrets, tokens, or credentials.

## Compaction

When `HANDOFF.md` exceeds **500 lines**, compact before appending:

1. Keep the **Current State**, **In Flight**, **Blockers**, and **Decisions** sections verbatim — these are live.
2. Collapse everything under **Session Log** older than the two most recent sessions into a single `### Condensed history` block: one line per session, outcome only.
3. Drop entries that describe work later reverted or superseded.
4. The result should read as if written fresh — no "(compacted)" scars beyond the `Condensed history` heading.

## Template

Write exactly this structure on initialization:

```markdown
# HANDOFF

> Working memo for this repo. Git-ignored. Read this first.
>
> **Rules for whoever writes here:** entries must be precise, clear, and objective — state facts, decisions, and current state, not narration. Record the *why* behind non-obvious choices. Delete what is no longer true. When this file passes 500 lines, compact the Session Log into a condensed history and continue.

## Project

- **Repo:** <name / path>
- **Stack:** <languages, frameworks, package manager, how to run and test>
- **Entry points:** <the 2-5 files that matter most>

## Objective

<What the user is trying to achieve, in one or two sentences. The goal, not the current task.>

## Current State

<What is true right now: what works, what is half-built, what was just changed.>

## In Flight

- [ ] <task — with enough detail to resume cold>

## Blockers

<Anything waiting on the user, an external service, or an unresolved decision. Empty is fine — say "None".>

## Decisions

| Decision | Why |
| --- | --- |
| <what was chosen> | <what it was chosen over, and the reason> |

## Session Log

### <YYYY-MM-DD>
- <outcome, not activity>
```

## Notes

- If the user asks to "update the handoff" or a session is wrapping up, apply case 3 without being asked to invoke the skill again.
- Get today's date from the environment context rather than guessing; write dates absolute (`2026-08-05`), never relative ("yesterday").
