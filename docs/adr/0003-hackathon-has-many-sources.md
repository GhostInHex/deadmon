# A hackathon has many sources; sources are not listings

The PRD deduplicated cross-platform duplicates by keeping one listing and discarding the rest. That silently throws away the second platform's stated deadline, which contradicts the requirement that a moved deadline gets caught rather than going stale.

Settled: **hackathon** is the real-world event (what the user cares about), **source** is one platform's claim about it. A hackathon has N sources. Each source keeps its own URL and its own stated dates; the hackathon's registration-close is resolved *across* them.

## Considered Options

- **One row wins, the rest are discarded.** Rejected: this is the contradiction above, and it is the reason dedupe is a first-class stage.
- **Merge into one row, keeping the earliest/latest date silently.** Rejected: a silent choice with no evidence is indistinguishable from a parse error, and `fail closed` forbids it.

## Consequences

- Verification is **per source**, and each source carries its own verdict. A hackathon can be live on Devfolio and unverified on Unstop.
- If sources disagree on the registration-close date, that is a surfaced conflict, not a silent resolution — the earliest credible date wins *and* the conflict is recorded.
- The fingerprint is deliberately conservative: a missed match means two records, a wrong match means a merged lie.
- Every dedupe decision is explainable in the UI, because story 9's principle (never silently drop something good) applies to dedupe as much as to filtering.