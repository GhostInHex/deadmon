# Mute keys to the hackathon and expires

Story 15 asks for per-listing mute. Implemented naively — keyed to the source URL — it silently rots: sources carry tracking parameters and rotated URLs, so the same hackathon arrives as a new URL on the next crawl, the mute does not apply, and the subscriber is alerted about an event they already dismissed. The PRD also lists a `muted` flag on the Alert row only, which cannot express "mute this until registration closes".

Settled: a **mute** keys to the **hackathon** (not the source), is **per subscriber**, and carries a **mute-until** timestamp.

## Considered Options

- **Mute keyed to source URL.** Rejected: URL drift defeats it, and the failure is invisible — the mute appears to work right up until it doesn't.
- **Permanent boolean mute.** Rejected: a hackathon re-listed next cycle with a new deadline would stay muted forever. `mute until` covers both "not now" and "this cycle".
- **Global mute-all toggle only.** Rejected: loses the per-event control story 15 asks for.

## Consequences

- Mute state lives on the hackathon with a subscriber FK, never on the source or the alert row.
- `mute until` defaults to the registration-close date, so a mute expires by itself and the next cycle can alert again.
- Story 15's *snooze* is the same field with a shorter timestamp. One concept, two durations.
- Alert dispatch checks mute by hackathon id before computing lead time, so a muted hackathon never even enters the 7d/3d/24h windows.