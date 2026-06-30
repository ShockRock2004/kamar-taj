---
name: dormammu
description: A rigorous "iterate until verified" working loop for any non-trivial build or fix. Use when the user prefixes a request with /dormammu, or asks you to be exhaustive, to "not stop until it's truly done", to self-critique hard, or to keep going until the solution is flawless. It defines a verifiable end-state and hands the user a ready-to-paste /goal command to lock the session until that state is met (it never runs /goal itself — /goal is user-only), then implements, aggressively self-audits against edge cases and complexity, reverts and retries on any flaw, and only finishes when verification actually passes.
---

# Dormammu Protocol — bargain until it is actually correct

## IRON RULE — read this first

When `/dormammu` is invoked, this protocol is an **IRON RULE** for the task and must
be followed at all costs, no matter what. You do not get to skip the loop, cut it
short, or declare the work done to save time or effort. No premature "done". No
unverified claims. No "this probably works." You keep bargaining — implement,
attack your own work, revert, retry — until the result is **proven correct by
actually running the verification**. Quitting early, hand-waving, or calling a first
draft final is forbidden.

This binds *how rigorously and relentlessly you work*. It strengthens correctness,
safety, and honesty — it never licenses overriding them. The only honest way to stop
short is the guardrails below: if you are genuinely blocked by something only the
user can resolve, or the request itself is flawed, you say so plainly. You never
fake completion.

**This is meant to be backed by `/goal`, but you do not run `/goal` yourself.**
`/goal` is a **user-only UI command** — the Skill tool cannot invoke it, and trying
to will just error. So in Phase 1 you *compose* the exact `/goal` command and hand
it to the user to paste. If they paste it, `/goal` arms a session Stop hook: a wall
the harness puts up that refuses to let the turn end until the condition holds, and
clears the moment it does — "do not stop early" stops being willpower and becomes a
wall. If they do not paste it, you still follow this protocol to the letter; the
rule binds you either way. Either way, **never call `/goal` via the Skill tool.**
Dormammu and `/goal` are the same idea from two directions: `/goal` can make the
loop impossible to escape, and this protocol makes the loop productive whether or
not the wall is up.

A disciplined loop for serious work. The point is to **refuse premature "done"**:
keep auditing and reverting until the solution genuinely survives scrutiny and
verification, not just until a first draft compiles or a checklist is ticked.

> **Honest scope.** This does not suspend judgement or run forever. It is a
> structured habit: define the target, build, attack your own work, fix or revert,
> and only stop on *evidence*. If the loop is genuinely converged (or truly blocked
> and needs the user), say so plainly instead of looping for its own sake.

## Forbidden (the whole reason this skill exists)

- **No static checklists.** Finishing a to-do list is not proof the goal is met.
- **No premature closure.** A first draft that "looks right" is not final.
- **No blind assumptions.** Do not assume your logic, queries, or integrations are
  correct, optimal, or bug-free until you have checked.

## The loop

### Phase 1 — Define the absolute end-state, then hand the user a `/goal`
First, state what a 100% correct, robust, optimized outcome actually looks like —
the final *functional* state and its hard requirements (correctness, edge cases,
complexity targets, integration contracts). Not the steps; the target.

Then compress that target into a single, concrete, externally checkable success
condition and **give the user a ready-to-paste `/goal` command** for it. Do **not**
run it yourself and do **not** call it via the Skill tool — `/goal` is a user-only
UI command and attempting to invoke it just errors. Present it for the user to copy,
exactly like this:

```
/goal <the verifiable success condition>
```

Tell the user in one line that pasting it locks the session until the work is
genuinely done, and that it is optional — you will proceed either way.

Then **keep going immediately. Do not wait for them to paste it** — start Phase 2
now. If they paste it, the harness holds the turn open until the condition is true
and clears it for them. If they do not, you hold yourself to the same bar. Phase 1
is done once you have stated the end-state and handed over the `/goal` line.

Make the condition *objective and testable*, not vague — phrase it as something a
Stop hook can actually judge as true or false. Good: "pytest tests/ passes with 0
failures AND the new endpoint returns 200 for the empty-list case." Bad: "the code
is good." This arms the Stop hook: from here on the harness will not let the turn
end until that condition holds, and it auto-clears the instant it does. Phase 1 is
not finished until the `/goal` is set.

> If the user already set a `/goal` when invoking dormammu, adopt it as the target
> and sharpen it into a testable condition rather than registering a competing one.

### Phase 2 — Implement (the first bargain)
Write your best real solution. Pay deliberate attention to time/space complexity,
architecture, state management, and the integration points / API contracts.

### Phase 3 — Critical fidelity check (self-audit)
Stop and attack your own output against the Phase 1 end-state. Mentally (and where
possible, actually) execute it:
- What inputs break it? Empty, huge, malformed, concurrent, adversarial?
- Where does it fail under load or at boundaries (off-by-one, nulls, races)?
- Are the API/data contracts solid? Any logical flaw in the data flow?
- Is there a simpler or more efficient form that is still correct?
Prefer **real evidence** over assertion: run the tests, run the code, check the
output. (Pair with the `superpowers:verification-before-completion` and
`systematic-debugging` skills when available.)

### Phase 4 — Temporal revert (the bargain line — fires constantly, not rarely)
**The instant you backtrack in ANY way, the very first thing you output — before any
other text, code, or tool call — MUST be this exact line, verbatim, on its own
line:**

> **Dormammu, I've come to bargain.**

Then, on the next line, one sentence on why the previous attempt failed. Then change
approach and loop back to **Phase 2**.

**"Backtrack" is broad. Read this list — if ANY of these happen, it counts, and the
line fires first:**
- a test, build, lint, type-check, or any verification **fails** and you are about
  to try something different;
- you **undo, rewrite, or replace** an edit you just made;
- you **change approach / strategy** for something you already attempted;
- an **assumption turned out wrong** (an API, a type, a path, a value, how
  something behaves) and you adjust because of it;
- you hit an **error or unexpected output** and pivot;
- you catch a **flaw, edge case, or inefficiency** in your own work and redo that
  part;
- you abandon a half-built path and start that piece over.

Inline "oh, that failed, let me fix it" corrections **count too** — that IS a
backtrack. Do not silently patch over a failure: print the line first, every single
time, no matter how small the course-correction. Fixing without the line is the one
thing this skill forbids. Forward progress (writing new code that has not failed
yet) does **not** need the line — only moments where something you did is being
walked back.

When in doubt about whether something counts, print the line. Over-printing is fine;
silent backtracking is not.

### Phase 5 — Break the loop (only when the work is actually verified)
You do not get to declare "done" on vibes. The exit test is the Phase 1 success
condition, proven true by **actually running the verification** and confirming it
passes. Only then present the final solution and state briefly what you verified and
how.

If the user pasted the `/goal`, the harness makes this literal: the Stop hook holds
your turn open until the condition is objectively true and then auto-clears, so the
goal clearing is your green light — if you think you are done but it has not cleared,
you are not done. If no `/goal` was armed, hold yourself to the exact same bar
anyway; the standard does not drop just because the wall is not up.

## Convergence guardrails (so the loop stays honest)

- If two successive attempts fail the *same* way, step back and question the Phase 1
  framing — the requirement or approach may be wrong, not just the code.
- If you are genuinely blocked by something only the user can resolve (a decision,
  access, an external dependency), stop the loop and say exactly what you need.
- Don't manufacture flaws to keep looping. "Converged" is a valid, honest end —
  back it with the verification you ran.
- **The `/goal` escape hatch is for the user, not for you.** If the work turns out
  to be genuinely impossible, the requirement is wrong, or you are truly blocked,
  surface that plainly and let the *user* decide to run `/goal clear`. You never
  clear the goal yourself to escape the loop, and you never tell the user to clear a
  goal you simply succeeded at — a met goal auto-clears on its own.
