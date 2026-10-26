# handoff

You open a fresh session and Claude knows nothing about your project, so you explain it again: the stack, the goal, the thing you were halfway through fixing. You do it every morning, and again every time the context runs out.

This skill keeps a HANDOFF.md at the root of your repo with the objective, the current state, what is in flight, what is blocking you, and why the strange decisions were made. A fresh agent reads that file before it touches any source, so it starts warm instead of grepping around for ten minutes trying to work out what you want.

It never overwrites what's already there. It updates in place and prunes whatever stopped being true, because stale notes are worse than missing ones. When the file grows past five hundred lines, it folds the old session log into a condensed history so it stays readable.

It hides the file in .git/info/exclude instead of .gitignore. Your working notes are your business and don't belong in a commit your teammates have to read.

It has no dependencies and no config. It works in any repo, and if you're not in git it falls back to the plain working directory.

## Install

It comes in the main kamar-taj bundle at https://github.com/ShockRock2004/kamar-taj,
or you can grab just this folder.

```bash
cp -R handoff ~/.claude/skills/
```

Restart Claude Code and run /handoff. The full protocol is in SKILL.md.

Your repo now remembers things. You still won't.
