# askagy

Claude has been agreeing with itself for an hour, and you can't tell any more whether the plan is good or just sounds good. This skill goes and asks somebody else.

agy is the Antigravity CLI. It runs as a separate agent on your machine and can't see your chat or your open files, which is why it's useful. A second opinion from something that shares your blind spots isn't worth much.

So the skill writes the prompt properly. It frames the job, hands over the context agy doesn't have, asks one specific question and says what shape the answer should take. Then it relays agy's reply as agy wrote it and adds its own view wherever the two disagree, keeping the two separate so you can compare them.

If agy isn't installed, it says so and stops. Making up a second opinion and putting somebody else's name on it would be worse than having none.

Every call spends your own Antigravity quota, so it warns you before running a long chain of them.

## Install

It comes in the main kamar-taj bundle at https://github.com/ShockRock2004/kamar-taj,
or you can grab just this folder.

```bash
cp -R askagy ~/.claude/skills/
```

Restart Claude Code and run /askagy. The full protocol is in SKILL.md.

It needs the Antigravity CLI on your PATH. Everything else is prompt writing.
