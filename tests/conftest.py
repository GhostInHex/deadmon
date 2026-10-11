"""Shared test support for deadmon.

Two things every test needs:
  * the path to the recorded fixture corpus — never the network
  * an autouse guard that makes any outbound socket use a test failure, so
    "no network in tests" is enforced mechanically rather than by convention
"""
from __future__ import annotations

import socket
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURES = REPO_ROOT / "fixtures"
UNSTOP = FIXTURES / "unstop"

# The known-good baseline a proposal must later reproduce (ADR-0015).
KNOWN_GOOD_FIXTURE = UNSTOP / "hackathons-open.json"
CLOSED_FIXTURE = UNSTOP / "hackathons-closed.json"
PAST_FIXTURE = UNSTOP / "hackathons-past.json"
# Ticket 04's declared test double for the `unverified` verdict. Named as a
# double on purpose: it is not a recording.
UNVERIFIED_DOUBLE = UNSTOP / "hackathons-unverified.json"

BLOCKED = "network access in tests is forbidden (PRD: deterministic, no network)"


def _blocked(*args, **kwargs):
    raise RuntimeError(BLOCKED)


@pytest.fixture(autouse=True)
def _no_network(monkeypatch):
    """Any test that tries to reach the network fails loudly."""
    monkeypatch.setattr(socket, "create_connection", _blocked)
    monkeypatch.setattr(socket, "getaddrinfo", _blocked)
    monkeypatch.setattr(socket.socket, "connect", _blocked)
