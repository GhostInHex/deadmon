# Slice 1 — one platform, end to end

Source of truth for this slice: `docs/PLAN.md` (Slice 1) and `docs/PRD.md`.
Read `GLOSSARY.md` and the ADRs before starting any ticket.

## Demoable target

> I crawl Unstop and see live listings with badges.

One platform through the whole pipeline, traced, on one server-rendered page.
Dedupe across platforms, eligibility filtering, alerts and the scheduler are
Slice 2 and 3 — out of scope here.

## Which platform, and why

Unstop is Slice 1's crawler. Its listing data arrives as a public JSON
endpoint, so no rendered-DOM adapter is needed and the known-good fixture is a
plain payload. Devfolio's listing grid is client-rendered and its API rejects
every parameter shape tried, so an adapter over the recorded Devfolio pages
extracts nothing; that page is intentionally reserved for Slice 4's break
(see `fixtures/README.md`).

## Settled decisions these tickets depend on

Where the PRD and the glossary disagree, the glossary wins. The four conflicts
that Slice 1 must not get wrong:

- A **verdict** is one of exactly `live`, `unverified`, `closed`. `unverified`
  means indeterminate — never "bad", never deleted
  ([ADR-0002](docs/adr/0002-unverified-is-a-verdict.md)).
- A **card** is a view over sources, one per hackathon, present in the schema
  from the first commit even though Slice 1 has one source per hackathon
  ([ADR-0010](docs/adr/0010-one-card-per-hackathon.md)).
- The dashboard has **two groups** — the feed and needs attention
  ([ADR-0007](docs/adr/0007-unverified-is-visible-not-hidden.md)). Slice 1 is
  two tables, not one.
- **Profile** belongs to a subscriber and tables are plural from the first
  commit ([ADR-0006](docs/adr/0006-profile-is-per-subscriber.md)).

## Vocabulary

The loop is the **Scout**; the per-platform unit of work is a **crawler**; the
code behind the scraper interface is an **adapter**; what extraction produces
is a **candidate** until it carries a verdict. Full terms and their `_Avoid_`
lists are in `GLOSSARY.md`.

## Status

`Status:` is the lifecycle state (`open`, `claimed`, `resolved`). `Triage:` is
readiness (`ready-for-agent` once unblocked). A ticket's blockers are done when
every issue file it lists is `resolved`.
