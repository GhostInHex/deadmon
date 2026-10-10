# Alert deduplication happens at dispatch, and alerts are never queued

Three decisions landed together. Q13 chose that suspected-same sources each alert on their own date until a person confirms the link — conservative by design. That produces one card sending two Telegram messages a day for what looks like one event, which is the product's worst-looking output. Q18 chose that closing a hackathon cancels its unsent alerts. Q19 chose that closing is terminal for feed purposes.

Settled: **alerts are dispatched at the sweep and never queued.** A **superseded** rule deduplicates at dispatch: within one lead-time window, a second source's alert for the same hackathon is suppressed unless its date is **earlier** than the one already alerted. A closed hackathon cancels every unsent alert, expires its mute, and stops tag computation; its rows and history survive.

## Considered Options

- **Merge deadlines on a suspected-same link so dispatch never sees duplicates.** Rejected: ADR-0010's whole point is that a link is unproven. Merging to make the output pretty reasserts the thing we refused to assert.
- **Alert once per hackathon per window, ignoring later dates.** Rejected: if a second source reveals an *earlier* credible date, that is the most important alert of the run and would be suppressed.
- **Queue alerts and send them in a batch.** Rejected: a 24h lead time queued behind a batch boundary is the ADR-0004 bug again, one layer down. The 24h alert must be able to fire the moment it is due.
- **Auto-close a hackathon when all sources pass their deadline.** Rejected: requires guessing that no new source will appear with a live event. Closure is evidence-driven, per source.

## Consequences

- Dispatch reads hackathon-level state (verdict, mute, last-alerted window + date) and never trusts a single source in isolation.
- **Superseded** is a distinct outcome from a suppressed duplicate: a suppressed duplicate is silent, a superseded alert is sent *because* it is earlier.
- Since alerts are never queued, "cancels every unsent alert" means: if the sweep that would have sent a 24h alert finds the hackathon closed, nothing is sent. There is no backlog to drain and no stale-alert storm after a long outage.
- Closed hackathons keep their rows, tags, and sent-alert history (ADR-0002). Tags stop being *computed* and *shown*; they are not erased.
- Slice 3's fake-sink tests must cover: two sources same window, two sources with the second earlier, alert due exactly as the hackathon closes, and mute expiring mid-window.