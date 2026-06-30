# Kamar-Taj

My stash of Claude Code skills. In Doctor Strange, Kamar-Taj is where you go to
learn the spells nobody put on the syllabus. Same idea here. Clone it, install a
skill, and Claude quietly picks up a new trick.

Two in the library so far.

## daily-log

Be honest with yourself. You let Claude debug and build things all day and you only
half know how any of it works. This fixes that.

At the end of the day it reads every Claude session you ran, works out what
actually got built, and writes you a plain English study guide. Then it renders
that into a dark mode PDF and drops it in your Google Drive, so you can read it on
the train home instead of nodding along to a diff you never really understood. It
also hands you a Slack standup you can paste without touching, and explains the git
commands you ran so you stop pasting them on faith.

Run `/daily-log`. Run `/daily-log light` when you are feeling stingy with tokens.
Lives in [`daily-log/`](daily-log/SKILL.md).

## dormammu

> "Dormammu, I've come to bargain."

The whole point of that scene is that Strange loses, on purpose, forever, until the
most powerful thing in the multiverse gives up out of sheer annoyance. This skill
does that to your code.

Point it at a problem and Claude stops being agreeable. It decides what "actually
done" means, takes its best shot, then turns on its own work and tries to break it.
The empty input, the million row list, the race nobody tests. When it finds the
crack it says the line, bins the attempt, and goes again. It does not get to call
anything finished until it has run the check and watched it pass.

No setup, no dependencies. Just a refusal to lose. Lives in
[`dormammu/`](dormammu/README.md).

## Install

```bash
git clone https://github.com/ShockRock2004/kamar-taj.git
cd kamar-taj
bash install.sh
```

Restart Claude Code and `/daily-log` and `/dormammu` are yours. Want only one? Copy
that folder into `~/.claude/skills/` and move on with your life.

## Fine print

`dormammu` needs nothing. `daily-log` runs on the Python you already have. The PDF
wants Node and Chrome, the upload wants rclone, and both just shrug and skip if you
do not have them. Specifics live in
[`daily-log/SKILL.md`](daily-log/SKILL.md).

MIT. Fork it, gut it, do your worst.

Not affiliated with Marvel. Dormammu has not, as far as I know, come to bargain
about the licensing.
