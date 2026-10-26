# Kamar-Taj

This is where I keep my Claude Code skills. In Doctor Strange, Kamar-Taj is where you
go to learn magic. This one is where Claude learns new tricks: clone the repo, install
a skill, and Claude gets a little smarter.

Six skills live here right now.

## wong

You let Claude build things all day and you have no idea how any of it works. This
skill is for that.

At the end of the day it reads all your Claude sessions and works out what actually
got built. Then it writes a simple study guide so you can learn it instead of nodding
along. It makes a dark mode PDF and drops it in your Google Drive for the commute
home. It also writes a short standup update for Slack and explains the git commands
you pasted without reading.

Run /wong, or /wong light to save some tokens. It lives in the wong folder.

## dormammu

Dormammu, I've come to bargain.

In the film Strange dies on a loop until the villain gives up. This skill does the
same thing to your buggy code.

Point it at a problem and Claude stops agreeing with itself. It works out what done
looks like and writes a first try. Then it goes after its own work looking for
cracks: empty inputs, huge inputs, that bug you hoped nobody would notice. When it
finds a flaw it throws the attempt away and starts again. It only stops once it has
watched the check pass.

There's no setup and nothing extra to install. It lives in the dormammu folder.

## agamotto

You want to merge a plan but you suspect Claude missed something obvious. This skill
brings in an outside reviewer to pick it apart.

Run it on your code and it summons the Eye of Agamotto. First it runs a quick self
check to catch the dumb mistakes before you pay for a real review. Then it sends your
work to a different AI whose job is to break it. The critic sends back a list of
flaws. Claude fixes the real ones and argues with the ones it thinks are wrong, and
they go back and forth for up to five rounds until the critic approves.

Run /agamotto. It lives in the agamotto folder.

## whiplash

Not quite my tempo.

You solved the problem, the tests went green, and you felt good about yourself. That
feeling is the problem. Nobody in an interview tells you the answer was fine but
slow. They just stop replying.

This one reviews your solution the way a hiring panel would. It reads the constraints
before judging your speed, and it traces your code on a real example before calling
anything a bug. Every complaint comes with the input that breaks your code and the
line that fixes it. It always ends with the best possible solution in your own
language, properly commented.

Run /whiplash. It lives in the whiplash folder.

## handoff

Every fresh session you explain the whole project again: the stack, the goal, the
thing you were halfway through fixing. Every morning, and again every time the
context runs out.

This one keeps a HANDOFF.md at your repo root so a new agent starts warm. It holds
the objective, the current state, what is in flight and what is blocking you. The
skill updates the file in place, never overwrites it, and prunes whatever stopped
being true. It hides the file in .git/info/exclude so your working notes never land
in a commit somebody else has to read.

Run /handoff. It lives in the handoff folder.

## askagy

Claude has been agreeing with itself for an hour and you can't tell any more whether
the plan is good or just sounds good.

This one asks somebody else. agy is the Antigravity CLI, and it runs as a separate
agent that can't see your chat or your open files. The skill writes it a proper
prompt, hands over the context it's missing, and relays the answer with agy's name on
it. It points out where the two of them disagree. If agy isn't installed it tells you
and stops instead of faking a second opinion.

Run /askagy. It lives in the askagy folder.

## Install

```bash
git clone https://github.com/ShockRock2004/kamar-taj.git
cd kamar-taj
bash install.sh
```

Restart Claude Code and you get /wong, /dormammu, /agamotto, /whiplash, /handoff and
/askagy. If you only want one, copy that folder into ~/.claude/skills/.

## Notes

dormammu, handoff and whiplash need nothing. wong uses Python, which you probably
already have. The PDF step needs Node and Chrome, and the upload needs rclone. askagy
needs the Antigravity CLI on your PATH. If a tool is missing, the skill skips that
part or tells you so. Each folder has more detail.

The code is MIT licensed, so do whatever you want with it.

Not affiliated with Marvel. Dormammu has not come to bargain about the license yet.
