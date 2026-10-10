# Profile is per-subscriber from day one

The PRD specified both "set my profile once" (single user, free tier) and a community-admin mode where one Scout serves a whole community with its own profile (paid tier). These are different data models. The demo will only ever have one subscriber.

Settled: **profile is per-subscriber from day one.** Slice 1 has exactly one subscriber; the schema is shaped so that adding a second is a row insert, not a migration.

## Considered Options

- **Singleton profile row, migrate later if the community tier ships.** Rejected: retrofitting subscriber fan-out means rewriting the alert dispatcher, the filter stage, and the dashboard query simultaneously — on the Sunday night before submission, for a feature that is explicitly post-hackathon (PRD non-goals).
- **Build the full community model now.** Rejected: out of time budget, and Slice 2 has three platforms to ship.

## Consequences

- `profiles` table with a foreign key from everything that depends on it. **Never a singleton `profile` row.** A future reader will see a multi-subscriber schema for a one-subscriber demo and assume over-engineering; this ADR is why.
- The free tier's "one alert profile" is a *plan limit* enforced at signup, not a data-model constraint.
- Slice 1 seeds exactly one subscriber. Alert dispatch iterates subscribers from the first commit, so adding the second is a data change.