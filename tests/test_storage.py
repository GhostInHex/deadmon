"""Ticket 05 — storage tests: a crawl run writes rows and reads back."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from deadmon.candidate import make_candidate
from deadmon.storage import SCHEMA_DIR, Store
from deadmon.verdict import CLOSED, LIVE, UNVERIFIED, Listing

NOW = datetime(2026, 10, 11, tzinfo=timezone.utc)


@pytest.fixture
def db(tmp_path):
    """A fresh database per test. The DDL files are the source of truth."""
    store = Store(tmp_path / "deadmon.db")
    store.open()
    yield store
    store.close()


def pair(verdict, title="Hack", url="https://unstop.com/hack", crawler="unstop", mode="online"):
    """A (candidate, listing) pair — what `record_run_listings` writes."""
    candidate = make_candidate(
        title=title,
        source_url=url,
        registration_close=datetime(2026, 11, 1, tzinfo=timezone.utc),
        mode=mode,
        crawler=crawler,
    )
    listing = Listing(
        candidate_title=title,
        source_url=url,
        verdict=verdict,
        verified_at=NOW,
        crawler=crawler,
    )
    return candidate, listing


def rows(store, sql, params=()):
    return store.connection().execute(sql, params).fetchall()


def test_the_ddl_files_are_the_source_of_truth(tmp_path):
    store = Store(tmp_path / "fresh.db")
    store.open()
    try:
        names = {r[0] for r in rows(store, "SELECT name FROM sqlite_master WHERE type='table'")}
        # Plural tables from the first commit (ADR-0006).
        assert {"hackathons", "sources", "crawl_runs", "subscribers", "profiles"} <= names
    finally:
        store.close()
    assert Path(SCHEMA_DIR).is_dir()
    assert any(Path(SCHEMA_DIR).glob("*.sql"))


def test_one_run_row_per_crawler_per_execution(db):
    first = db.start_run("unstop")
    second = db.start_run("unstop")
    assert first != second
    assert len(rows(db, "SELECT id FROM crawl_runs")) == 2


def test_a_run_records_start_finish_status_and_counts(db):
    run = db.start_run("unstop")
    db.record_run_listings(run, [pair(LIVE, url="https://unstop.com/a")])
    db.finish_run(run, status="success", live_found=1)
    row = rows(db, "SELECT * FROM crawl_runs WHERE id = ?", (run,))[0]
    keys = row.keys()
    for column in ("crawler", "started_at", "finished_at", "status", "listings_found"):
        assert column in keys and row[column] not in (None, ""), column
    assert row["live_found"] == 1 and row["closed_found"] == 0


def test_a_live_candidate_creates_one_hackathon_with_one_source(db):
    run = db.start_run("unstop")
    db.record_run_listings(run, [pair(LIVE, url="https://unstop.com/a")])
    db.finish_run(run, status="success", live_found=1)
    assert len(rows(db, "SELECT id FROM hackathons")) == 1
    assert len(rows(db, "SELECT id FROM sources")) == 1


def test_a_second_crawl_updates_rather_than_duplicates(db):
    for _ in range(3):
        run = db.start_run("unstop")
        db.record_run_listings(run, [pair(LIVE, url="https://unstop.com/a")])
        db.finish_run(run, status="success", live_found=1)
    assert len(rows(db, "SELECT id FROM hackathons")) == 1
    assert len(rows(db, "SELECT id FROM sources")) == 1
    assert len(rows(db, "SELECT id FROM crawl_runs")) == 3
    # exactly one verdict for that source, not one per run
    assert rows(db, "SELECT verdict FROM sources")[0]["verdict"] == LIVE


def test_an_unverified_candidate_is_a_stored_verdict_not_a_skipped_row(db):
    run = db.start_run("unstop")
    db.record_run_listings(run, [pair(UNVERIFIED, url="https://unstop.com/b")])
    db.finish_run(run, status="success")
    assert len(rows(db, "SELECT id FROM sources")) == 1
    assert rows(db, "SELECT verdict FROM sources")[0]["verdict"] == UNVERIFIED


def test_a_closed_verdict_is_retained_with_its_row_intact(db):
    run = db.start_run("unstop")
    db.record_run_listings(run, [pair(CLOSED, url="https://unstop.com/c")])
    db.finish_run(run, status="success", closed_found=1)
    row = rows(db, "SELECT * FROM sources")[0]
    assert row["verdict"] == CLOSED
    assert row["source_url"] == "https://unstop.com/c"
    assert row["verified_at"]


def test_every_verdict_carries_verified_at(db):
    run = db.start_run("unstop")
    db.record_run_listings(
        run,
        [
            pair(LIVE, url="https://unstop.com/1"),
            pair(UNVERIFIED, url="https://unstop.com/2"),
            pair(CLOSED, url="https://unstop.com/3"),
        ],
    )
    stored = rows(db, "SELECT verified_at FROM sources")
    assert len(stored) == 3
    assert all(row["verified_at"] for row in stored)


def test_re_running_the_same_crawl_produces_no_duplicates(db):
    set_of_pairs = [
        pair(LIVE, title="H1", url="https://unstop.com/1"),
        pair(CLOSED, title="H2", url="https://unstop.com/2"),
    ]
    for _ in range(2):
        run = db.start_run("unstop")
        db.record_run_listings(run, set_of_pairs)
        db.finish_run(run, status="success", live_found=1, closed_found=1)
    counts = {
        "hackathons": len(rows(db, "SELECT id FROM hackathons")),
        "sources": len(rows(db, "SELECT id FROM sources")),
        "crawl_runs": len(rows(db, "SELECT id FROM crawl_runs")),
    }
    assert counts == {"hackathons": 2, "sources": 2, "crawl_runs": 2}
    # no second verdict for the same source: one row, one verdict
    assert rows(db, "SELECT verdict FROM sources ORDER BY id")[0]["verdict"] == LIVE


def test_a_run_interrupted_mid_write_leaves_the_database_consistent(db):
    """The scheduler's resume test: kill part-way, then re-run."""
    run = db.start_run("unstop")
    partial = [
        pair(LIVE, title="Hack One", url="https://unstop.com/1"),
        pair(LIVE, title="Hack Two", url="https://unstop.com/2"),
    ]
    with pytest.raises(RuntimeError):
        db.record_run_listings(run, partial, crash_after_first=True)

    # consistent: the first row landed, the second did not, nothing half-written
    assert [r["source_url"] for r in rows(db, "SELECT source_url FROM sources ORDER BY id")] == [
        "https://unstop.com/1"
    ]
    # only one verdict for the source, never a duplicate
    assert len(rows(db, "SELECT id FROM sources")) == 1

    # the interrupted run is recorded, unfinished, and detectable
    state = db.resume_interrupted()
    assert [r["id"] for r in state] == [run]
    assert state[0]["finished_at"] is None

    # marking it interrupted, then re-running the same crawl, still adds no
    # duplicate rows and no second verdict for any source
    db.mark_interrupted(run)
    assert db.resume_interrupted() == []
    again = db.start_run("unstop")
    db.record_run_listings(again, partial)
    db.finish_run(again, status="success", live_found=2)
    assert len(rows(db, "SELECT id FROM sources")) == 2
    assert len(rows(db, "SELECT id FROM hackathons")) == 2
    # run history is newest-first; the re-run is the healthy record
    assert db.run_history()[0]["status"] == "success"
    assert db.run_history()[-1]["status"] == "interrupted"


def test_a_finished_run_is_not_resumed(db):
    run = db.start_run("unstop")
    db.record_run_listings(run, [pair(LIVE, url="https://unstop.com/1")])
    db.finish_run(run, status="success", live_found=1)
    assert db.resume_interrupted() == []


def test_run_history_is_per_crawler(db):
    for crawler in ("unstop", "unstop", "devpost"):
        run = db.start_run(crawler)
        db.record_run_listings(run, [pair(LIVE, crawler=crawler, url=f"u/{crawler}")])
        db.finish_run(run, status="success", live_found=1)
    assert len(db.run_history("unstop")) == 2
    assert len(db.run_history("devpost")) == 1


def test_run_history_carries_duration_figures(db):
    run = db.start_run("unstop")
    db.record_run_listings(run, [pair(LIVE, url="https://unstop.com/1")])
    db.finish_run(run, status="success", live_found=1)
    row = db.run_history("unstop")[0]
    assert row["started_at"] and row["finished_at"]
    assert row["finished_at"] >= row["started_at"]
    assert row["listings_found"] == 1


def test_the_subscriber_and_profile_tables_exist_and_are_empty(db):
    assert rows(db, "SELECT id FROM subscribers") == []
    assert rows(db, "SELECT id FROM profiles") == []


def test_profile_is_keyed_to_a_subscriber_not_a_singleton(db):
    """One row insert, not a migration, when a second subscriber arrives."""
    first = db.add_subscriber("student")
    second = db.add_subscriber("club")
    db.add_profile(first, mode="online")
    db.add_profile(second, mode="hybrid")
    profiles = rows(db, "SELECT subscriber_id FROM profiles ORDER BY id")
    assert [p["subscriber_id"] for p in profiles] == [first, second]


def test_a_run_rows_trace_reference_survives_the_connection(tmp_path):
    """`trace_ref` lives on the run row, so a link survives a restart (ticket 07)."""
    path = tmp_path / "trace.db"
    store = Store(path)
    store.open()
    run = store.start_run("unstop")
    store.record_run_listings(run, [pair(LIVE, url="https://unstop.com/1")])
    store.finish_run(run, status="success", live_found=1, trace_ref="local://abc")
    store.close()

    reopened = Store(path)
    reopened.open()
    try:
        assert reopened.trace_ref_for(run) == "local://abc"
        assert reopened.run_history("unstop")[0]["trace_ref"] == "local://abc"
    finally:
        reopened.close()


def test_no_database_file_is_ever_committed(tmp_path):
    """The schema files are the source of truth; a .db is disposable state."""
    for ddl in Path(SCHEMA_DIR).glob("*.sql"):
        assert ddl.suffix == ".sql"
    store = Store(tmp_path / "disposable.db")
    store.open()
    store.close()
    assert (tmp_path / "disposable.db").exists()
    assert not list(Path(SCHEMA_DIR).glob("*.db"))


def test_a_row_stores_every_candidate_field(db):
    run = db.start_run("unstop")
    candidate, listing = pair(LIVE, url="https://unstop.com/full")
    db.record_run_listings(run, [(candidate, listing)])
    row = rows(db, "SELECT * FROM sources")[0]
    assert row["registration_close"] == "2026-11-01T00:00:00+00:00"
    assert row["mode"] == "online"
    assert row["crawler"] == "unstop"
    assert row["title"] == "Hack"
