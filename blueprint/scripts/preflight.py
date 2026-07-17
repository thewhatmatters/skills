#!/usr/bin/env python3
"""Readiness check for blueprint (spec A6).

Verifies the skill's own assets for real: template + schema + example
present, then a live self-test — validate the bundled example and render
it to a temp file. Keyless, no network, no external binaries.

I/O: stdout JSON {overall, checks, summary} · stderr human board ·
exit 1 only on `down`. States: ready | degraded | down (no setup gates —
nothing here is user-recoverable; a broken install is `down`).
"""
import json
import os
import subprocess
import sys
import tempfile

MARK = {"ready": "✅", "degraded": "⚠ ", "down": "⛔"}
RANK = {"ready": 0, "degraded": 1, "down": 3}
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def check_assets():
    missing = [p for p in ("assets/template.html",
                           "schemas/architecture.schema.json",
                           "examples/web-app.architecture.json")
               if not os.path.exists(os.path.join(ROOT, p))]
    if missing:
        return ("down", None, f"missing: {', '.join(missing)}")
    return ("ready", None, "template + schema + example present")


def check_selftest():
    example = os.path.join(ROOT, "examples", "web-app.architecture.json")
    if not os.path.exists(example):
        return ("degraded", None, "no example to self-test")
    try:
        v = subprocess.run(
            [sys.executable, os.path.join(ROOT, "scripts", "validate.py"), example],
            capture_output=True, text=True, timeout=30)
        if v.returncode != 0:
            return ("down", None, "bundled example fails validation — install is broken")
        with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as tf:
            out = tf.name
        try:
            r = subprocess.run(
                [sys.executable, os.path.join(ROOT, "scripts", "render.py"),
                 example, f"--out={out}"],
                capture_output=True, text=True, timeout=30)
            ok = r.returncode == 0 and os.path.getsize(out) > 1000
        finally:
            if os.path.exists(out):
                os.unlink(out)
        if not ok:
            return ("down", None, "render self-test failed")
        return ("ready", None, "validate + render self-test passed")
    except (subprocess.TimeoutExpired, OSError) as e:
        return ("degraded", None, f"self-test could not run: {e}")


def main():
    checks = {"assets": check_assets()}
    checks["selftest"] = (check_selftest() if checks["assets"][0] == "ready"
                          else ("degraded", None, "skipped — assets missing"))
    overall = "ready"
    for s, _g, _d in checks.values():
        if RANK[s] > RANK[overall]:
            overall = s
    print("blueprint readiness", file=sys.stderr)
    for n, (s, g, d) in checks.items():
        print(f"  {MARK[s]} {n:<9} {d}", file=sys.stderr)
    print(f"  → overall: {overall}", file=sys.stderr)
    print(json.dumps({
        "overall": overall,
        "checks": {n: {"status": s, "gate": g, "detail": d}
                   for n, (s, g, d) in checks.items()},
        "summary": "; ".join(f"{n}={s}" for n, (s, _g, _d) in checks.items()),
    }, indent=2))
    sys.exit(1 if overall == "down" else 0)


if __name__ == "__main__":
    main()
