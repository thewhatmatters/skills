#!/usr/bin/env python3
"""Run Lighthouse against a URL and compare lab metrics to budgets (spec A4).

One concern: collect the lab numbers and the pass/fail per budget. Mapping
failures to fixes is the model's job (references/vitals.md).

Lighthouse resolution is layered (spec A11):
    $LIGHTHOUSE_BIN -> `lighthouse` on PATH -> `npx --yes lighthouse`
    -> degraded marker LIGHTHOUSE_UNAVAILABLE (exit 2)

Honesty note baked into the output: these are LAB metrics. INP is a field
metric and is NOT measured here — TBT is the lab proxy. Never report INP
from this script's output.

Default budgets (override with --budget key=value, repeatable):
    perf_score >= 0.90 · lcp_ms <= 2500 · cls <= 0.10 · tbt_ms <= 300

I/O:
    stdin  : —
    stdout : JSON {url, ok, error?, lab:{perf_score, lcp_ms, cls, tbt_ms,
             fcp_ms, speed_index_ms}, budgets, verdicts:{<metric>:
             {value, budget, pass}}, failed_audits:[{id, title, savings_ms?}]}
    stderr : progress diagnostics + markers (LIGHTHOUSE_UNAVAILABLE, LH_FAILED)
    exit   : 0 = measured (even if budgets fail) · 2 = could not measure

Timeout: 240s on the Lighthouse run — never hangs.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys

LH_TIMEOUT_S = 240
DEFAULT_BUDGETS = {"perf_score": 0.90, "lcp_ms": 2500.0, "cls": 0.10, "tbt_ms": 300.0}
# budget direction: perf_score is >=, the rest are <=
HIGHER_IS_BETTER = {"perf_score"}
FAILED_AUDITS_MAX = 12


def resolve_lighthouse():
    explicit = os.environ.get("LIGHTHOUSE_BIN")
    if explicit:
        return [explicit]
    if shutil.which("lighthouse"):
        return ["lighthouse"]
    if shutil.which("npx"):
        return ["npx", "--yes", "lighthouse"]
    return None


def resolve_chrome():
    """Chrome for lighthouse's launcher: $CHROME_PATH -> system Chrome ->
    Playwright's bundled Chromium (spec A11). None = let lighthouse try."""
    from pathlib import Path
    explicit = os.environ.get("CHROME_PATH")
    if explicit and Path(explicit).exists():
        return explicit
    mac = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    if Path(mac).exists():
        return mac
    for name in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser"):
        p = shutil.which(name)
        if p:
            return p
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            path = p.chromium.executable_path
            if Path(path).exists():
                return path
    except Exception:  # noqa: BLE001 — playwright optional here
        pass
    return None


def _error_summary(stderr_text):
    """The cause is at the TOP of a node stack trace — surface lines that
    name an error before falling back to the head of stderr."""
    lines = [ln for ln in (stderr_text or "").splitlines() if ln.strip()]
    named = [ln for ln in lines if "Error" in ln or "ERROR" in ln]
    return " | ".join((named or lines)[:3])[:400] or "lighthouse failed"


def run_lighthouse(cmd_base, url):
    cmd = cmd_base + [
        url, "--output=json", "--output-path=stdout", "--quiet",
        "--only-categories=performance",
        "--chrome-flags=--headless=new --no-sandbox",
    ]
    env = dict(os.environ)
    chrome = resolve_chrome()
    if chrome:
        env["CHROME_PATH"] = chrome
        print(f"chrome: {chrome}", file=sys.stderr)
    print(f"running: {' '.join(cmd)}", file=sys.stderr)
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True,
                              timeout=LH_TIMEOUT_S, env=env)
    except subprocess.TimeoutExpired:
        return None, f"timed out after {LH_TIMEOUT_S}s"
    except OSError as e:
        return None, str(e)
    if proc.returncode != 0 and not proc.stdout.strip():
        return None, _error_summary(proc.stderr)
    try:
        return json.loads(proc.stdout), None
    except ValueError:
        return None, "lighthouse emitted unparseable output"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True)
    ap.add_argument("--budget", action="append", default=[],
                    metavar="KEY=VALUE",
                    help=f"override a budget (keys: {', '.join(DEFAULT_BUDGETS)})")
    ap.add_argument("--agent", action="store_true", help=argparse.SUPPRESS)
    args = ap.parse_args()

    budgets = dict(DEFAULT_BUDGETS)
    for spec in args.budget:
        key, _, val = spec.partition("=")
        if key not in budgets or not val:
            print(f"BAD_BUDGET ignored: {spec!r} (keys: {', '.join(budgets)})",
                  file=sys.stderr)
            continue
        try:
            budgets[key] = float(val)
        except ValueError:
            print(f"BAD_BUDGET ignored: {spec!r} (not a number)", file=sys.stderr)

    cmd_base = resolve_lighthouse()
    if cmd_base is None:
        print("LIGHTHOUSE_UNAVAILABLE: no $LIGHTHOUSE_BIN, lighthouse, or npx",
              file=sys.stderr)
        print(json.dumps({"url": args.url, "ok": False,
                          "error": "lighthouse unavailable (Node/npx missing)"}))
        sys.exit(2)

    report, err = run_lighthouse(cmd_base, args.url)
    if report is None:
        print(f"LH_FAILED: {err}", file=sys.stderr)
        print(json.dumps({"url": args.url, "ok": False, "error": err}))
        sys.exit(2)

    audits = report.get("audits", {})

    def num(audit_id):
        return (audits.get(audit_id) or {}).get("numericValue")

    lab = {
        "perf_score": (report.get("categories", {}).get("performance") or {}).get("score"),
        "lcp_ms": num("largest-contentful-paint"),
        "cls": num("cumulative-layout-shift"),
        "tbt_ms": num("total-blocking-time"),
        "fcp_ms": num("first-contentful-paint"),
        "speed_index_ms": num("speed-index"),
    }
    verdicts = {}
    for key, budget in budgets.items():
        value = lab.get(key)
        if value is None:
            verdicts[key] = {"value": None, "budget": budget, "pass": None}
            continue
        ok = value >= budget if key in HIGHER_IS_BETTER else value <= budget
        verdicts[key] = {"value": round(value, 4), "budget": budget, "pass": ok}

    failed = [{"id": aid,
               "title": a.get("title"),
               "savings_ms": (a.get("details") or {}).get("overallSavingsMs")}
              for aid, a in audits.items()
              if a.get("score") is not None and a["score"] < 0.9
              and a.get("scoreDisplayMode") in ("numeric", "binary", "metricSavings")]
    failed.sort(key=lambda x: -(x["savings_ms"] or 0))
    truncated = len(failed) > FAILED_AUDITS_MAX
    if truncated:
        print(f"note: {len(failed) - FAILED_AUDITS_MAX} more failed audits truncated",
              file=sys.stderr)

    out = {"url": args.url, "ok": True,
           "note": "LAB metrics — TBT is the lab proxy; INP is field-only and not measured here",
           "lab": lab, "budgets": budgets, "verdicts": verdicts,
           "failed_audits": failed[:FAILED_AUDITS_MAX],
           "failed_audits_truncated": truncated}
    fails = [k for k, v in verdicts.items() if v["pass"] is False]
    print(f"vitals {args.url}: perf={lab['perf_score']} "
          f"budget fails: {fails or 'none'}", file=sys.stderr)
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
