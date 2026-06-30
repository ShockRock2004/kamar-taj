---
name: daily-log
description: Compile everything Claude did today across ALL sessions and repos into one dated teaching-guide markdown saved in "~/Daily Log", render it as a phone-readable PDF, and upload to Google Drive. Safe to run multiple times a day — it appends only newly-uncovered work to that day's single file rather than overwriting. Use when the user runs /daily-log, or says "log today's work", "end of day log", "daily log", "wrap up the day", or any similar end-of-day trigger. Accepts an effort level (light/medium/heavy, default heavy) to control token usage — e.g. "/daily-log medium" — and optionally a past date (YYYY-MM-DD).
---

# Daily Log — end-of-day learning guidebook

Turn a full day of Claude Code work (across every session and repo) into a single
dated markdown file written as a **teaching guide**, so the user can genuinely
learn the work: re-implement the code by hand, understand *why* each decision was
made, and be able to explain how it works because they actually understand it.

The output is NOT a changelog. It is a **beginner's textbook** — written so simply
and conversationally that someone with *no* software background could read it top
to bottom and understand both what was done and why. Every technical term is
defined in plain language the first time it appears; code stays technical but is
wrapped in plain-English explanation. Depth and the "why" matter more than
completeness of trivia. See the full **Writing style — REQUIRED** rules in step 4.

## Step 0. Read the effort level from the command
The user may pass an effort level as the first argument: **light**, **medium**, or
**heavy**. If none is given, default to **heavy**. (They may also pass a date; a
`YYYY-MM-DD` token is the date, a light/medium/heavy token is the effort. Either
order, both optional. e.g. `/daily-log medium`, `/daily-log light 2026-06-25`.)

Effort controls token usage — it scales BOTH the digest size (via `--effort` on
the collector) AND how much you do while writing:

- **light** — cheapest. Document only the **top 2–3** pieces of work. Do **not**
  run `git show`/extra file reads; rely on the digest + commit messages, and
  include at most **one** short code snippet total. Keep each section brief. Still
  produce the Git skills section, Slack summary, PDF, and upload.
- **medium** — balanced. Document the **top ~5** pieces. Pull real code (`git
  show`) for only the **2–3 most important** ones. Moderate depth.
- **heavy** (default) — the full treatment described below: every distinct piece
  of work, pull real code for each, full depth.

Carry the chosen level through all steps.

## Steps

### 1. Collect the day's raw material
Run the collector with the chosen effort (it reads every session transcript from
disk, so it captures *all* concurrent/closed sessions, not just this one):

```bash
python3 ~/.claude/skills/daily-log/collect_day.py --effort heavy
```

Replace `heavy` with the level from Step 0. To log a past day, add the date:
`python3 ~/.claude/skills/daily-log/collect_day.py --effort medium 2026-06-25`

It prints the path to a digest file (`~/Daily Log/.digest-<date>.md`).
**Read that digest fully.** It contains, per repo: the day's git commit map,
uncommitted change stats, and per session — the user's prompts, the files Claude
edited, Claude's explanatory prose, and any subagent results.

If the digest says no sessions were active, tell the user and stop.

### 2. Identify distinct features/tasks
Group the day's work into **distinct pieces of work**, not one-section-per-session.
Merge sessions/commits that advanced the same feature. A "piece of work" is
something the user could point to as one distinct piece of work (e.g.
"the verto agent call-delivery bug fix", "the predictive dialer abandon-rate
cap"). Aim for the few things that actually mattered; don't pad with
trivia.

### 3. Get the real code for each piece
**Effort gate:** on **light**, skip this step entirely (no `git show`/file reads —
use the digest + commit messages, max one snippet total). On **medium**, do this
only for the 2–3 most important pieces. On **heavy**, do it for every piece.

The digest lists commit SHAs and edited files but NOT full diffs. For each piece
you're documenting, pull the actual code so snippets are real, not paraphrased:

```bash
git -C <repo> show <sha>            # full diff for a commit
git -C <repo> show <sha> -- <path>  # one file's diff
git -C <repo> diff -- <path>        # uncommitted work
```

Or Read the current file at the relevant lines. Prefer showing the *key* lines
(the ones that carry the idea) over dumping whole files.

Consult the repo's `CLAUDE.md` and `docs/GOTCHAS.md` (if present) for landmines
relevant to the work — they're gold for the "Gotchas & lessons" section.

### 4. Write the teaching guide — INCREMENTAL, never overwrite

**Filename format.** The file is saved in `~/Daily Log/` and
named:

```
<YYYY-MM> - <DD> - <one line of what we did that day>.md
```

e.g. `2026-06 - 26 - Fixed agent call delivery and started Yotel 3D landing page.md`.
The one-line part is a short, plain-language headline of the day's work (no
hyphens in it, since the date separators already use " - "; keep it under ~12
words). The file's top `# ` heading must be the **same string** as the filename
without the `.md`.

**Finding today's file (important for the append logic).** Because the one-line
suffix varies, never look for an exact `<date>.md`. Instead find today's file by
its date prefix — list `~/Daily Log/` and match the file
beginning with `<YYYY-MM> - <DD> - ` (e.g. `ls "~/Daily Log/"`
and pick the one starting `2026-06 - 26 - `). There is at most one per day.

This skill may be run **several times in one day**. On every run after the first,
you must **add only the work not already documented** — never overwrite or
duplicate what's there.

Procedure:
1. **If no file for today exists** (no file matches the date prefix): create it
   with the full structure below (Day overview + one section per piece of work,
   numbered `## 1.`, `## 2.`, …), named in the format above.
2. **If today's file ALREADY exists** (found via the date prefix): Read it first.
   Build a set of what's already covered by scanning its existing `## N. <title>`
   headings and the commit SHAs / session ids in each **References** line. Then,
   from today's digest, identify pieces of work whose commits/sessions are **not
   yet** in that set.
   - **Keep the filename's one-line summary accurate for the whole day:** if the
     newly added work changes what the day's headline should be, rename the file
     (and update its `# ` heading to match) so the one-liner still reflects
     everything done that day. If the headline still fits, leave the name as is.
   - If there's nothing new, tell the user the file is already up to date and stop
     (do not rewrite it).
   - Otherwise, **append** new `## N.` sections (continue the existing numbering)
     for only the new work, using the same per-feature template.
   - Update the **Day overview** block in place: bump the Commits/Sessions counts
     and extend the Headline to mention the newly added work. Do not touch the
     existing feature sections.
   - Use Edit (targeted insertions), not a full overwrite, so prior sections —
     including any you hand-edited — are preserved verbatim.

Treat a "piece of work" as already covered if its commit SHA(s) or the session id
already appear in the file. Match on those identifiers, not on wording, so
re-running never produces a near-duplicate section.

#### Writing style — REQUIRED (this is the whole point)
Write it like a **textbook chapter for a complete beginner** — someone smart who
knows *nothing* about software. The reader should be able to follow every section
top to bottom with no prior context.

- **Conversational and simple.** Short sentences. Plain words. Explain like you're
  talking to a friend, not writing a report. Avoid jargon in the narrative.
- **Define every technical term the first time it appears**, in everyday language,
  using a blockquote box: `> **What "X" means.** …`. Use real-world analogies
  (an address book, a switchboard operator, a reservoir of water, a sticky note).
- **Stay technical only where technical precision is the point** — e.g. the actual
  code change, the exact file, the real trade-off. Show the real code, but wrap it
  in plain-English explanation before and after, and comment the snippet in plain
  language. Never just dump code.
- **Lead each section with the "everyday version"** — the plain-language story of
  what was broken/needed and why it matters — *before* any technical detail.
- Use a short **"How to read this document"** note at the very top, and a **"The
  big picture (read this first)"** overview that explains the projects in plain
  terms (what is this product, who uses it, why).
- Keep the "how to explain it" points in plain, confident, one-sentence form,
  followed by the one clever insight to explain simply.
- Be honest: clearly separate real shipped code from setup/exploration, and say so
  in plain words.

Match the tone of the most recent existing file in `~/Daily Log/` (read it as the
reference example if one exists).

Per-feature template and Day-overview structure (adapt headings to the
beginner-friendly voice above — these are the *contents* to cover, not rigid
labels to copy verbatim):

```markdown
# <YYYY-MM> - <DD> - <one line of what we did that day>

> **How to read this document.** (1-2 sentences telling a beginner how to use it.)

## The big picture (read this first)
Plain-language overview: what each project is, who uses it, what got done today.
Define "project/repository" and "commit" here in beginner terms.

---

## 1. <Plain-language title of the piece of work>   (<repo>)

### The everyday version
The story with no jargon — what was broken or needed, and why it matters to a
real person. Use an analogy.

### What was really going on / the fix (the technical bit)
Now the precise detail: the real cause, the real code change (shown and explained
in plain English with commented snippets), the exact file `path`. Put a
`> **What "term" means.**` box before each new technical word.

### How you could do this yourself, step by step
Numbered, concrete steps a beginner could follow.

### How to explain it (once you understand it)
- A plain one-sentence summary of what the work does.
- The one clever insight, explained simply.
- The trade-off to defend, in everyday terms.

### Lessons worth remembering
Plain-language takeaways + any relevant landmine from CLAUDE.md / docs/GOTCHAS.md.

**Where to find it:** files, commit SHA(s), session id(s).

---

## 2. <next piece…>

---

## Git skills used today
(Always the LAST section of the document. Built from the digest's "Git commands
Claude ran" blocks — see the dedicated instructions below.)

### <git operation, e.g. Committing changes>   `git commit`
**What it did** — in plain words, what this command accomplished today.
**Why** — why this step was needed at that point in the workflow.
**How to do it yourself** — the real command with a short note on what each part
and flag means, so the reader could run it by hand.

### <next git operation…>
```

#### The "Git skills used today" section — REQUIRED (always the last section)
End every day's document with a **## Git skills used today** section, built from
the **"Git commands Claude ran"** blocks in the digest (one block per session).

How to build it:
1. Gather all the git commands from every session in the digest. A captured entry
   may be a compound command (e.g. `cd repo && git add ... && git commit ...`);
   pull out the git part(s).
2. **Group them by git operation** (e.g. committing, creating a branch, creating a
   worktree, pushing, staging, stashing, restoring, rebasing, inspecting with
   log/diff/show/status). One subsection per distinct operation — do not list the
   same operation many times. If many commands are just read-only inspection
   (`git status`, `git log`, `git diff`, `git show`), cover them together in one
   short "Looking around the repo" subsection rather than one each.
3. For **each** operation, write three things in the beginner-friendly voice used
   everywhere else in the document:
   - **What it did** — what this accomplished in today's actual work.
   - **Why** — why that step was needed at that point.
   - **How to do it yourself** — the real command, with a plain note on what each
     part and important flag means, so the reader could run it by hand.
   Put a `> **What "X" means.**` box before the first use of a git term (commit,
   branch, staging area, worktree, remote, push, etc.).
4. Be honest about read-only vs state-changing actions, and note when something
   was destructive or risky (e.g. `reset --hard`, force push) and how to do it
   safely.

**On append runs:** keep a single "Git skills used today" section at the very end.
Add any git operations that appeared in new sessions and aren't already covered.
Do not duplicate operations that are already explained — extend, don't repeat. If
new work was appended above, make sure this section stays the LAST one in the file.

#### Render a phone-readable PDF, then upload to Google Drive (after writing/updating)
Once the day's file is written (or appended to), do two things, in order, passing
the file's full path:

```bash
# 1) markdown -> styled, phone-friendly PDF (rendered next to the .md)
bash ~/.claude/skills/daily-log/render_pdf.sh "/full/path/to/<YYYY-MM> - <DD> - <one line>.md"

# 2) upload to Google Drive (uploads the PDF + the .md)
bash ~/.claude/skills/daily-log/upload_to_drive.sh "/full/path/to/<YYYY-MM> - <DD> - <one line>.md"
```

- `render_pdf.sh` converts the markdown to a clean PDF (via `marked` + headless
  Chrome) so it's pleasant to read on a phone — Google Drive renders PDFs natively
  on mobile, unlike raw markdown.
- `upload_to_drive.sh` copies **only the PDF** into the user's Drive
  (`gdrive:Daily Log` by default) and then deletes the local PDF, so Drive holds the
  readable PDFs and the local `~/Daily Log` keeps only the editable `.md` sources.
  (Toggles `UPLOAD_MD` and `KEEP_LOCAL_PDF` at the top of the script change this.)

Both are **safe no-ops**: if Node/Chrome aren't available, the PDF step skips; if
rclone isn't installed/configured, the upload step skips. Each just prints a hint
and exits cleanly — never treat a "skipping" message as a failure. Run both on
every run (including append runs) so the Drive copies stay in sync, and report what
they print (rendered/uploaded vs skipped) in the final summary.

### 5. Print a Slack-ready daily update (ALWAYS do this after writing the file)
After the document is written (or updated), print a **3 paragraph** plain-language
summary of what was done that day, meant for the user to copy-paste straight into
Slack as their daily update. Put it in a fenced code block so it is easy to copy.

Rules for this Slack summary (follow exactly):
- **Exactly 3 paragraphs.** Blank line between them. No headings, no bullet points,
  no bold.
- **Moderately technical, and focused on what was actually done.** First person
  ("Today I ...", "I also ..."). Write for engineering teammates who know the
  stack, so name the real things: the actual files, components, functions,
  endpoints, libraries, root cause, and the concrete change made. Prefer specifics
  ("switched the FreeSWITCH directory dial string to verto_contact") over vague
  plain English ("fixed the call bug"). Don't over-explain basic concepts and skip
  the everyday analogies — that's what the document is for; this is the work log.
- **No hyphens at all.** Do not use the "-" character anywhere (rephrase rather
  than hyphenate; e.g. write "browser based" as two words or reword). Underscores
  in real identifiers like verto_contact are fine.
- **Minimal punctuation.** Mostly full stops. Avoid commas where you can, and avoid
  semicolons, colons, dashes, parentheses, and quotation marks.
- Keep it honest: cover the real work, and if a chunk was setup or exploration say
  so plainly.
- Roughly 3 to 5 sentences per paragraph. A natural arc is: paragraph 1 the main
  thing you fixed or built including the root cause and the fix, paragraph 2 the
  other concrete changes you made, paragraph 3 setup or infra or what is next.

On an **append** run, write the Slack summary for the **whole day so far** (all
sections in the file), not only the newly added work, since it is the day's update.

### 6. Report back
Give the user a short summary in chat (outside the Slack code block):
- the file path (new `<YYYY-MM> - <DD> - <one line>.md` name; note it if the file
  was renamed on an append run)
- whether this run **created** the file or **appended** to it, and on an append
  run: which new sections were added (and that prior sections were left untouched),
  or that it was already up to date
- whether the PDF was rendered and whether the Google Drive upload (PDF + md)
  succeeded or was skipped (per the helpers' output)
- number of features documented total, repos, and commits covered
- if any session's last timestamp was within a few minutes of "now" (looks
  still-active), note it and suggest re-running `/daily-log` after closing that
  session to capture the tail.

## Notes
- **One file per day, additive.** Running the skill again the same day extends the
  existing `<date>.md` with only the newly-uncovered work — it never creates a
  second file for that date and never overwrites prior sections.
- The collector and output folder live outside any product repo; nothing here is
  committed to work repos.
- Tunables (excluded projects, truncation caps, subagent inclusion) live at the
  top of `collect_day.py`.
- Be honest: if a piece of work is incomplete or was just exploration/Q&A rather
  than shipped code, document it as such rather than inventing an accomplishment.
