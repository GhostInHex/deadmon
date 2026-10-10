# Unverified is a verdict, not a status

Verification produces exactly one of three verdicts: **live**, **unverified**, **closed**. The PRD used "unverified" loosely for both "we couldn't find out" and "this listing is bad", and separately told us expired listings should "disappear automatically" *and* that failed verification should be "marked unverified rather than deleted" — contradictory rules, since expiry is itself a verification outcome.

Settled: **unverified** means indeterminate — page unreachable, blocked, or the deadline unparseable. **closed** is terminal and means confirmed over (registration passed, or cancelled). A closed hackathon leaves the feed but its **rows survive**.

## Considered Options

- **Delete expired rows** (literal reading of story 5). Rejected: Slice 5's before/after trace pair tabulates miss rate and false positives over runs. If a run that correctly detects expiry destroys rows, a run that *fails* to detect expiry looks identical to a healthy one — the evidence stops being evidence.
- **Keep expired on the dashboard, greyed.** Rejected: violates "I never get excited about a dead event again". The feed must be clean.

## Consequences

- A run that finds zero *new* listings may still have produced closed verdicts. "Listings found" in the trace comparison must distinguish **live found** from **closed found**, or Slice 5's miss-rate numbers are meaningless.
- An unverified verdict is **re-verified on the next crawl**, never cached as fact and never promoted without a fresh check.
- Every verdict is retained with `verified_at`, so "stale" is a computable question rather than a guess.