#!/usr/bin/env python3
"""Mechanical markdown lint via markdownlint-cli (spec A4/A11).

I/O: `lint.py FILE [FILE ...]` · stdout JSON
{status: ok|findings|unavailable|error, tool, findings: [{file, line, rule,
detail}], summary} · stderr diagnostics · exit 0 always (a missing tool or a
lint hit is data, not a failure — the judgment pass still runs).

Config encodes the mechanical subset of references/markdown-style.md
(ATX headings, dash bullets, blank-line discipline, fenced-language,
MD013 line-length OFF — soft house rule, judgment not lint).
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

CONFIG = {
    "default": True,
    "MD003": {"style": "atx"},
    "MD004": {"style": "dash"},
    "MD013": False,
    "MD024": {"siblings_only": True},
}
TIMEOUT_S = 120  # npx may download the CLI on first use


def resolve():
    """A11 ladder: $MARKDOWNLINT_BIN -> PATH -> npx. Returns (argv, label) or (None, None)."""
    override = os.environ.get("MARKDOWNLINT_BIN", "").strip()
    if override and shutil.which(override):
        return ([override], override)
    if shutil.which("markdownlint"):
        return (["markdownlint"], "markdownlint")
    if shutil.which("npx"):
        return (["npx", "--yes", "markdownlint-cli"], "npx markdownlint-cli")
    return (None, None)


def parse_json_output(raw):
    """markdownlint --json emits a JSON array (on stderr in cli versions)."""
    raw = raw.strip()
    if not raw:
        return []
    start = raw.find("[")
    if start == -1:
        return []
    return json.loads(raw[start:])


def emit(payload):
    print(json.dumps(payload, indent=2))
    sys.exit(0)


def main():
    files = [a for a in sys.argv[1:] if not a.startswith("-")]
    if not files:
        emit({"status": "error", "tool": None, "findings": [],
              "summary": "usage: lint.py FILE [FILE ...]"})
    missing = [f for f in files if not os.path.isfile(f)]
    if missing:
        emit({"status": "error", "tool": None, "findings": [],
              "summary": f"not a file: {', '.join(missing)}"})
    argv, label = resolve()
    if argv is None:
        emit({"status": "unavailable", "tool": None, "findings": [],
              "summary": "markdownlint unresolvable ($MARKDOWNLINT_BIN/PATH/npx) — judgment-only pass"})

    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as cf:
        json.dump(CONFIG, cf)
        config_path = cf.name
    try:
        proc = subprocess.run(
            argv + ["--json", "--config", config_path] + files,
            capture_output=True, text=True, timeout=TIMEOUT_S,
        )
    except subprocess.TimeoutExpired:
        emit({"status": "error", "tool": label, "findings": [],
              "summary": f"{label} timed out after {TIMEOUT_S}s"})
    except OSError as exc:
        emit({"status": "error", "tool": label, "findings": [],
              "summary": f"{label} failed to run: {exc}"})
    finally:
        try:
            os.unlink(config_path)
        except OSError:
            pass

    try:
        # cli emits --json results on stderr; try it first, then stdout.
        entries = parse_json_output(proc.stderr) or parse_json_output(proc.stdout)
    except json.JSONDecodeError:
        print(proc.stderr[:2000], file=sys.stderr)
        emit({"status": "error", "tool": label, "findings": [],
              "summary": "could not parse markdownlint output"})

    findings = [{
        "file": e.get("fileName", ""),
        "line": e.get("lineNumber", 0),
        "rule": "/".join(e.get("ruleNames", [])[:2]),
        "detail": (e.get("ruleDescription", "") +
                   (f" [{e['errorDetail']}]" if e.get("errorDetail") else "")),
    } for e in entries]
    emit({
        "status": "findings" if findings else "ok",
        "tool": label,
        "findings": findings,
        "summary": f"{len(findings)} mechanical finding(s) across {len(files)} file(s)",
    })


if __name__ == "__main__":
    main()
