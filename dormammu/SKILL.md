---
name: dormammu
description: A rigorous "iterate until verified" working loop for any non-trivial build or fix. Use when the user prefixes a request with /dormammu, or asks you to be exhaustive, to "not stop until it's truly done", to self-critique hard, or to keep going until the solution is flawless. Defines the end-state, implements, aggressively self-audits against edge cases and complexity, reverts and retries on any flaw, and only declares done after real verification.
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

### Phase 1 — Define the absolute end-state
Before writing code, state what a 100% correct, robust, optimized outcome actually
looks like — the final *functional* state and its hard requirements (correctness,
edge cases, complexity targets, integration contracts). Not the steps; the target.

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
If the audit finds *any* flaw, inefficiency, or missing requirement, revert.
Emit exactly this line, then act on it:

> "Dormammu, I've come to bargain. <one-sentence reason the current logic failed>."

Discard the flawed approach (don't just patch over it), form a new strategy, and
loop back to **Phase 2**.

### Phase 5 — Break the loop (only if Phase 3 passes)
Exit only when the solution survives a rigorous self-audit **with verification run
and output confirmed**. Then present the final solution and state briefly what you
verified and how.

## Convergence guardrails (so the loop stays honest)

- If two successive attempts fail the *same* way, step back and question the Phase 1
  framing — the requirement or approach may be wrong, not just the code.
- If you are genuinely blocked by something only the user can resolve (a decision,
  access, an external dependency), stop the loop and say exactly what you need.
- Don't manufacture flaws to keep looping. "Converged" is a valid, honest end —
  back it with the verification you ran.
