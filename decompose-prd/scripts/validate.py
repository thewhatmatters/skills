#!/usr/bin/env python3
"""Validate a prd.json against the Ralph-compatible schema + house rules (spec A4).

One concern: deterministically check the structure that decompose-prd must
always produce, so the NATIVE reasoning step can't quietly emit something a
Ralph runner will choke on. Catches the mechanical mistakes; the *quality* of
the decomposition (sizing, real dependency order) stays human/model judgment.

Checks (errors → invalid):
  - file parses as JSON; has project, branchName (starts "ralph/"), description,
    non-empty userStories list
  - warns if generatedAt / sourcePrd metadata is missing (A10 self-containment)
  - each story: id, title, description, acceptanceCriteria (non-empty list),
    integer priority, boolean passes, notes (str)
  - every story's acceptanceCriteria contains "Typecheck passes"
  - ids unique; priorities cover 1..N with no gaps/dupes
Checks (warnings → still valid):
  - ids not in US-001 sequential form
  - a UI-ish story (title/criteria mention ui/page/button/component/badge/...)
    with no browser-verify criterion

I/O: --in PATH (or stdin) · stdout JSON {ok, errors, warnings, story_count} ·
stderr human board · exit 1 on errors (invalid), else 0.
"""
import argparse
import json
import re
import sys

UI_HINT = re.compile(r"\b(ui|page|button|component|badge|dropdown|modal|screen|"
                     r"form|view|render|frontend|css|layout)\b", re.I)
VERIFY_HINT = re.compile(r"verify in browser|in the browser|browser", re.I)


def validate(doc):
    errors, warnings = [], []

    for key in ("project", "branchName", "description", "userStories"):
        if key not in doc:
            errors.append(f"missing top-level key: {key}")
    if isinstance(doc.get("branchName"), str) and not doc["branchName"].startswith("ralph/"):
        warnings.append(f"branchName should start with 'ralph/': {doc['branchName']!r}")
    # A10: the artifact should record what it was built from and when.
    for meta in ("generatedAt", "sourcePrd"):
        if not doc.get(meta):
            warnings.append(f"missing {meta} (A10: record source PRD + date so the "
                            f"artifact is self-contained)")
    if isinstance(doc.get("generatedAt"), str) and \
            not re.match(r"\d{4}-\d{2}-\d{2}", doc["generatedAt"]):
        warnings.append(f"generatedAt should be an ISO date (YYYY-MM-DD): "
                        f"{doc['generatedAt']!r}")

    stories = doc.get("userStories")
    if not isinstance(stories, list) or not stories:
        errors.append("userStories must be a non-empty list")
        return errors, warnings, 0

    ids, priorities = [], []
    for i, s in enumerate(stories):
        where = f"story[{i}]"
        if not isinstance(s, dict):
            errors.append(f"{where}: not an object")
            continue
        for key, typ in (("id", str), ("title", str), ("description", str),
                         ("priority", int), ("passes", bool), ("notes", str)):
            if key not in s:
                errors.append(f"{where}: missing {key}")
            elif not isinstance(s[key], typ) or (typ is int and isinstance(s[key], bool)):
                errors.append(f"{where}: {key} must be {typ.__name__}")
        ac = s.get("acceptanceCriteria")
        if not isinstance(ac, list) or not ac:
            errors.append(f"{where}: acceptanceCriteria must be a non-empty list")
            ac = []
        if not any(isinstance(c, str) and c.strip().lower() == "typecheck passes" for c in ac):
            errors.append(f"{where} ({s.get('id', '?')}): missing 'Typecheck passes' criterion")
        if isinstance(s.get("id"), str):
            ids.append(s["id"])
        if isinstance(s.get("priority"), int) and not isinstance(s.get("priority"), bool):
            priorities.append(s["priority"])
        # warnings
        if isinstance(s.get("id"), str) and not re.fullmatch(r"US-\d{3,}", s["id"]):
            warnings.append(f"{where}: id {s['id']!r} not in US-00N form")
        blob = " ".join(str(x) for x in [s.get("title", ""), *ac])
        if UI_HINT.search(blob) and not any(VERIFY_HINT.search(str(c)) for c in ac):
            warnings.append(f"{where} ({s.get('id', '?')}): looks like UI but has no "
                            f"browser-verify criterion")

    if len(ids) != len(set(ids)):
        errors.append("duplicate story ids")
    if priorities:
        if sorted(priorities) != list(range(1, len(priorities) + 1)):
            errors.append(f"priorities must be 1..{len(priorities)} with no gaps/dupes; "
                          f"got {sorted(priorities)}")

    return errors, warnings, len(stories)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", help="prd.json path (default: stdin)")
    ap.add_argument("--agent", action="store_true")
    args = ap.parse_args()

    try:
        raw = open(args.inp).read() if args.inp else sys.stdin.read()
        doc = json.loads(raw)
    except OSError as e:
        print(f"FATAL: cannot read input ({e})", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(json.dumps({"ok": False, "errors": [f"invalid JSON: {e}"],
                          "warnings": [], "story_count": 0}, indent=2))
        print(f"⛔ invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    errors, warnings, n = validate(doc)
    ok = not errors
    print(f"prd.json validation: {'✅ valid' if ok else '⛔ invalid'} "
          f"({n} stories, {len(errors)} errors, {len(warnings)} warnings)",
          file=sys.stderr)
    for e in errors:
        print(f"  ⛔ {e}", file=sys.stderr)
    for w in warnings:
        print(f"  ⚠  {w}", file=sys.stderr)
    print(json.dumps({"ok": ok, "errors": errors, "warnings": warnings,
                      "story_count": n}, indent=2))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
