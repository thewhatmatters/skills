#!/usr/bin/env python3
"""Extract friction signals from a session transcript for refine-skill (spec A4).

One concern: read a Claude Code session .jsonl and surface the raw signals that
hint a skill needs improvement — skill invocations, one-off bash workarounds,
file edits/writes, errors, and gate/degrade messages — each tagged with a
message index `i` so the NATIVE reasoning layer can cite and classify them.
This script ONLY extracts; it does not judge (classification lives in
references/reflection-model.md).

I/O: --transcript PATH (default newest .jsonl for this project) [--skill NAME]
     · stdout JSON · stderr diagnostics · never hangs (pure local file read).
Exit 0 with signals, 1 if the transcript can't be read.

JSON shape:
  {"transcript", "skill_filter",
   "skill_invocations": [{"i","skill","args"}],
   "signals": [{"i","kind","detail","path"?,"inside_skill"?}],
   "summary": {"messages","skill_invocations","signals","by_kind":{...}}}
"""
import argparse
import json
import os
import re
import sys

PROJECTS_DIR = os.path.expanduser("~/.claude/projects")
SKILLS_DIR = os.path.expanduser("~/.claude/skills")

# A bash command that wrangles data inline usually means the skill's own scripts
# left work for Claude to finish by hand — the strongest "skill bug" signal.
_WORKAROUND_RE = re.compile(r"python3?\s+-c|<<\s*['\"]?EOF|json\.load|re\.(sub|split|findall)")
# Script output that announces a gate or a degraded capability.
_GATE_RE = re.compile(r"\bgated\b|\bdegrade[d]?\b|→ overall: (?:degraded|gated|down)|\[[A-Z][A-Z0-9_]+\]")
_ERR_RE = re.compile(r"Traceback \(most recent call last\)|⛔|non-zero exit|exit code [1-9]|\bError:|\bException:")


def _encode(path):
    return os.path.join(PROJECTS_DIR, path.replace("/", "-").replace(".", "-"))


def project_transcript_dir(cwd=None):
    """Transcript dir for the session's project. Claude Code encodes the cwd by
    replacing '/' and '.' with '-'. Walk cwd then its ancestors so the skill
    still resolves when a script is run from a subdirectory."""
    cwd = cwd or os.getcwd()
    while True:
        d = _encode(cwd)
        if os.path.isdir(d) and any(f.endswith(".jsonl") for f in os.listdir(d)):
            return d
        parent = os.path.dirname(cwd)
        if parent == cwd:
            return _encode(cwd or os.getcwd())  # nothing matched; encoded cwd
        cwd = parent


def newest_transcript():
    d = project_transcript_dir()
    try:
        paths = [os.path.join(d, f) for f in os.listdir(d) if f.endswith(".jsonl")]
    except OSError:
        return None
    return max(paths, key=os.path.getmtime) if paths else None


def _text_of(content):
    """Flatten an assistant/user message content list to plain text."""
    if isinstance(content, str):
        return content
    out = []
    if isinstance(content, list):
        for blk in content:
            if isinstance(blk, dict) and isinstance(blk.get("text"), str):
                out.append(blk["text"])
    return " ".join(out)


def _result_text(content):
    """Text from a tool_result block's content (str or list of parts)."""
    if isinstance(content, str):
        return content
    out = []
    if isinstance(content, list):
        for part in content:
            if isinstance(part, dict) and isinstance(part.get("text"), str):
                out.append(part["text"])
    return " ".join(out)


def extract(path, skill_filter=None):
    invocations, signals = [], []
    i = 0
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            msg = entry.get("message")
            if not isinstance(msg, dict):
                continue
            content = msg.get("content")
            if not isinstance(content, list):
                continue
            i += 1
            for blk in content:
                if not isinstance(blk, dict):
                    continue
                bt = blk.get("type")
                if bt == "tool_use":
                    name = blk.get("name")
                    inp = blk.get("input") or {}
                    if name == "Skill":
                        invocations.append({"i": i, "skill": inp.get("skill"),
                                            "args": (inp.get("args") or "")[:160]})
                    elif name == "Bash":
                        cmd = inp.get("command", "")
                        if _WORKAROUND_RE.search(cmd):
                            signals.append({"i": i, "kind": "bash_workaround",
                                            "detail": cmd[:200]})
                    elif name in ("Edit", "Write"):
                        p = inp.get("file_path", "")
                        sig = {"i": i, "kind": "file_edit",
                               "detail": f"{name} {p}", "path": p}
                        if skill_filter:
                            sig["inside_skill"] = (f"/{skill_filter}/" in p
                                                   or p.endswith(f"/{skill_filter}"))
                        signals.append(sig)
                elif bt == "tool_result":
                    txt = _result_text(blk.get("content"))
                    # Only flag a real failure: an errored result, or a Traceback /
                    # explicit exit code. Bare "Error"/"Exception" appearing in
                    # displayed output (e.g. a Read of a script) is not a signal.
                    if blk.get("is_error") or _ERR_RE.search(txt):
                        signals.append({"i": i, "kind": "error", "detail": txt[:200]})
                    elif _GATE_RE.search(txt):
                        signals.append({"i": i, "kind": "gate", "detail": txt[:200]})
    return invocations, signals, i


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--transcript")
    ap.add_argument("--skill")
    args = ap.parse_args()

    path = args.transcript or newest_transcript()
    if not path or not os.path.isfile(path):
        print("  ⛔ no transcript found (pass --transcript=PATH)", file=sys.stderr)
        print(json.dumps({"error": "transcript not found", "transcript": path,
                          "skill_filter": args.skill, "skill_invocations": [],
                          "signals": [], "summary": {}}, indent=2))
        sys.exit(1)

    print(f"refine-skill extract_evidence: {os.path.basename(path)}", file=sys.stderr)
    invocations, signals, nmsg = extract(path, args.skill)

    by_kind = {}
    for s in signals:
        by_kind[s["kind"]] = by_kind.get(s["kind"], 0) + 1

    result = {
        "transcript": path,
        "skill_filter": args.skill,
        "skill_invocations": invocations,
        "signals": signals,
        "summary": {"messages": nmsg, "skill_invocations": len(invocations),
                    "signals": len(signals), "by_kind": by_kind},
    }
    print(f"  ✅ {len(invocations)} skill invocation(s), {len(signals)} signal(s) "
          f"across {nmsg} messages", file=sys.stderr)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(0)


if __name__ == "__main__":
    main()
