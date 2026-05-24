#!/usr/bin/env python3
"""All-skills triggering bake-off for the audit-skill `--triggers` mode.

One concern: given a labeled eval set, measure which skill each query actually
routes to in THIS environment (all installed skills present), so we can see
real triggering + cross-triggering between overlapping skills.

WHY NOT skill-creator's run_eval.py: it registers an ad-hoc command named
`<skill>-skill-<uuid>` and only counts a trigger on THAT name. When the skill is
already installed (our case — user-scope skills are always loaded), Claude fires
the *real* skill (e.g. {"skill":"deep-research"}), whose name ≠ the ad-hoc name,
so every trigger goes undetected → false 0/3. This harness instead presents all
real skills and records whichever one fires — the live routing decision.

METHOD: for each query, run `claude -p <q> --output-format stream-json`, parse
the first assistant `tool_use` named "Skill", record its `input.skill`, then
KILL the process immediately (we only want the routing decision, not to run the
skill). A wall-clock timer guarantees we never hang.

I/O CONTRACT
    stdin/args : --eval-set PATH (JSON: [{"query","expected"}, ...])
    stdout     : JSON {summary:{match,total}, results:[{query,expected,fired}]}
    stderr     : human-readable table + progress (diagnostics)
    exit       : 0 on completion — absence of `claude` is reported in JSON as
                 fired="(claude-cli-missing)", not a crash; 1 only when the eval
                 set file can't be read (no input to measure)

Run preflight.py first to gate on the `claude` CLI and confirm cost intent.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import date


def claude_bin():
    """Layered resolution (spec A11): $CLAUDE_BIN override → on-PATH `claude`."""
    return os.environ.get("CLAUDE_BIN") or shutil.which("claude")


def run_query(item, model, timeout):
    q = item["query"]
    exe = claude_bin()
    if not exe:
        return {"query": q, "expected": item.get("expected"), "fired": "(claude-cli-missing)"}
    cmd = [exe, "-p", q, "--output-format", "stream-json", "--verbose"]
    if model:
        cmd += ["--model", model]
    # CLAUDECODE is unset so a nested `claude -p` is allowed (the guard is only
    # for interactive terminal conflicts; programmatic subprocess use is safe).
    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                            env=env, text=True)
    killer = threading.Timer(timeout, proc.kill)
    killer.start()
    fired = None
    try:
        for line in proc.stdout:
            line = line.strip()
            if not line:
                continue
            try:
                e = json.loads(line)
            except Exception:
                continue
            if isinstance(e, dict) and e.get("type") == "assistant" \
                    and isinstance(e.get("message"), dict):
                for block in e["message"].get("content", []):
                    if isinstance(block, dict) and block.get("type") == "tool_use" \
                            and block.get("name") == "Skill":
                        fired = block.get("input", {}).get("skill") or "Skill(?)"
                        break
            if fired:
                break
    finally:
        killer.cancel()
        proc.kill()
        try:
            proc.wait(timeout=5)
        except Exception:
            pass
    return {"query": q, "expected": item.get("expected"), "fired": fired or "none"}


def main():
    ap = argparse.ArgumentParser(description="All-skills triggering bake-off")
    ap.add_argument("--eval-set", required=True, help="JSON [{query, expected}, ...]")
    ap.add_argument("--out", help="write result JSON here (default: stdout)")
    ap.add_argument("--model", default=None, help="model id for `claude -p` "
                    "(default: the CLI's configured model)")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--timeout", type=int, default=120, help="seconds per query")
    args = ap.parse_args()

    try:
        evals = json.loads(open(args.eval_set).read())
    except OSError as e:
        print(f"FATAL: cannot read eval set ({e})", file=sys.stderr)
        sys.exit(1)

    if not shutil.which("claude"):
        print("WARN: `claude` CLI not found — results will be inconclusive "
              "(run preflight.py).", file=sys.stderr)

    print(f"triggering bake-off: {len(evals)} queries, model="
          f"{args.model or 'default'}, {args.workers} workers", file=sys.stderr)
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        results = list(ex.map(lambda it: run_query(it, args.model, args.timeout), evals))

    match = sum(r["fired"] == r["expected"] for r in results)
    payload = {
        "summary": {"match": match, "total": len(results),
                    "model": args.model or "default", "date": date.today().isoformat(),
                    "eval_set": args.eval_set},
        "results": results,
    }

    print(f"\nrouting match: {match}/{len(results)}", file=sys.stderr)
    for r in results:
        mark = "OK " if r["fired"] == r["expected"] else "XX "
        print(f"  {mark} exp={str(r['expected']):13} fired={r['fired']:15} "
              f"{r['query'][:50]}", file=sys.stderr)

    out = json.dumps(payload, indent=2)
    if args.out:
        open(args.out, "w").write(out)
        print(f"\nwrote {args.out}", file=sys.stderr)
    else:
        print(out)


if __name__ == "__main__":
    main()
