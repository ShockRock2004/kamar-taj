---
name: agamotto
description: Agamotto — adversarial AI code/plan review with foresight. Opens the Eye of Agamotto banner on summon and does a quick foresight self-review, then sends the work to an external reviewer (Codex, or a fresh Claude reviewer subagent if codex is not installed or configured) while Claude fixes, looping until approved. Auto-detects plan/code/code-vs-plan mode. Invoke with /agamotto.
user_invocable: true
---

# Agamotto — Adversarial Code Review with foresight

> **Fork + credit:** Agamotto is a fork of the `adversarial-review` skill by
> dementev-dev (github.com/dementev-dev/adversarial-review, MIT). The review
> machinery below is the original work, preserved. Agamotto adds two things: it
> opens the Eye of Agamotto on summon, and it looks ahead with a foresight
> self-review before spending an external round (see Step 0).

> **Platform:** Claude Code only. This skill orchestrates Claude ↔ Codex interaction, where Claude is the executor and Codex is the external reviewer. Running this skill from Codex CLI itself creates a recursive loop — Codex would try to launch itself. If you are Codex — do NOT invoke this skill; perform the review directly.

Sends current work for adversarial review through an external AI model (OpenAI Codex by default). If codex is not installed or configured, it falls back to a fresh, independent Claude reviewer subagent that plays the same adversarial role. Auto-detects what to review: **plan** or **code**. Claude fixes issues based on reviewer feedback and resubmits until approved. Maximum 5 rounds.

---

## When to invoke

- `/agamotto` — auto-detect what to review
- `/agamotto plan` — force plan review
- `/agamotto code` — force code review
- `/agamotto <file-path>` — review a specific file (argument contains `/` or `.`)
- Override reasoning: `/agamotto xhigh` or `/agamotto medium` (one of: `low`, `medium`, `high`, `xhigh`)
- Override model: `/agamotto model:gpt-5.4` (argument with `model:` prefix)
- Override Codex sandbox: `/agamotto sandbox:read-only` (one of: `read-only`, `workspace-write`, `danger-full-access`, `inherit`)
- Override Codex approval policy: `/agamotto approvals:user` (one of: `user`, `auto_review`, `never`)
- Choose reviewer: `/agamotto reviewer:claude` (or `reviewer:codex`) — default auto-detects; uses codex if installed, else falls back to a fresh Claude reviewer subagent.

Overrides can be combined: `/agamotto plan xhigh sandbox:read-only`.

## Step 0 — The Eye opens (agamotto additions — do this FIRST, every summon)

Before Step 1, always do these two things, in order.

**0a. Open the Eye.** The very first thing you output on invocation is the Eye of
Agamotto banner. **Read** `~/.claude/skills/agamotto/eye.txt` (or `eye.txt` in this
skill's own directory / plugin-cache path), then **print its exact contents inside a
fenced ```text code block``` in your reply message.**

Do NOT `cat` it through a shell command — the Claude Code chat collapses shell
output ("Ran 1 shell command") and does not render it as art, so the banner would
be invisible. It must be in your own message, in a fenced block, to display.

Note on color: the chat renders markdown, not ANSI, so the in-chat banner is
monochrome — that is expected and fine. (A colored `eye.ans` exists for anyone who
`cat`s it in a real terminal outside the chat, but do not use it for the in-chat
banner.) If `eye.txt` genuinely cannot be found, skip silently — never fabricate or
approximate the art.

**0b. Look ahead before you pay (foresight self-review).** The Eye sees failures
before they happen. BEFORE dispatching the expensive external reviewer, do ONE
fast, timeboxed self-review of the same material you are about to send: skim for the
obvious, cheap defects the reviewer would certainly flag — missing error handling,
an unguarded edge case, a broken happy-path assumption, an obvious security slip —
and fix those now. This is a quick pass, NOT a replacement for the external review;
do not skip the real rounds. The point is to spend paid review rounds on the subtle
issues, not the ones you could have caught yourself. Note in one line what the
foresight pass fixed (or "foresight pass: nothing obvious"), then continue to Step 1.

**0c. Pick the reviewer.** Agamotto reviews with an external model. Decide which:
- If the operator passed `reviewer:claude` or `reviewer:codex`, honor it.
- Otherwise auto-detect: run `command -v codex`. If it resolves, use **codex** (the
  default external reviewer — Steps 4/7 as written). If it does NOT resolve, fall
  back to **claude** (see "Claude reviewer fallback" below).
- If codex resolves but a dispatch later fails with a launch or config error (for
  example not authenticated), tell the operator once and re-route THIS round through
  the Claude reviewer fallback instead of aborting.

Set `REVIEWER = codex | claude` and carry it through every round. State which
reviewer ran in the Step 5 round header.

## Claude reviewer fallback (when codex is unavailable)

When `REVIEWER = claude`, do NOT dispatch the codex runner subagent (Step 4 / Step
7) or any codex-specific machinery (session id, sandbox, `references/runner.md`, the
`/tmp` mutation snapshots). Instead, in place of each codex dispatch, launch a fresh
**Claude reviewer subagent** that produces the review file the rest of the skill
already expects:

- **Agent tool:** `subagent_type: "general-purpose"`, a capable model,
  `description: "Agamotto Claude reviewer, round N"`.
- **Prompt:** the SAME prompt body you built in Step 4 (the `<role>`,
  `<operating_stance>`, `<attack_surface>`, `<finding_bar>`, `<output_format>`, and
  `<reviewer_permissions>` blocks — including the exact `VERDICT: APPROVED|REVISE`
  output contract). Prepend: "You are a fresh, independent reviewer. You did NOT
  write this code. Read the diff and the cited files yourself. Do not edit, create,
  or delete any project file — you are a read-only auditor. Write your review, in the
  exact output_format, to `/tmp/codex-review-${REVIEW_ID}.md`, then reply with the
  single line `RUNNER_RESULT_AT: /tmp/codex-review-${REVIEW_ID}.md`."
- For a **resume** round, also give the subagent the prior review and the lead's
  structured response (Applied / Re-scoped / Rejected) plus the current diff, and
  ask it to re-review in the same format and overwrite the same review file.

Then continue at **Step 5** exactly as written: read `/tmp/codex-review-${REVIEW_ID}.md`,
run the semantic sanity checks, show it verbatim, parse the VERDICT, and loop. The
5-round cap and the fix / evaluate steps are identical.

> **Honest limitation.** A Claude subagent reviewing Claude's work is not as
> independent as a different model like codex — it shares some blind spots with the
> author. A fresh, adversarial, read-only subagent still gives real second-pair-of-
> eyes value, but prefer codex when available. The Claude fallback is the "better
> than no review" path.

## Instructions

> **Placeholders:** `${REVIEW_ID}`, `${ATTEMPT_ID}`, `${CODEX_SESSION_ID}`, `${REPO_ROOT}`, and `${BASE_BRANCH}` in the steps below are template placeholders, NOT shell variables. Substitute literal values directly into each tool call. In particular:
> - `${REPO_ROOT}` is ALWAYS an absolute path captured at Step 2; never replace it with `$(pwd)`.
> - `${REVIEW_ID}` is stable for the entire review (used in file paths).
> - `${ATTEMPT_ID}` is a fresh 6-digit random integer generated **per launch** — a new value for the initial exec, for any retry of that exec, for every resume in Step 7, and for any fresh-exec fallback. The combined marker `${REVIEW_ID}-${ATTEMPT_ID}` is embedded in the prompt (HTML comment) so the filesystem session-id fallback identifies exactly THIS launch's rollout. Do NOT reuse a prior launch's ATTEMPT_ID — that would make multiple rollouts match and reintroduce silent session drift.

### Step 1: Determine review mode

Determine what to review. Check in priority order:

**1. Explicit argument** (`plan`, `code`, file path) → use it.
   - For `plan` → skip all git checks, proceed to step 2 (REVIEW_ID only).

**2. Claude Code Plan Mode** — if context contains the system message "Plan mode is active" → mode = `plan`, skip git. In Plan Mode code is not edited, so code/code-vs-plan are impossible.

**3. Auto-detect** (no explicit argument, not in Plan Mode):

1. Check for code changes (any non-empty output means changes exist):
   - `git diff --name-only` — unstaged
   - `git diff --cached --name-only` — staged
   - `git diff --name-only ${BASE_BRANCH}...HEAD` — branch commits
2. Check if a plan exists in the current conversation context (from plan mode, tasks, or discussion).

| Code changes? | Plan in context? | Mode |
|--------------|-----------------|------|
| No | Yes | **plan** — review the plan |
| Yes | Yes | **code-vs-plan** — review implementation against plan |
| Yes | No | **code** — review code changes |
| No | No | Ask the user what to review |

#### Step 1 (continued): Capture overrides, detect operator language, emit runtime hint

**Parse the invocation arguments for overrides** (case-sensitive on the prefix). Apply them to the per-review configuration captured below. Any unrecognized token after stripping the mode and overrides is treated as an unknown argument — surface a one-line "ignoring unknown argument: <token>" warning and continue.

| Argument shape                            | Sets                                                                                  | Default if absent                                                                                                       |
|-------------------------------------------|---------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------|
| `model:<name>`                            | `CODEX_MODEL = <name>`                                                                | `CODEX_MODEL = gpt-5.5`                                                                                                 |
| `low` / `medium` / `high` / `xhigh`       | `CODEX_REASONING = <value>`                                                           | `CODEX_REASONING = high`                                                                                                |
| `sandbox:read-only`                       | `CODEX_SANDBOX = read-only`                                                           | `CODEX_SANDBOX = workspace-write`                                                                                       |
| `sandbox:workspace-write`                 | `CODEX_SANDBOX = workspace-write`                                                     | (same as default)                                                                                                       |
| `sandbox:danger-full-access`              | `CODEX_SANDBOX = danger-full-access`. **Emit a one-line warning** to the operator: `⚠ sandbox:danger-full-access — reviewer can write anywhere on disk; reserve for trusted local debugging.` | (n/a — explicit-only, never default) |
| `sandbox:inherit`                         | `CODEX_SANDBOX = inherit`. Runner skips bwrap preflight; effective sandbox is whatever the user's Codex config selects. | (n/a — explicit-only)                                                                                                  |
| `approvals:auto_review` (default)         | `CODEX_APPROVAL_POLICY = on-request`, `CODEX_APPROVALS_REVIEWER = auto_review`        | (same as default)                                                                                                       |
| `approvals:user`                          | `CODEX_APPROVAL_POLICY = on-request`, `CODEX_APPROVALS_REVIEWER = null` (omit `-c approvals_reviewer` → Codex falls back to its built-in `user` reviewer, which can ask the operator for approval). Nested approvals may hang the run from the parent Claude session — use only when explicitly desired. | (n/a — explicit-only) |
| `approvals:never`                         | `CODEX_APPROVAL_POLICY = never`, `CODEX_APPROVALS_REVIEWER = null`. Boundary crossings fail instead of asking. | (n/a — explicit-only)                                                                                                  |

Codex's `untrusted` approval policy is intentionally NOT exposed as an override — the skill needs predictable boundary semantics, not per-command trust prompts.

**Resume invariant.** Sandbox and approval mode are properties of the original Codex session. `codex exec resume` does NOT accept `-s` or approval-related `-c` flags. If the operator changes `sandbox:` or `approvals:` mid-review, the new value takes effect only on a fresh-exec dispatch (which consumes a round). Surface this in the warning if the operator passes a sandbox/approvals override on a re-invocation of the skill while a prior session is still live.

**No silent fallback** may change sandbox or approval semantics. If any of the captured values cannot be passed to Codex on the target host (e.g. an installed Codex CLI version that doesn't support `-c approvals_reviewer`), surface an explicit diagnostic before dispatch — do NOT downgrade silently.

**Detect operator language.** Inspect the last few human-authored messages in the current conversation. If they are predominantly in a non-English language, capture `OPERATOR_LANGUAGE = <name of language>` (e.g. `Russian`, `Spanish`, `Japanese`). If detection is ambiguous, default to `OPERATOR_LANGUAGE = English`. Runtime prose shown to the operator (warnings, summaries, intermediate updates) MUST use `OPERATOR_LANGUAGE` when practical. Repository files (this `SKILL.md`, `references/runner.md`, `README.md`, `docs/DESIGN.md`, specs under `docs/superpowers/specs/`) stay in English regardless.

**Emit the one-line runtime hint** about sandbox defaults — **once per review, before Step 2 starts**. The hint is suppressed when the operator passed an explicit `sandbox:*` override (any of `read-only`, `workspace-write`, `danger-full-access`, `inherit`):

```
ℹ workspace-write in effect; pass sandbox:read-only if sensitive ignored state lives under REPO_ROOT.
```

Translate the hint into `OPERATOR_LANGUAGE` if non-English. Do NOT repeat per round.

The conditional warning about already-dirty tracked files lives in Step 2 (it depends on a captured `REPO_ROOT`).

### Step 2: Generate Session ID, capture REPO_ROOT, determine base branch

**REVIEW_ID:** generate yourself, format `{unix_timestamp}-{random_8digit_number}`.
Example: `1711872000-48217593`. **Do NOT use bash** — substitute the value directly into commands in the following steps. 8-digit random makes collisions negligible (1 in 10^8 per same-second invocation).

**Capture REPO_ROOT:**

```bash
git rev-parse --show-toplevel
```

- **Exit 0, non-empty output** → absolute path. Save literally as `REPO_ROOT` (a template placeholder — substitute verbatim into codex commands; do NOT use `$(pwd)` anywhere).
- **Exit 128** (bare repo, or not in a work tree) → tell the user: `Cannot run adversarial review — current directory is not inside a git working tree.` Abort the skill.
- **Path contains single quote, double quote, `$`, backtick, newline** → tell the user: `REPO_ROOT path contains shell-special characters; cannot safely construct codex commands.` Abort.

**Submodule warning:** after capturing REPO_ROOT, run:

```bash
git rev-parse --show-superproject-working-tree
```

If this returns non-empty, the user is inside a git submodule. Tell the user: `You are inside a submodule. The review will be scoped to this submodule (${REPO_ROOT}), not the parent repo. If you meant to review the parent, invoke from there.` Proceed — this is a warning, not an abort.

**Conditional warning about already-dirty tracked files** (skip when `OPERATION=plan`). Now that `REPO_ROOT` is captured and validated, run `git -C "${REPO_ROOT}" status --porcelain` and inspect the output. If any line matches `^[ M][M ] ` (a tracked file already modified in working tree or index pre-review), emit this extra one-line warning (once per review):

```
ℹ <N> unstaged or staged tracked-file edit(s) detected. The porcelain mutation snapshot only detects status transitions; reviewer-side content drift of already-dirty files is NOT auto-caught. Commit/stash WIP first for stronger protection, or pass sandbox:read-only.
```

Translate to `OPERATOR_LANGUAGE`. Substitute `<N>` with the count of matching lines. Suppressed when no already-dirty tracked files exist. See `docs/DESIGN.md §4.20` and `README.md` "Safety considerations" for the residual-risk rationale.

**Determining base branch (only for `code` and `code-vs-plan` modes):**

For `plan` mode — skip base branch detection, proceed to step 3.

For other modes, determine the repository's base branch:

```bash
git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's|refs/remotes/origin/||'
```

If the command returns empty (remote HEAD not configured), use fallback:

```bash
git rev-parse --verify main 2>/dev/null && echo main || echo master
```

Save the result as `BASE_BRANCH` — used in `git diff ${BASE_BRANCH}...HEAD` below.

### Step 3: Prepare review material

**Plan review:**

- If the plan already exists as a file (in `project/`, plan file from Plan Mode, memory, or somewhere in the repo) — use the path directly. Do NOT copy. In Claude Code Plan Mode the plan is always a file.
- If the plan is only in the conversation context (outside Plan Mode) — write via **Write tool** to `/tmp/codex-plan-${REVIEW_ID}.md`.
- **Always print the plan file path for the user** so they can open it in their IDE:
  `Plan for review: <file-path>`

**Code review:**

Collect the list of changed files:

1. `git diff --name-only` — unstaged changes
2. `git diff --cached --name-only` — staged changes

Merge unstaged + staged (unique paths). If both are empty:

3. `git diff --name-only ${BASE_BRANCH}...HEAD` — branch commits (fallback)

Branch diff is used ONLY when there are no local changes — otherwise context bloats.
For branch diff, include the command `git diff ${BASE_BRANCH}...HEAD` (full diff) in the prompt.

The reviewer has access to the repo and will read full diffs and files on its own.
In the prompt (step 4), pass the file list and which git diff commands to run.

**Many files (> 50):** if the combined list exceeds 50 paths,
pass only git commands without the file list — the reviewer will figure it out.

If all sources are empty — no changes to review, inform the user.

**Code-vs-plan review:** prepare the plan path AND collect the list of changed files (as above).

### Step 4: Build the prompt body, dispatch the runner subagent

> **If `REVIEWER = claude`:** still build the prompt body as below, but do NOT
> dispatch the codex runner — hand that same body to the Claude reviewer subagent
> from the "Claude reviewer fallback" section, then resume at Step 5.

Main thread composes the prompt BODY (without the session marker — the subagent adds it). Select the right template from below based on review mode.

**Prompt body for plan review:**

```
<role>
You are a senior adversarial reviewer of implementation plans.
Your job is to break confidence in the plan, not to validate it.
</role>

<operating_stance>
Default to skepticism. Assume the plan has gaps until the evidence says otherwise.
Do not give credit for good intent or likely follow-up work.
If something only works on the happy path, treat that as a real weakness.
</operating_stance>

<task>
Review the implementation plan in <plan-path>.
</task>

<attack_surface>
Check each area. Skip if not applicable:
- Feasibility — will this approach actually work given the codebase and constraints?
- Missing steps — what is forgotten or assumed but not stated?
- Risk areas — what could go wrong during implementation? Data loss? Downtime?
- Sequencing — are steps in the right order? Are there hidden dependencies?
- Alternatives — is there a simpler or more robust approach?
- Rollback — can this be safely reverted if it fails halfway?
- Security — auth, data exposure, injection, unsafe operations
</attack_surface>

<finding_bar>
Each finding MUST answer:
1. What can go wrong? (concrete scenario, not hypothetical)
2. Why is this plan vulnerable? (cite specific section)
3. Impact — what breaks and how badly?
4. Recommendation — specific change to the plan
</finding_bar>

<scope_exclusions>
DO NOT comment on: formatting, wording style, speculative issues without concrete trigger scenario.
</scope_exclusions>

<calibration>
Prefer one strong finding over several weak ones.
If the plan is solid, say so clearly — false positives erode trust.

Judge the plan at its declared level of abstraction.
Do not demand implementation details unless their absence blocks feasibility,
safety, rollback, verification, or a public contract.
If a detail can reasonably be decided during implementation, do not count it
as a finding.
</calibration>

<output_format>
Use markdown headers for sections: Summary, Findings, Verdict.

Summary: one paragraph — what this plan does and your overall assessment.

Findings: for each finding, use a sub-header with [severity: critical|high|medium] and title.
Include these fields per finding:
- **Section:** which part of the plan
- **What can go wrong:** ...
- **Why vulnerable:** ...
- **Impact:** ...
- **Recommendation:** ...

If no findings: "No actionable findings."

Verdict rules: approve if no findings or all low severity; revise if any high/critical.
Choose exactly one. The LAST line of your response must be one of:
VERDICT: APPROVED
VERDICT: REVISE
</output_format>
```

**Prompt body for code review (≤ 50 files):**

```
<role>
You are a senior adversarial code reviewer.
Your job is to break confidence in the change, not to validate it.
</role>

<operating_stance>
Default to skepticism. Assume the change can fail in subtle, high-cost,
or user-visible ways until the evidence says otherwise.
Do not give credit for good intent, partial fixes, or likely follow-up work.
If something only works on the happy path, treat that as a real weakness.
</operating_stance>

<task>
Review the code changes in this repo. Changed files:

<file list from --name-only>

Changes include: <unstaged changes / staged changes / unstaged + staged changes / branch changes vs ${BASE_BRANCH}>.
Run <git diff commands> to see the full diffs.
</task>

<attack_surface>
Check each area. Skip if not applicable to this change:
- Auth & permissions: bypasses, privilege escalation, missing checks
- Data integrity: loss, corruption, partial writes, constraint violations
- Race conditions: TOCTOU, concurrent access, deadlocks
- Rollback safety: can this change be safely reverted?
- Schema drift: migrations, backward compatibility, data format changes
- Error handling: swallowed errors, missing retries, cascading failures
- Observability: will operators know when this breaks?
</attack_surface>

<finding_bar>
Each finding MUST answer:
1. What can go wrong? (concrete scenario, not hypothetical)
2. Why is this code vulnerable? (cite specific file and lines)
3. Impact — what breaks and how badly? (data loss > downtime > degraded UX)
4. Recommendation — specific fix with code reference
</finding_bar>

<scope_exclusions>
DO NOT comment on: code style, formatting, naming conventions,
speculative issues without concrete trigger scenario,
"nice to have" improvements unrelated to correctness or safety.
</scope_exclusions>

<calibration>
Prefer one strong finding over several weak ones.
Severity: critical (data loss/security) > high (bug in prod) > medium (edge case).
If the change is solid, say so clearly — false positives erode trust.
</calibration>

<output_format>
Use markdown headers for sections: Summary, Findings, Verdict.

Summary: one paragraph — what this change does and your overall assessment.

Findings: for each finding, use a sub-header with [severity: critical|high|medium] and title.
Include these fields per finding:
- **File:** path/to/file.ext lines N-M
- **What can go wrong:** ...
- **Why vulnerable:** ...
- **Impact:** ...
- **Recommendation:** ...

If no findings: "No actionable findings."

Verdict rules: approve if no findings or all low severity; revise if any high/critical.
Choose exactly one. The LAST line of your response must be one of:
VERDICT: APPROVED
VERDICT: REVISE
</output_format>
```

**Prompt body for code review (> 50 files):**

Same as ≤ 50 files above, but the `<task>` section is replaced with:

```
<task>
Review the code changes in this repo.
Changes include: <unstaged changes / staged changes / ...>.
Run <git diff commands> to see changed files and full diffs.
</task>
```

**Prompt body for code-vs-plan review:**

Same as code review (≤ 50 or > 50 variant depending on file count), but:
- `<task>` is extended to reference the plan file: `Review the code changes in this repo against the implementation plan in <plan-path>.`
- `<attack_surface>` appends these three items:
  ```
  - Completeness: does the implementation cover all plan steps?
  - Deviations: where does the code differ from the plan? Are deviations justified?
  - Missing: what from the plan is not yet implemented?
  ```

**Substitute template placeholders BEFORE writing to disk:**

The inlined prompt bodies above contain template placeholders that main must resolve with real captured values before the Write. Placeholders per mode:

| Placeholder | Value source | Applies to |
|---|---|---|
| `${BASE_BRANCH}` | captured at Step 2 (code & code-vs-plan only) | code, code-vs-plan |
| `<plan-path>` | captured at Step 3 | plan, code-vs-plan |
| `<file list from --name-only>` | result of `git diff --name-only` + `git diff --cached --name-only` (or branch diff) from Step 3 | code, code-vs-plan (≤50 files only) |
| `<unstaged changes / staged changes / ...>` | human-readable description derived from which diff commands had content | code, code-vs-plan |
| `<git diff commands>` | the exact commands main determined at Step 3 (e.g. `git diff`, `git diff --cached`, `git diff ${BASE_BRANCH}...HEAD`) | code, code-vs-plan |

Substitute `${BASE_BRANCH}` first (it appears nested inside `<unstaged changes / staged changes / ...>`), then compute the outer human-readable description based on which diffs have content. Main writes the substituted string to the Write tool — no template placeholders should remain in the body file sent to the runner.

**Append the operator-language block to the prompt body** when `OPERATOR_LANGUAGE != "English"` (captured in Step 1). Append the following block verbatim AFTER the `<output_format>` section and BEFORE any trailing content:

```
<language>
Respond in the operator's language: <OPERATOR_LANGUAGE>.
Keep these machine-readable literals unchanged in English (they are parsed by the lead and must not be translated):
- [severity: critical|high|medium]
- VERDICT: APPROVED
- VERDICT: REVISE
The Summary / Findings / Verdict section headers should also stay in English so the runner's content classifier and triage rg patterns continue to match.
</language>
```

Substitute the literal name of the detected language for `<OPERATOR_LANGUAGE>`. Do NOT translate the block itself — the reviewer reads English instructions and produces prose in the target language. When `OPERATOR_LANGUAGE = "English"`, OMIT the block entirely (default behavior).

**Reviewer permissions and approval semantics.** The Codex reviewer is an auditor, not a contributor. Append the following block to every prompt body (regardless of mode), AFTER the `<output_format>` section and AFTER the optional `<language>` block:

```
<reviewer_permissions>
You may run commands to verify findings when useful: tests, linters, build
commands, git inspection, MCP-backed doc lookups, web search, project CLI
introspection.

Do not create, edit, delete, commit, or apply fixes to project files.
Prefer commands that do not mutate the working tree.
Do not run commands likely to rewrite generated files, snapshots, migrations,
lockfiles, or configs.
If verification would require mutation, report that limitation instead.
If a command unexpectedly changes files, stop and report it.

You are an auditor, not a contributor. The lead applies fixes; you find issues.
</reviewer_permissions>
```

This is the primary safeguard against reviewer-side mutation. Workspace-level mutation detection (see "Workspace mutation snapshot" below) is the secondary safeguard.

**Write the prompt body to disk via Write tool:**

Write `/tmp/codex-body-${REVIEW_ID}.md` containing the substituted body text (no session marker — the runner adds it).

> **Plan Mode note:** Writing to `/tmp` via Write tool may trigger a permission prompt or exit Plan Mode. This is a known Claude Code limitation. Additionally, dispatching a subagent under Plan Mode may inherit the restriction — empirical behavior documented in DESIGN.md §12.7.

**Resolve the runner spec path:**

The runner spec lives at `references/runner.md` within the skill's install directory. Main cannot reliably introspect Claude Code's skill-invocation header from inside its own context (there is no tool for reading one's own system prompt — any attempt would be a hallucination risk). Therefore the discovery uses only concrete filesystem checks, in this priority order:

1. **User-scoped install** (primary): check `~/.claude/skills/agamotto/references/runner.md`:

```bash
ls ~/.claude/skills/agamotto/references/runner.md 2>/dev/null
```

If exit 0, set `RUNNER_SPEC_PATH` to the expanded absolute path and proceed.

2. **Plugin-marketplace install** (secondary): Claude Code's plugin system installs skills at paths like `~/.claude/plugins/cache/<marketplace>/<plugin>/<version>/skills/agamotto/`. Glob to find it:

```bash
ls ~/.claude/plugins/cache/*/*/*/skills/agamotto/references/runner.md 2>/dev/null | head -1
```

If the Glob returns one or more paths, take the first and set `RUNNER_SPEC_PATH`.

3. **Dev checkout** (tertiary): if neither above, try `$(git rev-parse --show-toplevel)/references/runner.md`:

```bash
REPO=$(git rev-parse --show-toplevel 2>/dev/null) && ls "$REPO/references/runner.md" 2>/dev/null
```

4. **Abort**: if no path yields a readable file, tell the user: `Could not locate references/runner.md. Expected locations: (1) ~/.claude/skills/agamotto/references/runner.md, (2) ~/.claude/plugins/cache/*/*/*/skills/agamotto/references/runner.md, (3) $(git rev-parse --show-toplevel)/references/runner.md. Re-install the skill.` Abort the skill.

Save the resolved absolute path as `RUNNER_SPEC_PATH`. Do NOT attempt to extract the path from any "Base directory for this skill:" line in the conversation — that line is a system injection Claude cannot reliably read from inside its own context.

**Workspace mutation snapshot (pre-dispatch):**

Mutation detection runs at two layers: the repo tree (git-tracked + new untracked files inside `REPO_ROOT`) and the skill's `/tmp` review inputs. A third class — gitignored files already inside `REPO_ROOT` — is documented as a known, operator-mitigated risk and is NOT detected automatically (see `README.md` "Safety considerations" and the runtime hint from Step 1).

Capture both layers BEFORE every runner dispatch (initial, resume, fresh-exec):

```bash
git -C "${REPO_ROOT}" status --porcelain > /tmp/codex-git-pre-${REVIEW_ID}.txt
sha256sum /tmp/codex-body-${REVIEW_ID}.md \
          /tmp/codex-plan-${REVIEW_ID}.md \
          /tmp/codex-resume-body-${REVIEW_ID}.md 2>/dev/null \
  > /tmp/codex-inputs-pre-${REVIEW_ID}.sha
```

The `2>/dev/null` is deliberate: not every review has all three files (plan-mode reviews skip the body, round-1 dispatches skip resume-body). Missing files are silently elided from the snapshot and are still caught later if they appear unexpectedly.

**Dispatch the runner subagent via Agent tool:**

**Do NOT Read `${RUNNER_SPEC_PATH}` in main.** Pass the path to the subagent; it reads the spec itself. This keeps runner.md (~12K) out of main's context — both the Read result AND the Agent prompt duplication. Saves ~12K per round × up to 5 rounds per review.

Invoke the Agent tool with:
- `subagent_type: "general-purpose"`
- `model: "sonnet"`
- `description: "Adversarial-review runner, round N"` (N is the current round number)
- `prompt:` a short bootstrap instruction + YAML input block (no inlined runner.md):

```
Read your full instruction spec at ${RUNNER_SPEC_PATH} and follow the steps there using this input:

---
REVIEW_ID: 1711872000-48217593
REPO_ROOT: /home/dementev/sources/myproject
OPERATION: initial
CODEX_MODEL: gpt-5.5
CODEX_REASONING: high
CODEX_SANDBOX: workspace-write
CODEX_APPROVAL_POLICY: on-request
CODEX_APPROVALS_REVIEWER: auto_review
PROMPT_BODY_PATH: /tmp/codex-body-1711872000-48217593.md
RESULT_PATH: /tmp/codex-runner-result-1711872000-48217593.json
---
```

Substitute the actual resolved `${RUNNER_SPEC_PATH}` (absolute path) and real values for every other placeholder. `RESULT_PATH` always follows the pattern `/tmp/codex-runner-result-${REVIEW_ID}.json`.

Use the values captured in Step 1 for `CODEX_MODEL`, `CODEX_REASONING`, `CODEX_SANDBOX`, `CODEX_APPROVAL_POLICY`, and `CODEX_APPROVALS_REVIEWER`. When `CODEX_APPROVALS_REVIEWER` is `null` (set by `approvals:user` or `approvals:never`), pass the literal string `null` as the YAML value — the runner interprets it and omits the `-c approvals_reviewer` flag.

**Do NOT run the Agent tool call in background.** Wait for the subagent to return. (Runner's own codex exec is also synchronous per runner Step R3.)

**Parse the subagent's response — two-channel protocol:**

Apply the regex `RUNNER_RESULT_AT:\s+(\S+)` (UNANCHORED — matches anywhere in the Agent tool's result text, tolerant of markdown fences and preamble). Take the first match's capture group as the result-file path.

If the regex finds NO match in the subagent's response, fall back to a Glob for the deterministic path `/tmp/codex-runner-result-${REVIEW_ID}.json` — REVIEW_ID is already known to main. If Glob also returns nothing, treat as `infra_error` with `errors: "runner did not write result file at deterministic path and did not emit RUNNER_RESULT_AT line"` and abort.

Read the file at the resolved path. Parse as JSON. Extract `result`, `verdict`, `review_file`, `codex_session_id`, `errors`, `user_warning`, `archived_stdout`, `archived_stderr`, `review_quality`, and the `triage` object.

**Backward compatibility for `review_quality` / `triage`.** A legacy runner result that omits `review_quality` and `triage` is treated as `review_quality = "unknown"` and `triage = { status: "skipped", finding_count: 0, max_severity: "none", covered_critical: 0, covered_high: 0, covered_medium: 0, truncated: false, needs_lead_judgment: false }`. No abort, no operator prompt; the legacy result is consumed as if the runner had emitted those values explicitly.

**Workspace mutation snapshot (post-dispatch).** BEFORE consulting the dispatch table below, and BEFORE applying any fixes, capture the post-state and diff against the pre-state:

```bash
git -C "${REPO_ROOT}" status --porcelain > /tmp/codex-git-post-${REVIEW_ID}.txt
sha256sum /tmp/codex-body-${REVIEW_ID}.md \
          /tmp/codex-plan-${REVIEW_ID}.md \
          /tmp/codex-resume-body-${REVIEW_ID}.md 2>/dev/null \
  > /tmp/codex-inputs-post-${REVIEW_ID}.sha

diff -q /tmp/codex-git-pre-${REVIEW_ID}.txt \
        /tmp/codex-git-post-${REVIEW_ID}.txt
diff -q /tmp/codex-inputs-pre-${REVIEW_ID}.sha \
        /tmp/codex-inputs-post-${REVIEW_ID}.sha
```

Two diffs, two cases:

1. **Tracked-file mutation** — the `git status --porcelain` diff shows new modified (`^[ M]M`) or deleted (`^[ D]D`) entries that didn't exist pre-dispatch, OR untracked files (`^\?\?`) that look like edits to real source files (not editor scratchpads). **HARD STOP** before applying any fixes. Surface an operator diagnostic:

   ```
   ❌ Reviewer or runner mutated tracked files during dispatch.
   Pre-state vs post-state diff:
   <output of `diff` on the two -porcelain files>
   Aborting before fixes. Inspect the diff and decide whether to revert
   or keep the changes manually. Re-run /agamotto when ready.
   ```

   Then skip Steps 5–9 and exit. Do NOT proceed to apply fixes — the artifact under review may have been silently mutated, invalidating the round.

2. **Untracked generated artifacts only** — `^\?\?` entries that look benign (e.g. build caches, log files). Warn the operator but allow continuation:

   ```
   ⚠ Reviewer left untracked files behind: <list>.
   Proceeding with the round, but please review whether these should be
   .gitignored or removed.
   ```

3. **`/tmp` review-input mutation** — the `sha256sum` diff is non-empty. Treat this exactly like tracked-file mutation: hard stop and surface the diagnostic. The reviewer should NEVER modify its own prompt body or plan file.

4. **No mutation** — both diffs are empty (or only show whitespace differences from the eager pre-snapshot). Proceed to the dispatch table.

The pre/post snapshot pair is repeated for every Codex dispatch (Step 4 initial, Step 7 resume, Step 7.4 fresh-exec). It is NOT optional — skipping it forfeits the only detection of reviewer-side mutation that does not depend on the reviewer self-reporting.

**If `user_warning` is non-null, surface it as a SEPARATE short user-visible message BEFORE the Step 5 verbatim-review message.** Format:

```
⚠ <user_warning contents>
```

Emit this on its own turn — do NOT concatenate into the Step 5 `## Adversarial Review — Round N` header message (that message's body must remain the review's verbatim content, nothing else). Emit the warning FIRST, then the Step 5 message. This preserves both the pre-refactor §2.4.4 "no-op refresh" diagnostic AND the Step 5 verbatim-display contract.

**Dispatch based on `result` × `OPERATION` × `review_quality`.** The table below is operation-aware: `degraded_environmental` on the initial dispatch is terminal because there is no prior valid round to fall back to, whereas the same classification on a resume can be re-routed through the existing fresh-exec fallback chain.

| `result`         | `OPERATION`   | `review_quality`         | Main thread action                                                                                                                                                                                                                                |
|------------------|---------------|--------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `success`        | any           | `valid`                  | Save `codex_session_id` (keep prior if `null` per §2.4.4). Surface `user_warning` if set. Proceed to Step 5: show review verbatim, run evaluation matrix in Step 6, advance round.                                                                |
| `success`        | any           | `degraded_content`       | Surface `user_warning`. Show review verbatim per Step 5. THEN ask the operator: "Reviewer output flagged as low-confidence — advance the round anyway, or abort?" Default to advance after a short wait if running headlessly.                    |
| `success`        | any           | `unknown`                | Surface `user_warning`. Treat as `valid` for round advancement (Step 5 + Step 6). Note the unknown classification in the final operator summary (Step 8).                                                                                          |
| `success`        | `initial`     | `degraded_environmental` | Surface `user_warning`. Do NOT show review verbatim (the file does not contain a real review). Treat as **terminal infrastructure failure** — abort the skill with the operator diagnostic. No prior valid review exists to fall back to.         |
| `success`        | `resume`      | `degraded_environmental` | Surface `user_warning`. Do NOT show review verbatim. Do NOT count this dispatch as a round. Route to the Step 7.4 fallback chain, using the **prior round's** maximum severity for the fallback decision.                                          |
| `success`        | `fresh-exec`  | `degraded_environmental` | Surface `user_warning`. Do NOT show review verbatim. Treat as **terminal not-verified** (the Step 8 NOT VERIFIED branch). Fresh-exec already was the fallback chain; a second environmental failure means the environment is reliably broken.    |
| `timeout`        | any           | n/a                      | **TERMINAL.** Runner already attempted twice internally (R4.1 + R5 retry = 2 × 10min). Tell user: "Reviewer timed out after two attempts (20 minutes total)." Abort the skill. User can re-invoke `/agamotto` to start fresh.            |
| `launch_failure` | `initial`     | n/a                      | **TERMINAL.** The runner already retried once internally (Step R5). Show `errors` to user, abort the skill.                                                                                                                                        |
| `launch_failure` | `resume`      | n/a                      | **TERMINAL for this round.** Route to the Step 7.4 fallback chain (runner already archived stdout/stderr to `-failed-resume.*` per `archived_stdout`/`archived_stderr`).                                                                            |
| `launch_failure` | `fresh-exec`  | n/a                      | **TERMINAL.** Fresh-exec was the fallback; show `errors`, abort with the not-verified terminal state.                                                                                                                                              |
| `infra_error`    | any           | n/a                      | Show `errors` to user (infrastructure: `/tmp` not writable, stderr file missing, RUNNER_RESULT_AT line absent, bwrap preflight failed). Abort.                                                                                                     |
| `input_error`    | any           | n/a                      | Bug in orchestration. Show `errors` to user. Abort.                                                                                                                                                                                                |

Whenever the dispatch outcome says "Surface `user_warning`", emit it on its own turn BEFORE the Step 5 verbatim message (or BEFORE the abort message, when there is no Step 5). Never concatenate the warning into the Step 5 header.

**Round-level attempt invariant:** exactly ONE runner dispatch per round (except when `degraded_environmental` on resume routes through fallback without counting as a round). The runner owns the full retry budget (≤2 attempts per dispatch, internal) regardless of failure type. Total codex invocations per round ≤ 2.

> **CRITICAL — main thread does NOT read stdout/stderr/JSONL/rollout files BY CONTENT.** Those live and die inside the subagent. Main reads: the runner result JSON at `RESULT_PATH`, the review file at `review_file`, and nothing else from `/tmp/codex-*`. Archival `mv` (on resume failure) is done by the runner, not main — main never references `/tmp/codex-stdout-*` or `/tmp/codex-stderr-*` in any Bash argv.

### Step 5: Read the review, show it, then check the verdict

**1. Read the review file.** Read `/tmp/codex-review-${REVIEW_ID}.md`.

**2. Semantic sanity checks.** The file MUST pass all of these:

- Exists and is non-empty.
- Contains a line exactly matching `^VERDICT: (APPROVED|REVISE)$`.
- If verdict is `REVISE` → file must also contain at least one line matching `\[severity:\s*(critical|high|medium)` (i.e. at least one structured finding).

If any check fails → this is a **launch failure** (model produced no actionable review):

- Show the user the `/tmp/codex-stderr-${REVIEW_ID}.txt` contents (if any) AND the raw review file.
- Offer ONE retry of Step 4 (re-launch the same round). Retry does NOT consume the round counter — the round counter advances only when a valid review is produced.
- Track the retry counter in your **current round's** reasoning only. The counter resets at the start of every new round.
- After a failed retry → hard abort the skill. Do NOT route to the Step 7 fresh-exec fallback (that path is for resume failures in rounds 2+, and depends on prior-round content).

**3. Show the review to the user. This is mandatory and blocking.**

> Your next user-visible message that is NOT a one-line `⚠ <warning>` diagnostic must begin with the header below, followed by the file contents **verbatim**. Not "I've received the review", not "The reviewer said:", not a summary — the literal file content.
>
> Do NOT wrap the review in a code fence (the review is already markdown, and an outer fence would break on inner fences).
>
> Do NOT call any Edit, Write, or fix-applying tool in the same message as the review. The review output is a standalone user-visible message.

Message format:

```
## Adversarial Review — Round N (mode: <plan|code|code-vs-plan>, model: <CODEX_MODEL>)

<verbatim contents of /tmp/codex-review-${REVIEW_ID}.md>
```

**4. Only AFTER the review message has been sent** — parse the VERDICT line and dispatch:

- `VERDICT: APPROVED` → Step 8 (Done).
- `VERDICT: REVISE` → Step 6 (Fixes).
- Maximum rounds reached (5 rounds) → Step 8 with the max-rounds note.

### Step 6: Evaluate findings, gate structural fixes, then apply

> **Precondition gate (check first).** Before calling any Edit, Write, or other fix-applying tool: confirm that you have already sent a user-visible message in THIS round whose body contains the verbatim review text (short `⚠ <user_warning>` diagnostic messages do NOT count). If you have not — STOP. Go back to Step 5 and send the review message now. This is the same rule that protects the "user sees the review" contract; a literal reader may otherwise slip past it.

**External feedback = suggestions to evaluate, not orders to follow.** Reviewer findings are inputs to your decision; applying them blindly causes real damage when the reviewer is technically wrong (e.g. a critical "bug" that is actually a feature request, or a security flag based on a misread of the threat model). Use `superpowers:receiving-code-review` when available; the key principles are inlined below as the always-available fallback.

#### Step 6.1: Build the evaluation matrix

For each finding in the verbatim review, fill out one row:

| # | Severity | Verified?                          | Type            | Action               |
|---|----------|------------------------------------|-----------------|----------------------|
| 1 | high     | ✓ Context7 confirms behavior       | architectural   | accept               |
| 2 | critical | ✗ cited issue is feature request   | tool-mechanic   | reject with reasoning|
| 3 | medium   | ✓ small repro confirms             | tool-mechanic   | accept               |
| 4 | medium   | re-scoped to docs-only fix         | architectural   | re-scope             |

`Action` options are EQUAL first-class outcomes:

- **`accept`** — finding is valid as stated; apply the proposed fix (or a minimal variant that resolves it).
- **`reject with reasoning`** — finding is technically wrong, out of scope, or contradicts an explicit user requirement; do NOT apply, and prepare a technical counter-argument for the re-review prompt (Step 7).
- **`re-scope`** — finding is partially valid; apply a narrower fix than the reviewer proposed (e.g. clarify wording instead of restructuring the section), and explain the narrowing in the re-review prompt.

Use runner triage (`triage.finding_count`, `triage.max_severity`, `triage.needs_lead_judgment`) ONLY as a hint to prioritize. The matrix is built from the verbatim review, not from triage; triage is too cheap to be authoritative.

**Verification methods by finding type:**

| Finding type                                                           | What constitutes verification                                                                            |
|------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------|
| Architectural / design                                                 | Reasoning + codebase grep, plus a pattern check against existing code                                    |
| Tool-mechanic (DSL syntax, config parser, API contract, library behavior) | **Empirical test on the real system** — reasoning alone is not enough. Open cited upstream issues by URL. |
| Style / convention                                                     | Match against actual codebase conventions                                                                |
| Security                                                               | Reasoning + concrete threat model                                                                        |

Tool-mechanic findings are the most dangerous to accept on reasoning alone — mental models of obscure tools are often wrong. If the reviewer cites an upstream issue or doc, **open it**; citations age, issues get reclassified, and the cited number may not describe what the reviewer thinks it does.

**Receiving-feedback principles** (inlined from `superpowers:receiving-code-review` for portability):

- Read every finding end-to-end before reacting.
- Restate each finding's technical claim in your own words (mentally — don't pad the response with it).
- Verify against codebase / docs / a quick run before accepting.
- Push back when wrong, with technical reasoning, not deference.
- No performative agreement ("you're absolutely right" is a violation of the discipline).
- Skip thanks. State the fix or the reasoning.

#### Step 6.2: Classify accepted/re-scoped fixes as structural vs non-structural

After every finding has an `Action`, walk the matrix once and classify each `accept` / `re-scope` row as **structural** or **non-structural**. `reject with reasoning` rows skip this step (nothing is applied).

**Structural fixes** — pause the operator before applying:

- Invocation grammar or argument semantics (new/removed arg, renamed mode, changed value semantics).
- Output format or parsed literals (e.g. the `VERDICT: APPROVED|REVISE` line, severity tags, section headers, named workflow states).
- Workflow steps, fallback semantics, or terminal states.
- Sandbox, approval, or security guarantees.
- Public configuration semantics (what an override does).
- Schema, migration, or data format changes.
- Broad architectural rewrites.
- Any fix whose scope you are uncertain about — when in doubt, classify as structural.

**Non-structural fixes** — apply without pausing:

- Wording / phrasing changes that do not change semantics.
- Correcting factual inaccuracies (wrong API name, wrong tool mechanic, wrong attribution).
- Removing outdated comments or examples.
- Adding clarifying sentences or examples that do not change observable behavior.
- Internal heuristic refinements with no externally visible effect.

#### Step 6.3: Structural operator gate (one pause per round)

Apply the **batch-pause rule**: do NOT pause once per fix. Walk the entire matrix first; then:

- If structural count is **zero** → apply everything (non-structural accepts + re-scopes) without pausing. No operator gate needed.
- If structural count is **≥ 1** AND the operator is present (a direct human message exists earlier in this session AND the host exposes a user-facing channel) → make exactly **one** pause showing:

  ```
  ### Round N — structural fixes pending operator sign-off

  **Structural (need go/no-go):**
  - [#N — one-line description]
  - ...

  **Non-structural (will auto-apply):**
  - [#M — one-line description]
  - ...

  **Rejected with reasoning (informational):**
  - [#K — one-line description]
  - ...

  Approve the structural batch? (yes / no / select specific items)
  ```

  Wait for operator response before applying any structural fix. Non-structural fixes still auto-apply.

- If structural count is **≥ 1** AND the operator explicitly requested autonomous mode (e.g. `/agamotto` invoked from a scheduled task, or an explicit "go ahead without asking" earlier in the conversation) → apply all structural fixes without pausing, but record this fact for the final operator summary (Step 8):

  ```
  Structural fixes applied without operator sign-off due to autonomous mode:
  - [#N — description]
  - ...
  ```

- If structural count is **≥ 1** AND no operator is reachable (headless / scheduled run with no explicit autonomous flag) → apply structural fixes anyway and record the same "applied without sign-off" note for Step 8. Refusing to apply would leave the artifact half-fixed; the operator reviews after the fact.

#### Step 6.4: Apply fixes

For each `accept` and `re-scope` row:

- **Plan review** — update the plan file (or temp file). Make the change minimal: address the specific finding, don't refactor surrounding sections.
- **Code review** — edit files, run tests if applicable, run a build if the change is non-trivial.
- **Code-vs-plan** — update whichever side is wrong (plan or code), per the matrix.

**Verify your own technical claims before publishing them.** When a fix or the re-review reply makes a claim about tool mechanics (DSL syntax, config parser, API contract, library behavior):

- If a quick test is possible, run it (a small repro, `docker run …`, a real database container) — not "I think this works".
- If a quick test is not possible, frame the claim as a hypothesis ("seems to", "needs verification") rather than as fact.

**Skip** a fix if it contradicts an explicit user requirement — note this in the re-review reply with reasoning, not silent omission.

Show the user a brief account:

```
### Round N fixes
- Applied: [#1 — what changed, 1 line]
- Re-scoped: [#3 — what changed, why narrower]
- Rejected: [#2 — short reason; full reasoning goes to the reviewer in Step 7]
```

#### Step 6.5: Severity-decline soft signal

After applying, glance at the round-by-round severity trajectory. Expect severity to decline across rounds:

```
R1: 3 critical, 6 high, 5 medium       (typical opening)
R2: 1 high, 1 medium, 3 low            (good)
R3: 1 high                             (closing in)
R4: APPROVED                           (terminal)
```

If severity stays flat (e.g. `high → high → high` across three consecutive rounds), something is structurally off — the lead may not understand the technology, the reviewer may be looping on the same misunderstanding, or the artifact has a deep problem that surface fixes can't reach. Pause and surface to the operator:

```
⚠ Severity has stayed at <level> for <N> rounds. This usually means
either (a) the artifact has a structural problem the current fixes
are not addressing, or (b) the reviewer is misreading something the
lead and reviewer disagree about. Continue, switch approach, or
abort?
```

This is a soft signal, not a hard gate. Default to continuing if the operator does not respond.

### Step 7: Resubmit to Codex (Rounds 2-5)

> **If `REVIEWER = claude`:** ignore the codex resume machinery in this step. Launch
> a fresh Claude reviewer subagent (per the "Claude reviewer fallback" section) with
> the prior review, your structured response, and the current diff, then resume at
> Step 5. There is no session id or resume for the Claude path — each round is a
> fresh subagent.

**Resume is the primary path.** Saves tokens and preserves session context. A fresh `codex exec` without resume is an **emergency fallback** when resume itself fails.

**Step 7.1: Write the structured resume prompt body to disk.**

The re-review body is NOT a "I applied your feedback, please re-check" note. It is a structured response that lets the reviewer (a) verify the applied fixes resolve the original findings, (b) contest the rejections with reasoning, and (c) catch new issues introduced by the fixes. Write `/tmp/codex-resume-body-${REVIEW_ID}.md` containing:

```
I've evaluated the findings.

## Applied
- [#N]: [what was changed and why, 1–2 lines]
- ...

## Re-scoped
- [#N]: [narrower scope, with reasoning for the narrowing]
- ...

## Rejected with reasoning
- [#N]: [technical reason for not applying — not "I disagree", but a concrete counter-argument the reviewer can engage with]
- ...

## Specific asks for re-review
1. Are my rejections technically valid? Where I rejected with reasoning, do you accept the counter-argument or push back?
2. Did the applied / re-scoped fixes resolve the original findings?
3. Did the fixes introduce any new issues?
```

Substitute the lists from Step 6's evaluation matrix (one bullet per finding per section). Sections with zero items can be omitted, but `## Specific asks for re-review` is always present. Do NOT include the session marker — the subagent adds it.

The three-section shape (Applied / Re-scoped / Rejected with reasoning) gives the reviewer a chance to contest the rejections. A re-review that says "your rejection of #2 is valid; here's why" is just as useful as one that fixes new issues — both keep the loop honest.

**Sonnet triage metadata from Step 4 is NOT passed to the reviewer.** Codex sees the verbatim findings (already in its conversation context from the prior round) and the lead's structured response. The runner's `triage.*` fields are an internal hint for the lead, never forwarded to Codex.

**Step 7.2: Dispatch the runner subagent for resume.**

Same Agent tool invocation as Step 4 (bootstrap instruction with `${RUNNER_SPEC_PATH}` + YAML input block; subagent Reads the spec itself). Reuse the `RUNNER_SPEC_PATH` resolved in Step 4 (do not re-resolve). Run the **pre-dispatch workspace mutation snapshot** described in Step 4 (`git status --porcelain` + `sha256sum` of the three `/tmp/codex-*-body-*` paths) BEFORE invoking the Agent tool.

Input block:

```yaml
---
REVIEW_ID: <same as initial round>
REPO_ROOT: <same>
OPERATION: resume
CODEX_MODEL: <same>
CODEX_REASONING: <same>
PROMPT_BODY_PATH: /tmp/codex-resume-body-<REVIEW_ID>.md
RESULT_PATH: /tmp/codex-runner-result-<REVIEW_ID>.json
CODEX_SESSION_ID: <uuid from previous round's runner result>
---
```

Sandbox and approval fields (`CODEX_SANDBOX`, `CODEX_APPROVAL_POLICY`, `CODEX_APPROVALS_REVIEWER`) are deliberately omitted from the resume YAML — `codex exec resume` does NOT accept these flags; the runner ignores them on `OPERATION=resume`. If the operator wants a different sandbox or approval policy for the rest of the review, the only path is to abort and re-invoke `/agamotto` with new overrides, which starts a fresh review with a fresh REVIEW_ID.

**Step 7.3: Parse the two-channel result and consult the dispatch table.**

Extract the `RUNNER_RESULT_AT:` line (same tolerant regex + Glob fallback as Step 4), read the JSON file, extract all 11 top-level fields. Run the **post-dispatch workspace mutation snapshot** (see Step 4) and treat tracked-file or `/tmp`-input mutation as a hard stop per the same rules.

Surface `user_warning` if non-null. Then consult the **operation-aware dispatch table in Step 4** with `OPERATION=resume`. In particular:

- `success` + `review_quality=valid` and `verdict=APPROVED` → Step 8 (approved).
- `success` + `review_quality=valid` and `verdict=REVISE` → save new `codex_session_id` (keep prior if `null` per §2.4.4) and go to Step 5.
- `success` + `review_quality=degraded_environmental` → do NOT show review verbatim, do NOT count as a round, route to the Step 7.4 fallback chain using the prior round's severity.
- `success` + `review_quality=degraded_content` → show verbatim per Step 5, ask the operator whether to advance.
- `success` + `review_quality=unknown` → treat as `valid` for advancement; note in the final summary.
- `timeout` or `launch_failure` → route to the Step 7.4 fallback chain (runner already archived stdout/stderr to `-failed-resume.*` per `archived_stdout`/`archived_stderr` on `launch_failure`).
- `infra_error` or `input_error` → show `errors`, abort.

**Round-level attempt invariant:** exactly ONE runner dispatch per resume round. Every failure result routes to fallback (not re-dispatch within the same round). Fallback's fresh-exec dispatch consumes a NEW round from the 5-round counter, which has its own independent 2-attempts-per-round budget. Total codex invocations per round ≤ 2 regardless of failure type. The `degraded_environmental` outcome on resume is the one exception that does NOT count as a round — it routes through fallback without consuming the round counter, because the resume produced no usable review.

**Step 7.4: Fallback chain** — triggered by `launch_failure` or repeated `timeout` from the runner.

*Severity classification:* parse the PREVIOUS round's review (kept in conversation history from Step 5.3's verbatim display) for the highest `[severity:` level. Default to `critical` if zero matches (format drift).

*Interactive mode* (direct user message earlier in this session): ask the user:

```
Resume failed — the reviewer's re-review did not produce a usable result.
Last round's maximum severity: <level>.

Options:
(a) Run a fresh `codex exec` with full previous-rounds context (higher token cost, new session)
(b) Conclude the review — show current findings as NOT VERIFIED
```

*Non-interactive mode:*
- Max severity `critical` or `high` → fresh exec automatically.
- Max severity `medium` only → Step 8 with the not-verified terminal state.

*Fresh-exec dispatch:* build a new PROMPT_BODY that is the original Step 4 prompt for the current mode, followed by sections `## Previous review rounds` (verbatim round-1..N reviews + fixes from conversation history) and `## Current state of the artifact`. Write to `/tmp/codex-body-${REVIEW_ID}.md` (overwriting the original).

**Archival note:** if the fallback was triggered by `launch_failure`, the runner already archived failed-resume stdout/stderr to `-failed-resume.*` paths during Step R5 — main does NOT need to `mv` anything. If triggered by repeated `timeout`, no archival happened (no second codex invocation produced useful diagnostics); main can proceed directly. Either way, main never touches `/tmp/codex-stdout-*` or `/tmp/codex-stderr-*` itself.

Dispatch the runner subagent with `OPERATION=fresh-exec` (same input schema, new PROMPT_BODY_PATH pointing at the rebuilt prompt). The fresh-exec consumes one round from the 5-round counter. Return to Step 5 with the new review.

### Step 8: Final result + operator summary

Every terminal state emits TWO messages, in this order:

1. **Per-state header block** (templates below) — the canonical "what happened" framing in English.
2. **Operator summary** — a separate operator-facing summary in `OPERATOR_LANGUAGE` (captured in Step 1; English by default). The summary comes AFTER the final verbatim reviewer response (if any) and does NOT replace it.

#### Terminal state templates

**Approved:**
```
## Adversarial Review — Summary (mode: <mode>, model: <CODEX_MODEL>)

**Status:** Approved after N round(s)

[Final review]

---
**Reviewed and approved by the reviewer. Awaiting your decision.**
```

**Maximum rounds reached:**
```
## Adversarial Review — Summary (mode: <mode>, model: <CODEX_MODEL>)

**Status:** Maximum reached (5 rounds) — not fully approved

**Remaining findings:**
[Unresolved issues from the last round]

---
**The reviewer still has findings. Please review them and decide how to proceed.**
```

**Not verified** (resume failed and the operator chose to conclude, headless with only medium severity, or a second `degraded_environmental` on fresh-exec):
```
## Adversarial Review — Summary (mode: <mode>, model: <CODEX_MODEL>)

**Status:** NOT VERIFIED — fixes applied, reviewer did not re-verify

**Last round's findings:**
[Verbatim findings from the last successful round]

**Applied fixes:**
[List of fixes per finding]

---
**WARNING: This is NOT an approval. Fixes were applied but never verified by the reviewer. Manual review is required before merging.**
```

**Aborted due to environmental failure** (initial dispatch returned `success + degraded_environmental`, or a workspace-mutation hard stop, or a `bwrap` preflight failure surfaced as `infra_error`):
```
## Adversarial Review — Summary (mode: <mode>, model: <CODEX_MODEL>)

**Status:** ABORTED — environmental failure before any valid review

**Diagnostic:**
[user_warning or errors from the runner result]

---
**No review was produced. Inspect the diagnostic and the README's "Safety considerations" / "Linux sandbox prerequisites" sections, then re-invoke /agamotto when the environment is ready.**
```

#### Operator summary (always emitted)

After the per-state header block, emit a separate operator-facing summary in `OPERATOR_LANGUAGE`. This summary is built from per-round decision summaries already shown earlier in the conversation (the matrix in Step 6.1, the fix-account in Step 6.4, the verbatim reviews in Step 5). Do NOT re-read Codex stdout/stderr/rollout files; main never has those in context.

Include:

- **Final status** — approved, maximum rounds reached, not verified, or aborted.
- **What changed across all review rounds** — a compact list of artifact changes (one bullet per file/section, not full diffs).
- **Findings applied / re-scoped / rejected** — counts per round, with one-line descriptions only for findings the operator should pay attention to (rejections, re-scopes, structural fixes).
- **Structural changes** — whether structural fixes were applied, and whether operator sign-off was obtained or was skipped due to autonomous / headless mode.
- **Verification performed and NOT performed** — what the reviewer ran vs. what the lead verified vs. what is still unverified.
- **Remaining findings or risks** — only for non-approved terminal states; otherwise omit this section.
- **Explanation of the status** — one sentence on what the status means for what the operator should do next (especially for `NOT VERIFIED` and `ABORTED`).

Constraints on the summary:

- Do NOT include full diffs.
- Do NOT repeat full reviewer findings verbatim unless an unresolved finding still matters.
- Keep it concise and operator-useful.
- If context compaction has made the per-round history incomplete (a known limitation — see `docs/DESIGN.md §9.2`), state that limitation explicitly in the summary instead of inventing details. A summary that says "round 2 details unavailable due to compaction" beats a fabricated round-2 account.

Render the summary in `OPERATOR_LANGUAGE`. Section headers and severity tags stay in English so the operator can grep them back if needed; everything else is in the operator's language.

### Step 9: Cleanup

**Conditional on terminal state:**

| Terminal state | Cleanup behavior |
|---|---|
| Approved | Remove all temp files |
| Maximum rounds reached | Remove all temp files |
| Not verified (fallback conclude) | Remove all temp files |
| Aborted (launch failure, redirect failure, infrastructure error) | **LEAVE files in place** for diagnostics |

**In Claude Code Plan Mode:** skip all cleanup (including deferred). `rm` will trigger a permission prompt. Files will be cleaned up on the next invocation outside Plan Mode.

**Outside Plan Mode, on a cleanup-eligible terminal state:**

```bash
rm -f /tmp/codex-plan-${REVIEW_ID}.md \
      /tmp/codex-prompt-${REVIEW_ID}.md \
      /tmp/codex-resume-prompt-${REVIEW_ID}.md \
      /tmp/codex-review-${REVIEW_ID}.md \
      /tmp/codex-stdout-${REVIEW_ID}.jsonl \
      /tmp/codex-stderr-${REVIEW_ID}.txt \
      /tmp/codex-stdout-${REVIEW_ID}-failed-resume.jsonl \
      /tmp/codex-stderr-${REVIEW_ID}-failed-resume.txt \
      /tmp/codex-body-${REVIEW_ID}.md \
      /tmp/codex-resume-body-${REVIEW_ID}.md \
      /tmp/codex-runner-result-${REVIEW_ID}.json \
      /tmp/codex-git-pre-${REVIEW_ID}.txt \
      /tmp/codex-git-post-${REVIEW_ID}.txt \
      /tmp/codex-inputs-pre-${REVIEW_ID}.sha \
      /tmp/codex-inputs-post-${REVIEW_ID}.sha
```

If the user declined `rm` — continue without error.

Do NOT delete plan files that existed before the review (only temp files created by this skill). On abort paths, old temp files remain for diagnostics and will be cleaned up by the OS on reboot, or overwritten by the next invocation using the same REVIEW_ID (collision probability is ~10⁻⁸ per same-second run).

## Rules

- Claude **actively fixes** issues based on reviewer feedback — this is NOT just message forwarding.
- Reviewer findings are shown **verbatim** — do not rephrase or shorten. The Step 5 "YOUR NEXT MESSAGE" instruction is blocking.
- Auto-detect review mode from context; user arguments take priority.
- With explicit `plan` argument or in Claude Code Plan Mode: skip git checks and base branch detection.
- **`REPO_ROOT` is captured at Step 2** and passed as an absolute literal to every runner dispatch.
- **`RUNNER_SPEC_PATH` is resolved at Step 4** (once per review) with priority: (1) `~/.claude/skills/agamotto/references/runner.md` (user-scoped install), (2) Glob `~/.claude/plugins/cache/**/skills/agamotto/references/runner.md` and take first hit (plugin-marketplace install), (3) `$(git rev-parse --show-toplevel)/references/runner.md` (dev checkout), (4) abort with installation error. Main never attempts to read Claude's own system prompt / skill-invocation header — that path is hallucination-prone and is explicitly disallowed.
- **Codex-exec mechanics live in the runner subagent** (`references/runner.md`): ATTEMPT_ID generation, prompt-with-marker writing (with a repeated Write call for mtime freshness — NOT Bash `touch`, which may be gated by inherited Plan Mode), synchronous launch, strict checks, two-tier session-id capture with positive content-bind, ONE internal retry on ANY failure type (launch_failure, timeout, stderr-infra), archival mv on resume failure. Main thread never reads codex stdout/stderr/rollout file CONTENT, and never references those paths in its own Bash argv.
- **Two-channel result protocol.** Runner writes structured JSON to `/tmp/codex-runner-result-${REVIEW_ID}.json` (authoritative) AND returns a single `RUNNER_RESULT_AT: <path>` line as its final message. Main extracts the path via regex (tolerant to markdown fences / minor wrapping), reads the JSON, and never relies on raw-JSON-in-message parsing.
- **Main thread reads only**: the runner result JSON at `RESULT_PATH` and the review file at `review_file`. Main does NOT Read `references/runner.md` — the runner spec is passed by path to the subagent, which Reads it itself. No other `/tmp/codex-*` reads.
- **Runner is dispatched via Agent tool** with `subagent_type: general-purpose, model: sonnet`. Agent tool call is synchronous (not `run_in_background`).
- **ALL runner failure results are TERMINAL at main** (`launch_failure`, `timeout`, `infra_error`, `input_error`). Runner retries once internally on ANY failure. Main does NOT re-dispatch and does NOT offer the user a retry — those lanes would compound retries across layers. Total codex invocations per round ≤ 2 (matches pre-refactor invariant: 1 initial + 1 retry). Fresh-exec fallback is a NEW round with its own independent 2-attempts budget.
- **`user_warning` from the runner must be surfaced to the user** on a single line BEFORE any other action. This preserves the pre-refactor §2.4.4 "both tiers empty, continuing with previous ID" diagnostic.
- **`CODEX_MODEL` / `CODEX_REASONING` / `CODEX_SANDBOX` / `CODEX_APPROVAL_POLICY` / `CODEX_APPROVALS_REVIEWER`** in the runner input schema refer to the codex-exec invocation (default model `gpt-5.5`, default sandbox `workspace-write`, default approval policy `on-request` with `auto_review` reviewer). The runner's OWN model is Sonnet, set via Agent tool's `model: "sonnet"`. Do NOT conflate. Sandbox and approval fields apply to `OPERATION=initial` and `OPERATION=fresh-exec` only; `codex exec resume` ignores them because they are properties of the original session.
- **Resume is the primary path for rounds 2-5.** Fresh-exec fallback consumes one round from the 5-round counter.
- **Step 9 cleanup `rm` glob covers ALL `/tmp/codex-*-${REVIEW_ID}*` files this skill writes** — initial-round body, resume-round body, prompts, review, stdout/stderr (current + archived failed-resume), runner result JSON, pre/post git-status snapshots, pre/post `sha256sum` snapshots. See the explicit list in Step 9.
- Cleanup is **conditional on terminal state**: remove temp files on approved/max-reached/not-verified/aborted-env; LEAVE them on abort due to launch failure / infra error (diagnostic value). Skip all cleanup in Plan Mode.
- **Default sandbox is `workspace-write`**, not `read-only`. The reviewer needs to run tests, build, query upstream docs, and exercise CLIs to verify findings — all write-class operations. Reviewer-side mutation is governed by (a) the `<reviewer_permissions>` prompt block (auditor, not contributor), and (b) the dual-layer mutation snapshot in Step 4 (`git status --porcelain` + `sha256sum` of `/tmp/codex-{body,plan,resume-body}-*`). Operators with sensitive ignored state in `REPO_ROOT` can opt out via `sandbox:read-only` (with the explicit trade-off that the reviewer loses empirical verification).
- **`review_quality` and `triage`** are part of the runner result schema and consumed by the operation-aware dispatch table in Step 4. Legacy runner results without these fields are treated as `review_quality=unknown` / `triage.status=skipped` and continue to work.
- **Workspace mutation snapshots are mandatory** before AND after every Codex dispatch (initial, resume, fresh-exec). Tracked-file mutation or `/tmp` review-input mutation is a hard stop before applying any fixes.
- **One-line runtime hint** about `workspace-write` and the `sandbox:read-only` opt-out is emitted exactly once per review (at Step 1, before Step 2), suppressed when the operator passed an explicit `sandbox:*` override.
- **Operator language** is detected at Step 1. Runtime prose (warnings, summaries, intermediate updates) uses `OPERATOR_LANGUAGE`; repository files stay in English; machine-readable literals (`[severity:]`, `VERDICT:`, section headers) stay in English regardless of language.
- **Reviewer findings are suggestions to evaluate, not orders to follow.** Step 6 builds an evaluation matrix with three first-class actions: `accept`, `reject with reasoning`, `re-scope`. The lead applies only accepted / re-scoped fixes; rejections go to Codex as structured counter-arguments in Step 7.
- **Structural fixes need operator sign-off** unless the operator explicitly requested autonomous mode or no operator is reachable. The batch-pause rule: exactly one operator prompt per round listing structural / non-structural / rejected. Headless runs apply structural fixes anyway but record "applied without operator sign-off" in the Step 8 operator summary.
- **Maximum 5 rounds** to protect against infinite loops.
- **Final operator summary** is emitted at every terminal state (approved, max rounds, not verified, aborted) in `OPERATOR_LANGUAGE`, AFTER the final verbatim reviewer response. Built from in-conversation per-round summaries — main never reads Codex stdout/stderr/rollout files.
- Show the user reviews and fixes for each round.
- If Codex CLI is not installed or crashed — tell the user: `npm install -g @openai/codex` (requires Codex CLI ≥ 0.132.0 for the `-c approval_policy` form; earlier versions may need different override syntax).
- If a fix contradicts an explicit user requirement — skip it, record it in the Step 7 `## Rejected with reasoning` section, and surface in the Step 8 operator summary.
