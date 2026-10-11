"""Unstop adapter: replay a recorded listing payload, extract every candidate.

Unstop's listing is a public JSON endpoint, so the payload *is* the page: one
JSON document, `data.data[]` holding every result the platform returned.
Extraction here reads candidates only. It never decides liveness — the
platform's `status` and `regn_open` flags are ignored outright, because a
recorded closed page still carries `status: "LIVE"` and `regn_open: 1`
(`fixtures/README.md`); only the registration-close date decides anything,
and that decision is verification's (ticket 04), not extraction's.

Every field the dashboard and later stages need is read, whether or not it is
present: a record with no team-size rule yields no team-size rule, and a
record with an empty prize summary yields an empty prize summary — never a
default, never an invented value (`Candidate.has` distinguishes read from
stuffed).

Dates arrive with a `+05:30` offset and are normalised to UTC at extraction
(ADR-0013). A timestamp with no stated zone cannot be normalised and is left
unread rather than guessed at.

The known-good baseline this adapter is validated against lives in
`tests/baselines/unstop-hackathons-open.json` (ticket 03, ADR-0015).
"""
from __future__ import annotations

import json
from collections.abc import Iterable
from datetime import datetime, timezone
from pathlib import Path

from ..candidate import VALID_MODES, Candidate, make_candidate
from ..scraper import Scraper

#: Unstop's origin, used when a record spells its own URL as a relative path.
UNSTOP_ORIGIN = "https://unstop.com/"

#: Prize rows name their currency as a Font Awesome icon key; the dashboard
#: needs the symbol. Anything unmapped keeps no symbol rather than a guess.
_CURRENCY_SYMBOLS = {
    "fa-rupee": "\u20b9",
    "fa-dollar": "$",
    "fa-euro": "\u20ac",
    "fa-pound": "\u00a3",
}

_RESULTS_KEY = ("data", "data")


class UnstopScraper(Scraper):
    """One platform's listing behind the scraper interface."""

    name = "unstop"

    def fetch(self, source: Path | str) -> bytes:
        """Return the raw payload for one recorded listing page.

        Network transport (the GET itself) is the Scout's fetch tier and is
        not this adapter's concern: this reads the recorded payload bytes, so
        replaying a fixture needs no network (ticket 08's "no network" rule).
        """
        return Path(source).read_bytes()

    def extract(self, payload: bytes) -> Iterable[Candidate]:
        """Produce candidates only — no claim about whether any is live."""
        document = json.loads(payload)
        records = _records(document)
        if not isinstance(records, list):
            return []
        return [_candidate(record) for record in records if isinstance(record, dict)]

    def run(self, source: Path | str) -> list[Candidate]:
        return super().run(source)


def _records(document: object) -> object:
    """Walk to the results list: Unstop wraps it in `data.data[]`."""
    node = document
    for key in _RESULTS_KEY:
        if not isinstance(node, dict) or key not in node:
            return []
        node = node[key]
    return node


def _candidate(record: dict) -> Candidate:
    requirements = record.get("regnRequirements") or {}

    title = record.get("title")
    if not isinstance(title, str):
        # Every result carries a title; without one the record is not a
        # candidate. Titles are kept verbatim — the platform stated them.
        title = ""

    return make_candidate(
        title=title,
        source_url=_source_url(record),
        registration_close=_instant(requirements.get("end_regn_dt")),
        mode=_mode(record),
        crawler=UnstopScraper.name,
        prize_summary=_prize_summary(record.get("prizes")),
        team_size_rule=_team_size_rule(requirements),
        eligibility_rules=_eligibility_rules(record.get("filters")),
        registration_open=_instant(requirements.get("start_regn_dt")),
    )


def _source_url(record: dict) -> str:
    """The absolute URL the fixture provides, never a relative path."""
    seo_url = record.get("seo_url")
    if isinstance(seo_url, str) and seo_url.strip():
        return seo_url
    public_url = record.get("public_url")
    if isinstance(public_url, str) and public_url.strip():
        # A record that spells its own path still needs an absolute source.
        return UNSTOP_ORIGIN + public_url.lstrip("/")
    return ""


def _mode(record: dict) -> str | None:
    """Mode is the platform's region field, or nothing.

    A region outside the three known modes (one record in the past fixture
    reads `india`) is not a mode; extraction leaves it unread rather than
    mapping it onto something it is not.
    """
    region = record.get("region")
    if isinstance(region, str) and region in VALID_MODES:
        return region
    return None


def _instant(value: object) -> datetime | None:
    """Parse a stated instant and normalise it to UTC (ADR-0013).

    Returns None for an absent, blank, unparseable, or zone-less timestamp —
    extraction does not guess a zone, and a date it cannot normalise is
    verification's `unverified`, never a default.
    """
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        parsed = datetime.fromisoformat(value.strip())
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return None
    return parsed.astimezone(timezone.utc)


def _prize_summary(prizes: object) -> str:
    """The prize text as stated, per rank, or the empty string.

    An empty prize block is an empty prize summary, not an error and not an
    invented value. Text is kept verbatim — the dashboard shows what the
    platform promised.
    """
    if not isinstance(prizes, list):
        return ""
    rows = []
    for prize in prizes:
        if not isinstance(prize, dict):
            continue
        parts = []
        cash = prize.get("cash")
        if isinstance(cash, (int, float)) and not isinstance(cash, bool):
            symbol = _CURRENCY_SYMBOLS.get(prize.get("currency"), "")
            parts.append(f"{symbol}{cash:,}")
        others = prize.get("others")
        if isinstance(others, str) and others.strip():
            parts.append(others.strip())
        if not parts and prize.get("certificate"):
            parts.append("Certificate")
        if not parts:
            continue
        rank = prize.get("rank")
        row = f"{rank}: " if isinstance(rank, str) and rank.strip() else ""
        rows.append(row + (parts[0] if len(parts) == 1 else " \u2014 ".join(parts)))
    return "; ".join(rows)


def _team_size_rule(requirements: dict) -> str | None:
    """The team-size rule as stated, or absent when the record has none."""
    minimum = requirements.get("min_team_size")
    maximum = requirements.get("max_team_size")
    if isinstance(minimum, int) and isinstance(maximum, int):
        if minimum == maximum:
            return f"{minimum} participant" if minimum == 1 else f"{minimum} participants"
        return f"{minimum}-{maximum} participants"
    if isinstance(maximum, int):
        return f"up to {maximum} participants"
    if isinstance(minimum, int):
        return f"at least {minimum} participants"
    return None


def _eligibility_rules(filters: object) -> tuple[str, ...] | None:
    """Typed eligibility rules, in the platform's order, or absent when none."""
    if not isinstance(filters, list):
        return None
    names = tuple(
        entry["name"].strip()
        for entry in filters
        if isinstance(entry, dict)
        and entry.get("type") == "eligible"
        and isinstance(entry.get("name"), str)
        and entry["name"].strip()
    )
    return names or None
