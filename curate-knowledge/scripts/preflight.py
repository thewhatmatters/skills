#!/usr/bin/env python3
"""Readiness check for curate-knowledge (spec A6).

Probes the OKF vault: present, writable, root index/log in place.
I/O: stdout JSON {overall, checks, summary} · stderr human board · exit 1 only on `down`.
States per check: ready | degraded | gated | down  (with a gate id).
"""
import argparse
import json
import os
import sys

DEFAULT_VAULT = os.path.expanduser(
    "~/Library/CloudStorage/Dropbox/Documents/Obsidian"
)
MARK = {"ready": "✅", "degraded": "⚠ ", "gated": "🔒", "down": "⛔"}
RANK = {"ready": 0, "degraded": 1, "gated": 2, "down": 3}


def check_vault(vault):
    if not os.path.isdir(vault):
        return ("gated", "VAULT_MISSING", f"vault not found at {vault}")
    if not os.access(vault, os.W_OK):
        return ("down", "VAULT_READONLY", f"vault not writable: {vault}")
    return ("ready", None, f"vault present and writable: {vault}")


def check_root_index(vault):
    path = os.path.join(vault, "index.md")
    if not os.path.isfile(path):
        return ("degraded", None, "root index.md missing (will be created on write)")
    head = open(path, encoding="utf-8").read(200)
    if "okf_version" in head:
        return ("ready", None, "root index.md present, okf_version declared")
    return ("ready", None, "root index.md present (no okf_version declared)")


def check_log(vault):
    if os.path.isfile(os.path.join(vault, "log.md")):
        return ("ready", None, "root log.md present")
    return ("degraded", None, "root log.md missing (will be created on write)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vault", default=DEFAULT_VAULT)
    ap.add_argument("--agent", action="store_true")
    args = ap.parse_args()
    vault = os.path.expanduser(args.vault)

    checks = {"vault": check_vault(vault)}
    # Index/log checks only make sense if the vault exists.
    if checks["vault"][0] in ("ready", "degraded"):
        checks["root_index"] = check_root_index(vault)
        checks["log"] = check_log(vault)

    overall = "ready"
    for s, _g, _d in checks.values():
        if RANK[s] > RANK[overall]:
            overall = s

    print("curate-knowledge readiness", file=sys.stderr)
    for n, (s, g, d) in checks.items():
        suffix = f"  [{g}]" if g else ""
        print(f"  {MARK[s]} {n:<10} {d}{suffix}", file=sys.stderr)
    print(f"  → overall: {overall}", file=sys.stderr)

    payload = {
        "overall": overall,
        "vault": vault,
        "checks": {n: {"status": s, "gate": g, "detail": d}
                   for n, (s, g, d) in checks.items()},
        "summary": ", ".join(f"{n}={s}" for n, (s, _g, _d) in checks.items()),
    }
    print(json.dumps(payload, indent=2))
    sys.exit(1 if overall == "down" else 0)


if __name__ == "__main__":
    main()
