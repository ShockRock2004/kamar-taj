# dormammu

![Dormammu](https://static.wikia.nocookie.net/marvelcinematicuniverse/images/0/08/Dormammu_1.png/revision/latest?cb=20170613180221)

> "Dormammu, I've come to bargain."

You know the scene. Strange flies into the Dark Dimension, makes a deal he has zero
leverage for, and gets killed for it. Then he does it again. And again. Thousands
of deaths on a loop, until the most powerful being in the multiverse gets so sick
of him that it just folds.

That is the entire skill.

Hit a problem with `/dormammu` and Claude stops nodding along. It decides what
"actually done" looks like, takes its best shot, then immediately turns on its own
work hunting for the thing that breaks it. The empty input. The list with a million
rows. The race condition you were quietly hoping nobody would notice. The query
that is secretly O(n^2) and smiling about it.

When it finds the crack, it says the line, throws the attempt in the bin, and comes
back with a different plan. It does not get to call anything finished until it has
run the check and watched it go green. A first draft that merely compiles does not
count.

It is honest about the loop, too. If it keeps faceplanting the same way, it stops
blaming the code and starts asking whether you requested the right thing. If it is
genuinely stuck on something only you can unblock, it tells you instead of spinning
forever. And it will not invent fake problems just to look busy.

No dependencies, no config. Just a refusal to lose.

## Install

Ships with the [kamar-taj](https://github.com/ShockRock2004/kamar-taj) bundle, or
grab it on its own:

```bash
cp -R dormammu ~/.claude/skills/
```

Restart Claude Code, then `/dormammu`. The actual protocol lives in `SKILL.md`.

---

*Image: Dormammu in Doctor Strange (2016), © Marvel Studios. Hotlinked from the MCU
Wiki for the vibe, not redistributed. Fan made, noncommercial, and very much not
endorsed by a cosmic god of the Dark Dimension.*
