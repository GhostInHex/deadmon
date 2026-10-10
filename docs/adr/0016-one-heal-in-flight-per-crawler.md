# One heal in flight per crawler, scoped to that adapter's files

A heal commits code, which runs on the next crawl. If the proposal itself breaks something, the watchdog sees a new break, heals it, and commits again — two generations later the Scout is rewriting its own scraper in a loop while the deadline sweep burns inference budget and Every's checkpoints fill with churn. Nothing in the loop can tell a cascade from progress.

Settled: **one heal in flight per crawler**, and a **proposal may only touch its own adapter's files**. A second break on the same crawler while a heal is running escalates instead of healing.

## Considered Options

- **Allow cascading heals with a depth limit.** Rejected: a depth limit still permits two generations of self-modification, and every generation needs its own sandbox validation run. The failure is not "too deep", it is that the agent is editing the code that judges its edits.
- **Allow proposals to touch shared modules** (dedupe, verification, date parsing). Rejected: a shared-module edit is a cross-adapter blast radius with no per-crawler blast-radius check available.
- **Serialize globally, one heal across all crawlers.** Rejected: too coarse when one platform breaks while three are healthy; it stalls unrelated adapters on a single incident.

## Consequences

- Proposals are validated against a scope allowlist before sandbox validation runs. A proposal touching a file outside its adapter's own directory is rejected pre-flight, not caught afterwards.
- A crawler whose heal fails escalates (ADR-0003's escalation path) with evidence attached; it does not get a third guess.
- Because the loop cannot iterate on itself, "healed scraper" always means "one proposal, validated once". That is what makes the heal log trustworthy evidence rather than a narrative.
- The demo's deliberate break proves detection → proposal → validation → commit → backfill exactly once, with no chance of a confusing second story.