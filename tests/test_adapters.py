"""Slice 2 — one platform per adapter, every adapter behind the same contract."""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import pytest

from deadmon.adapters import CRAWLERS
from deadmon.adapters.genai_works import GenaiWorksScraper
from deadmon.adapters.hackathon_com import HackathonComScraper
from deadmon.adapters.hackerrank import HackerRankScraper
from deadmon.adapters.lablab import LablabScraper
from deadmon.adapters.mlh import MlhScraper
from deadmon.crawl import crawl_all
from deadmon.storage import Store

pytestmark = pytest.mark.usefixtures("_no_network")

CORPUS = {
    "hackerrank": "fixtures/hackerrank/contests.html",
    "hackathon-com": "fixtures/hackathon-com/index.html",
    "lablab": "fixtures/lablab/event.html",
    "mlh": "fixtures/mlh/events-2026.html",
    "genai-works": "fixtures/genai-works/index.html",
}


def records(scraper, crawler):
    return list(scraper.extract(Path(CORPUS[crawler]).read_bytes()))


def test_the_registry_covers_six_crawlers_with_recorded_corpora():
    assert [name for name, _, _ in CRAWLERS] == [
        "unstop",
        "hackerrank",
        "hackathon-com",
        "lablab",
        "mlh",
        "genai-works",
    ]
    for name, _, corpus in CRAWLERS:
        assert corpus.is_dir(), name
        assert corpus != Path("fixtures/unstop") or name == "unstop"


def test_hackerrank_extracts_eleven_unique_contests():
    found = records(HackerRankScraper(), "hackerrank")
    assert len(found) == 11
    titles = {r.title for r in found}
    assert {
        "Salesforce Design Challenge",
        "micro1 Eval Hackathon",
        "Orchestrate October'26",
        "Justice League 1639642697",
        "HackerRank HackFest 2020",
    } <= titles
    # the carousel repeats promoted cards; each record is one contest
    assert len({(r.title, r.source_url) for r in found}) == 11
    assert all(r.source_url.startswith("https://www.hackerrank.com/") for r in found)
    # day-month strings carry no year and no zone, so close stays absent
    assert all(r.registration_close is None for r in found)
    assert all(r.mode is None for r in found)


def test_hackathon_com_extracts_four_events_with_modes():
    found = records(HackathonComScraper(), "hackathon-com")
    assert len(found) == 4
    assert found[0].title == "AI Builders Challenge - North America"
    assert all(r.mode == "online" for r in found)
    assert all(r.source_url.startswith("https://hackathon.com/event/") for r in found)
    assert all(r.registration_close is None for r in found)


def test_lablab_extracts_the_json_ld_catalogue_with_card_modes():
    found = records(LablabScraper(), "lablab")
    assert len(found) == 24
    assert found[0].title == "AMD AI League"
    assert found[0].source_url == (
        "https://lablab.ai/ai-hackathons/amd-lablab-ai-academy-challenge"
    )
    modes = Counter(r.mode for r in found)
    assert modes == {"online": 8, "hybrid": 3, "offline": 1, None: 12}
    # build windows are event bounds without year or zone, never closes
    assert all(r.registration_close is None for r in found)


def test_mlh_extracts_the_embedded_season_catalogue():
    found = records(MlhScraper(), "mlh")
    assert len(found) == 24
    modes = Counter(r.mode for r in found)
    assert modes == {"offline": 21, "online": 3}
    hackprix = next(r for r in found if r.title == "HackPrix Season 3")
    assert hackprix.source_url == "https://s3.hackprix.tech/"
    # event bounds are not registration closes, even tz-aware ones
    assert all(r.registration_close is None for r in found)


def test_genai_works_extracts_the_featured_close_with_its_year():
    found = records(GenaiWorksScraper(), "genai-works")
    assert len(found) == 1
    (record,) = found
    assert record.title == "Open Agent Hackathon 2026"
    assert record.source_url == "https://hackathon.genai.works/event/open-agent-hackathon-2026"
    assert record.registration_close == datetime(2026, 10, 22, 23, 59, tzinfo=timezone.utc)
    # the card states no mode, so a future close still verifies unverified
    assert record.mode is None


def test_a_missing_payload_is_a_file_error_not_an_empty_page(tmp_path):
    for scraper in (
        HackerRankScraper(),
        HackathonComScraper(),
        LablabScraper(),
        MlhScraper(),
        GenaiWorksScraper(),
    ):
        with pytest.raises(FileNotFoundError):
            scraper.fetch(tmp_path / "absent.html")
        with pytest.raises(FileNotFoundError):
            scraper.fetch(tmp_path / "page.json")


def test_crawl_all_runs_every_crawler_with_one_shared_store(tmp_path):
    db = tmp_path / "db" / "deadmon.db"
    db.parent.mkdir()
    sink = tmp_path / "traces"
    outcomes = crawl_all(
        db_path=db,
        sink_dir=sink,
        now=datetime(2026, 10, 11, tzinfo=timezone.utc),
    )
    # 4 unstop fixtures + one page per new crawler
    assert len(outcomes) == 9
    assert Counter(o.crawler for o in outcomes) == {
        "unstop": 4,
        "hackerrank": 1,
        "hackathon-com": 1,
        "lablab": 1,
        "mlh": 1,
        "genai-works": 1,
    }
    assert all(o.reference and o.run_id > 0 for o in outcomes)
    with Store(db).open() as store:
        assert len(store.run_history()) == 9
