"""Contract: plural tables from the first commit; DDL in versioned schema files."""
import sqlite3
from pathlib import Path

SCHEMA = Path(__file__).resolve().parent.parent / "src" / "deadmon" / "schema" / "001_baseline.sql"


def test_schema_contract():
    assert SCHEMA.is_file(), "DDL must live in versioned schema files"
    con = sqlite3.connect(":memory:")
    con.executescript(SCHEMA.read_text(encoding="utf-8"))
    tables = {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert {"hackathons", "sources", "crawl_runs", "subscribers", "profiles"} <= tables
    # no singular-profile table, no singleton assumption
    assert "profile" not in tables
    cols = {r[1] for r in con.execute("PRAGMA table_info(sources)")}
    assert {"verdict", "verified_at", "crawler", "source_url"} <= cols
    run_cols = {r[1] for r in con.execute("PRAGMA table_info(crawl_runs)")}
    assert {"trace_ref", "listings_found", "status"} <= run_cols
