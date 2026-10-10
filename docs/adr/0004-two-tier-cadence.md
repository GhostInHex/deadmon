# Two-tier crawl cadence: daily full crawl, hourly deadline sweep

The PRD specified a **daily** crawl and alerts at 7d / 3d / **24h** before registration close. These cannot both hold. A listing discovered Monday 09:00 closing Tuesday 15:00 is 30 hours out at crawl time — no lead time fires. By Tuesday 09:00 it is 6 hours out and the 24h mark was crossed on Monday afternoon while nothing was running. The most important alert, the last one, silently never sends.

Settled: **two-tier cadence.** A **daily full crawl** per platform discovers listings; a **deadline sweep** runs every few hours and re-verifies only listings currently inside a lead-time window.

## Considered Options

- **Send the 24h alert as "due" whenever a crawl notices it is past 24h.** Rejected: a deadline 3 hours out becomes an "urgent" notification indistinguishable from a genuine 24h one, and lead-time testing (Slice 3) loses the ability to prove a window fired correctly.
- **Crawl everything hourly.** Rejected: multiplies request volume against platforms the PRD commits to crawling "politely by design", and burns LLM budget for listings nobody will act on.

## Consequences

- The **deadline sweep** is a separate, much cheaper operation: a small set of URLs, verify only. It is the thing that makes the 24h lead time honest.
- A listing discovered with less than 24h remaining still gets an alert — at the tightest window it has already passed, labelled as such.
- **Scheduler tests must cover both tiers.** Slice 3's "no duplicate alerts" assertion has to hold across a sweep that fires and a daily crawl that re-sees the same listing.
- Polite-crawl posture is preserved: the sweep is rate-limited per platform and cache-first.