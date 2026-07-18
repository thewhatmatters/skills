#!/usr/bin/env python3
"""Readiness check for audit-vault (spec A6).

I/O: stdout JSON {overall, checks, summary} · stderr human board · exit 1 only on `down`.
States per check: ready | degraded | gated | down  (with a gate id).

Checks: vault present (down: VAULT_MISSING / SYNC_UNMOUNTED — nothing to
measure), curate-vault's verify_bundle entry point (degraded:
VAULT_TOOLS_MISSING — conformance section skipped), state dir writable
(degraded: STATE_UNWRITABLE — no growth deltas).
"""
import argparse
import json
import os
import sys

MARK = {"ready": "✅", "degraded": "⚠ ", "gated": "🔒", "down": "⛔"}
RANK = {"ready": 0, "degraded": 1, "gated": 2, "down": 3}
DEFAULT_VAULT = os.path.expanduser(
    "~/Library/Mobile Documents/iCloud~md~obsidian/Documents/OBSDN")
VERIFY = os.path.expanduser(
    "~/.claude/skills/curate-vault/scripts/verify_bundle.py")


def check_vault(vault):
    if os.path.isdir(vault) and os.path.isfile(os.path.join(vault, "index.md")):
        return ("ready", None, f"vault present: {vault}")
    provider_root = os.path.dirname(os.path.dirname(vault))
    if not os.path.isdir(provider_root):
        return ("down", "SYNC_UNMOUNTED",
                "vault sync provider root absent — start the sync client")
    return ("down", "VAULT_MISSING", f"no vault at {vault}")


def check_tools():
    if os.path.isfile(VERIFY):
        return ("ready", None, "curate-vault verify_bundle.py found")
    return ("degraded", "VAULT_TOOLS_MISSING",
            "verify_bundle.py not found — conformance section will be skipped")


def check_deep():
    agent = os.path.expanduser("~/.claude/agents/vault-verifier.md")
    if os.path.isfile(agent):
        return ("ready", None, "vault-verifier agent found (--deep available)")
    return ("degraded", "DEEP_UNAVAILABLE",
            "vault-verifier agent not found — --deep claim spot-check "
            "will be skipped and labeled not measured")


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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vault", default=DEFAULT_VAULT)
    ap.add_argument("--state-dir",
                    default=os.path.expanduser("~/.claude/.cache/audit-vault"))
    ap.add_argument("--agent", action="store_true")
    args = ap.parse_args()

    checks = {
        "vault": check_vault(os.path.expanduser(args.vault)),
        "tools": check_tools(),
        "state": check_state(os.path.expanduser(args.state_dir)),
        "deep": check_deep(),
    }
    overall = "ready"
    for s, _g, _d in checks.values():
        if RANK[s] > RANK[overall]:
            overall = s
    print("audit-vault readiness", file=sys.stderr)
    for n, (s, g, d) in checks.items():
        suffix = f"  [{g}]" if g else ""
        print(f"  {MARK[s]} {n:<6} {d}{suffix}", file=sys.stderr)
    print(f"  → overall: {overall}", file=sys.stderr)
    print(json.dumps({
        "overall": overall,
        "checks": {n: {"status": s, "gate": g, "detail": d}
                   for n, (s, g, d) in checks.items()},
        "summary": ", ".join(f"{n}={s}" for n, (s, _g, _d) in checks.items()),
    }, indent=2))
    sys.exit(1 if overall == "down" else 0)


if __name__ == "__main__":
    main()
