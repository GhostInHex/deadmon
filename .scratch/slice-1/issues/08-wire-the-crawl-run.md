# 08: The crawl run: wire adapter → verification → storage → trace behind one command

**What to build:** The demo moment. One command runs the Unstop crawler against
the recorded fixture and the real dashboard fills from real crawl output — a
candidate extracted, verified, stored, traced, and rendered as a card in the
feed. This is where the contracts land and compose; it is deliberately last,
because every module it wires has already been proven against its own seam.

**Blocked by:** 03, 04, 05, 07.

**Status:** open
**Triage:** blocked

- [ ] One command runs the Unstop crawler end to end against the recorded fixture, with no network access
- [ ] The run produces at least one live listing rendered as a card in the feed, plus one verdict of each of the other two kinds where the fixture set supports it
- [ ] The run writes one crawl-run row, one trace, and a trace link visible on the dashboard
- [ ] Run history shows the run with its per-crawler health figures
- [ ] The trace's live-found and closed-found counts agree with what the dashboard shows
- [ ] No module in the pipeline knows which platform it is talking to
- [ ] The whole suite is green with no network access
- [ ] `python tools/check_docs.py` still passes
- [ ] The slice is demoable as: I crawl Unstop and see live listings with badges

## Comments
