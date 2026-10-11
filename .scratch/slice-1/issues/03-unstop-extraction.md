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

**2026-10-11 — resolved.** Landed `src/deadmon/crawlers/unstop.py`
(`UnstopScraper`: fixture-backed `fetch`, `extract` over the payload's
`data.data[]`) and `tests/test_unstop_adapter.py` (14 tests).
`py -m pytest -q` 24 passed; `py tools/check_docs.py` ok (45 terms).

**Baseline recorded** — `tests/baselines/unstop-hackathons-open.json`, the
extraction output for the known-good fixture, hand spot-checked against three
records (HACK ATTACK, Outpost, Cascade'26):

- 25 candidates; all four required fields populated 25/25 (title, source_url,
  registration_close, mode).
- Optional fields present on all 25: prize_summary, team_size_rule,
  eligibility_rules, registration_open.
- Modes: online 8, offline 11, hybrid 6 — the fixture's `region` counts.
- Every registration close is UTC, every source URL is the `seo_url`.

**What the tests pin** (all assert on candidates out, never on which key was
read): 25/25 extracted; required fields 25/25 populated; source URL is the
absolute `seo_url` and never a relative path; registration close equals the
`regnRequirements` instant in UTC and, on the 18 of 25 records where the two
differ, is not the top-level `end_date`; all instants offset-zero UTC; a
declared `+05:30` payload converts to the exact expected instant; an absent or
`"TBA"` date stays unread (`registration_close` / `registration_open` None);
mode comes from `region` and is one of the three; team size and eligibility
present when the record has them and absent (via `Candidate.has`) when it does
not; empty prize block yields `""` and never an invented value; the extracted
Candidate dataclass exposes no verdict/live field; the recorded `closed` page
(all 24 records still `status: "LIVE"`, `regn_open: 1`) yields 24 candidates
with dates read and nothing judged; the `past` page yields 25 candidates, the
one `region: "india"` record extracted with mode unread rather than mapped; and
a replay with `socket.socket.connect` raising never touches the network.

**Judgments worth knowing:**

- **`india` region.** One record in `hackathons-past.json` carries
  `region: "india"`, which is not a mode. Extracted with mode `None` — mapping
  it onto `offline` would be an invention. Only the `open` baseline is the
  validation target, and it is all three real modes.
- **`prize_summary` is `""`, not absent, when the record has no prizes.** The
  criterion names an empty prize summary, so `has("prize_summary")` is True
  with an empty string — an absent prize block stays distinguishable from an
  unread one, exactly as team size and eligibility do in the other direction.
- **Prize text is verbatim**, per rank, joined with `"; "`; `fa-rupee` renders
  as `₹` and an unmapped currency keeps no symbol rather than a guessed one.
  A rank with neither cash nor `others` renders as `Certificate` only when the
  platform said so.
- **Titles are verbatim too** — one fixture title has a trailing space, and
  the platform stated it that way.
- **`fetch` is fixture-backed.** The HTTP GET is the Scout's fetch tier
  (ticket 08); this ticket's criterion is that a fixture replay needs no
  network, which the socket-refusing test proves.
- **Naive timestamps stay unread.** A zone-less date cannot be normalised
  (ADR-0013), so it is left as verification's `unverified` input rather than
  assumed to be IST.

**Not in scope, left for later tickets:** `unverified` is a verdict (04), and
the declared test double `hackathons-unverified.json` named in
`fixtures/README.md` belongs to 04.
