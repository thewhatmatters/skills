#!/usr/bin/env python3
"""Readiness check for gauntlet (spec A6).

Checks: critic binary (layered resolution), critic auth (LIVE single-turn
probe unless --no-live), git repo (correctness species), deterministic
gates discovery.

I/O: stdout JSON {overall, checks, summary, critic_cmd, gates} · stderr
human board · exit 1 only on `down`.
States per check: ready | degraded | gated | down (with a gate id).
Auth-vs-transient is unambiguous (spec A7a): only an auth-shaped error
gates; timeouts and other failures are `degraded`.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys

MARK = {"ready": "✅", "degraded": "⚠ ", "gated": "🔒", "down": "⛔"}
RANK = {"ready": 0, "degraded": 1, "gated": 2, "down": 3}

AUTH_MARKERS = ("unauthorized", "unauthenticated", "not logged in",
                "login required", "invalid api key", "credential", "401",
                "403", "sign in", "grok login")


def resolve_critic():
    """Layered resolution (spec A11): env override → PATH → known path."""
    override = os.environ.get("GAUNTLET_CRITIC_CMD", "").strip()
    if override:
        return override, f"env override GAUNTLET_CRITIC_CMD={override}"
    on_path = shutil.which("grok")
    if on_path:
        return on_path, f"grok on PATH ({on_path})"
    known = os.path.expanduser("~/.local/bin/grok")
    if os.access(known, os.X_OK):
        return known, f"known path {known}"
    return None, "no critic binary (GAUNTLET_CRITIC_CMD, grok on PATH, ~/.local/bin/grok)"


def check_critic():
    cmd, detail = resolve_critic()
    if cmd is None:
        return ("gated", "CRITIC_MISSING", detail), None
    return ("ready", None, detail), cmd


def check_auth(critic_cmd, live):
    if critic_cmd is None:
        return ("degraded", None, "skipped — no critic binary")
    if not live:
        return ("degraded", None, "live probe skipped (--no-live); auth unverified")
    try:
        proc = subprocess.run(
            [critic_cmd, "-p", "Reply with the single word OK.",
             "--max-turns", "1", "--output-format", "plain"],
            capture_output=True, text=True, timeout=60,
        )
    except subprocess.TimeoutExpired:
        return ("degraded", None, "live probe timed out (transient — not gated)")
    except OSError as e:
        return ("degraded", None, f"live probe failed to launch: {e}")
    blob = (proc.stdout + proc.stderr).lower()
    if proc.returncode == 0 and proc.stdout.strip():
        return ("ready", None, "live probe OK — critic responded")
    if any(m in blob for m in AUTH_MARKERS):
        return ("gated", "CRITIC_UNAUTHED",
                "critic returned an auth error — run `grok login`")
    return ("degraded", None,
            f"live probe failed (rc={proc.returncode}, non-auth — not gated)")


def check_repo():
    try:
        proc = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            capture_output=True, text=True, timeout=10,
        )
    except (subprocess.TimeoutExpired, OSError):
        return ("degraded", None, "git unavailable — correctness species off")
    if proc.returncode == 0 and proc.stdout.strip() == "true":
        return ("ready", None, "git repo — correctness species available")
    return ("degraded", None, "not a git repo — quality species only")


def check_gates():
    """Discover deterministic gates (the floor). Informational."""
    gates = []
    if os.path.exists("package.json"):
        try:
            scripts = json.load(open("package.json")).get("scripts", {})
        except (json.JSONDecodeError, OSError):
            scripts = {}
        for name in ("typecheck", "tsc", "test", "lint", "build"):
            if name in scripts:
                gates.append(f"npm run {name}")
    if os.path.exists("Makefile"):
        gates.append("make (inspect targets)")
    if os.path.exists("pyproject.toml"):
        gates.append("pytest / ruff (if configured)")
    if gates:
        return ("ready", None, "found: " + ", ".join(gates)), gates
    return ("degraded", None,
            "no gates auto-discovered — floor must be supplied or skipped"), gates


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--agent", action="store_true")
    ap.add_argument("--no-live", action="store_true",
                    help="skip the live critic auth probe")
    args = ap.parse_args()

    critic_check, critic_cmd = check_critic()
    gates_check, gates = check_gates()
    checks = {
        "critic": critic_check,
        "auth": check_auth(critic_cmd, live=not args.no_live),
        "repo": check_repo(),
        "gates": gates_check,
    }
    overall = "ready"
    for s, _g, _d in checks.values():
        if RANK[s] > RANK[overall]:
            overall = s

    print("gauntlet readiness", file=sys.stderr)
    for n, (s, g, d) in checks.items():
        suffix = f"  [{g}]" if g else ""
        print(f"  {MARK[s]} {n:<7} {d}{suffix}", file=sys.stderr)
    print(f"  → overall: {overall}", file=sys.stderr)

    payload = {
        "overall": overall,
        "checks": {n: {"status": s, "gate": g, "detail": d}
                   for n, (s, g, d) in checks.items()},
        "critic_cmd": critic_cmd,
        "gates": gates,
        "summary": "; ".join(f"{n}={s}" for n, (s, _g, _d) in checks.items()),
    }
    print(json.dumps(payload, indent=2))
    sys.exit(1 if overall == "down" else 0)


if __name__ == "__main__":
    main()
