# 01: Land the contracts: candidate record, verdict model, SQLite schema, scraper interface

**What to build:** Before anyone can build the pipeline, its seams have to exist
and be pinned. This ticket lands four contracts — the shape of a candidate, the
verdict model, the SQLite schema, and the scraper interface — each with a test
that fails when the contract changes. Nothing here crawls anything. It exists so
that every later slice lands without touching anybody else's module, which is
what makes them runnable in parallel.

**Blocked by:** None (can start immediately).

**Status:** resolved
**Triage:** ready-for-agent

- [x] The candidate record is one documented shape: title, source URL, registration close, and mode, plus the optional fields that may legitimately be absent (prize summary, team-size rule, eligibility rules, registration-open date)
- [x] An absent optional field stays absent — never filled with a default, a guess, or a value carried over from another source
- [x] The verdict model is exhaustive: exactly live, unverified, closed, where unverified means indeterminate and closed is terminal
- [x] Every verdict is stored with `verified_at`, so "stale" is a computable question rather than a guess
- [x] The schema declares plural tables from the first commit: hackathons, sources, crawl_runs, subscribers, profiles
- [x] A card is modelled as a view over sources with many sources per hackathon, so one-card-per-hackathon still holds when a second platform arrives
- [x] The DDL lives in versioned schema files; a committed database file is never the source of truth
- [x] The scraper interface declares fetch and extract behind one contract, so the orchestrator never learns which platform it is talking to
- [x] There is one test per contract that fails if the contract changes
- [x] `python tools/check_docs.py` still passes

## Comments

**2026-10-11 — resolved.** `src/deadmon/` layout landed: `candidate.py`
(Candidate + make_candidate; absent optionals stay absent via
`_optional_present`), `verdict.py` (live/unverified/closed exhaustive; Listing
requires tz-aware `verified_at`), `scraper.py` (Scraper ABC: fetch + extract,
`run()` takes no platform arg), `schema/001_baseline.sql` (plural tables;
sources carries verdict+verified_at; crawl_runs carries trace_ref and
live/closed counts; card proven as view-over-sources query in test).
Validation: `py -m pytest -q` 8 passed; `py tools/check_docs.py` ok (45 terms).
Commit `9e5db19`. Judgment: `py -m pytest` used — bare `pytest` not on PATH.
