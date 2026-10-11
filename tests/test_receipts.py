"""Ticket 04 — every crawl run is countable proof: numbered hashed receipts.

One receipt per crawl run (never per card), written as local JSON so the
demo needs no login wall, and verified by `deadmon-receipt-check`: an edited
receipt fails. Stdlib only, offline, fixtures never overwritten.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from deadmon.adapters.unstop import UnstopScraper
from deadmon.crawl import crawl_corpus, crawl_one_fixture, main
from deadmon.receipts import (
    build_receipt,
    canonical_hash,
    emit_receipt,
    receipt_path,
    verify_all,
    verify_receipt,
)
from deadmon.receipts import main as receipt_check
from deadmon.storage import Store

from tests.conftest import KNOWN_GOOD_FIXTURE

AS_OF = datetime(2026, 10, 11, tzinfo=timezone.utc)


@pytest.fixture
def workspace(tmp_path):
    (tmp_path / "traces").mkdir()
    (tmp_path / "db").mkdir()
    (tmp_path / "receipts").mkdir()
    return tmp_path


def run_corpus(workspace):
    return crawl_corpus(
        fixture_dir=Path("fixtures/unstop"),
        db_path=workspace / "db" / "deadmon.db",
        sink_dir=workspace / "traces",
        now=AS_OF,
        receipt_dir=workspace / "receipts",
    )


def test_each_crawl_run_emits_a_numbered_receipt_with_a_hash(workspace):
    outcomes = run_corpus(workspace)
    assert len(outcomes) == 4
    for outcome in outcomes:
        path = receipt_path(workspace / "receipts", outcome.run_id)
        assert path.exists()
        document = json.loads(path.read_text(encoding="utf-8"))
        assert document["receipt"] == outcome.run_id
        assert document["run_id"] == outcome.run_id
        assert document["crawler"] == "unstop"
        assert document["live"] == outcome.live_found
        assert document["closed"] == outcome.closed_found
        assert document["unverified"] == outcome.unverified_found
        assert document["trace"] == outcome.reference
        assert len(document["hash"]) == 64  # sha256 hex


def test_receipts_verify_clean(workspace, capsys):
    run_corpus(workspace)
    assert receipt_check(["--receipts", str(workspace / "receipts")]) == 0
    out = capsys.readouterr().out
    assert "4/4 receipt(s) verified." in out


def test_an_edited_receipt_fails_verification(workspace, capsys):
    outcomes = run_corpus(workspace)
    path = receipt_path(workspace / "receipts", outcomes[0].run_id)
    document = json.loads(path.read_text(encoding="utf-8"))
    document["live"] += 1  # tamper: inflate the feed count
    path.write_text(json.dumps(document, ensure_ascii=False, indent=1), encoding="utf-8")

    ok, message = verify_receipt(path)
    assert not ok
    assert "FAIL" in message
    assert receipt_check(["--receipts", str(workspace / "receipts")]) == 1
    assert "3/4 receipt(s) verified." in capsys.readouterr().out


def test_receipts_count_crawl_runs_not_cards(workspace):
    outcomes = run_corpus(workspace)
    receipts = sorted((workspace / "receipts").glob("receipt-*.json"))
    assert len(receipts) == len(outcomes) == 4  # one per run, not per card
    total_cards = sum(o.live_found + o.closed_found + o.unverified_found for o in outcomes)
    assert total_cards > len(receipts)


def test_local_json_fallback_needs_no_login(workspace):
    """No key, no neatlogs package path: receipt still lands as local JSON."""
    import pytest as _pytest

    with _pytest.MonkeyPatch.context() as patch:
        patch.delenv("NEATLOGS_API_KEY", raising=False)
        outcome = crawl_one_fixture(
            UnstopScraper(),
            KNOWN_GOOD_FIXTURE,
            store=Store(workspace / "db" / "deadmon.db").open(),
            now=AS_OF,
            sink_dir=workspace / "traces",
            receipt_dir=workspace / "receipts",
        )
    path = receipt_path(workspace / "receipts", outcome.run_id)
    document = json.loads(path.read_text(encoding="utf-8"))
    assert document["backend"] == "local"
    assert document["crawler"] == "unstop"
    ok, _ = verify_receipt(path)
    assert ok


def test_hash_is_stable_and_covers_canonical_fields(tmp_path):
    first = build_receipt(
        run_id=7, crawler="unstop", candidates=25, live=25, closed=0,
        unverified=0, trace="local://abc", backend="local",
    )
    second = build_receipt(
        run_id=7, crawler="unstop", candidates=25, live=25, closed=0,
        unverified=0, trace="local://abc", backend="local",
    )
    assert first["hash"] == second["hash"] == canonical_hash(first)
    # extra non-canonical keys do not change the seal
    first["note"] = "judge annotation"
    assert canonical_hash(first) == second["hash"]


def test_verify_all_reports_every_receipt_in_numbered_order(workspace):
    run_corpus(workspace)
    results = verify_all(workspace / "receipts")
    assert len(results) == 4
    assert [p.name for p, _, _ in results] == sorted(p.name for p, _, _ in results)
    assert all(ok for _, ok, _ in results)


def test_a_missing_receipt_directory_is_a_clean_failure(capsys, tmp_path):
    assert receipt_check(["--receipts", str(tmp_path / "absent")]) == 1
    assert "no receipts" in capsys.readouterr().err


def test_the_command_line_writes_receipts(workspace):
    code = main(
        [
            "--fixtures", "fixtures/unstop",
            "--db", str(workspace / "db" / "cli.db"),
            "--traces", str(workspace / "traces"),
            "--receipts", str(workspace / "receipts"),
            "--as-of", AS_OF.isoformat(),
            "--no-serve",
        ]
    )
    assert code == 0
    # the CLI runs every registered crawler (9 runs), not just Unstop: one
    # receipt per crawl run, whatever the crawler.
    assert len(list((workspace / "receipts").glob("receipt-*.json"))) == 9
