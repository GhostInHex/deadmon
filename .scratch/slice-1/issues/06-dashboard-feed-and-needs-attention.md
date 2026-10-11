# 06: Dashboard rendering: the feed and needs attention, one card per hackathon

**What to build:** One server-rendered page with two groups — the feed and needs
attention — where each hackathon renders as one card carrying its earliest
credible registration close, with every source listed underneath carrying its
own URL, stated date and verdict.

**Blocked by:** 01 (the schema contract). Rendered from rows conforming to the
contract and seeded in tests; the seam against real crawl output is proven in 08.

**Status:** claimed
**Triage:** ready-for-agent

- [x] Live listings appear in the feed as fact; unverified ones appear greyed in a separate needs-attention group; closed ones appear in neither
- [x] A card shows the earliest credible registration close across its sources, with each source's own stated date and verdict beneath it
- [x] With one source the card collapses to a single row, but the card remains a real view over sources rather than a listing row
- [x] The badge reads the verdict word, not "verified" — a live verdict says what was checked, while "verified" says nothing about it
- [x] Unverified records are excluded from every feed count
- [x] The needs-attention group shows a per-crawler count, because a growing greyed group is the operator's blocked-platform signal
- [x] The page renders from seeded rows conforming to the schema contract, with no fetch over the network
- [x] No single-page-application framework is introduced

## Comments

**2026-10-11 — resolved.** `src/deadmon/dashboard.py`: `cards_from_rows()` groups
stored source rows into **cards** (one per hackathon, ADR-0010), `build_view()`
splits them into the **feed** and **needs attention**, and `render_page()` /
`render_trace()` emit one server-rendered HTML page each. All pure functions —
the page renders from seeded rows with no fetch over the network and no SPA
framework (asserted by reading the module's own source in the test).

**The grayed group carries the operator signal.** `needs_attention_by_crawler()`
counts unverified sources per crawler and the summary line renders those counts
as badges, so a growing greyed group reads as "this platform is failing"
(ADR-0007) rather than as a list of bad rows.

**Judgment calls.**

1. **The ADR-0009 computation moved out of ticket 05's module into the
   dashboard.** `earliest_credible_close()` had landed in `storage.py`, but the
   dictionary/glossary frames the earliest credible close as *the card's*
   reading of its sources — a view concern, not a storage one. `Store` now
   returns rows through `source_rows()` and the dashboard chooses the date. The
   change is recorded here because it touches ticket 05's file; ticket 05's own
   tests are unaffected.
2. **Only a `live` source contributes the card's date.** A closed source's date
   is evidence it was credible once, not a live claim now, and an unverified
   source never had a parseable date. No contributing source yields "no
   credible registration close" — never a fallback (fail closed).
3. **Dates render with an explicit zone label.** Everything is stored UTC
   (ADR-0013) and Slice 1 has no subscriber timezone yet, so every date renders
   as `… UTC` rather than bare; a naive instant is labelled `zone unknown`
   instead of being silently trusted.
4. **Titles, URLs and verdicts are escaped.** A test feeds a script tag through
   a title and asserts the page contains the escaped form.
5. **Both the card abstraction and the two-group split are exercised with one
   source**, so the single-source collapse is proven to still be a view over
   sources rather than a listing row.

Validation: `py -m pytest -q` → **93 passed**. `py tools/check_docs.py` → ok.
Commit: `__SHA_06__`.

