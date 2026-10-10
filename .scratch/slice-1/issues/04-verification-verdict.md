# 04: Verification yields exactly one verdict and fails closed

**What to build:** One candidate in, exactly one verdict out, from a single code
path. Unproven is never asserted as fact and never deleted: a listing whose date
cannot be read is marked unverified and re-checked on the next crawl, and a
listing confirmed over is closed but keeps its row.

**Blocked by:** 01 (the candidate record and the verdict model). Gated on the
contract, not on the recorded fixtures — transport-level and unusable-date
cases are declared test doubles here, and 02's recorded versions strengthen the
corpus afterwards rather than blocking this ticket.

**Status:** open
**Triage:** blocked

- [ ] A verdict is live only when the candidate's source responds, its registration close parses to a real future date in a known timezone, and a mode is present
- [ ] A verdict is unverified when the source is unreachable, blocked or rate-limited, or when the date is unusable
- [ ] A verdict is closed when registration has passed or the event was cancelled
- [ ] The stage never decides a verdict from the platform's status or registration-open flags — both still read "live" on records whose registration has closed; only the registration-close date decides
- [ ] Verification never infers, defaults, or carries forward a deadline it did not read
- [ ] An unverified verdict is re-verified on the next crawl, never cached as fact, and never promoted without a fresh check
- [ ] A closed verdict is terminal but keeps its row, leaves the feed, and cancels any unsent alert
- [ ] Every verdict carries `verified_at`
- [ ] A test at the verification seam feeds one candidate in each state and asserts the verdict out
- [ ] No test in this ticket touches the network; transport failures are doubles and are labelled as such

## Comments
