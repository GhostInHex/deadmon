"""Unstop adapter: the code that knows one platform's payload.

Unstop publishes its listing grid as a public JSON endpoint, so the adapter is
a plain payload reader — no rendered DOM, no hydration wait. It implements
fetch + extract behind the scraper interface and knows nothing about
verification, dedupe or alerts.
"""
from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime, timezone
import json
from pathlib import Path

from ..candidate import Candidate, VALID_MODES, make_candidate
from ..scraper import Scraper


class UnstopScraper(Scraper):
    """One crawl run's worth of Unstop's public listing payload."""

    name = "unstop"

    def fetch(self, source: Path | str) -> bytes:
        """Read the recorded payload. No transport in Slice 1."""
        path = Path(source)
        if path.suffix.lower() in {".json"} and path.exists():
            return path.read_bytes()
        raise FileNotFoundError(f"Unstop adapter replays a recorded JSON payload, got {source!r}")

    def extract(self, payload: bytes) -> Iterable[Candidate]:
        page = json.loads(payload.decode("utf-8"))
        for record in page.get("data", {}).get("data", []):
            candidate = self._extract_record(record)
            if candidate is not None:
                yield candidate

    # -- extraction rules -------------------------------------------------

    def _extract_record(self, record: dict) -> Candidate | None:
        title = (record.get("title") or "").strip()
        if not title:
            return None
        return make_candidate(
            title=title,
            source_url=record.get("seo_url") or "",
            registration_close=_parse_datetime(
                (record.get("regnRequirements") or {}).get("end_regn_dt")
            ),
            mode=_mode(record.get("region")),
            crawler=self.name,
            prize_summary=_prize_summary(record.get("prizes")),
            team_size_rule=_team_size_rule(record.get("regnRequirements") or {}),
            eligibility_rules=_eligibility_rules(record.get("filters")),
            registration_open=_parse_datetime(
                (record.get("regnRequirements") or {}).get("start_regn_dt")
            ),
        )


def _parse_datetime(value) -> datetime | None:
    """ISO 8601 with offset, normalised to UTC at extraction (ADR-0013).

    A date that cannot be parsed stays absent — never guessed, never carried
    over, never defaulted. Verification fails closed on it later.
    """
    if not value or not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.strip())
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return None
    return parsed.astimezone(timezone.utc)


def _mode(region) -> str | None:
    if region in VALID_MODES:
        return region
    return None


def _team_size_rule(requirements: dict) -> str | None:
    smallest = requirements.get("min_team_size")
    largest = requirements.get("max_team_size")
    if not smallest or not largest:
        return None
    if smallest == largest:
        return f"{smallest} member{'s' if smallest > 1 else ''}"
    return f"{smallest}–{largest} members"


def _eligibility_rules(filters) -> tuple[str, ...]:
    if not filters:
        return ()
    return tuple(f["name"] for f in filters if f.get("type") == "eligible" and f.get("name"))


def _prize_summary(prizes) -> str:
    """Empty when the platform records no prizes — not an error, not invented."""
    if not prizes:
        return ""
    parts = []
    for prize in prizes:
        cash = prize.get("cash")
        rank = (prize.get("rank") or "").strip()
        if cash:
            amount = f"₹{int(cash):,}"
            parts.append(f"{rank} {amount}".strip() if rank else amount)
        for label, value in (("certificate", prize.get("certificate")),):
            if value:
                parts.append(label)
        if prize.get("others"):
            parts.append(str(prize["others"]).strip())
    return "; ".join(dict.fromkeys(p for p in parts if p))
