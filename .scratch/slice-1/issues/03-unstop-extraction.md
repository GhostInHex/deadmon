# 03: Unstop extraction: the full candidate set from the known-good fixture

**What to build:** The Unstop adapter replays the recorded fixture and produces
the complete candidate set — every record the platform returned, with every
field the dashboard and later stages need — not just enough fields to make one
row work.

**Blocked by:** 01 (the candidate record shape).

**Status:** open
**Triage:** blocked

- [ ] All 25 candidates in the known-good fixture are extracted
- [ ] Registration close is read from the registration-requirements block, never from the top-level event date, which carries a different meaning
- [ ] The source URL is the absolute form the fixture provides, not the relative path
- [ ] Dates carry a `+05:30` offset and are normalised to UTC at extraction
- [ ] Mode is read from the platform's region field and is one of online, hybrid, offline
- [ ] The team-size rule and the eligibility rules are extracted when present and absent when the record has none
- [ ] A record with an empty prize summary yields an empty prize summary — not an error, and not an invented value
- [ ] Extraction produces candidates only; it makes no claim about whether any of them is live
- [ ] Running the adapter against the fixture requires no network
- [ ] The extracted count and the set of populated required fields are recorded as the baseline this adapter is later validated against
- [ ] A test feeds the fixture through the adapter and asserts on the candidates out, never on which key was read

## Comments
