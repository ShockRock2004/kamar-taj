# dormammu

![Dormammu](https://static.wikia.nocookie.net/marvelcinematicuniverse/images/0/08/Dormammu_1.png/revision/latest?cb=20170613180221)

Dormammu, I've come to bargain.

You remember the scene. Strange flies in and picks a fight he can't win. He gets
killed, comes back and tries again, a thousand times over, until the villain gives
up. This skill puts your code through the same loop.

Point it at a problem with /dormammu and Claude stops being a yes man. It works out
what done means and takes a first shot. Then it attacks its own code to see what
breaks: empty inputs, huge inputs, the race condition nobody tests, the slow database
query pretending to be fine.

When it finds a flaw it says the line and throws the attempt in the bin. It can't
call itself done until it has watched the checks pass, and code that merely compiles
doesn't count.

It's honest about the loop too. If it keeps failing the same way, it asks whether
your request makes sense. If it gets stuck on something only you can fix, it tells
you instead of spinning forever. It won't invent bugs to look busy.

There's nothing to install and no config. It just refuses to quit.

## It is wired into /goal

/goal is a built in command that stops Claude from ending its turn until a goal is
met. When you start dormammu, it writes the /goal line for your task and asks you to
paste it, since only a human can run /goal. If you paste it, the harness holds the
loop in place instead of good intentions, and the goal deletes itself once the work
is done. If you don't, dormammu holds itself to the same standard anyway. dormammu is
the brains of the loop and /goal is the cage.

## Install

It comes in the main kamar-taj bundle at https://github.com/ShockRock2004/kamar-taj,
or you can grab just this folder.

```bash
cp -R dormammu ~/.claude/skills/
```

Restart Claude Code and run /dormammu. The full protocol is in SKILL.md.

The image is Dormammu from Doctor Strange (2016) and belongs to Marvel Studios. It is
linked from the MCU wiki, not stored here. This is a free fan-made tool with no
connection to Marvel.
