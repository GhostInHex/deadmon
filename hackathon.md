# hackathon.md — build log, Oct 10–12 2026

Auditable narrative of what was built, in order. One commit per green unit;
pushed history append-only.

## Oct 10 — Slice 1: first crawler

- Recorded the Unstop corpus live: `hackathons-open.json` (25 records, the
  known-good fixture), then `hackathons-closed.json` and
  `hackathons-past.json` for the `closed` verdict, both ways verification
  defines it.
- `closed` verdict proven from recorded pages; `unverified` proven
  unrecordable on this platform and covered by a declared test double.
- Devfolio measured: no usable data path (client-rendered grid, 422s).
  Shipped Slice 1 on the platform that works.

## Oct 11 — Slice 2: five more crawlers, provenance, dead ends

- Recorded one page per platform (HackerRank, hackathon.com, lablab, MLH,
  GenAI.works) with per-row limits: no tz-aware registration close except
  GenAI.works, mode mapped only where stated.
- Measured dead ends (Devpost 403, Hack2skill/HackerEarth shells, DoraHacks
  404) recorded as verdicts, not assumptions.
- Adapter tests, one command (`deadmon-crawl`) running every crawler.

## Oct 12 — Slice 4 (first frontier): heal watchdog

- Detection only: two consecutive zero-listing finished runs for one
  crawler yield exactly one break; unfinished runs never count.
- Proposal, sandbox validation, and the loop stay out — a break has to be
  right before anything acts on it.

## Oct 12 — Evidence pack frontier (tickets 01–04)

- `/judges` route: 7 rows mapping claims to rubric weights, v1 vs v2
  trace-pair table, receipt count plus hash check, copy-paste verifies.
- Hero one-liner (`Deadlines that stay true. Literally.`), comparison
  table, `$0.00/crawl stdlib-only` cost banner citing the modelled plan.
- `agent.md`, `llms.txt`, `skills/deadmon/SKILL.md`: one-fetch agent docs
  with the fail-closed contract stated upfront.
- Numbered hashed receipts per crawl run plus `deadmon-receipt-check`;
  an edited receipt fails; local JSON, no login wall.

## Oct 12 — Ticket 05: heal proof pack (this pack)

- Constructed the changed-layout snapshot beside the known-good fixture;
  known-good untouched, still 25.
- Recorded heal-001 end to end: baseline, break (watchdog fires on 0+0),
  allowlist-scoped proposal, sandbox validation against known-good shape,
  second clean crawl, backfill, MLH steady-state silence.
- Landed `PRODUCT.md`, `hackathon.md`, `docs/known-limits.md`.

## What remains

The heal loop beyond detection (proposal generation, sandbox validation as
a service, commit, scheduled backfill) is Slice 4 work, not this pack. The
loop is proven here as recorded evidence; it is not yet a running service.
