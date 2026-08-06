# askagy

Claude has been agreeing with itself for an hour. You cannot tell any more whether the plan is good or whether it just sounds good.

This skill goes and asks somebody else.

agy is the Antigravity CLI and it runs as a completely separate agent on your machine. It cannot see your chat. It cannot see your open files. It knows nothing at all. That is the entire point. A second opinion from something that shares your blind spots is not a second opinion.

So the skill writes the prompt properly. It frames the job and it hands over the context agy could not possibly have and it asks one sharp question and it states the shape of the answer it wants back. Then it relays the reply as agy said it and adds its own take wherever the two of them disagree. You get the comparison and not a blended mush.

It will not pretend. If agy is not installed it tells you and stops. Inventing a second opinion and putting somebody else's name on it is worse than having no second opinion at all.

Every call spends your own Antigravity quota so it warns you before a long chain of them.

## Install

It comes in the main kamar-taj bundle at https://github.com/ShockRock2004/kamar-taj
or you can just grab this single folder.

```bash
cp -R askagy ~/.claude/skills/
```

Restart Claude Code and run /askagy. Find the full protocol in SKILL.md.

Needs the Antigravity CLI on your PATH. The rest is just prompt writing.
