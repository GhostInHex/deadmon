"""Contract: the verdict model is exhaustive; every verdict carries verified_at."""
import pytest

from deadmon.verdict import CLOSED, LIVE, UNVERIFIED, VERDICTS, Listing, now_utc


def test_verdict_model_is_exhaustive():
    assert VERDICTS == (LIVE, UNVERIFIED, CLOSED) == ("live", "unverified", "closed")


def test_every_verdict_carries_verified_at():
    for verdict in VERDICTS:
        listing = Listing(
            candidate_title="T", source_url="https://example.test/x", verdict=verdict,
            verified_at=now_utc(),
        )
        assert listing.verified_at is not None
        assert listing.verified_at.tzinfo is not None


def test_unknown_verdict_rejected_and_naive_verified_at_rejected():
    with pytest.raises(ValueError):
        Listing(candidate_title="T", source_url="u", verdict="verified", verified_at=now_utc())
    from datetime import datetime

    with pytest.raises(ValueError):
        Listing(candidate_title="T", source_url="u", verdict="live", verified_at=datetime.now())
