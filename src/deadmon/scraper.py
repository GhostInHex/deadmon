"""Scraper interface: fetch + extract behind one contract.

The orchestrator (Scout) never learns which platform it is talking to.
Adapters implement this; verification, dedupe and alerts stay out.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable
from pathlib import Path

from .candidate import Candidate


class Scraper(ABC):
    """One platform's adapter behind the scraper interface."""

    name: str = "base"

    @abstractmethod
    def fetch(self, source: Path | str) -> bytes:
        """Return the raw payload for one listing page. No verification here."""
        raise NotImplementedError

    @abstractmethod
    def extract(self, payload: bytes) -> Iterable[Candidate]:
        """Produce candidates only — no claim about whether any is live."""
        raise NotImplementedError

    def run(self, source: Path | str) -> list[Candidate]:
        return list(self.extract(self.fetch(source)))
