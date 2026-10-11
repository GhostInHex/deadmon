"""Ticket 05 — the heal is proven twice: break, heal, second clean crawl, backfill.

Runs entirely offline against recorded fixtures in a scratch workspace, plus
assertions over the committed evidence pack in `docs/evidence/heal-001-unstop/`.

The break is a *constructed* snapshot (`fixtures/unstop-heal/`), declared as
such wherever it appears: Unstop did not change its layout overnight, so the
25-to-0 regression is staged, not recorded. The known-good fixture is never
touched. The proposal is a demo double — the real adapter is unchanged,
because no production code changes for a staged break.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from deadmon.adapters.unstop import UnstopScraper
from deadmon.crawl import crawl_one_fixture
from deadmon.heal.watch import detect_breaks
from deadmon.receipts import verify_receipt
from deadmon.storage import Store
from deadmon.verification import verify_crawl

from tests.conftest import KNOWN_GOOD_FIXTURE, REPO_ROOT

AS_OF = datetime(2026, 10, 11, tzinfo=timezone.utc)
HEAL_DIR = REPO_ROOT / "fixtures" / "unstop-heal"
SNAPSHOT = HEAL_DIR / "hackathons-open.v2-changed-layout.json"
EVIDENCE = REPO_ROOT / "docs" / "evidence" / "heal-001-unstop"


class HealedUnstopScraper(UnstopScraper):
    """Demo proposal double: the allowlist-scoped extraction-rule change.

    Reads the records under the new `data.results` key as well as the old
    `data.data` key. Selectors and extraction rules only — no new logic,
    no verification change, no other file touched (ADR-0018). Lives in the
    test, not in `src/`, because the break it heals is staged.
    """

    def extract(self, payload: bytes):
        page = json.loads(payload.decode("utf-8"))
        region = page.get("data", {})
        records = region.get("data") or region.get("results") or []
        for record in records:
            candidate = self._extract_record(record)
            if candidate is not None:
                yield candidate


def _workspace(tmp_path):
    for name in ("db", "traces", "receipts"):
        (tmp_path / name).mkdir()
    return tmp_path


def _crawl(scraper, fixture, workspace):
    return crawl_one_fixture(
        scraper,
        fixture,
        store=Store(workspace / "db" / "deadmon.db").open(),
        now=AS_OF,
        sink_dir=workspace / "traces",
        receipt_dir=workspace / "receipts",
    )


def test_the_known_good_fixture_is_untouched_and_still_yields_25(tmp_path):
    workspace = _workspace(tmp_path)
    outcome = _crawl(UnstopScraper(), KNOWN_GOOD_FIXTURE, workspace)
    assert outcome.candidates == 25
    assert outcome.live_found == 25


def test_the_changed_layout_snapshot_yields_zero_with_the_current_adapter():
    candidates = list(UnstopScraper().extract(SNAPSHOT.read_bytes()))
    assert candidates == []


def test_two_consecutive_zero_runs_fire_one_break_for_unstop(tmp_path):
    workspace = _workspace(tmp_path)
    first = _crawl(UnstopScraper(), SNAPSHOT, workspace)
    second = _crawl(UnstopScraper(), SNAPSHOT, workspace)
    assert (first.candidates, second.candidates) == (0, 0)

    with Store(workspace / "db" / "deadmon.db").open() as store:
        rows = store.run_history()
    (break_,) = detect_breaks(rows)
    assert break_.crawler == "unstop"
    assert break_.run_ids == (first.run_id, second.run_id)
    assert break_.trace_ref == second.reference


def test_mlh_off_season_zero_stays_steady_state_not_a_break():
    rows = [
        {"id": 1, "crawler": "mlh", "status": "success",
         "finished_at": "2026-10-11T00:00:00+00:00", "listings_found": 0,
         "trace_ref": "local://steady"},
    ]
    assert detect_breaks(rows) == []


def test_the_proposal_reproduces_the_known_good_shape_in_sandbox():
    real = list(UnstopScraper().extract(KNOWN_GOOD_FIXTURE.read_bytes()))
    healed = list(HealedUnstopScraper().extract(KNOWN_GOOD_FIXTURE.read_bytes()))
    assert len(healed) == len(real) == 25
    for candidate in healed:
        assert candidate.title
        assert candidate.source_url
        assert candidate.registration_close is not None
    assert sum(1 for r in verify_crawl(healed, now=AS_OF) if r.verdict == "live") == 25


def test_second_clean_crawl_and_backfill_after_the_heal(tmp_path):
    workspace = _workspace(tmp_path)
    clean = _crawl(HealedUnstopScraper(), SNAPSHOT, workspace)
    assert (clean.candidates, clean.live_found) == (25, 25)
    backfill = _crawl(HealedUnstopScraper(), KNOWN_GOOD_FIXTURE, workspace)
    assert (backfill.candidates, backfill.live_found) == (25, 25)
    ok, _ = verify_receipt(workspace / "receipts" / f"receipt-{clean.run_id:04d}.json")
    assert ok


def test_the_committed_evidence_pack_agrees_with_the_demo():
    event = json.loads((EVIDENCE / "heal-event.json").read_text(encoding="utf-8"))
    assert event["baseline"]["unstop_crawler"]["recent_live_yield"] == 25
    assert event["break"]["candidates_before"] == 25
    assert event["break"]["candidates_after"] == 0
    assert event["sandbox_validation"]["known_good_candidates"] == 25
    assert event["sandbox_validation"]["proposal_candidates"] == 25
    assert event["second_clean_crawl"]["live"] == 25
    assert event["backfill"]["live"] == 25
    assert event["mlh_steady_state"]["watchdog_breaks"] == 0

    receipts = sorted((EVIDENCE / "receipts").glob("receipt-*.json"))
    assert len(receipts) == 5
    for path in receipts:
        ok, message = verify_receipt(path)
        assert ok, message

    traces = sorted((EVIDENCE / "traces").glob("*.json"))
    assert len(traces) == 5
    for path in traces:
        document = json.loads(path.read_text(encoding="utf-8"))
        assert [span["name"] for span in document["spans"]] == [
            "fetch", "extract", "verify", "store",
        ]
