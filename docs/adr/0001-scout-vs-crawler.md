# Scout is the whole loop; the crawler is the per-platform unit

deadmon's PRD used "Scout" for both the scheduled agent loop and the per-platform unit of work. Settled on: **Scout** = the whole scheduled loop (one per system), **crawler** = one crawl run against one platform (`Devfolio crawler`), **adapter** = the scraper code behind the scraper interface.

This matters because a heal event must name the exact thing that broke. With one word for both, the heal log reads "Scout healed", which hides which of three adapters failed and makes the heal log useless for its stated purpose — per-platform health history.

## Considered Options

- **Drop "Scout" entirely**, call everything a crawler. Rejected: the PRD and demo narrative both lean on "the Scout heals itself", and the person-facing story is the agent, not the per-platform worker.
- **Keep Scout ambiguous**, document the intended reading. Rejected: ambiguity survives until 1am mid-Slice-4, when nobody re-reads the glossary.

## Consequences

A heal event's `platform` field refers to a **crawler**. The dashboard's per-platform health is **per-crawler**. Anywhere a name is generated programmatically, "crawler" is the term — not "agent", "worker", or "Scout".