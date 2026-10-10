# deadmon

**Like nodemon, but for deadlines.** An agent that never misses a deadline. Built for [neatHack](https://neatlogs.com/hackathon).

deadmon crawls hackathon platforms daily, extracts dates / prizes / eligibility, **verifies each listing is still live** (page up, deadline parses, genuinely online), filters against your profile, and alerts you before registration closes - on a dashboard and via Telegram.

The agent part: when a platform changes its layout and a scraper breaks, the Scout **detects the break, diagnoses it from the failing run's trace, proposes a fix using its own repo as context, validates the fix in a sandbox, and commits it** - healing its own code. You find out from the heal log, not from a week of silently missed listings.

## Repository contents

This repository currently holds the **project documentation and specs**. Implementation code has been removed.

```
docs/
  PRD.md           product requirements (Matt Pocock to-spec method)
  PLAN.md          48-hour build plan, slices, evidence checklist, demo script
  SPONSORS.md      setup guides for neatlogs, Entire, cfo.ai + sponsor links
  LLM_ACCESS.md    shared LiteLLM gateway: base URL, models, key + $20 budget
```

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

Documentation and planning stage for neatHack (Oct 10–12, 2026). Build order: `docs/PLAN.md` → slices 1–7.
