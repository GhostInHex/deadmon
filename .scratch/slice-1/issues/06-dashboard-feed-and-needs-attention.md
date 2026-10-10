# 06: Dashboard rendering: the feed and needs attention, one card per hackathon

**What to build:** One server-rendered page with two groups — the feed and needs
attention — where each hackathon renders as one card carrying its earliest
credible registration close, with every source listed underneath carrying its
own URL, stated date and verdict.

**Blocked by:** 01 (the schema contract). Rendered from rows conforming to the
contract and seeded in tests; the seam against real crawl output is proven in 08.

**Status:** open
**Triage:** blocked

- [ ] Live listings appear in the feed as fact; unverified ones appear greyed in a separate needs-attention group; closed ones appear in neither
- [ ] A card shows the earliest credible registration close across its sources, with each source's own stated date and verdict beneath it
- [ ] With one source the card collapses to a single row, but the card remains a real view over sources rather than a listing row
- [ ] The badge reads the verdict word, not "verified" — a live verdict says what was checked, while "verified" says nothing about it
- [ ] Unverified records are excluded from every feed count
- [ ] The needs-attention group shows a per-crawler count, because a growing greyed group is the operator's blocked-platform signal
- [ ] The page renders from seeded rows conforming to the schema contract, with no fetch over the network
- [ ] No single-page-application framework is introduced

## Comments
