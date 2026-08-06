# handoff

You open a fresh session and Claude knows nothing about your project. So you explain it again. The stack and the goal and the thing you were halfway through fixing. You do this every morning. You do it again every time the context runs out.

This skill kills that ritual.

It keeps a HANDOFF.md at the root of your repo. The objective. The current state. What is in flight. What is blocking you. Why the strange decisions were made. A fresh agent reads that file before it touches a single line of source. It starts warm instead of grepping around for ten minutes trying to work out what you want.

It never overwrites what is already there. It updates in place and prunes whatever stopped being true. Stale notes are worse than missing ones. When the file grows past five hundred lines it folds the old session log into a condensed history so the thing stays readable.

It hides the file in .git/info/exclude and not in .gitignore. Your working notes are your business. They do not belong in a commit your teammates have to read.

No dependencies. No config. It works in any repo and it degrades to the plain working directory if you are not even in git.

## Install

It comes in the main kamar-taj bundle at https://github.com/ShockRock2004/kamar-taj
or you can just grab this single folder.

```bash
cp -R handoff ~/.claude/skills/
```

Restart Claude Code and run /handoff. Find the full protocol in SKILL.md.

Your repo now remembers things. You still will not.
