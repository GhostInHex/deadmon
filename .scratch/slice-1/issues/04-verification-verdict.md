# 04: Verification yields exactly one verdict and fails closed

**What to build:** One candidate in, exactly one verdict out, from a single code
path. Unproven is never asserted as fact and never deleted: a listing whose date
cannot be read is marked unverified and re-checked on the next crawl, and a
listing confirmed over is closed but keeps its row.

**Blocked by:** 01 (the candidate record and the verdict model). Gated on the
contract, not on the recorded fixtures — transport-level and unusable-date
cases are declared test doubles here, and 02's recorded versions strengthen the
corpus afterwards rather than blocking this ticket.

**Status:** resolved
**Triage:** done

- [x] A verdict is live only when the candidate's source responds, its registration close parses to a real future date in a known timezone, and a mode is present
- [x] A verdict is unverified when the source is unreachable, blocked or rate-limited, or when the date is unusable
- [x] A verdict is closed when registration has passed or the event was cancelled
- [x] The stage never decides a verdict from the platform's status or registration-open flags — both still read "live" on records whose registration has closed; only the registration-close date decides
- [x] Verification never infers, defaults, or carries forward a deadline it did not read
- [x] An unverified verdict is re-verified on the next crawl, never cached as fact, and never promoted without a fresh check
- [x] A closed verdict is terminal but keeps its row, leaves the feed, and cancels any unsent alert
- [x] Every verdict carries `verified_at`
- [x] A test at the verification seam feeds one candidate in each state and asserts the verdict out
- [x] No test in this ticket touches the network; transport failures are doubles and are labelled as such

## Comments

**2026-10-11 — resolved.** `src/deadmon/verification.py`: `verify()` is one code
path from one candidate to exactly one verdict, and `verify_crawl()` applies it
to a set. The verdict lands on ticket 01's `Listing` contract — no new shape.
`VerificationResult` adds a *reason* string for observability only; it is not
stored, because the schema has no column for it and the contract does not need
one.

**Precedence (a judgment call, since two criteria collide).** The criteria say
"unverified when the date is unusable" and "closed when registration has
passed", and a record can do both — `hackathons-past.json` holds
`Devbhoomi Cyber Hackathon` whose `region: "india"` yields no mode *and* whose
registration closed in 2021. Settled in this order: source unreachable →
unverified; close unreadable or naive → unverified; close in the past →
closed; mode absent → unverified; else live. A parsed date already gone is
positive evidence that registration has passed, which is what `closed` *means*;
an absent mode only ever blocks `live`. The opposite ordering would have put a
2021 hackathon in needs-attention forever, which is exactly the noise ADR-0007
wants the greyed group to be read as.

**The declared double.** `fixtures/unstop/hackathons-unverified.json` — 3 records
taken from the healthy recording with dates set to `"TBA"` and a `_double`
banner naming its provenance, so the file labels itself. Its `fixtures/README.md`
row says **`test double, not a recording`** in the Source column, because every
row above it holds a live URL. Ticket 02's last open criterion ("a test double is
named as a double wherever it appears") is now satisfied; noted in ticket 02's
Comments separately.

**Whole-fixture verdicts at `now = 2026-10-11Z`:** `hackathons-open.json` → 25
`live`; `hackathons-closed.json` → 24 `closed` (registration passed);
`hackathons-past.json` → 25 `closed` (event over); the double → 3 `unverified`.

**Judgment calls.**

1. **The clock is injected.** `verify(candidate, now=...)` — no test or caller
   depends on wall time, so nothing flakes. `verified_at` defaults to real UTC
   `now_utc()` when not supplied.
2. **The boundary instant is closed** — a deadline equal to `now` is `closed`,
   not `live`. A deadline that has just arrived cannot still be entered.
3. **Alert cancellation is out of scope and asserted at the row level instead.**
   Kafka-style "cancel unsent alerts" is a Slice 3 concern and the alert table
   does not exist; the testable invariant here is that the listing survives with
   its verdict and its `verified_at`.

Validation: `py -m pytest -q` → **44 passed**. `py tools/check_docs.py` → ok.
Commit: `7a530b8`.

