---
name: askagy
description: Use when the user invokes /askagy, or asks to consult, cross-check, second-opinion, sanity-check, or hand off a question to Antigravity, agy, or the Antigravity CLI about the work currently in progress. Requires the Antigravity CLI (`agy`) to be installed; if it is not, the skill says so and stops rather than faking a second opinion.
---

# Ask Agy

## Overview

`agy` is the Antigravity CLI — a separate agent process on this machine, reachable non-interactively. It is a **cold-start agent**: it cannot see this conversation, the files you have open, or anything you already know. Its answer is only as good as the context you hand it in a single string.

Core principle: **the prompt is the entire interface.** Build it deliberately, then relay the reply as agy's, not your own.

## Step 0 — Find agy, or stop

Resolve the binary before doing anything else. First hit wins:

```bash
AGY="$(command -v agy 2>/dev/null)"
[ -z "$AGY" ] && [ -x "$HOME/AppData/Local/agy/bin/agy.exe" ] && AGY="$HOME/AppData/Local/agy/bin/agy.exe"
[ -z "$AGY" ] && [ -x "$HOME/.local/bin/agy" ]                && AGY="$HOME/.local/bin/agy"
[ -z "$AGY" ] && [ -x "/usr/local/bin/agy" ]                  && AGY="/usr/local/bin/agy"
echo "${AGY:-NOT_FOUND}"
```

If it resolves, carry `$AGY` through every call below. If it prints `NOT_FOUND`:

> **Say so plainly and stop.** Tell the user the Antigravity CLI is not installed or not on `PATH`, and that `/askagy` needs it. Offer to answer the question yourself instead, clearly labelled as your own view rather than a second opinion.

**Never fabricate a second opinion.** A made-up "agy says…" is worse than no second opinion at all — the entire value of this skill is that the answer came from a different process.

## The Prompt Recipe

Write the prompt as these four parts, in this order:

1. **Task framing** — one sentence naming the role and the job. "You are reviewing a Python data pipeline for correctness bugs."
2. **Context agy cannot see** — the relevant code, error text, file paths, versions, constraints, and what has already been tried and ruled out.
3. **The specific question** — one question, sharply stated. Not three loosely related ones.
4. **Output shape** — how you want the answer back. "List each bug as: file:line, one-sentence cause, minimal fix." Or "Answer in under 200 words, no preamble."

For code questions, prefer pointing agy at the directory with `--add-dir` over pasting large files. It can read them itself.

## Invocation

**Always use the Bash tool with a prompt file.** Shell argument handling mangles long inline prompts. Write the prompt to a temp file first, then pass it as a single argument:

```bash
PROMPT_FILE="$(mktemp -t agy-prompt-XXXXXX)"   # or $CLAUDE_JOB_DIR/tmp/agy_prompt.txt
# ...write the prompt into "$PROMPT_FILE"...
timeout 300 "$AGY" --print-timeout 240s --print "$(cat "$PROMPT_FILE")"
```

Set the Bash tool `timeout` above `--print-timeout`. Model calls typically take 10-60s; complex ones take minutes.

## Quick Reference

| Need | Flag |
|---|---|
| Machine-readable reply | `--output-format json` |
| Pick model | `--model <name>` |
| More reasoning | `--effort high` (low\|medium\|high) |
| Give it a codebase | `--add-dir /path/to/project` |
| Follow up on last reply | `--continue` |
| Resume a specific thread | `--conversation <id>` |
| Let it use tools unattended | `--dangerously-skip-permissions` (only if the user asked) |

**Model names change.** Run `"$AGY" models` to list what this install actually offers rather than assuming a name is still valid. Omit `--model` to use whatever the user configured as their default.

JSON reply shape: `{"conversation_id","status","response","duration_seconds","num_turns","usage":{...}}` — read `.response`, and keep `.conversation_id` if a follow-up is likely.

## Common Mistakes

| Mistake | What happens | Fix |
|---|---|---|
| PowerShell `Start-Process -ArgumentList @("-p","long prompt")` | Silently word-splits; agy replies *"your message might have been cut short"* | Use the Bash tool with `"$(cat file)"` |
| Piping the prompt to stdin | Fails: `flag needs an argument: -print` | agy takes the prompt as an argument only |
| Prompt assumes shared context ("the bug we discussed") | Agy answers a question it invented | Recipe part 2 — spell out the context |
| Bash timeout below `--print-timeout` | Call killed mid-flight, answer lost | Bash timeout > print-timeout |
| Hardcoding an install path | Breaks on every machine but one | Step 0 resolution |
| Presenting agy's reply as your own analysis | User can't weigh the second opinion | Attribute it, and say if you disagree |

## Reporting Back

Give the user agy's answer, attributed. Add your own take when you agree, disagree, or spot something agy missed — the value of a second opinion is the comparison, so don't flatten it into one voice.

Each call spends the user's Antigravity quota under their own account. For a long chain of calls, say so first.
