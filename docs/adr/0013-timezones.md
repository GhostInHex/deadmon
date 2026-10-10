# Store UTC, render and label in the subscriber's timezone

Lead times are computed from registration close. Registration closes are stated by platforms in wildly varying zones — a hackathon closing "23:59 Pacific" is next day 11:29 IST. Store everything UTC and render countdowns and dates in the subscriber's timezone, with the zone labelled.

## Considered Options

- **Store UTC, render in the platform's local time.** Rejected: shows the user a time they have to mentally convert, right at the moment they are deciding whether to act.
- **Store UTC, render bare with no label.** Rejected: a countdown silently meaning IST when the reader assumes PT is how a deadline is missed while staring at correct data.
- **Store in the user's local zone at extraction.** Rejected: destroys the source's stated zone and makes cross-source comparison (ADR-0009) impossible.

## Consequences

- Every date column and every countdown carries a visible zone label. There is no unlabelled date in the UI.
- Lead-time math is pure UTC arithmetic — the 7d/3d/24h windows are zone-independent, so the subscriber's zone only affects display, never the decision to send.
- Extraction normalises to UTC immediately; a date that cannot be normalised is not credible (ADR-0009) and blocks verification.
- Slice 3's timing tests run in UTC and must include at least one case spanning a date boundary in the subscriber's zone.