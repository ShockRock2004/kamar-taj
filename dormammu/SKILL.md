---
name: dormammu
description: A rigorous "iterate until verified" working loop for any non-trivial build or fix. Use when the user prefixes a request with /dormammu, or asks you to be exhaustive, to "not stop until it's truly done", to self-critique hard, or to keep going until the solution is flawless. On invocation it arms a /goal Stop hook with the verifiable end-state, so the session physically cannot end until the goal is objectively met; then it implements, aggressively self-audits against edge cases and complexity, reverts and retries on any flaw, and only finishes when verification passes and the /goal auto-clears.
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

**This is not run on willpower — it is enforced by `/goal`.** The very first thing
this protocol does is register the end-state as a `/goal` condition (see Phase 1).
`/goal` arms a session Stop hook that physically blocks you from ending your turn
until that condition holds, and auto-clears the moment it does. So "do not stop
early" is not a promise you have to keep by discipline; it is a wall the harness
holds up for you. Dormammu and `/goal` are the same idea from two directions:
`/goal` makes the loop impossible to escape, this protocol makes the loop productive
while you are trapped in it.

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

### Phase 1 — Define the absolute end-state, then ARM IT with `/goal`
First, state what a 100% correct, robust, optimized outcome actually looks like —
the final *functional* state and its hard requirements (correctness, edge cases,
complexity targets, integration contracts). Not the steps; the target.

Then **immediately register that target as a `/goal`**. Compress the end-state into
a single, concrete, externally checkable success condition and run:

```
/goal <the verifiable success condition>
```

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

### Phase 4 — Temporal revert (only if Phase 3 finds a flaw)
**Any time you backtrack — revert, discard an approach, or loop back because
something failed the audit — you MUST first print this exact line, verbatim, on its
own line, before anything else:**

> **Dormammu, I've come to bargain.**

This is mandatory on *every* backtrack with no exceptions: never skip it, never
paraphrase it, never backtrack silently. Print it word for word every single time.

Then, on the next line, give the one-sentence reason the current logic failed, e.g.
"…the loop reprocessed the same row because the cursor was never advanced." Then
discard the flawed approach (don't just patch over it), form a new strategy, and
loop back to **Phase 2**.

### Phase 5 — Break the loop (only when the `/goal` clears)
You do not decide when this ends — the `/goal` condition does. The Stop hook keeps
the turn open until the success condition you armed in Phase 1 objectively holds.
So the only way out is to *actually make it true*: run the verification, watch it
pass, and let the goal auto-clear. When it clears, present the final solution and
state briefly what you verified and how. If you think you are done but the goal has
not cleared, you are not done — find the gap and loop back to Phase 2.

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
