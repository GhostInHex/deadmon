"""Storage: a crawl run's output becomes state.

Applies the versioned DDL from `src/deadmon/schema/` — a committed database
file is never the source of truth — records one `crawl_runs` row per crawler per
execution, and upserts each listing as a hackathon with one source beneath it.

Idempotence is the whole point: `sources` is keyed on `(crawler, source_url)`,
so a second crawl of the same source updates the row rather than duplicating
it, and a run killed mid-write leaves nothing half-recorded.
"""
from __future__ import annotations

from contextlib import closing
from datetime import datetime, timezone
import sqlite3
from pathlib import Path

from .verdict import Listing

SCHEMA_DIR = Path(__file__).resolve().parent / "schema"

SCHEMA_FILES = ("001_baseline.sql",)

INTERRUPTED = "interrupted"


def apply_schema(connection: sqlite3.Connection) -> None:
    """Apply every versioned DDL file, in order."""
    for name in SCHEMA_FILES:
        path = SCHEMA_DIR / name
        connection.executescript(path.read_text(encoding="utf-8"))


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class Store:
    """One SQLite database, opened and closed around a crawl run."""

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self._connection: sqlite3.Connection | None = None

    # -- lifecycle --------------------------------------------------------

    def open(self) -> "Store":
        self.path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        apply_schema(connection)
        connection.commit()
        self._connection = connection
        return self

    def close(self) -> None:
        if self._connection is not None:
            self._connection.close()
            self._connection = None

    def connection(self) -> sqlite3.Connection:
        if self._connection is None:
            raise RuntimeError("Store is not open; call open() first")
        return self._connection

    def __enter__(self) -> "Store":
        return self.open()

    def __exit__(self, *_exc) -> None:
        self.close()

    # -- crawl runs -------------------------------------------------------

    def start_run(self, crawler: str) -> int:
        started = utc_now()
        with closing(self.connection().cursor()) as cursor:
            cursor.execute(
                "INSERT INTO crawl_runs (crawler, started_at, status) VALUES (?, ?, ?)",
                (crawler, started, "running"),
            )
            run_id = cursor.lastrowid
        self.connection().commit()
        return run_id

    def finish_run(
        self,
        run_id: int,
        *,
        status: str,
        listings_found: int | None = None,
        live_found: int = 0,
        closed_found: int = 0,
        trace_ref: str | None = None,
    ) -> None:
        """Close a run. `unverified` never enters the live count."""
        if listings_found is None:
            listings_found = live_found + closed_found
        finished = utc_now()
        with closing(self.connection().cursor()) as cursor:
            cursor.execute(
                """
                UPDATE crawl_runs
                   SET finished_at = ?, status = ?, listings_found = ?,
                       live_found = ?, closed_found = ?, trace_ref = ?
                 WHERE id = ?
                """,
                (finished, status, listings_found, live_found, closed_found, trace_ref, run_id),
            )
        self.connection().commit()

    def resume_interrupted(self) -> list[sqlite3.Row]:
        """Runs that never finished — the ones a killed process leaves behind."""
        return self.connection().execute(
            "SELECT * FROM crawl_runs WHERE finished_at IS NULL ORDER BY id"
        ).fetchall()

    def mark_interrupted(self, run_id: int) -> None:
        """Record a killed run as interrupted rather than leaving it ambiguous."""
        with closing(self.connection().cursor()) as cursor:
            cursor.execute(
                "UPDATE crawl_runs SET finished_at = ?, status = ? WHERE id = ?",
                (utc_now(), INTERRUPTED, run_id),
            )
        self.connection().commit()

    def run_history(self, crawler: str | None = None) -> list[sqlite3.Row]:
        """Per-crawler health: success, listings found, duration."""
        rows = self.connection().execute(
            """
            SELECT id, crawler, started_at, finished_at, status, listings_found,
                   live_found, closed_found, trace_ref
              FROM crawl_runs
             ORDER BY id DESC
            """
        ).fetchall()
        if crawler is not None:
            rows = [row for row in rows if row["crawler"] == crawler]
        return rows

    def trace_ref_for(self, run_id: int) -> str | None:
        row = self.connection().execute(
            "SELECT trace_ref FROM crawl_runs WHERE id = ?", (run_id,)
        ).fetchone()
        return row["trace_ref"] if row else None

    # -- listings ---------------------------------------------------------

    def record_run_listings(
        self, run_id: int, verified, *, crash_after_first: bool = False
    ) -> None:
        """Write a crawl's listings. Each source is one transaction.

        `verified` yields `(candidate, listing)` pairs: ticket 01's `Candidate`
        carries the fields, its `Listing` carries the verdict. The screen can
        write every schema column only if both reach it.

        `crash_after_first` exists for the interruption test only: it stops
        mid-way through, which is what a killed process looks like.
        """
        connection = self.connection()
        for index, (candidate, listing) in enumerate(verified):
            self._record_listing(connection, candidate, listing)
            # One commit per source: a killed process loses at most the source
            # it was writing, and the upsert below makes re-running idempotent.
            connection.commit()
            if crash_after_first and index == 0:
                raise RuntimeError(f"crawl run {run_id} interrupted mid-write")

    def _record_listing(
        self, connection: sqlite3.Connection, candidate, listing: Listing
    ) -> None:
        hackathon_id = self._hackathon_id(connection, listing.candidate_title)
        with closing(connection.cursor()) as cursor:
            cursor.execute(
                """
                INSERT INTO sources (
                    hackathon_id, crawler, source_url, title, registration_close,
                    mode, prize_summary, team_size_rule, eligibility_rules,
                    registration_open, verdict, verified_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT (crawler, source_url) DO UPDATE SET
                    hackathon_id = excluded.hackathon_id,
                    title = excluded.title,
                    registration_close = excluded.registration_close,
                    mode = excluded.mode,
                    prize_summary = excluded.prize_summary,
                    team_size_rule = excluded.team_size_rule,
                    eligibility_rules = excluded.eligibility_rules,
                    registration_open = excluded.registration_open,
                    verdict = excluded.verdict,
                    verified_at = excluded.verified_at
                """,
                (
                    hackathon_id,
                    listing.crawler,
                    listing.source_url,
                    listing.candidate_title,
                    _iso(candidate.registration_close),
                    candidate.mode,
                    candidate.prize_summary,
                    candidate.team_size_rule,
                    _rules(candidate.eligibility_rules),
                    _iso(candidate.registration_open),
                    listing.verdict,
                    _iso(listing.verified_at),
                ),
            )

    def _hackathon_id(self, connection: sqlite3.Connection, title: str) -> int:
        row = connection.execute(
            "SELECT id FROM hackathons WHERE title = ? ORDER BY id LIMIT 1", (title,)
        ).fetchone()
        if row is not None:
            return row["id"]
        with closing(connection.cursor()) as cursor:
            cursor.execute(
                "INSERT INTO hackathons (title, created_at) VALUES (?, ?)",
                (title, utc_now()),
            )
            return cursor.lastrowid

    # -- read back --------------------------------------------------------

    def cards(self) -> list[dict]:
        """One card per hackathon: a view over its sources (ADR-0010)."""
        sources = self.connection().execute(
            """
            SELECT s.id, s.crawler, s.source_url, s.title AS source_title,
                   s.registration_close, s.mode, s.verdict, s.verified_at,
                   h.id AS hackathon_id, h.title AS hackathon_title
              FROM sources s JOIN hackathons h ON h.id = s.hackathon_id
             ORDER BY h.id, s.id
            """
        ).fetchall()
        cards: dict[int, dict] = {}
        for row in sources:
            card = cards.setdefault(
                row["hackathon_id"],
                {
                    "hackathon_id": row["hackathon_id"],
                    "title": row["hackathon_title"],
                    "sources": [],
                },
            )
            card["sources"].append(dict(row))
        for card in cards.values():
            card["earliest_credible_close"] = earliest_credible_close(card["sources"])
            card["verdicts"] = {source["verdict"] for source in card["sources"]}
        return list(cards.values())

    # -- subscribers and profiles (empty at this stage, ADR-0006) ----------

    def add_subscriber(self, name: str) -> int:
        with closing(self.connection().cursor()) as cursor:
            cursor.execute(
                "INSERT INTO subscribers (name, created_at) VALUES (?, ?)", (name, utc_now())
            )
            subscriber_id = cursor.lastrowid
        self.connection().commit()
        return subscriber_id

    def add_profile(self, subscriber_id: int, *, mode: str | None = None) -> int:
        with closing(self.connection().cursor()) as cursor:
            cursor.execute(
                "INSERT INTO profiles (subscriber_id, mode, created_at) VALUES (?, ?, ?)",
                (subscriber_id, mode, utc_now()),
            )
            profile_id = cursor.lastrowid
        self.connection().commit()
        return profile_id


def earliest_credible_close(sources) -> str | None:
    """The earliest date read from a source that verified and parsed (ADR-0009).

    A closed source's date is evidence it was credible once but is not a live
    claim now, so only `live` sources contribute. No live source means no
    credible date — never a fallback.
    """
    closes = [
        source["registration_close"]
        for source in sources
        if source["verdict"] == "live" and source["registration_close"] is not None
    ]
    return min(closes) if closes else None


def _iso(value) -> str | None:
    return value.isoformat() if value is not None else None


def _rules(rules) -> str | None:
    if rules is None:
        return None
    return "\n".join(rules)
