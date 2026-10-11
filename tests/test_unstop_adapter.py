"""Contract: the Unstop adapter replays recorded fixtures and extracts them in full.

These tests feed a fixture through the adapter and assert on the candidates
that come out — never on which JSON key the adapter happened to read. The
targets come from `tests/baselines/unstop-hackathons-open.json`, the known-good
baseline (ticket 03, ADR-0015); the fixture bytes themselves are never edited.
"""
from __future__ import annotations

import json
import socket
from datetime import datetime, timezone
from pathlib import Path

from deadmon.candidate import VALID_MODES, OPTIONAL_CANDIDATE_FIELDS
from deadmon.crawlers.unstop import UnstopScraper

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures" / "unstop"
OPEN = FIXTURES / "hackathons-open.json"
CLOSED = FIXTURES / "hackathons-closed.json"
PAST = FIXTURES / "hackathons-past.json"
BASELINE = Path(__file__).resolve().parent / "baselines" / "unstop-hackathons-open.json"


def _records(payload: bytes) -> list[dict]:
    return json.loads(payload)["data"]["data"]


def _utc(instant: str) -> datetime:
    return datetime.fromisoformat(instant).astimezone(timezone.utc)


def _candidates(path: Path) -> list:
    return UnstopScraper().run(path)


def _by_source_url(candidates) -> dict[str, object]:
    return {c.source_url: c for c in candidates}


# --------------------------------------------------------------------------
# The whole candidate set, not just enough fields to make one row work
# --------------------------------------------------------------------------


def test_all_25_fixture_candidates_are_extracted():
    baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
    candidates = _candidates(OPEN)
    assert len(candidates) == 25
    assert len(candidates) == baseline["count"]


def test_required_fields_populated_for_every_candidate():
    candidates = _candidates(OPEN)
    populated = {
        name: sum(1 for c in candidates if getattr(c, name) is not None)
        for name in ("title", "source_url", "registration_close", "mode")
    }
    assert populated == {"title": 25, "source_url": 25, "registration_close": 25, "mode": 25}


def test_the_source_url_is_the_absolute_form_the_fixture_provides():
    records = {r["seo_url"]: r for r in _records(OPEN.read_bytes())}
    candidates = _by_source_url(_candidates(OPEN))
    assert set(candidates) == set(records)  # one candidate per fixture record
    for c in candidates.values():
        assert c.source_url.startswith("https://unstop.com/")
        assert c.source_url == records[c.source_url]["seo_url"]
        assert not c.source_url.startswith("/")  # never the relative path


# --------------------------------------------------------------------------
# Registration close: the registration-requirements block, never the event date
# --------------------------------------------------------------------------


def test_registration_close_is_read_from_the_registration_requirements_block():
    records = _records(OPEN.read_bytes())
    candidates = _by_source_url(_candidates(OPEN))
    read_from_event_date = 0
    for record in records:
        candidate = candidates[record["seo_url"]]
        expected = _utc(record["regnRequirements"]["end_regn_dt"])
        assert candidate.registration_close == expected
        if record["regnRequirements"]["end_regn_dt"] != record["end_date"]:
            # the top-level event date carries a different meaning
            assert candidate.registration_close != _utc(record["end_date"])
            read_from_event_date += 1
    assert read_from_event_date > 0  # the fixture really does distinguish the two


def test_dates_carry_their_offset_and_are_normalised_to_utc():
    candidates = _candidates(OPEN)
    for c in candidates:
        for instant in (c.registration_close, c.registration_open):
            assert instant is not None
            assert instant.tzinfo is not None
            assert instant.utcoffset().total_seconds() == 0


def test_a_stated_plus_0530_instant_normalises_to_utc():
    # Declared payload, not a fixture: one record, one stated +05:30 close.
    payload = {
        "data": {
            "data": [
                {
                    "title": "Declared",
                    "seo_url": "https://unstop.com/hackathons/declared-1",
                    "region": "online",
                    "prizes": [],
                    "filters": [],
                    "regnRequirements": {
                        "start_regn_dt": "2026-10-01T00:00:00+05:30",
                        "end_regn_dt": "2026-10-13T15:02:23+05:30",
                    },
                }
            ]
        }
    }
    (candidate,) = UnstopScraper().extract(json.dumps(payload).encode("utf-8"))
    assert candidate.registration_close == datetime(2026, 10, 13, 9, 32, 23, tzinfo=timezone.utc)
    assert candidate.registration_open == datetime(2026, 9, 30, 18, 30, tzinfo=timezone.utc)


def test_an_unusable_date_is_left_unread_not_guessed():
    # Declared double: an absent date and a "TBA" date are both unread.
    payload = {
        "data": {
            "data": [
                {
                    "title": "TBA close",
                    "seo_url": "https://unstop.com/hackathons/tba-1",
                    "region": "online",
                    "regnRequirements": {"end_regn_dt": "TBA", "start_regn_dt": "nonsense"},
                }
            ]
        }
    }
    (candidate,) = UnstopScraper().extract(json.dumps(payload).encode("utf-8"))
    assert candidate.registration_close is None
    assert candidate.registration_open is None
    assert not candidate.has("registration_open")


# --------------------------------------------------------------------------
# Mode, team size, eligibility, prizes
# --------------------------------------------------------------------------


def test_mode_is_read_from_the_platforms_region_field():
    records = _records(OPEN.read_bytes())
    candidates = _by_source_url(_candidates(OPEN))
    modes = {}
    for record in records:
        mode = candidates[record["seo_url"]].mode
        assert mode in VALID_MODES
        modes[mode] = modes.get(mode, 0) + 1
    expected = {}
    for record in records:
        if record["region"] in VALID_MODES:
            expected[record["region"]] = expected.get(record["region"], 0) + 1
    assert modes == expected
    assert set(modes) == {"online", "hybrid", "offline"}


def test_team_size_rule_and_eligibility_rules_are_extracted_when_present():
    records = _records(OPEN.read_bytes())
    candidates = _by_source_url(_candidates(OPEN))
    for record in records:
        candidate = candidates[record["seo_url"]]
        minimum = record["regnRequirements"]["min_team_size"]
        maximum = record["regnRequirements"]["max_team_size"]
        assert candidate.has("team_size_rule")
        assert str(minimum) in candidate.team_size_rule
        assert str(maximum) in candidate.team_size_rule
        expected = tuple(
            f["name"]
            for f in record["filters"]
            if f["type"] == "eligible"
        )
        assert candidate.eligibility_rules == expected


def test_team_size_rule_and_eligibility_are_absent_when_the_record_has_none():
    # Declared double: one record with no team size, no eligibility filters.
    payload = {
        "data": {
            "data": [
                {
                    "title": "Bare record",
                    "seo_url": "https://unstop.com/hackathons/bare-1",
                    "region": "offline",
                    "regnRequirements": {"end_regn_dt": "2026-10-13T15:02:23+05:30"},
                }
            ]
        }
    }
    (candidate,) = UnstopScraper().extract(json.dumps(payload).encode("utf-8"))
    assert candidate.team_size_rule is None
    assert not candidate.has("team_size_rule")
    assert candidate.eligibility_rules is None
    assert not candidate.has("eligibility_rules")
    assert candidate.prize_summary == ""


def test_an_empty_prize_summary_stays_empty_and_is_never_invented():
    records = _records(OPEN.read_bytes())
    candidates = _by_source_url(_candidates(OPEN))
    empty = [r for r in records if not r["prizes"]]
    rich = [r for r in records if r["prizes"]]
    assert empty and rich  # the fixture has both shapes
    for record in empty:
        summary = candidates[record["seo_url"]].prize_summary
        assert summary == ""
        assert candidates[record["seo_url"]].has("prize_summary")
    for record in rich:
        assert candidates[record["seo_url"]].prize_summary != ""


# --------------------------------------------------------------------------
# Extraction produces candidates only; it decides nothing about liveness
# --------------------------------------------------------------------------


def test_the_candidate_record_carries_no_liveness_field():
    from dataclasses import fields

    names = {f.name for f in fields(type(_candidates(OPEN)[0]))}
    assert names & {"verdict", "live", "closed", "status", "is_live"} == set()
    assert set(names) >= {"title", "source_url", "registration_close", "mode"} | set(OPTIONAL_CANDIDATE_FIELDS)


def test_the_recorded_closed_page_still_reads_live_but_extraction_says_nothing():
    records = _records(CLOSED.read_bytes())
    assert len(records) == 24  # 24 is what the endpoint served
    # every record on that page still claims LIVE with registration open
    assert all(r["status"] == "LIVE" and r["regn_open"] == 1 for r in records)
    candidates = _candidates(CLOSED)
    assert len(candidates) == 24
    for c in candidates:
        assert c.title and c.source_url and c.mode in VALID_MODES
        assert c.registration_close is not None  # the date is read, not judged


def test_the_past_fixture_extracts_every_record_including_an_unknown_region():
    records = _records(PAST.read_bytes())
    candidates = _candidates(PAST)
    assert len(candidates) == len(records) == 25
    unknown = sum(1 for r in records if r["region"] not in VALID_MODES)
    assert unknown == 1
    assert sum(1 for c in candidates if c.mode is None) == unknown
    for c in candidates:
        assert c.mode is None or c.mode in VALID_MODES


# --------------------------------------------------------------------------
# The baseline and the network-free replay
# --------------------------------------------------------------------------


def test_extraction_reproduces_the_known_good_baseline():
    baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
    candidates = _candidates(OPEN)
    assert [c.title for c in candidates] == [c["title"] for c in baseline["candidates"]]
    for candidate, expected in zip(candidates, baseline["candidates"]):
        assert candidate.source_url == expected["source_url"]
        assert candidate.mode == expected["mode"]
        assert candidate.registration_close == datetime.fromisoformat(expected["registration_close"])
        assert candidate.registration_open == datetime.fromisoformat(expected["registration_open"])
        assert candidate.prize_summary == expected["prize_summary"]
        assert candidate.team_size_rule == expected["team_size_rule"]
        assert candidate.eligibility_rules == tuple(expected["eligibility_rules"])
        assert sorted(
            name for name in OPTIONAL_CANDIDATE_FIELDS if candidate.has(name)
        ) == expected["optional_present"]


def test_replaying_the_fixture_requires_no_network(monkeypatch):
    def _refuse(*args, **kwargs):
        raise AssertionError("the adapter must not touch the network")

    monkeypatch.setattr(socket.socket, "connect", _refuse)
    candidates = UnstopScraper().run(OPEN)
    assert len(candidates) == 25
