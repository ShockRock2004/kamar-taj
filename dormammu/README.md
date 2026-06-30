# dormammu

![Dormammu](https://upload.wikimedia.org/wikipedia/en/8/80/Dormammu.png)

> "Dormammu, I've come to bargain."

A Claude Code skill that makes Claude work in a rigorous **iterate until verified**
loop. Named after the bargain that would not end: in Doctor Strange, Dr Strange
traps Dormammu in a time loop and keeps coming back until he gets the outcome he
wants. This skill does the same thing to a coding task. It refuses to call anything
done until it has attacked its own work, handled the edge cases, and actually run
the verification.

## What it does

When you prefix a request with `/dormammu` (or ask Claude to be exhaustive and not
stop until it is truly done), it runs this loop:

1. **Define the end-state.** What does a flawless, robust, optimized result look
   like? The target, not the steps.
2. **Implement** the best real solution, watching complexity and integration
   contracts.
3. **Self-audit hard.** Attack the output: edge cases, load, races, weak contracts,
   simpler-but-correct forms. Back it with real verification, not assertions.
4. **Revert on any flaw** with the line *"Dormammu, I've come to bargain. <reason>."*,
   discard the bad approach, and loop back to step 2.
5. **Stop only on evidence**, then say what was verified.

It also has honest guardrails: if it keeps failing the same way it questions the
requirement, if it is genuinely blocked it tells you instead of spinning, and it
will not invent flaws just to keep looping.

## Install

Part of the [kamar-taj](https://github.com/ShockRock2004/kamar-taj) skills repo, or
drop this folder into your Claude skills folder on its own:

```bash
cp -R dormammu ~/.claude/skills/
```

Restart Claude Code and use `/dormammu`. The full protocol lives in `SKILL.md`.

---

*Image: Dormammu, © Marvel. Linked from Wikipedia for illustration only and not
redistributed here. This is a fan-made, non-commercial tool with no affiliation to
Marvel.*
