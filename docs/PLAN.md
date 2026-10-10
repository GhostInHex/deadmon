# deadmon - 48h build plan (neatHack, Oct 10–12 2026)

Companion to `deadmon-prd.md`. Solo build, free tiers only. All repo commits must be dated Oct 10–12 - **create the repo at kickoff, not before.**

---

## Pre-event (now → Sat Oct 10, 9:00 AM IST) - no project code yet

- [ ] Register on Luma (team name), join Discord, complete web check-in early (first 350 checked-in teams get the **$25 AWS allowance**, not money credits - a restricted IAM login, us-east-1, EC2/Lambda/IAM/LBs only; see docs/SPONSORS.md (AWS allowance). Claim it while the link lasts)
- [ ] Create accounts: neatlogs (confirm free-tier trace retention), Entire (entire.io), cfo.ai
- [ ] Create Telegram bot via BotFather, save token (allowed pre-work, not project code)
- [ ] Get free API keys: Gemini AI Studio (or chosen free model), Tavily or SerpApi free tier (fallback enrichment only)
- [ ] Read: neatlogs-py SKILL.md (init/instrumentation order), Entire CLI (`entire enable`), cfo.ai Ari basics
- [ ] Sketch on paper: Listing schema fields, verification verdicts, the 5 test seams from the PRD
- [ ] Record 2–3 sample pages per platform (Devfolio, Unstop, Devpost) as HTML fixtures - legal, and they become your test corpus + demo safety net
- [ ] Draft the 4 #neatHack post texts in advance (fill in screenshots live)

---

## Build slices (tracer-bullet: each slice is end-to-end and demoable alone)

Work slices in this order. Stop each slice when it's green; don't start the next until the previous is demoable.

### Slice 1 - One platform, end to end (Sat, ~6h)
Devfolio adapter → extract → verify → SQLite → dashboard page showing listings with verification badges. One neatlogs trace per run, linked from the dashboard. **Demoable:** "I crawl Devfolio and see verified listings."

### Slice 2 - Pipeline hardening (Sat, ~5h)
Add Unstop + Devpost adapters behind the same scraper interface. Dedupe across platforms. Eligibility filter with your real profile (online, Indian-student-eligible, real prizes, AI/web-relevant). Scheduler runs the full loop. **Demoable:** "three platforms, one deduped, filtered feed."

### Slice 3 - Alerts (Sat eve / Sun AM, ~3h)
Telegram dispatcher + dashboard alert feed. Lead-time logic (7d/3d/24h) + new-match alerts + per-listing mute. Fake-sink tests for the timing logic. **Demoable:** phone buzzes with a deadline alert.

### Slice 4 - The self-heal loop (Sun, ~7h) ← the centerpiece, protect this time
Watchdog (zero-listings twice / schema failures) → snapshot + trace evidence → fix proposal using repo scraper code as context → sandbox validation against live page (no writes) → commit (Entire checkpoint) → backfill. Deliberately break a selector to prove it. **Demoable:** "I broke the Devfolio adapter; watch it heal itself."

### Slice 5 - Trace pair + measurement (Sun eve, ~3h)
Freeze a v1 (naive: no verification, no healing) run, capture its trace. Run v2, capture its trace. Tabulate: listings found, miss rate, false positives, cost, duration. These numbers go in the repo, the demo, and the submission. **Demoable:** the before/after comparison.

### Slice 6 - Business + evidence packaging (Mon AM, ~3h)
Ask cfo.ai Ari for the business plan (tiers, costs, revenue, runway); save it to the repo. Entire-graph screenshots. Write the README as the submission narrative (problem → agent → evidence → business).

### Slice 7 - Demo video + submission (Mon PM, ~4h)
Record (don't live-demo) the ≤3 min video per the script below. Post #neatHack #4. Submit as X quote-post of the official neatlogs submission post, 7:00–11:55 PM IST, with repo + demo link.

**Total work ≈ 31h → ~17h buffer/sleep across the 48h window.** If a slice overruns by >2h, cut scope per the cut list below, never by skipping Slice 5 (the trace pair is 25% of your marks).

### Scope cut list (in order, if time runs short)
1. Third platform adapter → ship with two (Devfolio + Unstop)
2. Weekly community digest → keep per-user alerts only
3. Dashboard polish → table + badges is enough
4. Never cut: verification stage, self-heal demo, trace pair, cfo.ai plan, demo video

---

## Evidence checklist (tick as you go - judges explicitly ask for these)

- [ ] Public repo, all commits dated Oct 10–12
- [ ] Before/after neatlogs trace pair with compared numbers (in repo + demo)
- [ ] Trace links/screenshots on dashboard run history
- [ ] Entire checkpoints / entire-graph output screenshots (human commits + self-heal commit)
- [ ] cfo.ai business plan in repo (pricing, costs, revenue, runway)
- [ ] Recorded run showing an action failing and the agent recovering (the self-heal)
- [ ] #neatHack public posts (4) - links saved in repo
- [ ] Demo video ≤3 min covering neatlogs, Entire, cfo.ai explicitly

---

## Demo video script (≤3 min, recorded)

- **0:00–0:30** - The problem: missed deadlines, seven tabs, stale aggregators. (Show your own 9 AM manual sweep.)
- **0:30–1:00** - Architecture: scheduler → per-platform adapters → verify → dedupe → filter → alerts; where neatlogs traces, where Entire checkpoints, where cfo.ai planned the business.
- **1:00–2:00** - Live (recorded) run: dashboard with verified badges → Telegram alert arrives → **break a selector on purpose → watchdog fires → self-heal → backfill**, all narrated.
- **2:00–2:45** - Before/after trace numbers (v1 vs v2) + the cfo.ai business plan (tiers, near-zero inference cost).
- **2:45–3:00** - Close: "an agent that never misses a deadline - and fixes itself when the web changes."

## Building in public (15% of marks - schedule it, don't improvise)

> Bonus: the $500 **community winner** is judged separately and **stacks with a
> top-3 placement** - it rewards genuine discussion, not follower count. Treat
> every post below as a bid for it.

1. **Sat kickoff:** "Building deadmon for #neatHack - an agent that never misses a deadline. Day 1: one platform end-to-end."
2. **Sat eve:** trace screenshot - "every crawl run traced with neatlogs; already caught 2 stale deadlines."
3. **Sun:** the self-heal moment - "Devfolio changed their layout mid-hackathon. My scraper fixed itself. Trace + commit inside."
4. **Mon:** final demo link + repo. Quote-post the official submission post for the actual entry.

---

## Risk register

| Risk | Mitigation |
|---|---|
| Platform blocks scraping | Polite crawling (rate limits, cache, structured endpoints first); adapter degrades to "unverified", run continues |
| Deadline parses ambiguously | Fail closed → unverified badge; primary-source link always shown |
| Self-heal loop eats the day | Timebox to 7h; fallback demo = recorded fixture run |
| Demo gremlins | Every beat recorded against fixtures; video is pre-recorded, never live |
| Scope creep (scholarships!) | Out of scope per PRD - say no |

---

## After the event (only if it wins / you keep it)

- Add remaining platforms (Hack2skill, HackerEarth, GenAI.works, HackerRank)
- Inbound Telegram commands (/mute, /snooze)
- Community tier: shared profile + weekly digest for dev clubs
- Dogfood it daily - it replaces the 9 AM manual sweep
