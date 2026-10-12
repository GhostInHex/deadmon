#!/usr/bin/env bash
# deadmon EC2 first-boot. Paste into the instance's User data when launching,
# or run as root on a fresh Ubuntu 24.04 t3.micro.
#
# Idempotent: safe to re-run. Installs the crawl service, its systemd unit and
# the state directory, then starts it. The database is created on first boot by
# storage.py - the committed schema is the source of truth, never a .db file.
set -euo pipefail

REPO_URL="${DEADMON_REPO:-https://github.com/GhostInHex/deadmon.git}"
APP_USER=deadmon
APP_DIR=/opt/deadmon
STATE_DIR=/var/lib/deadmon

echo "==> system user"
id -u "$APP_USER" >/dev/null 2>&1 || \
  useradd --system --home "$APP_DIR" --shell /usr/sbin/nologin "$APP_USER"

echo "==> directories"
mkdir -p "$APP_DIR" "$STATE_DIR/traces" /etc/deadmon
chown -R "$APP_USER:$APP_USER" "$STATE_DIR"

echo "==> code"
if [ -d "$APP_DIR/.git" ]; then
  git -C "$APP_DIR" pull --ff-only
else
  git clone "$REPO_URL" "$APP_DIR"
fi

echo "==> python + package"
# 3.11+ required. Ubuntu 24.04 ships 3.12; deadmon needs no third-party deps.
apt-get update -qq
apt-get install -y -qq python3-venv
python3 -m venv "$APP_DIR/venv"
"$APP_DIR/venv/bin/pip" install --quiet --upgrade pip
"$APP_DIR/venv/bin/pip" install --quiet "$APP_DIR"

# Optional: tracing to neatlogs. Pinned floor - see pyproject [tracing].
# Without it every run traces to the local JSON sink and the dashboard links
# still resolve, so this is genuinely optional.
if [ -n "${NEATLOGS_API_KEY:-}" ]; then
  "$APP_DIR/venv/bin/pip" install --quiet 'neatlogs>=1.4.26; python_version<"3.14"'
  install -o root -g "$APP_USER" -m 0640 /dev/null /etc/deadmon/env
  echo "NEATLOGS_API_KEY=$NEATLOGS_API_KEY" >> /etc/deadmon/env
fi

echo "==> fixtures"
# The crawl replays recorded fixtures, so they must be present and are tracked
# in git. Fail loudly rather than serving an empty dashboard.
if [ -z "$(ls -A "$APP_DIR/fixtures" 2>/dev/null)" ]; then
  echo "FATAL: fixtures/ is empty; the crawl has no corpus to replay" >&2
  exit 1
fi

echo "==> ownership"
chown -R "$APP_USER:$APP_USER" "$APP_DIR"

echo "==> service"
install -m 0644 "$APP_DIR/deploy/deadmon.service" /etc/systemd/system/deadmon.service
systemctl daemon-reload
systemctl enable --now deadmon

sleep 3
echo "==> smoke test"
curl -fsS "http://127.0.0.1:8080/api/feed" -o /tmp/feed.json
python3 - <<'PY'
import json
feed = json.load(open('/tmp/feed.json'))
print('  feed cards      :', len(feed['feed']))
print('  needs attention :', len(feed['needs_attention']))
print('  traced runs     :', len(feed['runs']))
print('  crawlers        :', ', '.join(sorted({r['crawler'] for r in feed['runs']})))
PY
curl -fsS -o /dev/null "http://127.0.0.1:8080/" && echo "  HTML dashboard  : ok"

echo
echo "done. API base URL for the Next.js app:  http://$(curl -fsS http://169.254.169.254/latest/meta-data/public-ipv4):8080"
echo "Set NEXT_PUBLIC_DEADMON_API to that, then deploy apps/web to Vercel."