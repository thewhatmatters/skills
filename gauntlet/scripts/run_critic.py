#!/usr/bin/env python3
"""Run one isolated critic pass over a packet file (spec A4: one concern).

Invokes the critic CLI (Grok) headless with a structured-output schema and
returns the validated verdict. The packet file IS the critic's whole world
— context isolation is enforced by construction (no repo access needed).

I/O: --packet=PATH (required, the assembled packet text) ·
--critic=CMD (optional; else layered resolution as in preflight) ·
--timeout=SECS (default 300) · stdout JSON
{status, verdict, findings, summary, raw_excerpt} · diagnostics stderr.

Exit codes: 0 = valid verdict · 1 = critic unavailable (caller falls back
to the subagent critic) · 2 = invalid/unparseable output (caller retries
once, then falls back). Never hangs: hard subprocess timeout.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys

SCHEMA = {
    "type": "object",
    "properties": {
        "verdict": {"type": "string", "enum": ["APPROVED", "REVISE"]},
        "findings": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "severity": {"type": "string",
                                 "enum": ["critical", "important", "minor"]},
                    "category": {"type": "string"},
                    "confidence": {"type": "string",
                                   "enum": ["high", "medium", "low"]},
                    "location": {"type": "string"},
                    "issue": {"type": "string"},
                    "evidence": {"type": "string"},
                    "suggested_test": {"type": "string"},
                },
                "required": ["severity", "category", "confidence",
                             "location", "issue"],
            },
        },
        "summary": {"type": "string"},
    },
    "required": ["verdict", "findings"],
}


def resolve_critic(explicit):
    if explicit:
        return explicit
    override = os.environ.get("GAUNTLET_CRITIC_CMD", "").strip()
    if override:
        return override
    on_path = shutil.which("grok")
    if on_path:
        return on_path
    known = os.path.expanduser("~/.local/bin/grok")
    return known if os.access(known, os.X_OK) else None


def fail(code, status, detail, raw=""):
    print(f"run_critic: {detail}", file=sys.stderr)
    print(json.dumps({"status": status, "verdict": None, "findings": [],
                      "summary": detail, "raw_excerpt": raw[:2000]}))
    sys.exit(code)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--packet", required=True)
    ap.add_argument("--critic")
    ap.add_argument("--timeout", type=int, default=300)
    args = ap.parse_args()

    critic = resolve_critic(args.critic)
    if critic is None:
        fail(1, "unavailable", "no critic binary resolves")
    if not os.path.exists(args.packet):
        fail(2, "invalid", f"packet file not found: {args.packet}")

    cmd = [critic, "--prompt-file", args.packet,
           "--output-format", "json",
           "--json-schema", json.dumps(SCHEMA),
           "--max-turns", "3"]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True,
                              timeout=args.timeout)
    except subprocess.TimeoutExpired:
        fail(1, "unavailable", f"critic timed out after {args.timeout}s")
    except OSError as e:
        fail(1, "unavailable", f"critic failed to launch: {e}")

    if proc.returncode != 0:
        fail(1, "unavailable",
             f"critic exited rc={proc.returncode}", proc.stderr)

    try:
        envelope = json.loads(proc.stdout)
    except json.JSONDecodeError:
        fail(2, "invalid", "critic stdout is not JSON", proc.stdout)

    result = envelope.get("structuredOutput")
    if not isinstance(result, dict):
        fail(2, "invalid", "no structuredOutput in critic response",
             proc.stdout)
    if result.get("verdict") not in ("APPROVED", "REVISE"):
        fail(2, "invalid", f"bad verdict: {result.get('verdict')!r}",
             proc.stdout)
    findings = result.get("findings")
    if not isinstance(findings, list):
        fail(2, "invalid", "findings is not a list", proc.stdout)

    print(f"run_critic: {result['verdict']} with {len(findings)} finding(s)",
          file=sys.stderr)
    print(json.dumps({
        "status": "ok",
        "verdict": result["verdict"],
        "findings": findings,
        "summary": result.get("summary", ""),
        "raw_excerpt": "",
    }, indent=2))


if __name__ == "__main__":
    main()
