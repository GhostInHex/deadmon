# 03: Unstop extraction: the full candidate set from the known-good fixture

**What to build:** The Unstop adapter replays the recorded fixture and produces
the complete candidate set — every record the platform returned, with every
field the dashboard and later stages need — not just enough fields to make one
row work.

**Blocked by:** 01 (the candidate record shape).

**Status:** resolved
**Triage:** done

- [x] All 25 candidates in the known-good fixture are extracted
- [x] Registration close is read from the registration-requirements block, never from the top-level event date, which carries a different meaning
- [x] The adapter never decides liveness from the platform's status or registration-open flags — recorded closed pages still carry both set to live; only the registration-close date distinguishes them
- [x] The source URL is the absolute form the fixture provides, not the relative path
- [x] Dates carry a `+05:30` offset and are normalised to UTC at extraction
- [x] Mode is read from the platform's region field and is one of online, hybrid, offline
- [x] The team-size rule and the eligibility rules are extracted when present and absent when the record has none
- [x] A record with an empty prize summary yields an empty prize summary — not an error, and not an invented value
- [x] Extraction produces candidates only; it makes no claim about whether any of them is live
- [x] Running the adapter against the fixture requires no network
- [x] The extracted count and the set of populated required fields are recorded as the baseline this adapter is later validated against
- [x] A test feeds the fixture through the adapter and asserts on the candidates out, never on which key was read

## Comments

**2026-10-11 — resolved.** `src/deadmon/adapters/unstop.py` implements the
`Scraper` ABC: `fetch(path)` reads a recorded JSON payload (no transport in
Slice 1) and `extract(payload)` yields candidates. A bare record with no title
yields nothing. `tests/conftest.py` was added with the wave — it holds the
fixture paths and an autouse guard that makes any outbound socket call a test
failure, so "no network in tests" is mechanical rather than a convention.

**Baseline for later validation** (ADR-0015): the known-good fixture yields
**25 candidates**, all four required fields populated — `title`, `source_url`,
`registration_close`, `mode` — across 25 records. Modes: 11 offline, 8 online,
6 hybrid. Prize summary populated on 17, present-and-empty on 8 (the records
whose `prizes` is `[]`). Every close parsed from `+05:30` and stored UTC.

The other two recorded versions extract the same way: `hackathons-closed.json`
→ 24 candidates, `hackathons-past.json` → 25. No candidate count is asserted
against 24-as-a-truncation or 25-from-`per_page`; the number is simply what the
adapter yields, so ticket 02's traps cannot become a broken test.

**Judgment calls.**

1. **Registration close precedence over everything.** Close comes from
   `regnRequirements.end_regn_dt`; the test asserts the fixture really separates
   it from top-level `end_date` on at least one record, otherwise the test would
   prove nothing.
2. **`region: 'india'` yields `mode: None`.** One record in
   `hackathons-past.json` carries a region outside the three modes. The adapter
   does not guess a mode — `None` means the page did not state one, which fails
   closed in ticket 04. Verified: only `Devbhoomi Cyber Hackathon` is affected.
3. **`prize_summary` is a derived string, present even when empty.** Empty is
   `""`, `has('prize_summary')` is True, and no candidate ever carries a
   fabricated `₹0`.
4. **Liveness independence is tested by poisoning a live record** (in memory,
   never in the file): `status: "CLOSED"`, `regn_open: 0` on a record with a
   future close extracts exactly as its healthy twin.

Validation: `py -m pytest -q` → **24 passed** (8 contract tests from ticket 01 +
16 here). `py tools/check_docs.py` → ok (45 terms). Commit: `bbb7fb4`.

