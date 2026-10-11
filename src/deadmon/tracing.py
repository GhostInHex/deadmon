"""Tracing: every crawl run is one trace, and tracing can never break the run.

A finished crawl run cannot depend on an observability vendor's uptime, so this
module owns *sink selection* rather than a single hard-wired call.

Sinks:

* `NeatlogsSink` — used when the `neatlogs` package imports **and**
  `NEATLOGS_API_KEY` is set. The run is handed to neatlogs' `LLMTracker` and its
  session id is recorded as the trace's external id.
* `LocalSink` — the default. It writes the trace document as JSON next to the
  run, so the detail page keeps working after a restart, and the client
  measures latency itself.

Latency is captured by the client on every span, and token/cost are carried by
the client too: both are 0 in Slice 1 by fact (no model call happens yet), not
by omission — Slice 4's proposal step records them through the same client
rather than by instrumenting each stage.

Capture is best-effort in the strict sense: any failure inside a sink is
recorded on the trace and swallowed, because a broken tracing service must
never take a crawl run down with it.
"""
from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timezone
import json
import logging
import os
from pathlib import Path
import time
import uuid

LOG = logging.getLogger(__name__)

NEATLOGS = "neatlogs"
LOCAL = "local"


@dataclass
class Span:
    name: str
    attributes: dict = field(default_factory=dict)
    started_at: str = ""
    ended_at: str | None = None
    duration_ms: float | None = None
    events: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "attributes": self.attributes,
            "started_at": self.started_at,
            "ended_at": self.ended_at,
            "duration_ms": self.duration_ms,
            "events": self.events,
        }


@dataclass
class Trace:
    """One crawl run, as one trace."""

    crawler: str
    reference: str
    backend: str
    spans: list[Span] = field(default_factory=list)
    token_usage: int = 0
    cost_usd: float = 0.0
    error: str | None = None

    def document(self) -> dict:
        return {
            "crawler": self.crawler,
            "reference": self.reference,
            "backend": self.backend,
            "spans": [span.to_dict() for span in self.spans],
            "token_usage": self.token_usage,
            "cost_usd": self.cost_usd,
            "error": self.error,
        }


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def make_reference() -> str:
    """Always resolvable inside deadmon: the dashboard links `/trace/<ref>`."""
    return f"local://{uuid.uuid4().hex}"


class TraceClient:
    """Owns span measurement and aggregation; the stage code never does."""

    def __init__(self, crawler: str, *, sink_dir: Path | None = None, backend: str = LOCAL):
        self.crawler = crawler
        self.trace = Trace(
            crawler=crawler,
            reference=make_reference(),
            backend=backend,
        )
        self._sink_dir = Path(sink_dir) if sink_dir else Path(".runs/traces")
        self._tracker = None
        self._failed = False

    # -- lifecycle --------------------------------------------------------

    @property
    def reference(self) -> str:
        return self.trace.reference

    def external_id(self) -> str | None:
        """The neatlogs session id, when the run actually reached neatlogs."""
        return getattr(self._tracker, "session_id", None) if self._tracker else None

    def start(self) -> "TraceClient":
        if self.trace.backend != NEATLOGS:
            return self
        try:
            import neatlogs  # optional dependency; never required

            self._tracker = neatlogs.init(api_key=os.environ.get("NEATLOGS_API_KEY", ""))
            if self._tracker is not None:
                self.trace.reference = f"neatlogs://{self._tracker.session_id}"
        except Exception as exc:  # tracing must never break a crawl run
            self.trace.backend = LOCAL
            self.trace.error = f"neatlogs unavailable: {exc}"
            LOG.warning("neatlogs unavailable, tracing locally: %s", exc)
        return self

    @contextmanager
    def span(self, name: str, **attributes):
        """Measure one span. Usage records token/cost the client attributed."""
        span = Span(name=name, attributes=dict(attributes), started_at=_now_iso())
        start = time.perf_counter()
        self.trace.spans.append(span)
        try:
            yield span
        except BaseException as exc:
            span.events.append({"error": f"{type(exc).__name__}: {exc}"})
            raise
        finally:
            span.ended_at = _now_iso()
            span.duration_ms = round((time.perf_counter() - start) * 1000, 3)

    def record_usage(self, *, tokens: int = 0, cost_usd: float = 0.0) -> None:
        self.trace.token_usage += int(tokens)
        self.trace.cost_usd += float(cost_usd)

    def close_and_link(self) -> str:
        """Persist the trace and return the reference to store on the run row."""
        try:
            self._sink_dir.mkdir(parents=True, exist_ok=True)
            path = self._sink_dir / f"{self.trace.reference.split('://', 1)[-1]}.json"
            path.write_text(
                json.dumps(self.trace.document(), ensure_ascii=False, indent=1), encoding="utf-8"
            )
        except Exception as exc:  # a sink that cannot be written must not fail the run
            self.trace.error = f"trace sink unusable: {exc}"
            LOG.warning("trace sink unusable: %s", exc)
        return self.trace.reference

    # -- read back --------------------------------------------------------

    @staticmethod
    def load(reference: str, sink_dir: Path | None = None) -> Trace | None:
        directory = Path(sink_dir) if sink_dir else Path(".runs/traces")
        path = directory / f"{reference.split('://', 1)[-1]}.json"
        if not path.exists():
            return None
        document = json.loads(path.read_text(encoding="utf-8"))
        return Trace(
            crawler=document["crawler"],
            reference=document["reference"],
            backend=document["backend"],
            spans=[Span(**span) for span in document["spans"]],
            token_usage=document.get("token_usage", 0),
            cost_usd=document.get("cost_usd", 0.0),
            error=document.get("error"),
        )


def trace_client(crawler: str, *, sink_dir: Path | None = None) -> TraceClient:
    """Pick a sink: neatlogs when it is importable and keyed, local otherwise."""
    client = TraceClient(crawler, sink_dir=sink_dir)
    if neatlogs_available():
        client.trace.backend = NEATLOGS
    return client


def neatlogs_available() -> bool:
    if not os.environ.get("NEATLOGS_API_KEY"):
        return False
    try:
        import neatlogs  # noqa: F401

        return True
    except Exception:
        return False


def span_names(trace: Trace) -> list[str]:
    return [span.name for span in trace.spans]


def duration_ms(trace: Trace) -> float:
    return round(sum(span.duration_ms or 0.0 for span in trace.spans), 3)
