# Kamar-Taj

This is where I keep my Claude Code skills. In Doctor Strange this is the place you
go to learn magic. Here you come to give Claude new tricks. You clone the repo and
install a skill and Claude suddenly gets smarter.

Six skills live here right now.

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

## whiplash

Not quite my tempo.

You solved the problem and the tests went green and you felt good about yourself.
That feeling is the problem. Nobody in an interview tells you the answer was fine
but slow. They just stop replying.

This one reviews your solution the way a hiring panel would. It reads the
constraints before it judges your speed. It traces your code on a real example
before it dares call anything a bug. Every complaint arrives with the input that
breaks you and the exact line that replaces it. It always ends with the best
possible solution written in your own language and commented properly.

Run /whiplash. It lives in the whiplash folder.

## handoff

Every fresh session you explain the whole project again. The stack and the goal and
the thing you were halfway through fixing. Every morning. Every time the context
runs out.

This one keeps a HANDOFF.md at your repo root so a new agent starts warm. The
objective and the current state and what is in flight and what is blocking you. It
updates in place and it never overwrites and it prunes whatever stopped being true.
It hides the file in .git/info/exclude so your working notes never land in a commit
somebody else has to read.

Run /handoff. It lives in the handoff folder.

## askagy

Claude has been agreeing with itself for an hour and you cannot tell any more
whether the plan is good or whether it just sounds good.

This one goes and asks somebody else. agy is the Antigravity CLI and it runs as a
completely separate agent that cannot see your chat or your open files. The skill
writes it a proper prompt and hands over the context it could not possibly have and
relays the answer attributed. It flags the places where the two of them disagree. If
agy is not installed it tells you and stops instead of faking a second opinion.

Run /askagy. It lives in the askagy folder.

## Install

```bash
git clone https://github.com/ShockRock2004/kamar-taj.git
cd kamar-taj
bash install.sh
```

Restart Claude Code and you get /wong and /dormammu and /agamotto and /whiplash and
/handoff and /askagy. If you only want one of them just copy that folder into
~/.claude/skills/.

## Notes

dormammu and handoff and whiplash need absolutely nothing. wong uses Python which
you probably already have. The PDF stuff needs Node and Chrome and the upload wants
rclone. askagy needs the Antigravity CLI on your PATH. If you lack any of those
tools the skill just skips that part or tells you plainly. Find more details in each
folder.

The code is MIT licensed so do whatever you want with it.

Not linked to Marvel in any way. Dormammu has not come to bargain about the license
yet.
