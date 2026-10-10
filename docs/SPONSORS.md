# Sponsor guide - neatHack mandatory tools

All three tools below are **required** by the challenge: every project must use
neatlogs, Entire, and cfo.ai, each with a clear role, and the demo video must
explicitly cover all three (architecture, implementation, runtime, reasoning,
result). This doc is the setup + usage reference.

## Judging criteria (how marks are weighted)

| Criterion | Weight |
|---|---|
| The agent | 30% |
| Use of neatlogs, Entire and cfo.ai | 25% |
| Demo video | 20% |
| Building in public | 15% |
| Usefulness and originality | 10% |

Note: the 25% is for **all three tools combined**, not 25% each.

## Prizes ($19,000 total)

$4,000 in cash, plus partner credits and neatlogs Pro.

| Placement | Cash | Dodo Payments credits | neatlogs Pro |
|---|---|---|---|
| 1st place | $2,000 | $5,000 | 3 months (worth $1,500) |
| 2nd place | $1,000 | $3,000 | 3 months (worth $1,500) |
| 3rd place | $500 | $1,000 | 3 months (worth $1,500) |
| Community winner | $500 | - | - |

**Community winner:** a separate award for the project that generates the
strongest genuine community interest during the hackathon. You can win it
**alongside a top-three placement**. Judged on product/demo quality, launch &
content quality, shares & discussion, and genuine excitement - *not* follower
count. Bought likes or bot activity disqualify a team. (Partner usage is not
part of community-winner scoring.)

## 1. neatlogs - observability for the agent (part of the 25% "use of the tools")

**What it is:** tracing/observability platform for AI agents. Every run is
captured: model and tool calls with inputs/responses, state changes, retries,
failures, latency, token usage, and cost. Tagline: *"the fastest path from
failure to fix."*

**Role in deadmon:** every crawl run is a trace; every pipeline stage
(fetch → extract → verify → dedupe → filter → alert) is a span. The
**before/after trace pair** (v1 naive vs v2 verified + self-healing, with
compared numbers) is the core evidence for the tools criterion.

**Setup:**
```bash
pip install neatlogs          # already in requirements.txt
```
1. Sign up at https://neatlogs.com and create a free API key (dashboard → API keys).
2. Put it in `.env` as `NEATLOGS_API_KEY`.
3. In code, call `init_neatlogs()` (see `scout/observe.py`) **before importing
   any LLM library** - auto-instrumentation patches on import, so order matters.
4. End scripts with flush/shutdown; long-running servers init once at startup.

**Where it's wired:** `scout/observe.py` (`init_neatlogs()`, `span()`),
`scheduler.py` (trace per platform run, spans per stage), `verify.py`
(spans per check), `selfheal.py` (spans per heal step).

**Evidence to collect:** trace links for every run (stored on the run row,
linked from the dashboard), the v1/v2 trace pair with numbers
(listings found, miss rate, false positives, cost, duration), screenshots for
the repo and the demo.

## 2. Entire - session checkpoints for the build (part of the 25% "use of the tools")

**What it is:** a developer platform that captures AI agent coding sessions and
links them to git commits as **checkpoints** - a searchable record of how the
code was written, stored on the `entire/checkpoints/v1` branch. Works with
Claude Code, Cursor, Codex, Copilot, Gemini, and others.

**Role in deadmon:** twofold -
- Your own coding sessions while building are captured as checkpoints
  (evidence you built with an agent loop).
- The **self-heal loop commits its own fixes**, and Entire captures those too:
  an agent's sessions, building an agent, fixing code. The entire-graph output
  is a beautiful artifact for the demo.

**Setup:**
```bash
# macOS/Linux via Homebrew, or: go install github.com/entireio/cli/cmd/entire@latest
brew tap entireio/tap
brew install entireio/tap/entire

cd deadmon
entire enable          # installs git hooks; run this BEFORE your first commit
entire status          # verify it's active
```
Do this right after cloning, before writing any code. Every commit from then
on carries a checkpoint.

**Evidence to collect:** `entire-graph` output / checkpoint list screenshots
(human commits + at least one self-heal commit), saved in the repo and shown
in the demo.

## 3. cfo.ai (Ari) - the business plan (part of the 25% "use of the tools")

**What it is:** an AI CFO agent ("Ari") for founders - connects to your stack,
builds a live financial model, and answers questions about pricing, costs,
revenue, runway, and scenarios.

**Role in deadmon:** produce the business plan that ships in the
submission - pricing tiers, costs, revenue logic, runway. Ours:
- **Free** - 1 alert profile + dashboard (acquisition)
- **Community** - dev clubs & college communities: shared profile + weekly
  digest (~₹399–499/mo)
- **Pro** - power users (later)
- **Costs:** free-tier models → near-zero inference; free-tier hosting;
  Telegram free. **The story is margin, not scale.**

**Setup:** sign up at https://cfo.ai, ask Ari to model the plan above
(pricing, costs, revenue, runway), export/save it into the repo
(`docs/business-plan.md`), and cover it in the demo video (2:00–2:45 mark).

## Sponsor & partner sites

| Who | Site | Why it matters here |
|---|---|---|
| neatlogs (host) | https://neatlogs.com | Hackathon host; observability platform; API keys + docs |
| neatHack page | https://neatlogs.com/hackathon | Challenge statement, marking scheme, deadlines |
| Entire (sponsor) | https://entire.io | Session checkpoints; CLI install |
| cfo.ai (sponsor) | https://cfo.ai | Ari, the AI CFO; business plan |
| AWS (partner) | - | 5,000 credits for the first 350 checked-in teams - do web check-in early |
| Crustdata (partner) | - | 5,000 credits per participant |
| Dodo Payments (partner) | - | Prize credits for top 3 only: $5k (1st) / $3k (2nd) / $1k (3rd) |

## Judging-evidence checklist (where each artifact comes from)

- [ ] Before/after neatlogs trace pair + compared numbers → **neatlogs**
- [ ] Trace links/screenshots on dashboard run history → **neatlogs**
- [ ] Entire checkpoints / entire-graph output → **Entire**
- [ ] Business plan (pricing, costs, revenue, runway) in repo → **cfo.ai**
- [ ] Failing → recovering run (self-heal) → **neatlogs trace + Entire commit**
- [ ] #neatHack public posts → your X account
- [ ] Public repo, commits dated Oct 10–12 → this repo
