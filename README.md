# Kamar-Taj

This is where I keep my Claude Code skills. In Doctor Strange this is the place you
go to learn magic. Here you come to give Claude new powers. You clone it you install
a skill and Claude can do something new.

Two skills live here right now.

## daily-log

You let Claude build and fix things all day and you barely know how any of it works.
This sorts that out.

At the end of the day it reads all your Claude sessions and works out what got
built. Then it writes you a simple study guide so you can actually learn it. It
turns that into a dark mode PDF and drops it in your Google Drive so you can read it
on the way home. It also gives you a short standup to paste into Slack and it
explains the git commands you used.

Run /daily-log. Run /daily-log light if you want to spend fewer tokens. It lives in
the daily-log folder.

## dormammu

Dormammu I've come to bargain.

In the film Strange keeps dying on a loop until the villain gives up. This skill
does the same thing to your code.

You point it at a problem and Claude stops just agreeing with itself. It works out
what done really means. It writes a first try. Then it attacks its own work to find
what breaks. Empty inputs. Huge inputs. The bug you hoped nobody would notice. When
it finds a flaw it bins the attempt and tries again. It only stops once it has run
the check and seen it pass.

No setup. No extra tools. It just refuses to quit. It lives in the dormammu folder.

## Install

```bash
git clone https://github.com/ShockRock2004/kamar-taj.git
cd kamar-taj
bash install.sh
```

Restart Claude Code and you have /daily-log and /dormammu. If you only want one just
copy that folder into ~/.claude/skills/.

## Notes

dormammu needs nothing. daily-log uses Python which you already have. The PDF wants
Node and Chrome and the upload wants rclone. If you do not have them it just skips
that bit. More detail is in daily-log/SKILL.md.

It is MIT so do whatever you want with it.

Not linked to Marvel in any way. Dormammu has not come to bargain about the license
yet.
