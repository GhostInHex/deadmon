# A hackathon's registration-close is the earliest credible date across its sources

A hackathon has N sources (ADR-0003) and profiles are per-subscriber (ADR-0006). Left open: when two sources state different registration-close dates, which one does an alert use — and does the answer vary per subscriber? ADR-0003 asserted "earliest credible date wins" as a consequence rather than a decision, and never said whether it could differ per person.

Settled: the hackathon's **registration close** is the **earliest credible date** across its sources. One date per hackathon, shared by every subscriber. Disagreement is surfaced on the card, never resolved per-person.

## Considered Options

- **Per-subscriber date, resolved per profile.** Rejected: registration close is a fact about the event, not an opinion about the person. Allowing it to vary per subscriber means two people get contradictory alerts about one hackathon and neither can be called wrong.
- **Latest credible date wins.** Rejected: it can make you miss the deadline. The product's entire claim is never missing one; a late date is the failure mode everything else is built to avoid.
- **Ask the operator to resolve conflicts manually.** Rejected: conflicts are the normal case across platforms, not an exception. Manual resolution does not survive three platforms.

## Consequences

- A **credible date** is one that parsed and verified on its source. An unparseable date contributes nothing — it does not default, carry forward, or drag the earliest toward the past.
- Two sources can disagree while both are credible. The card shows the chosen date and lists each source's own date and verdict underneath, so the disagreement is visible rather than smoothed over.
- Because the date is shared, one deadline sweep serves every subscriber regardless of profile. The sweep does not fan out per profile.
- An earlier date is only ever changed by new evidence from a source — never by a subscriber action.