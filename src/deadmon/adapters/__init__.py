"""Platform adapters — one module per platform behind the scraper interface.

The crawler registry lives here, not in `crawl.py`: no module outside
`adapters/` names a platform, so the orchestrator never learns which
platform it is talking to (`test_no_module_knows_which_platform...`).

Each entry is (crawler name, scraper class, recorded-corpus directory).
Corpora are recorded live and never edited; see `fixtures/README.md`.
"""
from pathlib import Path

from .genai_works import GenaiWorksScraper
from .hackathon_com import HackathonComScraper
from .hackerrank import HackerRankScraper
from .lablab import LablabScraper
from .mlh import MlhScraper
from .unstop import UnstopScraper

CRAWLERS: tuple[tuple[str, type, Path], ...] = (
    ("unstop", UnstopScraper, Path("fixtures/unstop")),
    ("hackerrank", HackerRankScraper, Path("fixtures/hackerrank")),
    ("hackathon-com", HackathonComScraper, Path("fixtures/hackathon-com")),
    ("lablab", LablabScraper, Path("fixtures/lablab")),
    ("mlh", MlhScraper, Path("fixtures/mlh")),
    ("genai-works", GenaiWorksScraper, Path("fixtures/genai-works")),
)

__all__ = [
    "CRAWLERS",
    "GenaiWorksScraper",
    "HackathonComScraper",
    "HackerRankScraper",
    "LablabScraper",
    "MlhScraper",
    "UnstopScraper",
]
