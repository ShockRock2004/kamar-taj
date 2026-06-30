# Kamar-Taj

A small sanctum of Claude Code skills.

In Doctor Strange, Kamar-Taj is the hidden academy where sorcerers train and learn
their craft. This repo is the same idea for Claude Code: a place that holds the
skills (think of them as spells) that make Claude work the way you want. Clone it,
install the spells you like, and Claude picks up new tricks.

Two spells live here so far.

## The spells

### daily-log
Tired of prompting Claude all day without really understanding what happened under
the hood? `daily-log` reads all of your Claude sessions at the end of the day and
writes them up as a friendly study guide you genuinely learn from, then renders it
as a dark mode PDF and syncs it to your phone via Google Drive. It also prints a
ready to paste standup and explains the git commands you used. See
[`daily-log/`](daily-log/SKILL.md).

### dormammu
"Dormammu, I've come to bargain." A rigorous iterate until verified working loop.
It refuses to call anything done until it has attacked its own work, handled the
edge cases, and actually run the verification, reverting and retrying on any flaw.
See [`dormammu/`](dormammu/README.md).

## Install

Each skill is its own folder. Clone the repo and run the installer to drop them
into your Claude skills folder:

```bash
git clone https://github.com/ShockRock2004/kamar-taj.git
cd kamar-taj
bash install.sh
```

Restart Claude Code (or start a new session) and the spells are ready: `/daily-log`
and `/dormammu`.

Want just one? Copy that single folder:

```bash
cp -R daily-log ~/.claude/skills/
```

## What you might need

* **dormammu** needs nothing. It is pure protocol.
* **daily-log** uses Python 3, which you already have. For the PDF it uses Node.js
  and Google Chrome, and for the Google Drive upload it uses rclone. Those are
  optional and skip themselves cleanly if a tool is missing. Details in
  [`daily-log/SKILL.md`](daily-log/SKILL.md).

## License

MIT. Do whatever you like with it. See the LICENSE file.

Built with Claude Code. Fan-made and not affiliated with Marvel.
