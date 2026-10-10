# A break is a regression against a baseline, not an absence of listings

The original trigger was "a crawler yields zero listings twice consecutively". Devfolio genuinely has weeks with no new hackathons, so that condition fires on a healthy crawler during a quiet period. The Scout would then self-heal working code, commit it, and fill the heal log with false alarms — and the self-heal demo, which is 30% of the marks and the demo's centrepiece, would show the agent modifying code that was never broken.

Settled: a **break** is a *regression* against a per-platform **baseline** of recent yield. Zero listings is suspicious only for a crawler that has recently been yielding some.

## Considered Options

- **Keep zero-twice as the trigger.** Rejected: fires on quiet weeks. A false heal is worse than no heal — it spends the demo, the commit history, and the operator's trust on a non-event.
- **Alert on every zero-yield run, let a human judge.** Rejected: buries the real break in routine noise, and hands the agent's job to the operator.
- **Fixed expected-count threshold per platform.** Rejected: hackathon volume is genuinely seasonal and bursty. A fixed number breaks every quiet week.

## Consequences

- The Scout must maintain a **baseline** per crawler — a rolling record of recent yield. Slice 4 cannot ship without it, and Slice 1's crawl-run rows must record `listings found` in a form the baseline can consume later.
- "Spike in schema-validation failures" stays a break trigger, unchanged.
- Escalation (two failed validations) is unchanged.
- **A quiet platform is a legitimate steady state**, and the heal log staying empty is a correct outcome, not a bug to fix. Worth saying out loud in the demo so a judge reads the empty log as health rather than absence.