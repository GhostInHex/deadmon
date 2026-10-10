# Unverified listings are visible, greyed, in a separate group

Round 1 over-corrected: the glossary defined a Listing as "a candidate that verification returned live for", which deletes exactly the records the PRD wants kept. PRD story 8 says unverified listings are "marked 'unverified' rather than deleted or shown as fact", and the risk table says a blocked adapter "degrades to 'unverified' rather than breaking the run". The PRD also says the opposite — "a listing is not shown until it passes" — so this was always ambiguous.

Settled: **a candidate keeps a verdict and a record regardless.** Verdicts are live / unverified / closed. **live** listings appear in the feed as fact. **unverified** listings appear greyed in a separate **needs attention** group. **closed** ones leave the feed but keep their row.

## Considered Options

- **Hide unverified listings** (the literal reading of "not shown until it passes"). Rejected: if a platform blocks us, hiding every affected listing makes the dashboard look empty. That is indistinguishable from deadmon having silently missed everything — the precise failure the product exists to prevent.
- **Show unverified inline with live, distinguished only by badge colour.** Rejected: the feed's entire promise is "these deadlines I trust". Mixing untrusted records into it spends the trust the verification stage earned.

## Consequences

- The dashboard has two groups: the **feed** (live) and **needs attention** (unverified). Closed listings appear in neither.
- An unverified listing is never counted as a listing in any feed count, trace metric, or Slice 5 comparison — it is a candidate with a verdict, not a live listing.
- **Needs attention** doubles as the operator's blocked-platform signal: a growing greyed group means an adapter is failing, which is the early warning the watchdog consumes.
- Slice 1's "verified listings table with badges" is really two tables. Budget for it.