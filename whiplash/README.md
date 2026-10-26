# whiplash

> "Not quite my tempo."

You solved it, the tests went green, and you closed the tab feeling good about yourself. That feeling is the problem. Nobody in an interview tells you the answer was fine but slow. They just stop replying.

This skill reviews your solution the way a real panel would. Hand it a link, a screenshot or pasted code. It reads the constraints before judging your speed and traces your code on a real example before calling anything a bug. Then it scores you out of five on correctness, optimality, edge cases, code quality, and how well you could explain it out loud.

Every complaint comes with the exact input that breaks your code and the line that replaces it, written out in full.

It ends with the best possible solution in your language. It compiles, and it has comments on every line a beginner would trip over. That's the section you'll actually scroll to, so the skill always includes it.

It's hard on the code and never on you. It won't inflate a mediocre answer to be polite, because being polite now is how you get rejected in six weeks.

By default it judges against a new grad bar at a top tier product company and the correctness-first bar that banks use. Tell it your own target companies or level and it uses those instead.

## Install

It comes in the main kamar-taj bundle at https://github.com/ShockRock2004/kamar-taj,
or you can grab just this folder.

```bash
cp -R whiplash ~/.claude/skills/
```

Restart Claude Code and run /whiplash. The full protocol is in SKILL.md.

Fair warning: it won't say good job.
