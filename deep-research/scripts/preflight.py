#!/usr/bin/env python3
"""Readiness check for deep-research (spec A6).

One concern: confirm everything is in place to run a research pass. Four
checks: target dir writable, search-provider keys loadable, network
reachable, HTML render available. Per the skill's dual-mode design (spec A3),
missing keys do NOT block — they downgrade to NATIVE via SKILL.md Step 2's
gate, and NATIVE mode produces the same artifact via Claude's built-in
WebSearch/WebFetch.

USAGE
    python3 scripts/preflight.py [--out=PATH] [--agent]

    --out=PATH  output directory the report will be written to (default: cwd)
    --agent     non-interactive; report only, never prompt

I/O CONTRACT
    stdout : a single JSON object — {overall, checks{...}, summary}
    stderr : a human readiness board
    exit   : 0 if overall ∈ {ready, degraded, gated};
             1 if overall == down (a hard blocker)

PER-CHECK STATUS  ∈ {ready, degraded, gated, down}  (+ a gate id when not ready)
    target   output dir writable / safe              down → TARGET_UNWRITABLE
    keys     TAVILY or EXA loadable from .env        gated → KEYS_MISSING
                                                     (recoverable: NATIVE
                                                     mode is a graceful
                                                     dead-end per A7d)
    network  Tavily or Exa endpoint reachable        degraded → OFFLINE
                                                     (informational; NATIVE
                                                     still works via the
                                                     model's built-in tools)
    html     scripts/report.py present               degraded → HTML_UNAVAILABLE
                                                     (informational; markdown
                                                     path still works fully)
"""

import argparse
import json
import os
import ssl
import sys
import urllib.request
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
REPORT_SCRIPT = SCRIPT_DIR / "report.py"

# Endpoints we probe — small GET against the provider's host, short timeout.
NET_PROBES = (
    ("Tavily", "https://api.tavily.com/"),
    ("Exa", "https://api.exa.ai/"),
)
NET_TIMEOUT = 3

MARK = {"ready": "✅", "degraded": "⚠ ", "gated": "🔒", "down": "⛔"}
RANK = {"ready": 0, "degraded": 1, "gated": 2, "down": 3}


def log(msg):
    print(msg, file=sys.stderr)


def check_target(out):
    """Can we create the report under <out>?"""
    probe = Path(out).expanduser()
    while not probe.exists() and probe != probe.parent:
        probe = probe.parent
    if probe.is_dir() and os.access(probe, os.W_OK):
        return ("ready", None, f"{out} writable")
    return ("down", "TARGET_UNWRITABLE", f"cannot write under {probe}")


def check_keys():
    """Are TAVILY_API_KEY or EXA_API_KEY loadable via the shared loader?

    Uses _env.load() then inspects os.environ — never prints key values.
    """
    try:
        sys.path.insert(0, str(SCRIPT_DIR))
        import _env  # noqa: PLC0415
        _env.load()
    except Exception as e:  # noqa: BLE001
        return ("gated", "KEYS_MISSING",
                f"_env loader failed ({e.__class__.__name__}); NATIVE mode used")
    tav = bool(os.environ.get("TAVILY_API_KEY"))
    exa = bool(os.environ.get("EXA_API_KEY"))
    if tav and exa:
        return ("ready", None, "TAVILY + EXA both available")
    if tav:
        return ("ready", None, "TAVILY available (EXA optional)")
    if exa:
        return ("ready", None, "EXA available (TAVILY optional)")
    return ("gated", "KEYS_MISSING",
            "neither TAVILY_API_KEY nor EXA_API_KEY set in ~/.claude/skills/.env "
            "— NATIVE mode (built-in WebSearch) is automatic")


_SSL_CTX = "unset"


def _ssl_context():
    """certifi-backed SSL context when available, else default verification.

    Same layered pattern as generate-skill/scripts/docs.py — macOS
    python.org builds don't trust via the system keychain, so stdlib
    urllib fails cert verification while the script's own actual search
    path (requests, which bundles certifi) succeeds. Without this fix,
    preflight reports OFFLINE while search.py works fine — a false
    negative that misleads the operator. Spec A11.
    """
    global _SSL_CTX
    if _SSL_CTX == "unset":
        try:
            import certifi  # noqa: PLC0415
            _SSL_CTX = ssl.create_default_context(cafile=certifi.where())
        except Exception:  # noqa: BLE001
            _SSL_CTX = None
    return _SSL_CTX


def check_network():
    """Is at least one provider endpoint reachable? Informational, not blocking."""
    last_err = None
    for label, url in NET_PROBES:
        try:
            req = urllib.request.Request(
                url, headers={"User-Agent": "deep-research-preflight/1.0"}
            )
            with urllib.request.urlopen(
                req, timeout=NET_TIMEOUT, context=_ssl_context()
            ) as r:
                if r.status < 500:
                    return ("ready", None, f"{label} reachable (http {r.status})")
        except Exception as e:  # noqa: BLE001
            last_err = e
    return ("degraded", "OFFLINE",
            f"no provider endpoint reachable "
            f"({last_err.__class__.__name__ if last_err else 'no probe'}); "
            "cache/NATIVE used")


def check_html():
    """Is the HTML render path available? Informational, not blocking."""
    if REPORT_SCRIPT.is_file():
        return ("ready", None, "report.py present (HTML render available)")
    return ("degraded", "HTML_UNAVAILABLE",
            f"missing {REPORT_SCRIPT.name} — markdown still works; "
            "pass --no-html to silence")


def main():
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--out", default=str(Path.cwd()))
    ap.add_argument("--agent", action="store_true")
    args = ap.parse_args()

    checks = {
        "target": check_target(args.out),
        "keys": check_keys(),
        "network": check_network(),
        "html": check_html(),
    }

    overall = "ready"
    for status, _gate, _detail in checks.values():
        if RANK[status] > RANK[overall]:
            overall = status

    log("deep-research readiness")
    for name, (status, gate, detail) in checks.items():
        g = f"  [{gate}]" if gate else ""
        log(f"  {MARK[status]} {name:<8} {detail}{g}")
    log(f"  → overall: {overall}")
    if overall == "down":
        log("  (a hard blocker is present — resolve the ⛔ item above)")
    elif overall in ("gated", "degraded"):
        log("  (can proceed; gates auto-degrade to NATIVE per SKILL.md Step 2)")

    payload = {
        "overall": overall,
        "checks": {
            n: {"status": s, "gate": g, "detail": d}
            for n, (s, g, d) in checks.items()
        },
        "summary": f"{overall}: " + ", ".join(
            f"{n}={s}" for n, (s, _g, _d) in checks.items()
        ),
    }
    print(json.dumps(payload, indent=2))
    sys.exit(1 if overall == "down" else 0)


if __name__ == "__main__":
    main()
