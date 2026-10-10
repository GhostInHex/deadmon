# Fuzzy dedupe proposes a link, it never merges

ADR-0003 settled that a hackathon has N sources and dedupe must not discard a platform's stated deadline. That left the matching rule open, and it was self-defeating: exact-key matching means "Smart India Hackathon 2026", "Smart India Hackathon", and "SIH 2026" never collide, so dedupe returns nothing and the dashboard shows the same event three times — failing the deduplication requirement while technically obeying *fail closed*.

Settled: match on **normalised title + a date window**. A confident match links sources to one hackathon. An uncertain match raises a **suspected same** proposal and is displayed as one card with a note; it never merges records automatically.

## Considered Options

- **Exact fingerprint match only.** Rejected: as above, does not deduplicate anything in practice.
- **Fuzzy match merges automatically.** Rejected: a wrong merge is the worst failure in this product — it hides a real hackathon or attaches a wrong deadline. `fail closed` forbids asserting a link not established by evidence.
- **Skip cross-platform dedupe entirely; ship per-platform feeds.** Rejected: loses a stated user story and Slice 2's "three platforms, one deduped feed" demo.

## Consequences

- **Fingerprint** becomes normalised-title + date-window proximity, not a hash. A collision is a *probability*, not a proof — which is exactly why a confident match is only ever a link, and an uncertain one is a proposal.
- Suspected-same links need a **dismiss** action. Auto-linking two records that are genuinely different must be reversible by one click, or the merge bug becomes unrecoverable.
- The dedupe seam's test (PRD test 3, "synthetic duplicates across two fake platforms") must now cover three cases: exact, fuzzy-proposed, and genuinely-distinct titles that look similar.