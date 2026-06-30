# dormammu

![Dormammu](https://static.wikia.nocookie.net/marvelcinematicuniverse/images/0/08/Dormammu_1.png/revision/latest?cb=20170613180221)

Dormammu I've come to bargain.

You remember the scene. Strange flies in and picks a fight he cannot win. He gets
murdered. Then he comes back and tries again. He dies on a loop a thousand times
until the bad guy just gives up.

That is the entire skill.

You point it at a problem with /dormammu and Claude stops being a yes man. It
figures out what done actually means. It takes a first shot. Then it viciously
attacks its own code to see what breaks. Empty inputs. Massive inputs. That tricky
race condition nobody ever tests. That incredibly slow database query pretending to
be fine.

When it spots a flaw it says the magic line and throws the attempt in the bin. It
does not get to call itself done until it watches the checks pass. Code that just
compiles does not count here.

It is brutally honest about the loop too. If it keeps failing the exact same way it
asks if your request was actually sensible. If it gets completely stuck on something
only you can fix it tells you instead of spinning forever. It will never invent fake
bugs just to look busy.

No tools to install. No annoying config. It just refuses to quit.

## It is wired into /goal

This is the clever part. /goal is a built in command that builds a wall. It stops
Claude from ending the turn until a goal is truly met. dormammu uses this trick.
When you start the skill dormammu writes the perfect /goal line and asks you to
paste it. Only a human can run /goal so dormammu cannot do it alone. If you paste
the command the loop is trapped by the wall and not just by good intentions. The
goal deletes itself the second the work is truly finished. If you refuse to paste it
dormammu still holds itself to the exact same standard. dormammu is the brains of
the loop and /goal is the cage.

## Install

It comes in the main kamar-taj bundle at https://github.com/ShockRock2004/kamar-taj
or you can just grab this single folder.

```bash
cp -R dormammu ~/.claude/skills/
```

Restart Claude Code and run /dormammu. Find the complete protocol in SKILL.md.

The image is Dormammu from Doctor Strange 2016 and belongs totally to Marvel
Studios. It is linked directly from the MCU wiki and not stored here. This is a fan
made tool given away for free and it has absolutely no link to Marvel.
