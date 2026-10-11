"""Tracing: every crawl run is one trace, and tracing can never break the run.

A finished crawl run cannot depend on an observability vendor's uptime, so this
module owns *sink selection* rather than a single hard-wired call.

Sinks:

* `NeatlogsSink` — used when the `neatlogs` package imports **and**
  `NEATLOGS_API_KEY` is set. `neatlogs.init()` is called once per process; the
  run is then exported as one trace, rooted on a `WORKFLOW` span, with each
  stage as a child `CHAIN` span. Its trace id is recorded as the reference.
* `LocalSink` — the default. It writes the trace document as JSON next to the
  run, so the detail page keeps working after a restart, and the client
  measures latency itself.

Both sinks are written when neatlogs is available: the local document is what
`/trace/<ref>` renders, so the link deadmon stores on a run row keeps
resolving even if the service is later unreachable.

Latency is captured by the client on every span, and token/cost are carried by
the client too: both are 0 in Slice 1 by fact (no model call happens yet), not
by omission — Slice 4's proposal step records them through the same client
rather than by instrumenting each stage.

Capture is best-effort in the strict sense: any failure inside a sink is
recorded on the trace and swallowed, because a broken tracing service must
never take a crawl run down with it.
"""
from __future__ import annotations

from contextlib import ExitStack, contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timezone
import json
import logging
import os
from pathlib import Path
import threading
import time
import uuid

LOG = logging.getLogger(__name__)

NEATLOGS = "neatlogs"
LOCAL = "local"

# The regional ingest endpoint. Set on init so a project never silently falls
# back to a different region's backend.
INGEST_ENDPOINT = "https://ingest.neatlogs.com"

# One crawl run is one trace: fetch -> extract -> verify -> store. The workflow
# name describes the pipeline this process runs, not the app it ships in.
WORKFLOW_NAME = "unstop-crawl-run"

_init_lock = threading.Lock()
_initialised = False


def init_neatlogs() -> bool:
    """Configure the SDK once per process. Idempotent; never raises.

    `init()` reads `NEATLOGS_API_KEY` from the environment when no key is
    passed explicitly. A second call with the same configuration is a no-op, so
    one crawl run per fixture all sharing this call is expected.
    """
    global _initialised
    if _initialised:
        return True
    with _init_lock:
        if _initialised:
            return True
        import neatlogs  # optional dependency; never required

        neatlogs.init(
            api_key=os.environ.get("NEATLOGS_API_KEY", ""),
            endpoint=INGEST_ENDPOINT,
            workflow_name=WORKFLOW_NAME,
            # The SDK's own logging is not part of deadmon's output. Its INFO
            # chatter is dropped so a crawl run's stdout stays readable; note the
            # SDK still writes one line from its atexit handler after the process
            # is done, which some runners surface as logging noise on an
            # otherwise green run.
            log_level="WARNING",
        )
        _initialised = True
        return True


@contextmanager
def _detached():
    """Suppress the ambient span for the block, so the next root is a true root.

    Only active once the SDK is installed; without it this is a no-op, which is
    what keeps tracing.py importable with no dependency at all.
    """
    try:
        from opentelemetry import context as otel_context
    except Exception:
        yield
        return
    token = otel_context.attach(otel_context.Context())
    try:
        yield
    finally:
        otel_context.detach(token)


def shutdown() -> None:
    """Drain buffered spans and stop the exporter. Called once at process exit."""
    global _initialised
    if not _initialised:
        return
    try:
        import neatlogs

        neatlogs.flush(timeout_millis=10_000)
        neatlogs.shutdown(timeout_millis=10_000)
    except Exception:  # shutdown must never break the process that called it
        LOG.warning("neatlogs shutdown failed", exc_info=True)
    finally:
        _initialised = False


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
        self._stack = ExitStack()
        self._neatlogs_trace_id: str | None = None
        self._failed = False

    # -- lifecycle --------------------------------------------------------

    @property
    def reference(self) -> str:
        return self.trace.reference

    def external_id(self) -> str | None:
        """The neatlogs trace id, when the run actually reached neatlogs."""
        return self.trace_id

    @property
    def trace_id(self) -> str | None:
        """The exported trace id, or None when tracing stayed local."""
        if self.trace.backend != NEATLOGS:
            return None
        return self._neatlogs_trace_id

    def start(self) -> "TraceClient":
        """Open the trace. One crawl run is one WORKFLOW root in neatlogs."""
        if self.trace.backend != NEATLOGS:
            return self
        try:
            init_neatlogs()
            import neatlogs

            # A crawl run is its own trace, so the root must not inherit an
            # ambient span. `crawl_corpus` opens one client per fixture without
            # closing the previous one first, so without this the second run
            # nests under the first and both report the same trace id. The
            # empty context is what tells the SDK "no parent".
            self._stack.enter_context(_detached())
            root = self._stack.enter_context(
                neatlogs.trace(f"crawl-run · {self.crawler}", kind="WORKFLOW")
            )
            context = root.get_span_context()
            if context is not None and context.trace_id:
                self._neatlogs_trace_id = format(context.trace_id, "032x")
                self.trace.reference = f"{NEATLOGS}://{self._neatlogs_trace_id}"
            root.set_attribute("neatlogs.workflow_name", WORKFLOW_NAME)
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
            with self._neatlogs_span(name, span):
                yield span
        except BaseException as exc:
            span.events.append({"error": f"{type(exc).__name__}: {exc}"})
            raise
        finally:
            span.ended_at = _now_iso()
            span.duration_ms = round((time.perf_counter() - start) * 1000, 3)

    @contextmanager
    def _neatlogs_span(self, name: str, span: Span):
        """Mirror one stage into neatlogs as a CHAIN span under the run's root.

        A stage is a fixed step in the pipeline, not a decision, so CHAIN is the
        honest kind. Attributes are stamped on exit because the caller fills them
        in while the block runs.
        """
        if self.trace.backend != NEATLOGS:
            yield None
            return
        try:
            import neatlogs

            with neatlogs.trace(name, kind="CHAIN") as remote:
                try:
                    yield remote
                finally:
                    for key, value in span.attributes.items():
                        remote.set_attribute(f"deadmon.{key}", value)
                    remote.set_attribute("deadmon.duration_ms", span.duration_ms)
        except Exception as exc:  # a lost stage must not fail the pipeline
            self.trace.error = f"neatlogs span lost: {exc}"
            LOG.warning("neatlogs span lost for %s: %s", name, exc)
            yield None

    def record_usage(self, *, tokens: int = 0, cost_usd: float = 0.0) -> None:
        self.trace.token_usage += int(tokens)
        self.trace.cost_usd += float(cost_usd)

    def close_and_link(self) -> str:
        """Persist the trace and return the reference to store on the run row."""
        try:
            self._stack.close()
        except Exception as exc:  # an exporter that cannot close must not fail the run
            self.trace.error = f"trace export failed: {exc}"
            LOG.warning("trace export failed: %s", exc)
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
