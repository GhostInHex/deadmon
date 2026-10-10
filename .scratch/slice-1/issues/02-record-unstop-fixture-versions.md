# 02: Record the Unstop fixture versions that exercise the other two verdicts

**What to build:** Verification has to prove `unverified` and `closed` from
recorded pages, not from invented ones. Record what the platform actually
serves in those states and add each as a new fixture version beside the healthy
one, with provenance recorded so a future reader knows where it came from and
when.

**Blocked by:** None (can start immediately). Runs alongside 01 — it is recording
work with no code dependency.

**Status:** resolved
**Triage:** done

- [x] New fixtures are recorded live from the public Unstop endpoint, never hand-edited, and never derived by editing the healthy fixture
- [x] The healthy fixture is untouched — it stays the known-good baseline that a proposal must later reproduce
- [x] Each new fixture is a new version added beside the old one; nothing is overwritten
- [x] `fixtures/README.md` gains a provenance row per new file: source URL, record date, and the verdict state it exercises
- [x] Where a state cannot be recorded live — a timeout or a hard block is not something a server will hand you as a file — that fact is written into `fixtures/README.md` and the state is covered by a declared test double instead
- [ ] A test double is named as a double wherever it appears, so no test result is mistaken for recorded evidence

## Comments

**2026-10-11 — recorded.**

Two new fixture versions recorded live, five requests total (~2 s apart, normal
browser user-agent):

| File | Bytes | Records | Source URL |
|---|---|---|---|
| `fixtures/unstop/hackathons-closed.json` | 273 755 | 24 (page total 114) | `.../search-result?opportunity=hackathons&oppstatus=closed&per_page=25` |
| `fixtures/unstop/hackathons-past.json` | 211 898 | 25 (page total 6720) | `.../search-result?opportunity=hackathons&oppstatus=past&per_page=25` |

Saved byte-for-byte, SHA-256 verified against the response body, UTF-8, no
re-keying. The healthy fixture is untouched (302 365 bytes, original mtime).
`closed` is now provable two ways — registration already passed, and the event
being over. The two new pages share zero titles with each other or with the
healthy fixture.

**`unverified` is not recordable from this platform.** No status filter the route
accepts produces an absent or unparseable date; across 100 records sampled from
every accepted status, every one carried a parseable ISO-8601 `end_regn_dt`, and
no error bodies were served. Prescribed declared double:
`fixtures/unstop/hackathons-unverified.json` with `"TBA"` dates, labelled as a
double in its contents. **Not created here** — ticket 04 creates it, which is why
the final criterion above stays open.

**Traps that will corrupt results if ignored:**

1. `oppstatus=closed` records still carry `status: "LIVE"` and `regn_open: 1`.
   Switching on either classifies all 24 as live. **Only `end_regn_dt`
   distinguishes a closed registration.** Now a criterion on 03 and 04.
2. `oppstatus=past`, `all`, and `draft` return the same page; they differ only in
   the echoed pagination string. A fixture's meaning comes from its content, not
   from the parameter that fetched it.
3. Some past records have `end_regn_dt` *after* `end_date`. Both parse, both are
   past, the verdict is still `closed`.
4. `hackathons-closed.json` holds 24 records despite `per_page=25` — that is what
   the endpoint served. Do not write a test asserting 25.
5. Listing order is not date-sorted; paging is not a time filter.
6. All dates carry `+05:30`, so ADR-0013 UTC normalisation applies to the new
   fixtures exactly as to the healthy one.

_Recording done out-of-band by a subagent (no Orca Run/Dispatch provenance)._
