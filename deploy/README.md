# deadmon deploy notes

**Two deploys, one seam** ([ADR-0020](../docs/adr/0020-dashboard-moves-to-nextjs.md)):

| Piece | Where | What it is |
|---|---|---|
| Crawl pipeline + JSON API | EC2 t3.micro | Python, systemd, SQLite. The product. |
| Dashboard, landing, pricing | Vercel | Next.js/TypeScript, renders the JSON. |

The EC2 instance serves `/api/feed` read-only. Vercel reads it. Nothing else
crosses the boundary.

## Why two hosts

`PLAN.md` says free tiers only. A t3.micro covers the crawl - it replays
recorded fixtures with no network, so the instance does almost nothing except
serve JSON. Lambda was rejected because Slice 1's SQLite database and its
fixtures both want a filesystem that survives between runs, which turns a
scheduled invocation into a state-management problem rather than a deployment.

Next.js sits on Vercel because that is where Next belongs, and because it keeps
Node off the instance entirely.

## The web app

```bash
cd apps/web
npm install
cp .env.example .env.local     # then set NEXT_PUBLIC_DEADMON_API
npm run dev                    # http://127.0.0.1:3000
npm run build && npm run start # production
```

`NEXT_PUBLIC_DEADMON_API` is the crawl service's public base URL — the EC2
address, e.g. `http://your-instance:8080`. It is baked in at build time, so
changing hosts means a redeploy, not a restart.

With the API unreachable the pages still render: the dashboard says the crawl
service is not reachable and the landing figures fall back to an em-dash. A dead
backend reads as "no data yet", never as a broken site.

## Deploy the crawl service

## Install

Run on the instance as a user with sudo:

```bash
sudo useradd --system --home /opt/deadmon --shell /usr/sbin/nologin deadmon
sudo mkdir -p /opt/deadmon /var/lib/deadmon/traces
sudo chown -R deadmon:deadmon /var/lib/deadmon

# The code. Fixtures come along: the crawl replays them, so the instance needs
# the repo, not just the wheel.
sudo git clone <your-remote> /opt/deadmon
sudo python3 -m venv /opt/deadmon/venv
sudo /opt/deadmon/venv/bin/pip install /opt/deadmon
sudo chown -R deadmon:deadmon /opt/deadmon
```

`pip install /opt/deadmon` picks up the `deadmon-crawl` console script and the
versioned DDL from `package-data`; neither needs a `PYTHONPATH`.

### Tracing

Optional. Without it, every run is traced to a local JSON file and the dashboard
trace links still work.

```bash
sudo install -o root -g deadmon -m 0640 /dev/null /etc/deadmon/env
sudo sh -c 'echo "NEATLOGS_API_KEY=..." >> /etc/deadmon/env'
```

Install the optional extra to actually reach neatlogs:

```bash
sudo /opt/deadmon/venv/bin/pip install '/opt/deadmon[tracing]'
```

> **Do not `pip install neatlogs` unpinned.** The `tracing` extra carries a
> `>=1.4.26` floor for a reason. An older SDK's `init()` takes only
> `(api_key, tags, debug)`, so `tracing.py`'s call with `endpoint=` and
> `workflow_name=` raises `TypeError` inside the try block. The fail-safe
> swallows it and falls back to the local sink, so **the crawl looks completely
> healthy while every trace stays local** - and the log line to look for is
> `neatlogs unavailable`. Check it is really tracing:
>
> ```bash
> sudo journalctl -u deadmon | grep -c 'neatlogs unavailable'   # want 0
> curl -s localhost:8080/runs.json | grep -o 'neatlogs://' | head -1
> ```

`tracing.py` only picks that sink when the package imports **and** the key is
set, and it swallows any failure - a broken tracing service must never take a
crawl run down with it (ticket 07). That property is correct and is why this
misconfiguration hides so well.

The SDK supports Python `>=3.10,<3.14`, so the venv must not be a 3.14
interpreter; on 3.14 the install fails and tracing silently stays local.
Check with `/opt/deadmon/venv/bin/python -c "import sys; print(sys.version)"`.

### The service

```bash
sudo cp deploy/deadmon.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now deadmon
sudo systemctl status deadmon
sudo journalctl -u deadmon -f
```

## Verify

```bash
# on the instance
curl -s localhost:8080/api/feed | head -c 300      # the seam Next.js reads
curl -s localhost:8080/          | grep -c 'card'   # the HTML fallback still renders
sudo systemctl is-active deadmon                   # active
```

`/` still serves the server-rendered HTML dashboard. That route is kept on
purpose: the pipeline stays demonstrable with no Node toolchain and no network,
which is the safety net if the Vercel side is down on demo day.

## Three things that will bite you

**Port 8765 is reserved on Windows** (OS exclusion range 8700-8799), so the
original default dies with `WinError 10013` when you record a demo on a dev
machine. 8080 is used instead. On Linux 8765 is fine - this only bites the
recording, not the instance.

**The Python command needs no `PYTHONPATH`.** Before the packaging commit it
only ran with `PYTHONPATH=src` set by hand. If you see
`ModuleNotFoundError: No module named 'deadmon'`, the install step was skipped.

**`NEXT_PUBLIC_DEADMON_API` is build-time.** Pointing the app at a different
instance needs a Vercel redeploy, not a restart.

## Security group

Inbound: port 8080 from your own IP, or from anywhere only while recording.
Outbound: none needed today - the crawl replays recorded fixtures.

```bash
aws ec2 authorize-security-group-ingress --group-id sg-XXXX \
    --protocol tcp --port 8080 --cidr "$(curl -s ifconfig.me)/32"
```

The API is read-only and unauthenticated, and the whole app has no accounts
(Slice 1 runs with exactly one subscriber). Do not expose 8080 to `0.0.0.0/0`.

## Not yet deployed

This covers Slice 1 only. Slice 4's self-heal needs to commit to this repo from
the instance, which means the deploy user needs a git identity and push access -
deliberately left out rather than quietly given wide credentials.