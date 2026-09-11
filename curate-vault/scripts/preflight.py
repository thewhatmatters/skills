#!/usr/bin/env python3
"""Readiness check for curate-vault (spec A6).

Probes the OKF vault: present, writable (harvest) or readable (--audit),
root index/log in place. --audit also checks snapshot state dir + optional
vault-verifier agent.

I/O: stdout JSON {overall, checks, summary} · stderr human board · exit 1 only on `down`.
States per check: ready | degraded | gated | down  (with a gate id).
"""
import argparse
import json
import os
import re
import sys

DEFAULT_VAULT = os.path.expanduser(
    "~/Library/Mobile Documents/iCloud~md~obsidian/Documents/OBSDN"
)
DEFAULT_STATE = os.path.expanduser("~/.cursor/cache/audit-vault")
VERIFY = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                      "verify_bundle.py")
DEEP_AGENT = os.path.expanduser("~/.cursor/agents/vault-verifier.md")
MARK = {"ready": "✅", "degraded": "⚠ ", "gated": "🔒", "down": "⛔"}
RANK = {"ready": 0, "degraded": 1, "gated": 2, "down": 3}


def check_vault(vault, audit=False):
    if not os.path.isdir(vault):
        # A vault under ~/Library/CloudStorage can be absent *transiently*
        # when the sync client (Dropbox etc.) isn't running. That is not a
        # missing vault — creating a fresh bundle there would diverge from
        # the synced copy once the client comes back.
        m = re.match(r"^(.*/Library/CloudStorage/[^/]+)(/|$)", vault)
        if m and not os.path.isdir(m.group(1)):
            status = "down" if audit else "gated"
            return (status, "SYNC_UNMOUNTED",
                    f"cloud-sync root absent ({m.group(1)}) — sync client "
                    "likely not running; do NOT create a new vault here")
        status = "down" if audit else "gated"
        return (status, "VAULT_MISSING", f"vault not found at {vault}")
    if not os.access(vault, os.R_OK):
        return ("down", "VAULT_UNREADABLE", f"vault not readable: {vault}")
    if not audit and not os.access(vault, os.W_OK):
        return ("down", "VAULT_READONLY", f"vault not writable: {vault}")
    if audit and not os.access(vault, os.W_OK):
        return ("ready", None, f"vault present (read-only): {vault}")
    return ("ready", None, f"vault present and writable: {vault}")


def check_state(state_dir):
    try:
        os.makedirs(state_dir, exist_ok=True)
        probe = os.path.join(state_dir, ".probe")
        with open(probe, "w") as fh:
            fh.write("ok")
        os.remove(probe)
        return ("ready", None, f"state dir writable: {state_dir}")
    except OSError as e:
        return ("degraded", "STATE_UNWRITABLE",
                f"state dir not writable ({e}) — no growth deltas")


def check_deep():
    if os.path.isfile(DEEP_AGENT):
        return ("ready", None, "vault-verifier agent found (--deep available)")
    return ("degraded", "DEEP_UNAVAILABLE",
            "vault-verifier agent not found — --deep will be skipped")


def check_tools():
    if os.path.isfile(VERIFY):
        return ("ready", None, "verify_bundle.py found")
    return ("degraded", "VAULT_TOOLS_MISSING",
            "verify_bundle.py missing — conformance section skipped")


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
    ap.add_argument("--audit", action="store_true")
    ap.add_argument("--state-dir", default=DEFAULT_STATE)
    args = ap.parse_args()
    vault = os.path.expanduser(args.vault)

    checks = {"vault": check_vault(vault, audit=args.audit)}
    # Index/log checks only make sense if the vault exists.
    if checks["vault"][0] in ("ready", "degraded"):
        checks["root_index"] = check_root_index(vault)
        checks["log"] = check_log(vault)
    if args.audit:
        checks["tools"] = check_tools()
        checks["state"] = check_state(os.path.expanduser(args.state_dir))
        checks["deep"] = check_deep()

    overall = "ready"
    for s, _g, _d in checks.values():
        if RANK[s] > RANK[overall]:
            overall = s

    print("curate-vault readiness", file=sys.stderr)
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
