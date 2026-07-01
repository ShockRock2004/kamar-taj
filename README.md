# Kamar-Taj

This is where I keep my Claude Code skills. In Doctor Strange this is the place you
go to learn magic. Here you come to give Claude new tricks. You clone the repo and
install a skill and Claude suddenly gets smarter.

Three skills live here right now.

## wong

You let Claude build things all day and you have no idea how any of it works. This
skill fixes that embarrassing problem.

It reads all your Claude sessions at the end of the day. It figures out what
actually got built. Then it writes a simple study guide so you can actually learn it
instead of just nodding along. It makes a dark mode PDF and throws it into your
Google Drive for the commute home. It also writes a short standup update for Slack
and explains those weird git commands you just pasted blindly.

Run /wong. Run /wong light to save some tokens. It lives in the wong folder.

## dormammu

Dormammu I've come to bargain.

In the film Strange keeps dying on a loop until the villain gives up. This skill
does the exact same thing to your buggy code.

You point it at a problem and Claude finally stops agreeing with itself. It figures
out what done actually looks like. It writes a first try. Then it aggressively
attacks its own work to find the cracks. Empty inputs. Massive inputs. That stupid
bug you prayed nobody would notice. When it finds a flaw it throws the whole thing
away and tries again. It only stops when it watches the check pass with its own
eyes.

No setup. No extra tools. It just refuses to quit. It lives in the dormammu folder.

## agamotto

You want to merge a plan but you know Claude probably missed something obvious. This
skill brings in an outside expert to tear it apart.

You run it on your code and it summons the Eye of Agamotto. First it does a quick
self check to catch the stupid mistakes before you spend money on a real review.
Then it sends your work to a completely different and utterly ruthless AI. The critic
tries its best to break your code and sends back a list of flaws. Claude reads the
feedback. It fixes the real problems and argues aggressively about the fake ones.
They fight it out for up to five rounds until the critic finally approves.

Run /agamotto. It lives in the agamotto folder.

## Install

```bash
git clone https://github.com/ShockRock2004/kamar-taj.git
cd kamar-taj
bash install.sh
```

Restart Claude Code and you get /wong and /dormammu and /agamotto. If you only want one of them
just copy that folder into ~/.claude/skills/.

## Notes

dormammu needs absolutely nothing. wong uses Python which you probably already have.
The PDF stuff needs Node and Chrome and the upload wants rclone. If you lack those
tools it just skips that part. Find more details in wong/SKILL.md.

The code is MIT licensed so do whatever you want with it.

Not linked to Marvel in any way. Dormammu has not come to bargain about the license
yet.
