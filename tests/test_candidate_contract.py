"""Contract: the candidate record is one documented shape; absent stays absent."""
from datetime import datetime, timezone

from deadmon.candidate import (
    OPTIONAL_CANDIDATE_FIELDS,
    REQUIRED_CANDIDATE_FIELDS,
    make_candidate,
)


def test_candidate_contract_shape():
    assert REQUIRED_CANDIDATE_FIELDS == ("title", "source_url", "registration_close", "mode")
    assert set(OPTIONAL_CANDIDATE_FIELDS) == {
        "prize_summary",
        "team_size_rule",
        "eligibility_rules",
        "registration_open",
    }


def test_absent_optional_stays_absent():
    c = make_candidate(
        title="T",
        source_url="https://example.test/x",
        registration_close=datetime(2026, 11, 1, tzinfo=timezone.utc),
        mode="online",
    )
    for name in OPTIONAL_CANDIDATE_FIELDS:
        assert getattr(c, name) is None
        assert not c.has(name)
    # None passed explicitly is still absent, never defaulted
    c2 = make_candidate(
        title="T",
        source_url="https://example.test/x",
        registration_close=None,
        mode=None,
        prize_summary=None,
    )
    assert c2.prize_summary is None
    assert not c2.has("prize_summary")
