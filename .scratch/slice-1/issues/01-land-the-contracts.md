# 01: Land the contracts: candidate record, verdict model, SQLite schema, scraper interface

**What to build:** Before anyone can build the pipeline, its seams have to exist
and be pinned. This ticket lands four contracts — the shape of a candidate, the
verdict model, the SQLite schema, and the scraper interface — each with a test
that fails when the contract changes. Nothing here crawls anything. It exists so
that every later slice lands without touching anybody else's module, which is
what makes them runnable in parallel.

**Blocked by:** None (can start immediately).

**Status:** open
**Triage:** ready-for-agent

- [ ] The candidate record is one documented shape: title, source URL, registration close, and mode, plus the optional fields that may legitimately be absent (prize summary, team-size rule, eligibility rules, registration-open date)
- [ ] An absent optional field stays absent — never filled with a default, a guess, or a value carried over from another source
- [ ] The verdict model is exhaustive: exactly live, unverified, closed, where unverified means indeterminate and closed is terminal
- [ ] Every verdict is stored with `verified_at`, so "stale" is a computable question rather than a guess
- [ ] The schema declares plural tables from the first commit: hackathons, sources, crawl runs, subscribers, profiles
- [ ] A card is modelled as a view over sources with many sources per hackathon, so one-card-per-hackathon still holds when a second platform arrives
- [ ] The DDL lives in versioned schema files; a committed database file is never the source of truth
- [ ] The scraper interface declares fetch and extract behind one contract, so the orchestrator never learns which platform it is talking to
- [ ] There is one test per contract that fails if the contract changes
- [ ] `python tools/check_docs.py` still passes

## Comments
