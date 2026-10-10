"""Ticket 03 — the Unstop adapter extracts the full candidate set.

Asserts on the candidates out, never on which JSON key was read: the recorded
payload is compared against what the adapter produces.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone

import pytest

from deadmon.adapters.unstop import UnstopScraper
from deadmon.candidate import VALID_MODES, make_candidate

from tests.conftest import KNOWN_GOOD_FIXTURE

# The baseline this adapter is later validated against (ADR-0015): a proposal
# must reproduce this count and these populated fields, not merely return
# something non-empty.
KNOWN_GOOD_CANDIDATE_COUNT = 25

scraper = UnstopScraper()


def payload() -> dict:
    return json.loads(KNOWN_GOOD_FIXTURE.read_text(encoding="utf-8"))


def records() -> list[dict]:
    return payload()["data"]["data"]


def candidates() -> list:
    return scraper.run(KNOWN_GOOD_FIXTURE)


def test_every_record_in_the_fixture_yields_a_candidate():
    assert len(candidates()) == KNOWN_GOOD_CANDIDATE_COUNT == len(records())


def test_required_fields_are_populated_for_the_whole_set():
    for candidate in candidates():
        assert candidate.title.strip(), candidate
        assert candidate.source_url.startswith("https://"), candidate
        assert candidate.mode in VALID_MODES, candidate
        assert candidate.registration_close is not None, candidate


def test_registration_close_comes_from_the_registration_requirements():
    """Never the top-level event date, which carries a different meaning."""
    differing = 0
    for record, candidate in zip(records(), candidates()):
        stated = record["regnRequirements"]["end_regn_dt"]
        event_end = record["end_date"]
        assert candidate.registration_close == datetime.fromisoformat(stated).astimezone(timezone.utc)
        if datetime.fromisoformat(stated).astimezone(timezone.utc) != datetime.fromisoformat(
            event_end
        ).astimezone(timezone.utc):
            differing += 1
    # The fixture must actually separate the two dates, or this test proves nothing.
    assert differing > 0, "fixture's registration close and event end never differ"


def test_dates_are_normalised_to_utc_at_extraction():
    for candidate in candidates():
        assert candidate.registration_close.tzinfo == timezone.utc
        assert candidate.registration_close.utcoffset().total_seconds() == 0
    raw = [r["regnRequirements"]["end_regn_dt"] for r in records()]
    assert all(date.endswith("+05:30") for date in raw), "fixture no longer carries +05:30"


def test_source_url_is_the_absolute_form():
    for record, candidate in zip(records(), candidates()):
        assert candidate.source_url == record["seo_url"]
        assert candidate.source_url.startswith("https://unstop.com/")
        assert not candidate.source_url.startswith(("http://", "unstop.com"))


def test_mode_is_read_from_the_platform_region_field():
    assert {c.mode for c in candidates()} <= set(VALID_MODES)
    by_region = {r["region"] for r in records()}
    assert {c.mode for c in candidates()} == by_region


def test_extraction_never_decides_liveness_from_platform_flags():
    """`status` and `regn_open` read live on records that have closed.

    A record carrying status CLOSED and regn_open 0, but a future registration
    close, must extract exactly as its healthy twin does.
    """
    healthy = records()[0]

    def extract(record):
        return list(scraper.extract(json.dumps({"data": {"data": [record]}}).encode()))

    baseline = extract(healthy)[0]
    poisoned = dict(healthy)
    poisoned["status"] = "CLOSED"
    poisoned["regn_open"] = 0
    result = extract(poisoned)[0]

    assert result.registration_close == baseline.registration_close
    assert result.mode == baseline.mode
    assert result.source_url == baseline.source_url


def test_extraction_produces_candidates_only():
    for candidate in candidates():
        assert not hasattr(candidate, "verdict"), "extraction made a liveness claim"
        assert not hasattr(candidate, "verified_at")


def test_prize_summary_present_or_empty_never_invented():
    empty = [c for c in candidates() if c.prize_summary == ""]
    populated = [c for c in candidates() if c.prize_summary]
    # 8 of 25 records carry `prizes: []` in the recorded page.
    assert len(empty) == sum(1 for r in records() if not r["prizes"])
    assert len(empty) == 8
    for candidate in empty:
        assert candidate.has("prize_summary"), "empty prize summary must still be read"
    for candidate in populated:
        assert candidate.has("prize_summary")
    assert not any("₹0" in (c.prize_summary or "") for c in candidates())


def test_team_size_rule_read_when_present_absent_when_not():
    for record, candidate in zip(records(), candidates()):
        requirements = record["regnRequirements"]
        if requirements.get("min_team_size") and requirements.get("max_team_size"):
            assert candidate.has("team_size_rule"), candidate
            assert candidate.team_size_rule
        else:
            assert not candidate.has("team_size_rule"), candidate
            assert candidate.team_size_rule is None


def test_eligibility_rules_read_when_present_absent_when_not():
    eligible = {f["name"] for f in records()[0]["filters"] if f.get("type") == "eligible"}
    assert candidates()[0].has("eligibility_rules")
    assert set(candidates()[0].eligibility_rules) == eligible
    assert not any(
        f for r in records() for f in r["filters"] if f.get("type") != "eligible"
    ), "fixture now carries non-eligible filter rows; eligibility rule changed shape"


def test_registration_open_is_an_optional_field_that_may_be_absent():
    for record, candidate in zip(records(), candidates()):
        if record["regnRequirements"].get("start_regn_dt"):
            assert candidate.has("registration_open")
            assert candidate.registration_open.tzinfo == timezone.utc


def test_absent_optional_field_stays_absent_for_a_bare_record():
    bare = {
        "title": "  A bare record  ",
        "seo_url": "https://unstop.com/hackathons/bare-1",
        "region": "online",
        "status": "LIVE",
        "regn_open": 1,
        "end_date": "2027-01-01T00:00:00+05:30",
        "prizes": [],
        "filters": [],
        "regnRequirements": {
            "end_regn_dt": "2027-01-02T23:59:00+05:30",
            "start_regn_dt": None,
            "min_team_size": None,
            "max_team_size": None,
        },
    }
    candidate = list(scraper.extract(json.dumps({"data": {"data": [bare]}}).encode()))[0]
    assert candidate.title == "A bare record"
    assert candidate.registration_close == datetime(2027, 1, 2, 18, 29, tzinfo=timezone.utc)
    assert candidate.prize_summary == ""
    assert candidate.has("prize_summary")
    assert not candidate.has("team_size_rule")
    assert not candidate.has("registration_open")
    assert candidate.eligibility_rules == ()


def test_an_unusable_date_stays_absent_rather_than_guessed():
    """Fail closed: extraction never invents a deadline it could not read."""
    record = dict(records()[0])
    record["regnRequirements"] = dict(record["regnRequirements"], end_regn_dt="TBA")
    candidate = list(scraper.extract(json.dumps({"data": {"data": [record]}}).encode()))[0]
    assert candidate.registration_close is None


def test_replaying_the_fixture_requires_no_network():
    """`fetch` is given a path; nothing here resolves a hostname."""
    with pytest.raises(Exception):
        socket_guard = __import__("socket")
        socket_guard.getaddrinfo("unstop.com", 443)
    assert scraper.fetch(KNOWN_GOOD_FIXTURE) == KNOWN_GOOD_FIXTURE.read_bytes()


def test_a_candidate_is_built_through_the_shared_contract():
    candidate = make_candidate(
        title="T",
        source_url="https://unstop.com/x",
        registration_close=datetime(2027, 1, 1, tzinfo=timezone.utc),
        mode="online",
        crawler="unstop",
        prize_summary="",
    )
    assert candidate.crawler == "unstop"
    assert candidate.has("prize_summary")
