# Session capability note

Recorded while diagnosing why Entire reported zero checkpoints across the whole
build. The integration is installed and healthy; nothing was ever captured
because of when the plugin was installed, and that is worth writing down.

## The symptom

`entire status` reported enabled, `entire doctor` passed every check, the git
hooks fired on every commit, and `entire checkpoint list` still returned zero.
The dashboard read "Stalled. No activity." across all 55 commits.

## What was actually true

Three separate things each had to be true, and two of them looked true while
being false:

1. **Hooks installed** — genuinely true. `pre-commit` ran `docs-check` on a
   normal commit, and `.entire/logs/entire.log` gained entries at each commit.
2. **Agent integration installed** — genuinely true. `entire agent list` showed
   `opencode` enabled, and `.opencode/plugins/entire.ts` was committed hours
   before the commit under test.
3. **A session was registered** — false, and this is the one that mattered.

The plugin fires `entire hooks opencode session-start` on the **`session.created`**
event. That event fires once, when a session opens. This repository's session
was already open when the plugin was installed, so it never fired, so Entire
never registered a session, so every commit had nothing to attach a checkpoint
to.

`entire doctor` does not catch this: it verifies wiring, not registration. The
tell is that `.entire/` contains only `logs/` and `settings.json` — if session
state were being written, it would be there.

## Why restarting did not obviously fix it

Restarting OpenCode creates a new session, which *should* fire
`session.created`. But it is easy to conclude "I restarted, so it is working"
without a commit having been made in the new session, and a checkpoint only
appears once both have happened.

## How to confirm, instead of assuming

```bash
entire doctor                 # wiring only - can be green with zero sessions
entire checkpoint list       # the number that matters
tail -f .entire/logs/entire.log   # look for "session-start", not just "redaction configured"
```

`"msg":"redaction configured"` on its own means hooks ran and found nothing to
attach to. `"msg":"session-start"` is the line that means capture is live.

## Worth knowing for the demo

Entire checkpoints record the **agent session** that produced a commit, not the
commit history. Git history is the durable record and is already complete; the
Entire graph is the extra evidence of how the code was written. This repo's
build predates session capture, so that evidence starts when capture starts —
it cannot be backfilled, because the session transcripts were never recorded.

## Update 2026-10-12: capture is live

A Claude Code session (with the `claude-code` agent hooks) registered
successfully on session start — `entire session current` resolves to the live
session and `entire doctor` is green. Two things changed versus the broken
state above:

1. **A session is registered.** The missing piece was never the hooks; it was
   registration. This session proves the Claude Code `SessionStart` hook fires
   correctly.
2. **`commit_linking` set to `always`** in `.entire/settings.json` (local-only;
   `.entire/` is gitignored). Every commit from a registered session now links
   without the interactive `[Y]es/[n]o/[a]lways` prompt, which is a failure
   mode for non-interactive commits.

This commit itself is the first checkpoint candidacy: made from the registered
session, so `entire checkpoint list` should show one entry afterwards. The 55
pre-existing commits stay checkpoint-less (no session context was ever
recorded for them) — expected, not a bug.