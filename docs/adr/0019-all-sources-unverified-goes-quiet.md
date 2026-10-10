# A hackathon with no credible source drops to needs attention and goes quiet

Three linked sources, all live, card showing three days remaining. Tomorrow every source goes unverified — the platform is blocking, rate-limiting, or serving a page whose dates no longer parse. The card has no credible date, but it is not closed either. It is floating: not in the feed, not closed, alerts unable to compute a lead time.

Settled: a hackathon whose **every** source is unverified drops to **needs attention**, and its alerts stop silently. No alert is sent for a hackathon deadmon cannot currently vouch for. A partial loss of sources changes nothing — one credible source is enough.

## Considered Options

- **Send a "we lost track of this" alert.** Rejected: a fourth alert type nobody asked for, and it would fire for every listing on a platform during a transient block — turning an infrastructure hiccup into notification spam.
- **Keep the card in the feed at its last known date.** Rejected: asserts a deadline deadmon can no longer verify. `fail closed` (ADR-0002) forbids carrying forward a date that was not read.
- **Close the hackathon when all sources go unverified.** Rejected: unverified is indeterminate, not over. Closing would delete it from the feed permanently and lose a live event that a single successful re-verification would restore.
- **Keep alerting on the last credible date.** Rejected: worst option — alerts about a deadline nobody has confirmed, timed from a date that may be wrong.

## Consequences

- "Credible source" is computed live. One source verifying keeps the hackathon fully in the feed with normal alerts.
- The silence is the signal, and it is legible: grey card in needs attention, muted Telegram. That matches the product's core promise — never assert what you cannot verify.
- Every hackathon has a *scrape confidence* visible on the card: how many sources are live versus unverified versus closed. Partial degradation is visible rather than silent.
- Because unverified resolves rather than deleting, a blocked platform that recovers restores the feed automatically on the next successful verification, with no backfill needed. Backfill (ADR-0011) remains reserved for genuine gaps where crawling never happened.