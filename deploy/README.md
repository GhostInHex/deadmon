# deadmon deploy notes

One crawl run, then the dashboard, on a single EC2 instance. This is the whole
deployment: an HTTP server over a local SQLite file, driven by systemd.

## Why this shape

`PLAN.md` says free tiers only. A t3.micro covers it - the crawl replays
recorded fixtures with no network, so the instance does almost nothing except
serve one page. Lambda was rejected because Slice 1's SQLite database and its
fixtures both want a filesystem that survives between runs, which turns a
scheduled invocation into a state-management problem rather than a deployment.

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
sudo /opt/deadmon/venv/bin/pip install 'neatlogs'   # or: pip install '/opt/deadmon[tracing]'
```

`tracing.py` only picks that sink when the package imports **and** the key is
set, and it swallows any failure - a broken tracing service must never take a
crawl run down with it (ticket 07).

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
curl -s localhost:8080/          | grep -c 'card'   # cards in the feed
curl -s localhost:8080/runs.json | head -c 400      # run history
sudo systemctl is-active deadmon                   # active
```

The dashboard binds `0.0.0.0:8080`. It is served with no authentication, so
keep it behind the EC2 security group (see below) or a tunnel - do not expose it
to `0.0.0.0/0`.

## Two things that will bite you

**Port 8765 is reserved on Windows** (OS exclusion range 8700-8799), so the
README's original default dies with `WinError 10013` when you record a demo on
a dev machine. 8080 is used instead. On Linux 8765 is fine - this only bites the
recording, not the instance.

**The README's command needs no `PYTHONPATH`.** Before the packaging commit it
only ran with `PYTHONPATH=src` set by hand. If you see
`ModuleNotFoundError: No module named 'deadmon'`, the install step was skipped.

## Security group

Inbound: port 8080 from your own IP, or from anywhere only while recording.
Outbound: none needed today - the crawl replays recorded fixtures.

```bash
aws ec2 authorize-security-group-ingress --group-id sg-XXXX \
    --protocol tcp --port 8080 --cidr "$(curl -s ifconfig.me)/32"
```

## Not yet deployed

This covers Slice 1 only. Slice 4's self-heal needs to commit to this repo from
the instance, which means the deploy user needs a git identity and push access -
deliberately left out rather than quietly given wide credentials.