# 05: Storage: a crawl run writes hackathon and source rows, and can be read back

**What to build:** A crawl's output becomes state. Candidates carrying verdicts
are written as hackathons and sources, the run that produced them is recorded,
and a run that is killed mid-flight resumes without duplicating rows or
re-asserting a verdict it already holds.

**Blocked by:** 01 (the schema and the verdict model).

**Status:** resolved
**Triage:** done

- [x] One crawl run row is recorded per crawler per execution, with start, finish, status, listings found, and its trace reference
- [x] A live candidate creates one hackathon with one source beneath it, keyed so a second crawl of the same source updates rather than duplicates
- [x] An unverified candidate keeps a record in exactly the same way — unverified is a stored verdict, not a skipped row
- [x] A closed verdict is retained with its row intact
- [x] Re-running the same crawl against the same fixture produces no duplicate rows and no second verdict for the same source
- [x] A run interrupted mid-write leaves the database consistent and resumable
- [x] The subscriber and profile tables exist and are empty at this stage, because the model is not a singleton even though the demo runs with exactly one
- [x] No committed database file is the source of truth; the schema files are
- [x] A test kills a run part-way through and asserts no duplicate rows and no duplicated alerts

## Comments

**2026-10-11 — resolved.** `src/deadmon/storage.py`: `apply_schema()` reads
`src/deadmon/schema/001_baseline.sql` (ticket 01's versioned DDL — not touched)
into a fresh connection; `Store` opens, closes and context-manages that
database. `start_run` / `finish_run` / `mark_interrupted` own `crawl_runs`;
`record_run_listings` upserts every listing; `cards()` and `run_history()` read
back. 18 tests.

**The seam that needed deciding.** Ticket 01's `Listing` carries verdict +
identity, and its `Candidate` carries the fields; the schema wants both on one
row. Rather than edit ticket 01's resolved contract, `record_run_listings`
takes `(candidate, listing)` pairs, so the split is explicit at the storage
boundary instead of hidden in a merged type.

**Idempotence.** `sources` is `UNIQUE(crawler, source_url)` and written with an
upsert, so a second crawl of the same source updates the row. Hackathons are
matched by title inside the same crawler — Slice 1 has one crawler, so this is
the correct key today; **Slice 2 replaces it with the fingerprint** (glossary),
and that is recorded here so nobody mistakes title-matching for dedupe.

**Crash test.** `record_run_listings(..., crash_after_first=True)` raises after
the first source is committed. The test then asserts: one row landed, the run
is unfinished, `resume_interrupted()` finds it, `mark_interrupted` closes it,
and re-running the same crawl leaves two sources and one verdict each.

**Judgment calls.**

1. **One commit per source, not one per run.** Progress is durable per row, so
   a killed run loses at most the source it was writing and the upsert makes
   the retry idempotent. Committing once per run would have rolled a
   half-completed crawl back entirely — still consistent, but it re-does work
   the database had already safely recorded.
2. **`resume_interrupted()` finds any run with `finished_at IS NULL`**, whatever
   its status text, and `mark_interrupted()` writes the terminal status. The
   killed run is detected from the absence of a finish, not from a status flag
   a dead process could not have written.
3. **"No duplicated alerts" is asserted at the row level.** The alert table is
   Slice 3 and does not exist; the invariant that exists and is testable is one
   verdict per source, never one per run. Cancellation is noted on ticket 04.
4. **`listings_found` defaults to `live_found + closed_found`** — an unverified
   record is not a live listing and never enters any run count (ADR-0007).

Validation: `py -m pytest -q` → **62 passed**. `py tools/check_docs.py` → ok.
Commit: `e45a3d2`.

