# 07: One neatlogs trace per crawl run

**What to build:** Every crawl run is a trace, and the dashboard links to it. A
run becomes debuggable in one click: which crawler, which stage, how long, how
many listings, and what it cost.

**Blocked by:** 01 (the crawl-run table that stores the trace reference).

**Status:** open
**Triage:** blocked

- [ ] Every crawl run produces one trace, stored with the run and linked from the dashboard
- [ ] Spans cover each platform and each pipeline stage
- [ ] The trace reference is stored on the run row, so the link survives a restart
- [ ] Listings found is split into live found and closed found, so a healthy run that found only closed records is distinguishable from a failed one
- [ ] An unverified record is never counted as a live listing in any run metric
- [ ] Run history on the dashboard shows per-crawler health: success, listings found, duration
- [ ] Token, cost and latency are captured by the tracing client rather than hand-instrumented per stage
- [ ] Trace capture never breaks a crawl run when the tracing service is unavailable

## Comments
