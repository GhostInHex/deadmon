"""Receipts: countable proof that a crawl run happened, hash-sealed.

Every crawl run emits one numbered receipt — a small JSON document carrying
the run id, the crawler name, the verdict counts, the trace reference, and a
sha256 hash over those canonical fields. An edited receipt fails
verification, which is the whole point: a judge re-runs the hash and trusts
the evidence was not edited.

The receipt is always local JSON under `.runs/receipts/` (gitignored runtime
output, like the database and the trace documents). It does not depend on
any service: when neatlogs is absent the trace already falls back to the
local sink, and the receipt is still written — the demo never hits a login
wall.

One receipt per crawl run, never per card (spec: receipts count crawl runs,
not cards). Numbering is the run id, zero-padded in the filename.

Stdlib only: `hashlib` + `json`. The suite stays offline.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

DEFAULT_RECEIPT_DIR = Path(".runs") / "receipts"

# The canonical fields the hash covers. `hash` itself is never hashed.
CANONICAL_FIELDS = (
    "receipt",
    "run_id",
    "crawler",
    "candidates",
    "live",
    "closed",
    "unverified",
    "trace",
    "backend",
)


def canonical_hash(document: dict) -> str:
    """sha256 over the canonical fields, sorted keys, compact separators."""
    canonical = {key: document[key] for key in CANONICAL_FIELDS if key in document}
    payload = json.dumps(
        canonical, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def build_receipt(
    *,
    run_id: int,
    crawler: str,
    candidates: int,
    live: int,
    closed: int,
    unverified: int,
    trace: str,
    backend: str,
) -> dict:
    """Assemble a receipt and seal it with its hash."""
    document = {
        "receipt": run_id,
        "run_id": run_id,
        "crawler": crawler,
        "candidates": candidates,
        "live": live,
        "closed": closed,
        "unverified": unverified,
        "trace": trace,
        "backend": backend,
    }
    document["hash"] = canonical_hash(document)
    return document


def receipt_path(receipt_dir: Path, run_id: int) -> Path:
    return Path(receipt_dir) / f"receipt-{run_id:04d}.json"


def emit_receipt(document: dict, receipt_dir: Path) -> Path:
    """Write one numbered receipt as local JSON. Returns the path."""
    directory = Path(receipt_dir)
    directory.mkdir(parents=True, exist_ok=True)
    path = receipt_path(directory, int(document["receipt"]))
    path.write_text(
        json.dumps(document, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
    return path


def verify_receipt(path: Path) -> tuple[bool, str]:
    """Recompute the hash. `True` means untouched; any edit fails."""
    try:
        document = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return False, f"{path}: unreadable ({exc})"
    expected = document.get("hash")
    if not isinstance(expected, str):
        return False, f"{path}: no hash to verify against"
    if canonical_hash(document) == expected:
        return True, f"{path}: OK"
    return False, f"{path}: FAIL — content does not match its hash"


def verify_all(receipt_dir: Path) -> list[tuple[Path, bool, str]]:
    """Verify every receipt in a directory, in numbered order."""
    directory = Path(receipt_dir)
    results = []
    for path in sorted(directory.glob("receipt-*.json")):
        ok, message = verify_receipt(path)
        results.append((path, ok, message))
    return results


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="deadmon-receipt-check",
        description="Verify numbered crawl-run receipts: an edited receipt fails.",
    )
    parser.add_argument(
        "paths", nargs="*", type=Path, help="receipt file(s) to verify"
    )
    parser.add_argument(
        "--receipts",
        type=Path,
        default=DEFAULT_RECEIPT_DIR,
        help="receipt directory (default: .runs/receipts)",
    )
    args = parser.parse_args(argv)

    targets = list(args.paths)
    if not targets:
        targets = sorted(Path(args.receipts).glob("receipt-*.json"))
    if not targets:
        print(f"no receipts in {args.receipts}", file=sys.stderr)
        return 1

    failed = 0
    for path in targets:
        ok, message = verify_receipt(path)
        print(message)
        if not ok:
            failed += 1
    print(f"\n{len(targets) - failed}/{len(targets)} receipt(s) verified.")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
