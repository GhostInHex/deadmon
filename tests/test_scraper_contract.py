"""Contract: fetch + extract behind one scraper interface; card is a view over sources."""
import inspect
import sqlite3
from pathlib import Path

from deadmon.scraper import Scraper

SCHEMA = Path(__file__).resolve().parent.parent / "src" / "deadmon" / "schema" / "001_baseline.sql"


def test_scraper_interface_contract():
    assert set(Scraper.__abstractmethods__) == {"fetch", "extract"}
    assert "platform" not in inspect.signature(Scraper.run).parameters
    # orchestrator talks to Scraper, never to a platform name
    assert hasattr(Scraper, "run")


def test_card_is_view_over_sources():
    con = sqlite3.connect(":memory:")
    con.executescript(SCHEMA.read_text(encoding="utf-8"))
    con.execute("INSERT INTO hackathons (title, created_at) VALUES ('H', '2026-10-11T00:00:00+00:00')")
    hid = con.execute("SELECT id FROM hackathons").fetchone()[0]
    for url in ("https://a.test/1", "https://b.test/1"):
        con.execute(
            "INSERT INTO sources (hackathon_id, crawler, source_url, title, verdict, verified_at)"
            " VALUES (?, 'unstop', ?, 'H', 'live', '2026-10-11T00:00:00+00:00')",
            (hid, url),
        )
    cards = con.execute(
        "SELECT h.id, h.title, COUNT(s.id) FROM hackathons h"
        " JOIN sources s ON s.hackathon_id = h.id GROUP BY h.id"
    ).fetchall()
    assert cards == [(hid, "H", 2)]  # one card per hackathon, many sources beneath
