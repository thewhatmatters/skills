#!/usr/bin/env python3
"""Readiness check for use-grid-system (spec A6).

I/O: stdout JSON {overall, checks, summary} · stderr human board · exit 1 only on `down`.
States per check: ready | degraded | gated | down  (with a gate id).

Nothing here is network-bound: the skill emits CSS scaffold and composes other
skills for the browser work, so the worst state is `degraded` (an optional tool
absent), never `down` unless the output target is unwritable.
"""
import argparse, json, os, shutil, sys

MARK = {"ready": "✅", "degraded": "⚠ ", "gated": "🔒", "down": "⛔"}
RANK = {"ready": 0, "degraded": 1, "gated": 2, "down": 3}


def check_python():
    ok = sys.version_info >= (3, 7)
    return ("ready", None, f"python {sys.version_info.major}.{sys.version_info.minor}") if ok \
        else ("degraded", "PY_OLD", "python < 3.7; NATIVE fallback still works")


def check_target(out):
    path = out or "."
    base = path if os.path.isdir(path) else os.path.dirname(os.path.abspath(path)) or "."
    if os.access(base, os.W_OK):
        return ("ready", None, f"output target writable ({base})")
    return ("down", "TARGET_RO", f"output target not writable ({base})")


def check_node():
    # Optional: only needed to compose tailwindcss-react-grid-overlay in React apps.
    if shutil.which("npx") or shutil.which("node"):
        return ("ready", None, "node/npx present (React overlay composable)")
    return ("degraded", "NODE_ABSENT",
            "node/npx absent — overlay still works via the framework-agnostic JS")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--agent", action="store_true")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    checks = {
        "python": check_python(),
        "target": check_target(args.out),
        "node": check_node(),
    }
    overall = "ready"
    for s, _g, _d in checks.values():
        if RANK[s] > RANK[overall]:
            overall = s

    print("use-grid-system readiness", file=sys.stderr)
    for n, (s, g, d) in checks.items():
        suffix = f"  [{g}]" if g else ""
        print(f"  {MARK[s]} {n:<8} {d}{suffix}", file=sys.stderr)
    print(f"  → overall: {overall}", file=sys.stderr)

    payload = {
        "overall": overall,
        "checks": {n: {"status": s, "gate": g, "detail": d}
                   for n, (s, g, d) in checks.items()},
        "summary": "; ".join(f"{n}={s}" for n, (s, _g, _d) in checks.items()),
    }
    print(json.dumps(payload, indent=2))
    sys.exit(1 if overall == "down" else 0)


if __name__ == "__main__":
    main()
