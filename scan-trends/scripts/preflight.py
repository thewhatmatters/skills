#!/usr/bin/env python3
"""
Preflight readiness check — run BEFORE the sources so the skill knows it will
"fire on all cylinders" (or which gates to fire first).

Usage: python3 preflight.py            (X session is always really verified)
       python3 preflight.py --deep      (also launch-tests bundled Chromium)

Prints a human-readable board to STDERR and a machine-readable JSON object to
STDOUT for the skill's Step 0.5 to parse:

  {"sources": {"<name>": {"status": "...", "detail": "...", "gate": <id|null>}},
   "env_warnings": [...],
   "summary": {"ready": N, "degraded": N, "gated": N, "down": N}}

status: ready | degraded (runs, weaker) | gated (recoverable setup gap) | down
gate:   "x_login" | "web_key" | null   (keys into Recoverable Setup Gates)
"""
import sys, os, json, socket
import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _env  # noqa: E402

DEEP = "--deep" in sys.argv[1:]
PROFILE_DIR = os.environ.get("X_PROFILE_DIR") or os.path.expanduser(
    "~/.scan-trends/x-profile"
)


def _reach(url, timeout=5):
    try:
        requests.get(url, timeout=timeout)
        return True
    except Exception:
        return False


def _chromium_ok():
    try:
        from playwright.sync_api import sync_playwright
    except Exception:
        return False, "playwright not importable"
    override = os.environ.get("PW_CHROMIUM_PATH")
    sandbox = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
    if override and os.path.exists(override):
        return True, f"PW_CHROMIUM_PATH={override}"
    if os.path.exists(sandbox):
        return True, "sandbox chromium"
    try:
        with sync_playwright() as p:
            path = p.chromium.executable_path
            if path and os.path.exists(path):
                if DEEP:
                    b = p.chromium.launch(headless=True,
                                          args=["--no-sandbox"])
                    b.close()
                    return True, "bundled chromium (launch OK)"
                return True, "bundled chromium"
    except Exception as e:
        return False, f"chromium unavailable: {e}"
    return False, "no chromium"


def _x_session():
    """Really verify X auth the same way x.py authenticates: cookie mode
    (X_AUTH_TOKEN/X_CT0) if set, else the persistent profile. A profile dir can
    exist with no valid session, so always launch and check, not file heuristics."""
    try:
        import x as xmod
    except Exception as e:
        return "gated", f"x.py unimportable: {e}", "x_login"

    cookies = xmod.x_cookies()
    if not cookies:
        if not os.path.isdir(PROFILE_DIR) or not (
            os.path.isdir(os.path.join(PROFILE_DIR, "Default")) or any(
                n.lower().startswith(("cookies", "default"))
                for n in os.listdir(PROFILE_DIR))):
            return "gated", "no cookies & no profile — X not authed", "x_login"

    try:
        from playwright.sync_api import sync_playwright, TimeoutError as PWT
        with sync_playwright() as p:
            browser = None
            if cookies:
                lk = {"headless": True, "args": ["--no-sandbox"]}
                if xmod.BROWSER_PATH:
                    lk["executable_path"] = xmod.BROWSER_PATH
                browser = p.chromium.launch(**lk)
                ctx = browser.new_context(user_agent=xmod._UA)
                ctx.add_cookies(xmod._cookie_objs(*cookies))
                label = "cookie auth"
            else:
                ctx = p.chromium.launch_persistent_context(
                    PROFILE_DIR, headless=True, args=["--no-sandbox"])
                label = "profile session"
            pg = ctx.pages[0] if ctx.pages else ctx.new_page()
            # Distinguish "logged out" (a real setup gap → gate) from a
            # transient x.com outage (never a gate — spec A7a), the same way
            # runtime x.py separates NO_SESSION from TIMEOUT.
            verdict = None
            try:
                pg.goto("https://x.com/home", timeout=20000)
                try:
                    pg.wait_for_selector(
                        '[data-testid="SideNav_AccountSwitcher_Button"]',
                        timeout=8000)
                    verdict = ("ready", f"{label} verified", None)
                except PWT:
                    if xmod._looks_logged_out(pg):
                        verdict = ("gated",
                                   f"{label} invalid (logged out/expired)",
                                   "x_login")
                    else:
                        verdict = ("degraded",
                                   f"{label} unverified — x.com slow or "
                                   "changed markup (transient); retry later",
                                   None)
            except PWT:
                verdict = ("degraded",
                           "x.com unreachable (transient); retry later", None)
            for closer in (ctx, browser):
                try:
                    closer and closer.close()
                except Exception:
                    pass
            return verdict
    except Exception as e:
        return "degraded", f"session unverifiable ({e}) — transient, not a gate; retry later", None


def _web_provider():
    _env.load()
    if os.environ.get("TAVILY_API_KEY"):
        return "ready", "Tavily key present", None
    if os.environ.get("EXA_API_KEY"):
        return "ready", "Exa key present", None
    return "gated", "no TAVILY_API_KEY / EXA_API_KEY (DDG-only)", "web_key"


def main():
    chromium_ok, chromium_detail = _chromium_ok()
    x_status, x_detail, x_gate = _x_session()
    w_status, w_detail, w_gate = _web_provider()

    sources = {}

    sources["Reddit"] = (
        {"status": "ready", "detail": "reachable", "gate": None}
        if _reach("https://www.reddit.com/search.json?q=test&limit=1")
        else {"status": "down", "detail": "unreachable from here", "gate": None}
    )
    sources["Hacker News"] = (
        {"status": "ready", "detail": "Algolia reachable", "gate": None}
        if _reach("https://hn.algolia.com/api/v1/search?query=test&hitsPerPage=1")
        else {"status": "down", "detail": "Algolia unreachable", "gate": None}
    )
    sources["Polymarket"] = (
        {"status": "ready", "detail": "gamma reachable", "gate": None}
        if _reach("https://gamma-api.polymarket.com/markets?limit=1")
        else {"status": "down", "detail": "gamma unreachable", "gate": None}
    )
    sources["YouTube"] = (
        {"status": "ready", "detail": chromium_detail, "gate": None}
        if chromium_ok
        else {"status": "down", "detail": chromium_detail, "gate": None}
    )
    sources["X/Twitter"] = {"status": x_status, "detail": x_detail, "gate": x_gate}
    sources["Web"] = {"status": w_status, "detail": w_detail, "gate": w_gate}

    summary = {"ready": 0, "degraded": 0, "gated": 0, "down": 0}
    for v in sources.values():
        summary[v["status"]] = summary.get(v["status"], 0) + 1

    warnings = _env.perm_warnings()

    icon = {"ready": "✓", "degraded": "⚠", "gated": "✗", "down": "✗"}
    print("scan-trends preflight", file=sys.stderr)
    for name, v in sources.items():
        print(f" {icon[v['status']]} {name:<12} {v['detail']}", file=sys.stderr)
    for w in warnings:
        print(f" ⚠ env         {w}", file=sys.stderr)
    print(f" → {summary['ready']} ready, {summary['degraded']} degraded, "
          f"{summary['gated']} gated, {summary['down']} down", file=sys.stderr)

    print(json.dumps({"sources": sources, "env_warnings": warnings,
                       "summary": summary}, indent=2))


if __name__ == "__main__":
    main()
