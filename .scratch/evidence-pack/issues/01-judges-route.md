# 01: Add judges route with rubric weights and verify commands

**What to build:** the end-to-end behaviour this ticket makes work,
from the user's perspective, not a layer-by-layer implementation list.

A judge opens `/judges` and scores deadmon in 60 seconds: a table maps
each claim to a rubric weight, copy-paste commands verify each claim,
a v1 vs v2 trace pair shows numbers, a receipt count with a hash check
proves evidence was not edited.

**Blocked by:** None (can start immediately).

**Status:** ready-for-agent

- [ ] `/judges` route renders in the Next.js app
- [ ] Each row maps a claim to a rubric weight
- [ ] Copy-paste commands verify each claim without reading code
- [ ] v1 vs v2 trace-pair table shows before/after numbers
- [ ] Receipt count plus hash check command present
- [ ] Copy uses glossary words: crawler, proposal, card, verdict
