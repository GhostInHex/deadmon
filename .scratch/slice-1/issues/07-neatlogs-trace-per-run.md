# 07: One neatlogs trace per crawl run

**What to build:** Every crawl run is a trace, and the dashboard links to it. A
run becomes debuggable in one click: which crawler, which stage, how long, how
many listings, and what it cost.

**Blocked by:** 01 (the crawl-run table that stores the trace reference).

**Status:** claimed
**Triage:** ready-for-agent

- [x] Every crawl run produces one trace, stored with the run and linked from the dashboard
- [x] Spans cover each platform and each pipeline stage
- [x] The trace reference is stored on the run row, so the link survives a restart
- [x] Listings found is split into live found and closed found, so a healthy run that found only closed records is distinguishable from a failed one
- [x] An unverified record is never counted as a live listing in any run metric
- [x] Run history on the dashboard shows per-crawler health: success, listings found, duration
- [x] Token, cost and latency are captured by the tracing client rather than hand-instrumented per stage
- [x] Trace capture never breaks a crawl run when the tracing service is unavailable

## Comments

**2026-10-11 — resolved.** `src/deadmon/tracing.py`: `TraceClient` produces one
`Trace` per crawl run, measures every span itself, and returns a `trace_ref`
that `finish_run` stores on the run row. 12 tests.

**The two sinks.** `neatlogs` 1.1.8 was inspected from its wheel (it is an
LLM-call auto-instrumenter: `init(api_key, tags)` → `LLMTracker`, sessions carry
a `session_id`). Slice 1 makes no model call, so a neatlogs trace of a crawl run
carries the **span tree and attributes**, which is exactly what a future heal
needs. The sink is chosen by `trace_client()`: `NeatlogsSink` only when the
package imports *and* `NEATLOGS_API_KEY` is set, `LocalSink` otherwise. **No
dependency was added to `pyproject.toml`** — the import is optional, so the
suite is green with the package absent and with the key unset.

**Verified against the real package (out of band).** Installed to a throwaway
`--target` directory so the project environment is untouched, then:
`backend chosen with a key: neatlogs`, `neatlogs session id:
70d53051-405f-40bd-82fd-c11a9a066e81`, `reference:
neatlogs://70d53051-…`, `backend after run: neatlogs | error: None`, spans
`['crawl', 'extract']` with client-measured latencies. The key used was a
placeholder; nothing in the test suite imports neatlogs or sets a key.

**Judgment calls.**

1. **`trace_ref` is always resolvable inside deadmon** — `/trace/<ref>` renders
   the stored document, and the neatlogs session id is stored as the trace's
   external id. This keeps a real link working when the service is absent, and
   it is the honest reading of "trace capture never breaks a crawl run".
2. **Local traces persist under `.runs/traces/`** (gitignored runtime state), so
   the detail page survives a restart. The run row stores only `trace_ref` —
   **no schema change**, so ticket 01's DDL and ticket 05's ownership are
   untouched. The trade-off: the trace document is not committed evidence, so
   `docs/evidence/` screenshots remain the durable artifact for the trace pair.
3. **`record_usage(tokens=…, cost_usd=…)` is on the client, not the stages.**
   Slice 1 records 0 by fact — no model call happens yet — so the numbers are
   absent-by-cause rather than hand-instrumented. The criterion is met
   structurally; the values are still trivially zero.
4. **Every span measures its own latency** in `TraceClient.span`, and a span
   records an error event and re-raises — tracing observes a failure without
   swallowing the pipeline's exception.
5. **`live_found` and `closed_found` are separate columns** (already in ticket
   01's schema) and `listings_found` never counts an unverified record.

Validation: `py -m pytest -q` → **74 passed**. `py tools/check_docs.py` → ok.
Commit: `__SHA_07__`.

