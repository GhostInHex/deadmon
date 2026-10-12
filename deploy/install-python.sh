#!/usr/bin/env bash
# Rebuild the venv on a Python the optional tracing SDK supports.
#
# Ubuntu 26.04 ships only Python 3.14, and neatlogs declares
# Requires-Python >=3.10,<3.14 - so a stock `python3 -m venv` installs a
# version the SDK cannot be installed into, and every crawl run silently falls
# back to the local trace sink. Pin 3.13.
#
# uv is installed to /usr/local, not ~/.local: uv's default puts CPython under
# $HOME/.local/share/uv, and when run through sudo that lands in /root, which
# the deadmon service user cannot traverse. The venv's `python` then symlinks
# into /root and every invocation fails with "Permission denied" even though
# pip reports a successful install.
set -euo pipefail

export DEBIAN_FRONTEND=noninteractive
UV_PYTHON_INSTALL_DIR=/usr/local/share/uv

apt-get update -qq
apt-get install -y -qq curl ca-certificates >/dev/null

if ! command -v uv >/dev/null 2>&1; then
  curl -LsSf https://astral.sh/uv/install.sh | env UV_INSTALL_DIR=/usr/local/bin sh
fi

rm -rf /root/.local/share/uv
uv python install 3.13

# Only rebuild when the current interpreter cannot take the SDK, so a redeploy
# does not needlessly churn a working venv.
if [ ! -x "$APP_DIR/venv/bin/python" ] || ! "$APP_DIR/venv/bin/python" -c 'import sys; raise SystemExit(0 if sys.version_info[:2] < (3, 14) else 1)' 2>/dev/null; then
  echo "==> rebuilding venv on 3.13"
  rm -rf "$APP_DIR/venv"
  uv venv --python 3.13 "$APP_DIR/venv"
  "$APP_DIR/venv/bin/python" -m ensurepip --upgrade >/dev/null 2>&1 || true
  "$APP_DIR/venv/bin/python" -m pip install --quiet --upgrade pip
  "$APP_DIR/venv/bin/python" -m pip install --quiet "$APP_DIR"
  if [ -n "${NEATLOGS_API_KEY:-}" ]; then
    "$APP_DIR/venv/bin/python" -m pip install --quiet 'neatlogs>=1.4.26'
  fi
fi

chown -R "$APP_USER:$APP_USER" "$APP_DIR"

echo "==> versions"
"$APP_DIR/venv/bin/python" --version
"$APP_DIR/venv/bin/python" -c 'import neatlogs; print("neatlogs", neatlogs.__version__)' \
  || echo "neatlogs absent - runs will use the local trace sink"