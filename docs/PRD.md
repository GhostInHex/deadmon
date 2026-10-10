# PRD: deadmon - an agent that never misses a deadline

> Written with Matt Pocock's `to-spec` (to-prd) method: synthesized from conversation, no interview. Framed from the user's perspective; technical concerns live in Implementation Decisions.
> Status: draft - validate before breaking into issues.
> Event: neatHack (neatlogs), 48h build Oct 10–11 2026, submissions Oct 12.

---

## Problem Statement

As a student developer, I keep missing hackathons I would have joined. Discovery is scattered across seven platforms (Devfolio, Devpost, Unstop, Hack2skill, HackerEarth, GenAI.works, HackerRank), listings go stale, registration deadlines are buried three clicks deep, and "online" filters lie. By the time I hear about a good one, registration has closed. I end up doing what I did on Oct 8 - asking an assistant to sweep everything manually, every single morning.

Worse, the tools that aggregate hackathons are dumb lists: they show expired events, duplicate the same hackathon across platforms, and never tell me whether *I'm* eligible or whether the deadline is real. I don't need another list. I need something that watches the platforms for me, verifies what's actually live, and taps me on the shoulder before a deadline closes - and I need to trust it enough to stop checking manually.

## Solution

deadmon is an autonomous agent that crawls hackathon platforms daily, extracts dates / prizes / eligibility / mode, **verifies each listing is still live** (page up, deadline parses, genuinely online), filters listings against my profile, and maintains a dashboard plus deadline alerts. It runs on a schedule without me watching it.

The part that makes it an *agent* rather than a cron job with a scraper: when a platform changes its layout and a scraper breaks, the Scout detects the break, diagnoses it from the failing run's trace, proposes a fix using the repo's own scraper code as context, validates the fix against the live page, and commits it - healing itself. I find out from the heal log, not from a week of silently missed listings.

From my perspective, the experience is: I open the dashboard, I see verified-live hackathons with countdowns I can trust, I get alerted at 7 days / 3 days / 24 hours before registration closes, and when a platform breaks the site, the Scout fixes its own scraper and tells me it did.

---

## User Stories

### Discovery & listings

1. As a student developer, I want to see all upcoming hackathons from every tracked platform in one dashboard, so that I stop opening seven tabs every morning.
2. As a student developer, I want each listing to show registration-close date, start date, mode (online/hybrid/offline), prize pool, and team-size rules, so that I can judge fit at a glance.
3. As a student developer, I want listings deduplicated across platforms (the same hackathon on Devfolio and Unstop appears once), so that the dashboard isn't noisy.
4. As a student developer, I want to filter listings by mode, prize minimum, and date range, so that I only see what's relevant this month.
5. As a student developer, I want expired or cancelled listings to disappear automatically, so that I never get excited about a dead event again.

### Verification (trust)

6. As a student developer, I want every listing to carry a verification badge ("verified live 2h ago") linked to the primary source page, so that I can trust the deadline without re-checking it myself.
7. As a student developer, I want the Scout to re-verify deadlines on every crawl, so that a moved deadline gets caught instead of silently going stale.
8. As a student developer, I want listings whose verification failed to be marked "unverified" rather than deleted or shown as fact, so that I'm never misled.
9. As a student developer, I want to see *why* a listing was filtered out (e.g. "offline-only", "students ineligible"), so that I trust the filter instead of suspecting it dropped something good.

### Eligibility & personal fit

10. As a student developer, I want to set my profile once (student status, country, interests, team preference), so that the Scout filters to hackathons I can actually enter.
11. As a student developer, I want the Scout to flag listings that need a team vs allow solo, so that I can plan ahead.
12. As a student developer, I want a "worth applying" score or tag per listing based on my criteria (online, student-eligible, real prizes, skill-relevant), so that triage is instant.

### Alerts (never miss a deadline)

13. As a student developer, I want an alert 7 days, 3 days, and 24 hours before a matching hackathon's registration closes, so that I never miss a deadline again.
14. As a student developer, I want alerts delivered where I'll actually see them (Telegram), so that they don't rot in an inbox.
15. As a student developer, I want to mute or snooze alerts per listing, so that I'm not nagged about events I've already decided on.
16. As a student developer, I want an alert when a *new* matching hackathon appears, so that discovery is push, not pull.

### Self-healing (the agent part)

17. As a Scout operator, I want to be notified when a platform's layout breaks a scraper (with the failing trace linked), so that I know something needs attention.
18. As a Scout operator, I want the Scout to attempt a fix itself first and only escalate if the fix fails validation, so that I don't wake up to do routine maintenance.
19. As a Scout operator, I want every self-heal recorded in a heal log (what broke, what changed, validation result), so that I can audit what the agent did to its own code.
20. As a Scout operator, I want a healed scraper to backfill the listings it missed while broken, so that no deadlines slip through the gap.

### Observability & debugging

21. As a Scout operator, I want every crawl run linked to its neatlogs trace from the dashboard, so that I can debug a flaky platform in one click.
22. As a Scout operator, I want per-platform run history (success rate, listings found, duration, cost), so that I can see which sources are healthy.
23. As a Scout operator, I want to see inference cost per crawl, so that I can confirm the free-model unit economics hold.

### Community tier (business)

24. As a dev-community admin, I want to run the Scout for my community with our own filter profile, so that my members get relevant alerts.
25. As a dev-community admin, I want a weekly digest of upcoming deadlines for my community, so that I don't have to curate it by hand.
26. As a student developer on the free tier, I want one alert profile and dashboard access free forever, so that I can use the Scout without paying.

---

## Implementation Decisions

### Architecture: pipeline of small modules behind one orchestrator

- The Scout is a **scheduled agent loop**, not a chatbot. A scheduler triggers a crawl run; an orchestrator walks each platform through the same stages: **fetch → extract → verify → dedupe → filter → alert**. Each stage is a module with a narrow interface so stages can be tested and swapped independently.
- **Scraper interface (the #1 seam):** every platform adapter implements the same contract - given the platform, return normalized listings. The orchestrator never knows which platform it's talking to. New platforms are added by adding one adapter, nothing else changes.
- **Verification is a pipeline stage, not an afterthought.** A listing is not shown until it passes: liveness (source page responds), date sanity (registration-close parses to a future date in a known timezone), mode check (page actually indicates online/hybrid/offline), and dedupe (fingerprint match against existing listings). Failed verifications mark the listing unverified; they never silently promote it.
- **State lives in SQLite.** Listings, crawl runs, verifications, alerts, and heal events are all rows. The agent resumes across restarts from the database - a killed run picks up where it left off. No in-memory-only state that matters.
- **Self-heal loop:** a watchdog watches scraper health per platform (selector yields zero listings twice in a row, schema validation failures spike, HTTP pattern changes). On trigger it: captures the failing evidence (page snapshot + neatlogs trace link) → proposes a selector/extraction fix using the repo's existing scraper code plus the new page structure as context → validates the fix against the live page in a sandbox (no writes) → commits the fix, which Entire captures as a checkpoint → backfills missed listings. If validation fails twice, it escalates to the operator with everything attached instead of guessing further.
- **Alerts via Telegram Bot API** (free, minutes to set up). Dashboard alert feed mirrors them. Lead times: 7d / 3d / 24h before registration close, plus new-match alerts.
- **Dashboard is one server-rendered page** (no SPA framework): verified listings table with countdowns and badges, run history with trace links, heal log, per-platform health. Speed of build beats UI ambition.
- **Models: free tiers only** (e.g. Gemini free-tier API). This is both a personal constraint and the business story - near-zero inference cost makes the freemium unit economics work. Model choice is behind a thin wrapper so it can be swapped without touching the pipeline.

### Data & schema

- **Listing:** platform, title, source URL, registration-close (timestamp + timezone), start date, mode, prize summary, team-size rule, eligibility notes, fingerprint (for dedupe), verification status + verified-at, first-seen-at.
- **Crawl run:** platform, started/finished at, status, listings found, neatlogs trace ID.
- **Alert:** listing ref, type (new-match / 7d / 3d / 24h), sent-at, channel, muted flag.
- **Heal event:** platform, what broke (evidence), fix summary, validation result, commit ref, backfilled count.
- Timezones are normalized at extraction; a date that can't be normalized blocks verification (fail closed, never guess a deadline).

### External contracts

- **neatlogs:** every crawl run is a trace; spans per platform and per pipeline stage; token/cost/latency captured automatically. The trace ID is stored on the run row and linked from the dashboard.
- **Entire:** CLI enabled in the repo from the first commit; every commit (human or self-heal) lands with Entire checkpoints. Evidence artifact: entire-graph output / checkpoint list screenshots.
- **cfo.ai (Ari):** used during the build to produce the business plan (pricing tiers, costs, revenue, runway); the plan ships in the repo and is covered in the demo.
- **Telegram Bot API:** outbound alerts only. No inbound commands in scope (maybe `/mute` later - out of scope).
- Scraping posture: polite by design - prefer structured endpoints/RSS where a platform offers them, fall back to HTML; rate-limit per platform, cache aggressively, identify with a user agent. The Scout must never hammer a site.

### What "done" means for the hackathon build

- 3 platform adapters live (Devfolio, Unstop, Devpost); architecture supports N.
- Full pipeline green on a scheduled run: extract → verify → dedupe → filter → dashboard + Telegram alert.
- One demonstrated self-heal: deliberately break a selector, show detection → fix → validation → commit → backfill.
- Before/after neatlogs trace pair with compared numbers (v1 naive vs v2 verified+healing).
- Dashboard deployed or runnable with one command; demo video ≤3 min covering neatlogs, Entire, cfo.ai.

---

## Testing Decisions

- **What makes a good test here:** deterministic, no network. A good test feeds a recorded page fixture through a module and asserts on *external behavior* - listings out, verification verdicts, alerts emitted - never on implementation details like which selector string was used.
- **Test seams (highest first):**
  1. **Scraper interface** - the primary seam. Every adapter is tested against recorded HTML fixtures (healthy page, changed-layout page, dead page), never the live site. A fixture corpus per platform is the single most valuable test asset.
  2. **Verification pipeline** - fixture listings in each state (live, expired, unparseable date, mode mismatch) assert the correct verdict. This is where "fail closed" is proven.
  3. **Dedupe** - synthetic duplicate listings across two fake platforms assert single output.
  4. **Alert dispatcher** - a fake sink captures emitted alerts; assert lead-time logic (7d/3d/24h) and muting without touching Telegram.
  5. **Self-heal loop** - a deliberately broken fixture asserts: break detected → fix proposed → sandbox validation passes → heal event recorded. The live-page validation step is tested with a fixture, not the network.
- **Which modules get tests:** all five seams above, plus the scheduler's resume-from-DB behavior (kill mid-run, assert no duplicate alerts).
- **Prior art:** greenfield repo - no existing tests to follow. Use pytest with a `fixtures/` corpus of recorded pages. The fixture corpus doubles as the demo's safety net (demo runs against fixtures if the network misbehaves).

---

## Out of Scope

- Scholarships, internships, and jobs tracking (a future product, not this build).
- Automatic registration for hackathons (manual registration stays manual - safer with platform ToS and with how I actually register).
- Email/SMS/push alert channels beyond Telegram + dashboard.
- Inbound Telegram commands (e.g. `/mute`) - muting happens in the dashboard.
- Multi-user accounts and auth; the community tier is a second filter profile + digest, not a multi-tenant system.
- A public API.
- Historical backfill beyond 90 days.
- Non-English listing sources.
- Mobile app.

---

## Further Notes

### How this maps to the neatHack rubric

- **The agent (30%):** the self-heal loop is the centerpiece - planning (crawl plan per platform), tool use (fetchers, parsers, validators), state (SQLite resume), recovery (heal loop), verification (pipeline stage), iteration (v1→v2 traces).
- **Tool trio (25%):** neatlogs traces every run with a before/after pair and compared numbers (miss rate, false positives, cost); Entire checkpoints capture both human commits and self-heal commits; cfo.ai produces the freemium business plan.
- **Demo (20%):** scripted arc - dashboard → live crawl → deliberately broken selector → self-heal → trace numbers → business plan. Record it; don't run it live.
- **Building in public (15%):** 4 #neatHack posts (kickoff, day-1 trace screenshot, the self-heal moment, final demo).
- **Usefulness/originality (10%):** I am the first user - it replaces my manual 9 AM sweep.

### Risks & mitigations

- **Platform ToS / blocking:** mitigate with polite crawling (rate limits, caching, structured endpoints first). If a platform blocks, that adapter degrades to "unverified" rather than breaking the run.
- **Deadline parsing ambiguity:** fail closed - unverified badge, never a guessed date. Primary-source link always shown.
- **Demo flakiness:** every demo beat has a fixture-backed fallback; the video is recorded, not live.
- **Scope creep into scholarships:** explicitly out of scope (see above).

### Business inputs for cfo.ai (Ari)

- Tiers: Free (1 alert profile, dashboard) / Community (dev clubs & college communities - shared profile + weekly digest, ~₹399–499/mo) / Pro (power users - unlimited profiles, API-ish exports, later).
- Costs: inference (free-tier models → near-zero), hosting (free tier / small VPS), Telegram (free).
- Revenue logic: communities pay to stop hand-curating deadline digests; students convert via community exposure.
- Runway: solo builder, near-zero burn - the story is margin, not scale.

### Open questions (resolve before build)

1. Which 3 platforms first? (Recommendation: Devfolio, Unstop, Devpost - highest relevance to my criteria.)
2. Telegram bot token - create before the event (2 min, allowed pre-work).
3. neatlogs free-tier limits - confirm trace retention covers the event + judging window.
