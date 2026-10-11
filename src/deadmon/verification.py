"""Verification: one candidate in, exactly one verdict out.

Verdicts are exactly `live`, `unverified`, `closed` (ADR-0002). `unverified`
means *indeterminate* — never "bad", never deleted, re-verified on the next
crawl. `closed` is terminal and keeps its row.

Fail closed: this stage never infers, defaults, or carries forward a deadline
it did not read. A registration close it cannot read produces `unverified`,
never a guess.

Precedence, applied in order:
  1. source does not respond                 -> unverified (could not find out)
  2. registration close unusable / naive     -> unverified (could not find out)
  3. registration close in the past          -> closed (confirmed over)
  4. mode absent                             -> unverified (page stated no mode)
  5. otherwise                               -> live

Step 3 sits above step 4 on purpose: a parsed date already in the past is
positive evidence that registration has passed, which is what `closed` means.
An absent mode only ever blocks `live`.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from .candidate import Candidate
from .verdict import CLOSED, LIVE, UNVERIFIED, Listing, now_utc

# Where the payload came from. A verdict may rest on a recording; it may not
# claim the web was checked when nothing fetched it.
REPLAYED = "replayed"
LIVE = "live"


@dataclass(frozen=True)
class VerificationResult:
    """One verdict, with the reason it was reached.

    The reason is observability, not a new stored field: `Listing` is the
    contract and carries the verdict alone.
    """

    listing: Listing
    reason: str

    @property
    def verdict(self) -> str:
        return self.listing.verdict


def verify(
    candidate: Candidate,
    *,
    source_responds: bool = True,
    provenance: str = REPLAYED,
    now: datetime | None = None,
    verified_at: datetime | None = None,
) -> VerificationResult:
    """Produce exactly one verdict for one candidate.

    `source_responds` means *the fetch tier returned a payload for this
    candidate*. It says nothing about freshness, which is what `provenance`
    records: `REPLAYED` for a recorded fixture, `LIVE` for a payload fetched now.

    The distinction matters because "the payload said the date is in the future"
    is a fact about the payload. "The page is still up" is a claim about the
    web, and a replay cannot support it. The verdict reasons below say which one
    was actually established.
    """
    clock = now if now is not None else now_utc()
    checked_at = verified_at if verified_at is not None else now_utc()

    listing = _listing(candidate, UNVERIFIED, checked_at)

    if not source_responds:
        return _result(listing, UNVERIFIED, "source did not respond")
    close = candidate.registration_close
    if close is None:
        return _result(listing, UNVERIFIED, "registration close could not be read")
    if close.tzinfo is None:
        return _result(listing, UNVERIFIED, "registration close carries no timezone")
    if close <= clock:
        return _result(listing, CLOSED, "registration has passed")
    if candidate.mode is None:
        return _result(listing, UNVERIFIED, "page stated no mode")
    if provenance == LIVE:
        return _result(listing, LIVE, "source responded, deadline future, mode present")
    return _result(
        listing,
        LIVE,
        "recorded payload replayed: deadline future, mode present. "
        "Not a live source check.",
    )


def verify_crawl(
    candidates,
    *,
    now: datetime | None = None,
    source_responds=None,
    provenance: str = REPLAYED,
    verified_at: datetime | None = None,
) -> list[VerificationResult]:
    """Verify a whole candidate set. Every candidate gets exactly one verdict.

    A candidate is never dropped here: an unreachable source yields
    `unverified`, not silence.

    Defaults to `provenance=REPLAYED`, so the crawl's default reason cannot
    read as a live check. Slice 1 has no live transport; when one lands it
    passes `provenance=LIVE` explicitly.
    """
    responds = source_responds or (lambda _candidate: True)
    return [
        verify(
            candidate,
            source_responds=responds(candidate),
            provenance=provenance,
            now=now,
            verified_at=verified_at,
        )
        for candidate in candidates
    ]


def _listing(candidate: Candidate, verdict: str, verified_at: datetime) -> Listing:
    return Listing(
        candidate_title=candidate.title,
        source_url=candidate.source_url,
        verdict=verdict,
        verified_at=verified_at,
        crawler=candidate.crawler,
    )


def _result(listing: Listing, verdict: str, reason: str) -> VerificationResult:
    return VerificationResult(
        listing=Listing(
            candidate_title=listing.candidate_title,
            source_url=listing.source_url,
            verdict=verdict,
            verified_at=listing.verified_at,
            crawler=listing.crawler,
        ),
        reason=reason,
    )


__all__ = ["VerificationResult", "verify", "verify_crawl", "LIVE", "UNVERIFIED", "CLOSED"]
