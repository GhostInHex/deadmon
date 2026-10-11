"""Ticket 04 — verification yields exactly one verdict and fails closed.

Transport failures are *declared test doubles*: no test here touches the
network, and the doubles are named as doubles in their test names.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from deadmon.adapters.unstop import UnstopScraper
from deadmon.candidate import make_candidate
from deadmon.verdict import CLOSED, LIVE, UNVERIFIED, VERDICTS
from deadmon.verification import VerificationResult, verify, verify_crawl

from tests.conftest import (
    CLOSED_FIXTURE,
    KNOWN_GOOD_FIXTURE,
    PAST_FIXTURE,
    UNVERIFIED_DOUBLE,
)

NOW = datetime(2026, 10, 11, tzinfo=timezone.utc)
FUTURE = NOW + timedelta(days=30)
PAST = NOW - timedelta(days=1)


def candidate(close, *, mode="online", crawler="unstop"):
    return make_candidate(
        title="T",
        source_url="https://unstop.com/x",
        registration_close=close,
        mode=mode,
        crawler=crawler,
    )


def test_the_verdict_model_is_exhaustive():
    assert set(VERDICTS) == {"live", "unverified", "closed"}
    assert (LIVE, UNVERIFIED, CLOSED) == ("live", "unverified", "closed")


def test_live_requires_all_three_conditions():
    assert verify(candidate(FUTURE), now=NOW).verdict == LIVE


def test_unverified_when_the_deadline_cannot_be_read():
    result = verify(candidate(None), now=NOW)
    assert result.verdict == UNVERIFIED
    assert result.listing.verdict == UNVERIFIED
    assert "could not be read" in result.reason


def test_unverified_when_the_page_states_no_mode():
    result = verify(candidate(FUTURE, mode=None), now=NOW)
    assert result.verdict == UNVERIFIED
    assert result.reason == "page stated no mode"


def test_closed_when_registration_has_passed():
    result = verify(candidate(PAST), now=NOW)
    assert result.verdict == CLOSED
    assert result.listing.verdict == CLOSED


def test_verdict_never_read_from_platform_status_flags():
    """Ticket 02's trap: `status: "LIVE"` / `regn_open: 1` sit on closed records.

    The candidate contract carries neither attribute, so the platform's own
    flags cannot reach this stage at all — only the date decides.
    """
    subject = candidate(FUTURE)
    assert not hasattr(subject, "status")
    assert not hasattr(subject, "regn_open")
    assert verify(subject, now=NOW).verdict == LIVE
    assert verify(candidate(PAST), now=NOW).verdict == CLOSED


def test_a_past_close_outranks_an_absent_mode():
    """A parsed date already gone is positive evidence registration has passed."""
    result = verify(candidate(PAST, mode=None), now=NOW)
    assert result.verdict == CLOSED


def test_a_deadline_is_never_inferred_or_defaulted():
    unset = verify(candidate(None), now=NOW)
    repeated = verify(candidate(None), now=NOW + timedelta(days=1), verified_at=NOW)
    assert unset.verdict == repeated.verdict == UNVERIFIED
    assert not candidate(None).has("registration_open")


def test_every_verdict_carries_verified_at():
    for subject in (candidate(FUTURE), candidate(FUTURE, mode=None), candidate(PAST)):
        listing = verify(subject, now=NOW, verified_at=NOW).listing
        assert listing.verified_at == NOW
        assert listing.verified_at.tzinfo is not None


def test_the_verification_clock_is_injected_never_assumed():
    """The boundary instant itself is closed: a deadline that has just arrived."""
    assert verify(candidate(FUTURE), now=NOW).verdict == LIVE
    assert verify(candidate(FUTURE), now=FUTURE).verdict == CLOSED
    assert verify(candidate(FUTURE), now=FUTURE + timedelta(seconds=1)).verdict == CLOSED


def test_transport_failure_is_a_declared_double_double_not_a_network_test():
    """Named double: `source_responds=False` stands in for an unreachable page."""
    responds = lambda _candidate: False  # declared double: no transport
    results = verify_crawl([candidate(FUTURE)], source_responds=responds, now=NOW)
    assert [r.verdict for r in results] == [UNVERIFIED]
    assert results[0].reason == "source did not respond"


def test_the_declared_double_fixture_verifies_unverified():
    """`hackathons-unverified.json` is a declared double, not a recording."""
    double = UnstopScraper().run(UNVERIFIED_DOUBLE)
    assert [c.registration_close for c in double] == [None] * 3
    assert [r.verdict for r in verify_crawl(double, now=NOW)] == [UNVERIFIED] * 3


def test_the_recorded_closed_pages_verify_closed_both_ways():
    for fixture in (CLOSED_FIXTURE, PAST_FIXTURE):
        results = verify_crawl(UnstopScraper().run(fixture), now=NOW)
        assert results, fixture
        assert {r.verdict for r in results} == {CLOSED}, fixture


def test_the_recorded_healthy_page_verifies_live():
    results = verify_crawl(UnstopScraper().run(KNOWN_GOOD_FIXTURE), now=NOW)
    assert len(results) == 25
    assert {r.verdict for r in results} == {LIVE}


def test_an_unverified_verdict_is_re_verified_on_the_next_crawl():
    """Never cached as fact, never promoted without a fresh check."""
    first = verify(candidate(FUTURE, mode=None), now=NOW, verified_at=NOW)
    assert first.verdict == UNVERIFIED
    second = verify(candidate(FUTURE), now=NOW, verified_at=NOW + timedelta(minutes=1))
    assert second.verdict == LIVE
    assert second.listing.verified_at > first.listing.verified_at


def test_a_closed_verdict_is_terminal_but_keeps_its_row():
    result = verify(candidate(PAST), now=NOW, verified_at=NOW)
    assert result.verdict == CLOSED
    assert result.listing.source_url == "https://unstop.com/x"
    assert result.listing.candidate_title == "T"


def test_unverified_is_never_counted_as_live():
    subjects = [
        candidate(FUTURE),
        candidate(FUTURE, mode=None),
        candidate(None),
        candidate(PAST),
    ]
    assert [r.verdict for r in verify_crawl(subjects, now=NOW)] == [
        LIVE,
        UNVERIFIED,
        UNVERIFIED,
        CLOSED,
    ]


def test_verification_is_platform_agnostic():
    verdicts = {
        verify(candidate(FUTURE, crawler=crawler), now=NOW).verdict
        for crawler in ("unstop", "devfolio", "devpost", "hack2skill")
    }
    assert verdicts == {LIVE}


def test_one_candidate_in_one_verdict_out():
    result = verify(candidate(FUTURE), now=NOW)
    assert isinstance(result, VerificationResult)
    assert result.verdict == result.listing.verdict
    assert result.reason


def test_reachable_payload_replayed_offline():
    """`source_responds` defaults to True; the payload is replayed, not fetched."""
    payload = KNOWN_GOOD_FIXTURE.read_bytes()
    results = verify_crawl(UnstopScraper().extract(payload), now=NOW)
    assert {r.verdict for r in results} == {LIVE}
