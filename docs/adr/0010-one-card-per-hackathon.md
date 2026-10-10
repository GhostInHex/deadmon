# A hackathon renders as one card; suspected-same never merges

Two decisions met here. Story 3 wants a hackathon to appear once. Q8 chose fuzzy dedupe that only ever *proposes*. Q13 chose that a suspected-same pair never merges deadlines. Left open: how a pair with two live deadlines renders, given that one card can only show one countdown.

Settled: **one card per hackathon**, showing the earliest credible registration close, with every source listed underneath carrying its own URL, stated date, and verdict. Dismissing a suspected-same link splits the card into two immediately.

## Considered Options

- **Two cards until the link is confirmed.** Rejected: reintroduces the triplicate dashboard that ADR-0005 exists to prevent, and the confirmation step never happens — it stays a permanent manual chore.
- **Merge deadlines on a fuzzy link, one card.** Rejected: silently attaching the wrong deadline to a real hackathon is the worst failure this product has. `fail closed` forbids asserting a link not established by evidence.
- **One card, latest date shown.** Rejected: can hide a nearer deadline.

## Consequences

- The card is a **view over sources**, not a claim that the sources are one. Dismissal is a first-class action (ADR-0005), not a rare escape hatch — which makes it safe, because the cost of a wrong link is one click to undo.
- Until a link is confirmed, **each source still alerts on its own date**. The card's single countdown is a reading aid; it is not what dispatch uses.
- Slice 1 ships with one source per hackathon, so the card collapses to a single row. The card abstraction must exist in the schema from the start, or Slice 2 becomes a rewrite.
- The dedupe test must cover: confirmed link, suspected-same pair, and two genuinely distinct events with similar titles.