#!/usr/bin/env python3
"""Daily-log collector / distiller.

Walks every Claude Code session transcript under ~/.claude/projects, keeps the
sessions that were active on a target local date, and distills each one down to
the signal that's useful for an end-of-day learning writeup:

  - your actual prompts (the asks that drove the day)
  - Claude's explanatory prose (the "why")
  - the files Claude edited (cross-reference; real code comes from git)
  - the git commands Claude ran (for the "Git skills" teaching section)
  - per-repo git activity for the day (commit map + uncommitted stats)

It writes a single consolidated markdown digest and prints its path. The
`/daily-log` skill reads that digest and turns it into a teaching guide.

Usage:
    python3 collect_day.py [YYYY-MM-DD]      # default: today (local time)

Pure stdlib. No network. Read-only except for the digest file it writes.
"""

from __future__ import annotations

import glob
import json
import os
import re
import subprocess
import sys
from datetime import datetime, date as date_cls

# --------------------------------------------------------------------------- #
# Tunables                                                                     #
# --------------------------------------------------------------------------- #
HOME = os.path.expanduser("~")
PROJECTS_DIR = os.path.join(HOME, ".claude", "projects")
OUTPUT_DIR = os.path.join(HOME, "Daily Log")  # ~/Daily Log — portable across machines

# Project-slug substrings to skip entirely (e.g. personal experiments). Empty by
# default — scope is "all projects". Example: ["Downloads-Carbon-Research"].
EXCLUDE_SLUGS: list[str] = []

# Cap per assistant text block so the digest stays small.
MAX_ASSISTANT_CHARS = 1800
# Keep only the most substantial assistant prose blocks per session (longest
# first), so a heavy day's digest stays under the ~256 KB single-read limit.
MAX_PROSE_BLOCKS_PER_SESSION = 25
# Cap per user prompt (your asks are the spine — keep them generous).
MAX_USER_CHARS = 6000
# Include subagent transcripts (final assistant message only) under their parent.
INCLUDE_SUBAGENTS = True

# Effort presets — chosen with `--effort {light,medium,heavy}` (default heavy).
# Lower effort => smaller digest => fewer tokens for the writing model to read.
# (The skill ALSO scales how much it does at each level; see SKILL.md.)
EFFORT_PRESETS = {
    "light":  {"MAX_ASSISTANT_CHARS": 450,  "MAX_PROSE_BLOCKS_PER_SESSION": 6,  "INCLUDE_SUBAGENTS": False},
    "medium": {"MAX_ASSISTANT_CHARS": 1000, "MAX_PROSE_BLOCKS_PER_SESSION": 14, "INCLUDE_SUBAGENTS": False},
    "heavy":  {"MAX_ASSISTANT_CHARS": 1800, "MAX_PROSE_BLOCKS_PER_SESSION": 25, "INCLUDE_SUBAGENTS": True},
}
# Skip user lines that are harness/command noise rather than real asks.
NOISE_PREFIXES = ("<command-name>", "<local-command-stdout>", "<command-message>",
                  "Caveat: The messages below", "<bash-input>", "<bash-stdout>")
EDIT_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}
# Matches a git invocation at the start of a command or after a shell separator,
# so we catch `git ...` and `cd repo && git ...` but not words like "digit".
GIT_CMD_RE = re.compile(r"(?:^|[\s;&|(])git\s")


# --------------------------------------------------------------------------- #
# Helpers                                                                      #
# --------------------------------------------------------------------------- #
def parse_ts_local(ts: str) -> datetime | None:
    """Parse an ISO8601 UTC timestamp ('...Z') and convert to local time."""
    if not ts:
        return None
    try:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        return dt.astimezone()  # to local tz (IST here)
    except (ValueError, TypeError):
        return None


def text_from_content(content) -> str:
    """Flatten a message.content (str or list of blocks) to plain text.

    Skips tool_use / tool_result / thinking blocks — we only want prose.
    """
    if isinstance(content, str):
        return content
    if not isinstance(content, list):
        return ""
    parts = []
    for block in content:
        if isinstance(block, dict) and block.get("type") == "text":
            parts.append(block.get("text", ""))
    return "\n".join(p for p in parts if p)


def edited_files_from_content(content) -> list[str]:
    """Pull file_path values out of Edit/Write/MultiEdit tool_use blocks."""
    out = []
    if not isinstance(content, list):
        return out
    for block in content:
        if (isinstance(block, dict) and block.get("type") == "tool_use"
                and block.get("name") in EDIT_TOOLS):
            fp = (block.get("input") or {}).get("file_path")
            if fp:
                out.append(fp)
    return out


def git_commands_from_content(content) -> list[str]:
    """Pull git command strings out of Bash tool_use blocks.

    Returns the full command (so `cd repo && git commit ...` is kept intact),
    only for commands that actually invoke git.
    """
    out = []
    if not isinstance(content, list):
        return out
    for block in content:
        if (isinstance(block, dict) and block.get("type") == "tool_use"
                and block.get("name") == "Bash"):
            cmd = (block.get("input") or {}).get("command")
            if cmd and GIT_CMD_RE.search(cmd):
                out.append(cmd.strip())
    return out


def is_noise(text: str) -> bool:
    t = text.lstrip()
    return any(t.startswith(p) for p in NOISE_PREFIXES)


def truncate(text: str, cap: int) -> str:
    text = text.strip()
    if len(text) <= cap:
        return text
    return text[:cap].rstrip() + f"\n…[truncated {len(text) - cap} chars]"


def run_git(repo: str, args: list[str]) -> str:
    try:
        res = subprocess.run(
            ["git", "-C", repo, *args],
            capture_output=True, text=True, timeout=30,
        )
        return res.stdout.strip()
    except (subprocess.SubprocessError, OSError):
        return ""


def is_git_repo(path: str) -> bool:
    return bool(run_git(path, ["rev-parse", "--is-inside-work-tree"]))


# --------------------------------------------------------------------------- #
# Session parsing                                                              #
# --------------------------------------------------------------------------- #
def parse_session(path: str, target: date_cls) -> dict | None:
    """Parse one .jsonl transcript; return a distilled dict if active on target."""
    user_asks: list[str] = []
    assistant_prose: list[str] = []
    edited: list[str] = []
    git_cmds: list[str] = []
    cwd = None
    branch = None
    session_id = None
    active = False
    first_ts = None  # earliest timestamp ON the target day
    last_ts = None    # latest timestamp ON the target day

    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue

                session_id = session_id or obj.get("sessionId")
                cwd = cwd or obj.get("cwd")
                branch = branch or obj.get("gitBranch")

                dt = parse_ts_local(obj.get("timestamp"))
                if dt is not None and dt.date() == target:
                    active = True
                    if first_ts is None or dt < first_ts:
                        first_ts = dt
                    if last_ts is None or dt > last_ts:
                        last_ts = dt

                typ = obj.get("type")
                msg = obj.get("message") or {}
                content = msg.get("content")

                # Only mine messages stamped on the target day.
                if dt is None or dt.date() != target:
                    continue

                if typ == "user" and obj.get("userType") == "external" \
                        and not obj.get("isMeta") and not obj.get("isSidechain"):
                    text = text_from_content(content)
                    if text and not is_noise(text):
                        user_asks.append(truncate(text, MAX_USER_CHARS))
                elif typ == "assistant":
                    text = text_from_content(content)
                    if text:
                        assistant_prose.append(truncate(text, MAX_ASSISTANT_CHARS))
                    edited.extend(edited_files_from_content(content))
                    git_cmds.extend(git_commands_from_content(content))
    except OSError:
        return None

    if not active:
        return None

    # de-dupe edited files, preserve order
    seen = set()
    edited_unique = [f for f in edited if not (f in seen or seen.add(f))]

    # de-dupe git commands, preserve order
    gseen = set()
    git_unique = [c for c in git_cmds if not (c in gseen or gseen.add(c))]

    # Keep only the most substantial prose blocks (longest carry the most "why"),
    # so heavy days stay under the single-read size limit.
    if len(assistant_prose) > MAX_PROSE_BLOCKS_PER_SESSION:
        assistant_prose = sorted(assistant_prose, key=len, reverse=True)[
            :MAX_PROSE_BLOCKS_PER_SESSION]

    return {
        "session_id": session_id or os.path.basename(path),
        "path": path,
        "cwd": cwd,
        "branch": branch,
        "first_ts": first_ts,
        "last_ts": last_ts,
        "user_asks": user_asks,
        "assistant_prose": assistant_prose,
        "edited_files": edited_unique,
        "git_commands": git_unique,
    }


def subagent_finals(session_uuid_dir: str, target: date_cls) -> list[str]:
    """Final assistant message of each subagent transcript active on target."""
    finals = []
    sub_glob = os.path.join(session_uuid_dir, "subagents", "*.jsonl")
    for sub in sorted(glob.glob(sub_glob)):
        last_text = None
        active = False
        try:
            with open(sub, "r", encoding="utf-8", errors="replace") as fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        obj = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    dt = parse_ts_local(obj.get("timestamp"))
                    if dt and dt.date() == target:
                        active = True
                    if obj.get("type") == "assistant":
                        text = text_from_content((obj.get("message") or {}).get("content"))
                        if text:
                            last_text = text
        except OSError:
            continue
        if active and last_text:
            finals.append(truncate(last_text, MAX_ASSISTANT_CHARS))
    return finals


# --------------------------------------------------------------------------- #
# Git activity                                                                 #
# --------------------------------------------------------------------------- #
def git_activity(repo: str, target: date_cls) -> dict:
    since = f"{target.isoformat()} 00:00:00"
    until = f"{target.isoformat()} 23:59:59"
    commits = run_git(repo, [
        "log", "--all", f"--since={since}", f"--until={until}",
        "--date=short", "--pretty=format:%h | %an | %s", "--stat",
    ])
    diff_stat = run_git(repo, ["diff", "--stat"])
    staged_stat = run_git(repo, ["diff", "--staged", "--stat"])
    return {"commits": commits, "diff_stat": diff_stat, "staged_stat": staged_stat}


# --------------------------------------------------------------------------- #
# Main                                                                         #
# --------------------------------------------------------------------------- #
def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(
        description="Collect a day's Claude work into a digest for the daily-log skill.")
    parser.add_argument("date", nargs="?", help="YYYY-MM-DD (default: today, local time)")
    parser.add_argument("--effort", choices=["light", "medium", "heavy"], default="heavy",
                        help="how much detail to capture (lower = fewer tokens). Default heavy.")
    args = parser.parse_args()

    # Apply the effort preset to the digest-size tunables.
    global MAX_ASSISTANT_CHARS, MAX_PROSE_BLOCKS_PER_SESSION, INCLUDE_SUBAGENTS
    preset = EFFORT_PRESETS[args.effort]
    MAX_ASSISTANT_CHARS = preset["MAX_ASSISTANT_CHARS"]
    MAX_PROSE_BLOCKS_PER_SESSION = preset["MAX_PROSE_BLOCKS_PER_SESSION"]
    INCLUDE_SUBAGENTS = preset["INCLUDE_SUBAGENTS"]

    if args.date:
        try:
            target = datetime.strptime(args.date, "%Y-%m-%d").date()
        except ValueError:
            print(f"Bad date '{args.date}', expected YYYY-MM-DD", file=sys.stderr)
            return 2
    else:
        target = datetime.now().astimezone().date()

    if not os.path.isdir(PROJECTS_DIR):
        print(f"No projects dir at {PROJECTS_DIR}", file=sys.stderr)
        return 1

    # Collect sessions, grouped by repo (cwd).
    by_repo: dict[str, list[dict]] = {}
    total_sessions = 0
    for proj_dir in sorted(glob.glob(os.path.join(PROJECTS_DIR, "*"))):
        slug = os.path.basename(proj_dir)
        if any(ex in slug for ex in EXCLUDE_SLUGS):
            continue
        for jsonl in sorted(glob.glob(os.path.join(proj_dir, "*.jsonl"))):
            sess = parse_session(jsonl, target)
            if not sess:
                continue
            # nothing of substance? still record (e.g. only assistant prose)
            if not (sess["user_asks"] or sess["assistant_prose"]
                    or sess["edited_files"] or sess["git_commands"]):
                continue
            if INCLUDE_SUBAGENTS:
                uuid_dir = os.path.splitext(jsonl)[0]
                if os.path.isdir(uuid_dir):
                    sess["subagent_finals"] = subagent_finals(uuid_dir, target)
                else:
                    sess["subagent_finals"] = []
            else:
                sess["subagent_finals"] = []
            repo = sess["cwd"] or slug
            by_repo.setdefault(repo, []).append(sess)
            total_sessions += 1

    # Build digest.
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUT_DIR, f".digest-{target.isoformat()}.md")
    lines: list[str] = []
    w = lines.append

    w(f"# Daily digest — {target.isoformat()}")
    w("")
    w(f"_Generated by collect_day.py. Effort: {args.effort} · "
      f"Sessions: {total_sessions} · Repos: {len(by_repo)}._")
    w("")
    if not by_repo:
        w("No Claude sessions were active on this date.")
        _write(out_path, lines)
        print(out_path)
        return 0

    for repo in sorted(by_repo):
        sessions = sorted(by_repo[repo], key=lambda s: s["first_ts"] or datetime.now().astimezone())
        is_repo = is_git_repo(repo) if os.path.isdir(repo) else False
        w(f"\n---\n\n## Repo: `{repo}`")
        branches = sorted({s["branch"] for s in sessions if s["branch"]})
        if branches:
            w(f"**Branches seen:** {', '.join(branches)}")
        w("")

        # Git activity for the day (once per repo).
        if is_repo:
            ga = git_activity(repo, target)
            w("### Git activity (this day)")
            if ga["commits"]:
                w("```")
                w(ga["commits"])
                w("```")
            else:
                w("_No commits dated this day on any branch._")
            if ga["diff_stat"]:
                w("\n**Uncommitted (working tree) — not date-filtered:**")
                w("```")
                w(ga["diff_stat"])
                w("```")
            if ga["staged_stat"]:
                w("\n**Staged — not date-filtered:**")
                w("```")
                w(ga["staged_stat"])
                w("```")
            w("")

        # Per session.
        for i, s in enumerate(sessions, 1):
            span = ""
            if s["first_ts"] and s["last_ts"]:
                span = (f"  ({s['first_ts'].strftime('%H:%M')}"
                        f"–{s['last_ts'].strftime('%H:%M')})")
            w(f"### Session {i}: `{s['session_id'][:8]}`"
              f"  branch=`{s['branch'] or '?'}`{span}")

            if s["user_asks"]:
                w("\n**Your prompts (the asks):**")
                for a in s["user_asks"]:
                    w("> " + a.replace("\n", "\n> "))
                    w("")

            if s["edited_files"]:
                w("**Files Claude edited:**")
                for f in s["edited_files"]:
                    w(f"- `{f}`")
                w("")

            if s["git_commands"]:
                w("**Git commands Claude ran:**")
                w("```bash")
                for c in s["git_commands"]:
                    w(c)
                w("```")
                w("")

            if s["assistant_prose"]:
                w("**Claude's explanations (the why):**")
                for p in s["assistant_prose"]:
                    w(p)
                    w("")

            if s.get("subagent_finals"):
                w(f"**Subagent results ({len(s['subagent_finals'])}):**")
                for sf in s["subagent_finals"]:
                    w(sf)
                    w("")

    _write(out_path, lines)
    print(out_path)
    return 0


def _write(path: str, lines: list[str]) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    raise SystemExit(main())
