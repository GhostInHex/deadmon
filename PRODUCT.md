# PRODUCT.md — deadmon

deadmon watches hackathon platforms so a student developer never misses a
registration close. The Scout runs every platform through fetch, extract,
verify, dedupe, filter, alert: a daily full crawl plus a frequent deadline
sweep. Verification is per source and yields exactly one verdict — `live`,
`unverified`, or `closed` — and deadmon fails closed: a deadline it did not
read is never inferred, defaulted, or carried forward.

The feed holds live cards. Needs attention holds unverified sources, greyed
but visible. Closed rows leave the feed and survive in the record. One card
per hackathon; each source keeps its own verdict. Profiles belong to
subscribers; reason tags explain fit, never a numeric score.

When a platform breaks a crawler, the agent repairs itself: a break is a
regression against a per-crawler baseline, the proposal may change selectors
and extraction rules only, sandbox validation reproduces the known-good
fixture, and backfill re-crawls the gap. Proof: `docs/evidence/heal-001-unstop/`.

## Numbers (measured, fixture-backed, `--as-of 2026-10-11`)

- 77 candidates in: 25 live, 49 closed, 3 unverified (one declared double).
- 22 cards in the feed, 3 cards needing attention.
- 4 crawl runs in the main corpus, one trace and one hashed receipt each.
- heal-001: Unstop 25 to 0 overnight, watchdog fires, proposal validates,
  second clean crawl 25 live, backfill 25 live, MLH zero stays steady.
- Cost per crawl: $0.00, stdlib only — modelled, not measured (no model
  calls on the crawl path). Tiers in `docs/business-plan.md` are a modelled
  draft, never traction.

## Verify

```console
py -m pytest -q
deadmon-crawl --reset --no-serve --as-of 2026-10-11T00:00:00+00:00
deadmon-receipt-check
```

Judges start at `/judges`. Agent builders start at `agent.md`.
Limits are stated honestly in `docs/known-limits.md`.
