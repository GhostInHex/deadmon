# Operations runbook

One page for "is it up, and what do I check". Everything here was verified
against the live instance while deploying it.

## Is it up?

```bash
curl -s http://<instance>:8080/api/feed | head -c 200
```

`{"feed": [...], "needs_attention": [...], "runs": [...]}` means healthy. An
empty body or a connection error means the service is down; go to the service
section below.

## The one check that catches almost everything

```bash
curl -s http://<instance>:8080/api/feed | grep -o 'neatlogs://' | head -1
```

**A hit means tracing is live. No hit means every trace is `local://` and you
are debugging in the dark** — which is exactly how this instance ran for an hour
after it looked perfectly healthy.

Three things cause that, in the order they actually happen:

| Symptom | Cause | Fix |
|---|---|---|
| `pip install 'neatlogs>=1.4.26'` resolves to 1.1.8 | Interpreter is 3.14; neatlogs requires `<3.14` | `deploy/install-python.sh` pins 3.13 |
| `Permission denied` on every run, pip says success | uv put CPython in `/root`, unreachable by the `deadmon` user | install uv to `/usr/local/bin` |
| `neatlogs unavailable` in the log, one line per run | `NEATLOGS_API_KEY` unset in the service environment | write `/etc/deadmon/env`, mode 0640, `root:deadmon` |

Check what you actually have:

```bash
/opt/deadmon/venv/bin/python --version                  # want 3.13.x
/opt/deadmon/venv/bin/python -c 'import neatlogs'       # want no error
sudo systemctl show deadmon -p EnvironmentFiles
```

## Service

```bash
systemctl status deadmon
journalctl -u deadmon -f
sudo systemctl restart deadmon
```

The service runs `deadmon-crawl`, which crawls then serves in one process. A
restart re-crawls and appends nine run rows — it never truncates, because
`--reset` is deliberately absent from the unit. Run history is evidence; wiping
it on every boot is a demo trick, not a deployment.

## Data

The database is SQLite at `/var/lib/deadmon/deadmon.db` and is **gitignored by
design**: the committed schema in `src/deadmon/schema/` is the source of truth,
and `storage.py` recreates the file from it on first boot. The crawl replays
recorded fixtures, so the instance needs the repo, not a database dump.

```bash
sqlite3 /var/lib/deadmon/deadmon.db 'select crawler, count(*) from sources group by crawler;'
```

Expect six crawlers. Five returning entirely `unverified` is correct, not
broken: those platforms do not expose a timezone-aware registration close, so
there is nothing to verify and they fail closed rather than guess.

## When the dashboard is empty

In order:

1. `curl /api/feed` — is the service serving at all?
2. Is the security group allowing 8080 from your source?
3. Is the Next.js `NEXT_PUBLIC_DEADMON_API` pointing at the right host? It is
   baked in at **build** time, so a changed IP needs a redeploy, not a restart.

## Credential handling

`/etc/deadmon/env` holds `NEATLOGS_API_KEY`, mode 0640, owned by `root:deadmon`.
Never in the repo, never in a commit. `.env.example` documents the variable
name only.

The EC2 security group opens 8080 to `0.0.0.0/0` because Vercel's serverless IPs
are dynamic and cannot be allowlisted. That means the feed is world-readable —
fine for public hackathon listings, not fine for subscriber data. Close it when
accounts exist:

```bash
aws ec2 revoke-security-group-ingress --group-id sg-XXXX \
    --protocol tcp --port 8080 --cidr 0.0.0.0/0
```

SSH on 22 is also open during setup. Lock it down once provisioning is done:

```bash
aws ec2 revoke-security-group-ingress --group-id sg-XXXX \
    --protocol tcp --port 22 --cidr 0.0.0.0/0
```