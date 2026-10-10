# The heal loop is itself instrumented; a failing proposal is an operator fault

The Scout heals scrapers, but nothing watched the healer. If the proposal step throws on every attempt — expired API key, model unavailable, budget exhausted — a broken crawler escalates forever, silently. The dashboard still shows the feed populated with older listings, so the only failing component is the one nobody is looking at. This is the same absence-of-signal failure ADR-0011 removed, one level up.

Settled: the heal loop is instrumented and carries its own baseline. A crawler that has broken and has not healed within N sweeps is a distinct signal from one that has never broken. Errors originating in the proposal step are an **operator fault**, not a crawler break — different cause, different fix, different alarm.

## Considered Options

- **Treat a failed proposal as an ordinary escalation.** Rejected: escalation says "a human should look at a scraper." A dead API key needs a human to check billing, and it will burn every escalation for every crawler until noticed. The signal is buried in the wrong queue.
- **Alert when the heal loop itself fails.** Rejected: alert channel is for deadlines, not operations. Operational faults belong in the heal log and run history, not Telegram.
- **Rely on crawl success to indicate health.** Rejected: a crawl can succeed for days while every heal proposal errors. Feed freshness proves extraction works, not that self-repair does.

## Consequences

- Run history shows, per crawler: broken, healing, healed, or escalated — and for escalated, whether the cause was a crawler fault or an operator fault.
- An operator fault is a distinct dashboard state from an unresolved crawler break. They look identical from the outside and require opposite responses.
- Slice 4 cannot report "self-healing works" without also proving the loop's own health, since a demo that silently never healed is indistinguishable from one where healing is disabled.