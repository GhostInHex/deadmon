# Validation asserts against the known-good fixture; fixtures are versioned, never overwritten

Two halves of one decision. Sandbox validation originally meant "the proposal extracts something". A changed selector that matches the page footer also returns results — 9 candidates, non-empty, validation green, committed. That is the fake heal: a green heal log containing a scraper that returns garbage, and the demo shows exactly that heal. Meanwhile a legitimately-changed page leaves the old fixture asserting against a page that no longer exists, so either it fails forever or the heal rewrites its own test.

Settled: validation asserts the proposal reproduces the **known-good fixture**'s shape — comparable candidate count, required fields populated, dates parseable. Non-empty is the floor, not the bar. **Fixtures are versioned**: a heal adds a new fixture beside the old and links both on the heal event.

## Considered Options

- **Non-empty result counts as validated.** Rejected: the footer-selector scraper passes. This is the single check that would let the demo's central moment be a lie.
- **Validate against the live page only.** Rejected: the live page is what changed; it has no defined expected output.
- **Overwrite the fixture when a heal succeeds.** Rejected: the agent silently rewrites its own test, and a wrong heal becomes undetectable — the test is edited by the thing under test.
- **Run the adapter's full test suite as validation.** Rejected: slow, network-flaky, and the suite is the thing that may encode the stale page.

## Consequences

- Slice 1 must record a **known-good fixture** per platform as it ships, or Slice 4 has nothing to diff or validate against. This is the strongest argument yet for the fixture corpus already in the plan's pre-event list.
- The heal event links old fixture, new fixture, and the validation result — so "the agent changed its test" is always traceable, never invisible.
- A retired fixture is retired explicitly and stays in history; it is never deleted by a heal it might contradict.
- Validation stays deterministic and offline per PRD test 1. Only the diff step (ADR-0014) touches a live page.