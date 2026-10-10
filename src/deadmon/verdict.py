"""Verdict model: exactly one of live / unverified / closed, always with verified_at.

- live: source responds, registration close parses to a real future date in
  a known timezone, and a mode is present. Enters the feed.
- unverified: indeterminate — unreachable, blocked, rate-limited, or the date
  is unusable. Never asserted as fact, never deleted; re-verified next crawl.
- closed: confirmed over — registration passed or event cancelled. Terminal;
  keeps its row, leaves the feed, cancels unsent alerts.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone


LIVE = "live"
UNVERIFIED = "unverified"
CLOSED = "closed"

VERDICTS = (LIVE, UNVERIFIED, CLOSED)


@dataclass(frozen=True)
class Listing:
    """A candidate carrying a verdict — one platform's source for a hackathon."""

    candidate_title: str
    source_url: str
    verdict: str
    verified_at: datetime
    crawler: str = "unstop"

    def __post_init__(self) -> None:
        if self.verdict not in VERDICTS:
            raise ValueError(f"verdict must be one of {VERDICTS}, got {self.verdict!r}")
        if self.verified_at.tzinfo is None:
            raise ValueError("verified_at must be timezone-aware")


def now_utc() -> datetime:
    return datetime.now(timezone.utc)
