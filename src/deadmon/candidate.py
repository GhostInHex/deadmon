"""Candidate record: what extraction produces before anything is proven.

One documented shape: title, source URL, registration close, and mode,
plus optional fields that may legitimately be absent. An absent optional
field stays absent — never defaulted, guessed, or carried over.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


REQUIRED_CANDIDATE_FIELDS = ("title", "source_url", "registration_close", "mode")
OPTIONAL_CANDIDATE_FIELDS = (
    "prize_summary",
    "team_size_rule",
    "eligibility_rules",
    "registration_open",
)

VALID_MODES = ("online", "hybrid", "offline")


@dataclass(frozen=True)
class Candidate:
    title: str
    source_url: str
    registration_close: datetime | None
    mode: str | None
    prize_summary: str | None = None
    team_size_rule: str | None = None
    eligibility_rules: tuple[str, ...] | None = None
    registration_open: datetime | None = None
    crawler: str = "unstop"
    _optional_present: frozenset[str] = field(default=frozenset(), compare=False, repr=False)

    def has(self, name: str) -> bool:
        """True when an optional field was actually read from the source."""
        return name in self._optional_present


def make_candidate(
    *,
    title: str,
    source_url: str,
    registration_close: datetime | None,
    mode: str | None,
    crawler: str = "unstop",
    **optionals,
) -> Candidate:
    """Build a candidate; only explicitly passed optionals count as present."""
    unknown = set(optionals) - set(OPTIONAL_CANDIDATE_FIELDS)
    if unknown:
        raise TypeError(f"unknown candidate fields: {sorted(unknown)}")
    present = frozenset(k for k, v in optionals.items() if v is not None)
    return Candidate(
        title=title,
        source_url=source_url,
        registration_close=registration_close,
        mode=mode,
        crawler=crawler,
        _optional_present=present,
        **{k: v for k, v in optionals.items() if k in OPTIONAL_CANDIDATE_FIELDS},
    )
