# dormammu

![Dormammu](https://static.wikia.nocookie.net/marvelcinematicuniverse/images/0/08/Dormammu_1.png/revision/latest?cb=20170613180221)

Dormammu I've come to bargain.

You know the scene. Strange flies in and makes a deal he cannot win. He gets killed.
Then he comes back and does it again. He dies on a loop thousands of times until the
villain gives up.

That is the whole skill.

You point it at a problem with /dormammu and Claude stops just agreeing with itself.
It works out what done actually means. It takes a first shot. Then it turns on its
own work to find what breaks. Empty inputs. Huge inputs. The race nobody tests. The
slow query that is pretending to be fine.

When it finds a flaw it says the line and bins the attempt and tries again. It does
not get to say it is done until it has run the check and seen it pass. A draft that
just compiles does not count.

It is honest about the loop too. If it keeps failing the same way it asks whether you
asked for the right thing. If it is stuck on something only you can fix it tells you
instead of looping forever. And it will not make up fake problems just to look busy.

No tools to install. No config. It just will not quit.

## It is wired into /goal

This is the clever part. /goal is a built in command that sets a session goal and
puts up a wall that stops Claude from ending the turn until that goal is actually
met. dormammu uses it. The moment you start, it writes your end state as a /goal
condition that can be checked as true or false. After that the loop is not held up
by good intentions. It is held up by the wall. Claude cannot say it is done until
the goal is really met, and the goal clears itself the second it is. dormammu is the
brains of the loop and /goal is the cage.

## Install

It comes with the kamar-taj bundle at https://github.com/ShockRock2004/kamar-taj or
you can grab just this one.

```bash
cp -R dormammu ~/.claude/skills/
```

Restart Claude Code and run /dormammu. The full protocol is in SKILL.md.

Image is Dormammu from Doctor Strange 2016 and belongs to Marvel Studios. It is
linked from the MCU wiki for the look and not stored here. This is a fan made and
free tool with no link to Marvel.
