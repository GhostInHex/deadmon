# deadmon

**Like nodemon, but for deadlines.** An agent that never misses a deadline. Built for [neatHack](https://neatlogs.com/hackathon).

deadmon crawls hackathon platforms daily, extracts dates / prizes / eligibility, **verifies each listing is still live** (page up, deadline parses, genuinely online), filters against your profile, and alerts you before registration closes - on a dashboard and via Telegram.

The agent part: when a platform changes its layout and a scraper breaks, the Scout **detects the break, diagnoses it from the failing run's trace, proposes a fix using its own repo as context, validates the fix in a sandbox, and commits it** - healing its own code. You find out from the heal log, not from a week of silently missed listings.

## Repository contents

Documentation and specs, plus the Slice 1 implementation of the crawl pipeline.

```
docs/
  PRD.md           product requirements (Matt Pocock to-spec method)
  PLAN.md          48-hour build plan, slices, evidence checklist, demo script
  SPONSORS.md       setup guides for neatlogs, Entire, cfo.ai + sponsor links
  LLM_ACCESS.md     shared LiteLLM gateway: base URL, models, key + $20 budget
src/deadmon/       the pipeline: adapters, verification, storage, tracing, dashboard, crawl
tests/             pytest suite — deterministic, no network (fixtures/ is the corpus)
deploy/            systemd unit + install notes for running it on one instance
```

**Slice 1 — one platform, end to end.** The Unstop crawler replays its recorded
fixtures with no network, verifies what it extracted, stores it, traces the crawl
run, and renders live listings as cards with verdict badges (`live` /
`unverified` / `closed`) on one server-rendered page.

```bash
pip install -e ".[test]"

deadmon-crawl                          # crawl the corpus, then serve http://127.0.0.1:8080/
deadmon-crawl --reset --no-serve       # crawl only, printing one line per crawl run
```

`python -m deadmon.crawl` works too, but only after `pip install` — the package
lives under `src/` and is not importable from a bare checkout.

> **Use 8080, not 8765.** 8765 falls inside a Windows reserved port range
> (8700–8799) and the server dies with `WinError 10013` on a Windows dev
> machine. 8080 is safe on both.

Dedupe across platforms, eligibility filtering, alerts and the scheduler are
Slices 2 and 3.

## Deploy

One instance, one service — see [`deploy/README.md`](deploy/README.md).

```bash
sudo cp deploy/deadmon.service /etc/systemd/system/
sudo systemctl daemon-reload && sudo systemctl enable --now deadmon
```

Set `NEATLOGS_API_KEY` in `/etc/deadmon/env` to trace runs to neatlogs; without
it, traces fall back to a local JSON sink and the dashboard links still resolve.

## Docs

- [`docs/PRD.md`](docs/PRD.md) - what we're building and why
- [`docs/PLAN.md`](docs/PLAN.md) - the 48h build plan
- [`docs/SPONSORS.md`](docs/SPONSORS.md) - sponsor setup, usage, and links
- [`docs/LLM_ACCESS.md`](docs/LLM_ACCESS.md) - shared LLM gateway access (LiteLLM)

## The three mandatory tools (25% of the marks)

| Tool | Role in this project |
|---|---|
| **neatlogs** | Traces every crawl run; before/after trace pair proves v1 → v2 improvement |
| **Entire** | Captures coding sessions as git checkpoints - including the self-heal commits |
| **cfo.ai (Ari)** | Business plan: pricing, costs, revenue, runway - saved in repo, covered in demo |

## Status

Slice 1 is complete and deployable: the Unstop crawl runs end to end against the
recorded corpus, 109 tests pass with no network, and the dashboard renders live
listings with verdict badges. Next is Slice 2 (more platforms, dedupe,
eligibility) per `docs/PLAN.md`.
