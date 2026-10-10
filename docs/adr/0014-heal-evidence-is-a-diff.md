# The heal loop is given a diff against the last known-good fixture

A changed-layout page still returns HTTP 200 and still looks like a page — extraction yields zero candidates and no error. Handing the proposal "the failing run's trace plus a raw HTML snapshot" asks the model to guess new selectors from a full document dump. That is a low-probability guess with a real chance of committing something subtly wrong, and it is the centrepiece of the demo.

Settled: the proposal's evidence is a **diff** between the failing **snapshot** and the last **known-good fixture**, scoped to the regions the adapter actually reads.

## Considered Options

- **Hand the model the whole snapshot and the failing trace.** Rejected: no signal about *what changed*, and a large prompt for a free model. The model has to diff a page in its head — the one thing it is worst at.
- **Give the model the failing trace only.** Rejected: the trace says "zero listings found"; it cannot say which selector stopped matching.
- **Diff every byte of the page.** Rejected: pages churn constantly (ads, counters, timestamps) and a full diff is mostly noise. Scope it to the regions the adapter reads.

## Consequences

- The **snapshot** and the **known-good fixture** are both first-class stored artifacts, captured per break. Without a stored known-good fixture there is nothing to diff against, so fixtures must exist from Slice 1, not be retrofitted for Slice 4.
- The proposal prompt is small and highly structured: changed region, old selector, new markup. This matters for the free-model budget.
- Platform churn that does not touch the adapter's regions produces an empty diff — itself a useful signal that the break has another cause.
- The diff is recorded on the heal event, so a failed proposal can be diagnosed without re-running the model.