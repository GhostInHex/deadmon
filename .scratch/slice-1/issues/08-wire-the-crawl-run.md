# 08: The crawl run: wire adapter → verification → storage → trace behind one command

**What to build:** The demo moment. One command runs the Unstop crawler against
the recorded fixture and the real dashboard fills from real crawl output — a
candidate extracted, verified, stored, traced, and rendered as a card in the
feed. This is where the contracts land and compose; it is deliberately last,
because every module it wires has already been proven against its own seam.

**Blocked by:** 03, 04, 05, 07.

**Status:** resolved
**Triage:** done

- [x] One command runs the Unstop crawler end to end against the recorded fixture, with no network access
- [x] The run produces at least one live listing rendered as a card in the feed, plus one verdict of each of the other two kinds where the fixture set supports it
- [x] The run writes one crawl-run row, one trace, and a trace link visible on the dashboard
- [x] Run history shows the run with its per-crawler health figures
- [x] The trace's live-found and closed-found counts agree with what the dashboard shows
- [x] No module in the pipeline knows which platform it is talking to
- [x] The whole suite is green with no network access
- [x] `python tools/check_docs.py` still passes
- [x] The slice is demoable as: I crawl Unstop and see live listings with badges

## Comments

**2026-10-11 — resolved.** `src/deadmon/crawl.py` wires the seam:

```
py -m deadmon.crawl                      # crawl the recorded corpus, then serve :8765
py -m deadmon.crawl --reset --no-serve    # crawl and print only, from a clean slate
```

Each fixture is replayed through `fetch → extract → verify → store → trace` under
one `TraceClient`, one `crawl_runs` row and one trace. The dashboard is then
served by a stdlib `ThreadingHTTPServer` — no framework, no SPA, no network.
16 tests.

**The demo run, at `now = 2026-10-11T00:00Z` (pinned with `--as-of`):**

| fixture | runs | candidates | live | closed | unverified |
|---|---|---|---|---|---|
| `hackathons-closed.json` | #1 | 24 | 0 | 24 | 0 |
| `hackathons-open.json` | #2 | 25 | 25 | 0 | 0 |
| `hackathons-past.json` | #3 | 25 | 0 | 25 | 0 |
| `hackathons-unverified.json` (declared double) | #4 | 3 | 0 | 0 | 3 |

The page shows **22 cards in the feed, 3 greyed cards in needs attention** and
49 closed rows in neither group. All three verdicts are visible at once.

**Why 22 live cards and not 25 — a real finding, not a bug.** 25 + 24 + 25 + 3 =
77 candidates, but only 74 rows survive: the declared unverified double is built
from three records of the healthy fixture, so crawling it re-reads three source
URLs the healthy run had already claimed and **updates their verdict to
unverified**. That is precisely what ADR-0002 asks of a re-verification — the
verdict is replaced, never duplicated — and it is why the trace's per-run
`live` count (25) and the dashboard's live row count (22) differ *after* the
double is crawled. Both are correct: the trace describes that run, the
dashboard describes the latest evidence. The test
`test_the_trace_counts_agree_with_the_dashboard` asserts the invariant that
matters by running the healthy fixture alone, where 25 = 25 = 25.

**Judgment calls.**

1. **`--as-of <instant>` pins the verification clock.** The fixtures decay:
   every close in `hackathons-open.json` runs 2026-10-12 → 2026-11-05, so after
   Nov 5 the same command correctly yields closed verdicts instead of live ones.
   The default is the real clock; `--as-of` makes the recorded state replayable,
   and the report's demo command pins it so the demo cannot silently rot.
2. **`--reset` exists because runs are append-only.** Re-running the demo
   accumulates run rows (correctly — a run history is a history). `--reset`
   deletes `.runs/` first and is used by the demo command; it is an explicit
   opt-out, never the default.
3. **Trace reference format is `local://<uuid4>`** (or `neatlogs://<session>`
   when the neatlogs sink is live). It is stored on the run row, linked from the
   dashboard as `/trace/<ref>`, and the detail page renders the span table. A
   missing document renders "No trace document" rather than a 500.
4. **`/runs.json` exists** as a machine-readable view of run history, so the
   evidence pair Slice 5 needs can be pulled without scraping HTML.
5. **`README.md` was corrected.** It claimed "Implementation code has been
   removed" and listed only `docs/`; that stopped being true at ticket 01. It
   now lists `src/` and `tests/` and carries the demo command. Nothing else in
   the file was touched.

Validation: `py -m pytest -q` → **109 passed** (8 from 01, 16 from 03, 20 from
04, 18 from 05, 12 from 07, 19 from 06, 16 from 08). `py tools/check_docs.py` →
ok (45 terms). The server was verified over a real socket: `GET /` → 200 with
the two groups and the badges, `GET /runs.json` → 200 with 4 runs, `GET
/trace/<ref>` → 200 with the span table. Commit: `6d3b216`.

