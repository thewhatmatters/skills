# Generation recipe

This file is loaded by `SKILL.md` Step 5 — progressive disclosure (spec A1).
It is the only place that holds scaffold templates; everything else stays
lean.

The 13 architecture patterns are NOT duplicated here. They live in
`~/.claude/skills/skill-architecture.md` (A1–A13). The recipe references them
by id (e.g. "spec A6 = preflight") so a future spec edit changes both the
generator and the auditor automatically.

## Substitution convention

Placeholders in the templates below use **`<<TOKEN>>` syntax**. Claude does a
plain textual replacement of every `<<TOKEN>>` with the value from §"Input
contract" when writing each file. **Do NOT touch any `{ }` you see** — those
are literal Python (f-strings, dict literals, `.format()` placeholders) and
must be emitted verbatim into the generated script.

| Token | Value source |
|---|---|
| `<<NAME>>` | input `name` |
| `<<ONE_LINER>>` | input `one_liner` |
| `<<DESCRIPTION>>` | input `description` (full trigger-rich text) |
| `<<TODAY>>` | today's date, ISO (e.g. `2026-05-19`) |
| `<<CC_VERSION>>` | input `cc_version` from `docs.py` |
| `<<DEPS_NOTES_OR_EMPTY>>` | input `deps_notes` or empty |
| `<<EXTRA_FLAG_ROWS_OR_BLANK>>` | extra rows in SKILL.md flags table (or empty) |
| `<<SECRETS_NOTE_OR_BLANK>>` | secrets convention bullets (only when `needs_secrets`) |
| `<<REFERENCES_LINK_OR_BLANK>>` | README "Where to look next" bullet for `references/` (only when used) |
| `<<KEY_NAME>>` / `<<PURPOSE>>` / `<<KEY_URL_OR_BLANK>>` | one per secret key, in the Step-7 paste block |

---

## Input contract (what Step 4 must have collected)

| Key | Source | Constraint |
|---|---|---|
| `name` | `--name=` or interactive | `^[a-z][a-z0-9-]*$`, ≤ 64 chars (live skills.md) |
| `one_liner` | interactive | one sentence, ≤ ~140 chars |
| `description` | interactive | trigger-rich; combined with `when_to_use` ≤ 1536 chars (live skills.md) |
| `needs_scripts` | flag / inferred | bool |
| `needs_secrets` | interactive | bool (false if `needs_scripts` false) |
| `deps_notes` | interactive (optional) | free text — used in handoff seed |
| `out_dir` | `--out=` (default `~/.claude/skills`) | parent for `<name>/` |
| `live_fields` | docs.py JSON Step 2 | set of valid frontmatter field names |
| `cc_version` | docs.py JSON Step 2 | string (e.g. `2.1.144`) |
| `dry_run` | flag | bool |

## Pre-write validation (fail fast — do NOT write any file if any item fails)

1. `name` matches the regex above and `<out_dir>/<name>` does not already
   exist. If it exists, STOP with a clobber error; do not merge.
2. Every frontmatter key you intend to write is in `live_fields`. The
   conservative minimum is **`name` + `description`** — these are documented
   in every Claude Code version we've seen. Optional adds (only if useful and
   present in `live_fields`): `when_to_use`, `allowed-tools`, `argument-hint`.
   **Never** invent a key.
3. `len(description + when_to_use_if_any)` ≤ 1536.
4. If `needs_secrets` and not `needs_scripts` → contradiction; ask once or
   set `needs_scripts = true`.

## Files to write (in this order)

### 1. `<out_dir>/<name>/SKILL.md`

```
---
name: <<NAME>>
description: <<DESCRIPTION>>
---

# <<NAME>>

<<ONE_LINER>>

## What it does

(One short paragraph. Spec A1: this body stays lean — bulky detail goes in
`references/` and is loaded only when relevant.)

## How to run

(Trigger phrases the user can say, plus any `/<<NAME>>` invocation.)

## Flags

| Flag | Meaning |
|------|---------|
| `--agent` | non-interactive; no prompts/pauses (spec A7b/A9) |
| `--out=PATH` | artifact location (spec A9) |
<<EXTRA_FLAG_ROWS_OR_BLANK>>

## Step 0 — Mode probe

(If `needs_scripts`: probe python3 + scripts/. Choose SCRIPTS or NATIVE per
spec A3. If `!needs_scripts`: this section becomes one line — "this is a
docs-only skill; no probe needed".)

## Steps 1..N — (skill-specific flow)

(A short numbered list. Each step that calls a script: one line + the script
name. Bulky logic goes into the script's own docstring, not here.)

## Conventions this skill follows

- Spec is `~/.claude/skills/skill-architecture.md`.
- Scripts: JSON stdout / diagnostics stderr / graceful failure (spec A4).
<<SECRETS_NOTE_OR_BLANK>>
```

### 2. `<out_dir>/<name>/README.md`

```
# <<NAME>>

**What it is:** <<ONE_LINER>>

## What you get

(Concrete artifacts/outputs in 1–3 bullets.)

## How to run

(Trigger phrases or `/<<NAME>>` invocation; one example.)

## What it needs

(One-time setup, if any. If `needs_secrets`: point at the shared
`~/.claude/skills/.env` and the keys this skill expects.)

## How it works (high level)

(3–5 numbered steps in plain language. No code. Names of any sources or
external dependencies named once.)

## Where to look next

- `SKILL.md` — operating instructions Claude follows.
- `handoff.md` — design decisions and the "why".
<<REFERENCES_LINK_OR_BLANK>>
```

### 3. `<out_dir>/<name>/handoff.md`

Seed only — the user expands it as decisions are made.

```
# <<NAME>> — Handoff & decisions

Living record of what this skill is, the decisions behind it, and any
non-obvious constraints (spec A12).

Created: <<TODAY>>  ·  Generator: skill-generator @ CC <<CC_VERSION>>

## 1. Purpose
<<ONE_LINER>>

## 2. Reusable patterns (link to spec A1..A13)
This skill follows `~/.claude/skills/skill-architecture.md` patterns A1–A13;
note here any deliberate deviations.

## 3. Decision log
- <<TODAY>>: scaffolded by skill-generator.

## 4. Known limitations / environment caveats
(empty)

## 5. Audit rubric coverage
See `skill-architecture.md` §B; this skill targets every PASS that applies.

## 6. Notes
<<DEPS_NOTES_OR_EMPTY>>
```

### 4. `<out_dir>/<name>/references/.gitkeep`

Empty file so the directory exists for future progressive-disclosure content.

### 5. `<out_dir>/<name>/scripts/` (ONLY if `needs_scripts`)

Copy verbatim from this skill's own scripts/ as templates:

- `_env.py` — copy `skill-generator/scripts/_env.py` byte-for-byte
  (trendscan handoff §5: flat name, do not rename).
- `preflight.py` — write the minimal skeleton below, then the user extends
  it with per-source checks.
- `report.py` — write the minimal skeleton below ONLY if the skill produces
  a user-facing artifact (spec A10).

#### `preflight.py` skeleton

Substitute `<<NAME>>`. Leave every `{ }` exactly as written — they are
Python f-strings the emitted script uses at runtime.

```python
#!/usr/bin/env python3
"""Readiness check for <<NAME>> (spec A6).

I/O: stdout JSON {overall, checks, summary} · stderr human board · exit 1 only on `down`.
States per check: ready | degraded | gated | down  (with a gate id).
"""
import argparse, json, sys
MARK = {"ready": "✅", "degraded": "⚠ ", "gated": "🔒", "down": "⛔"}
RANK = {"ready": 0, "degraded": 1, "gated": 2, "down": 3}


def check_spec():
    # TODO: real check — replace this stub.
    return ("ready", None, "spec present")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--agent", action="store_true")
    ap.parse_args()
    checks = {"spec": check_spec()}
    overall = "ready"
    for s, _g, _d in checks.values():
        if RANK[s] > RANK[overall]:
            overall = s
    print("<<NAME>> readiness", file=sys.stderr)
    for n, (s, g, d) in checks.items():
        suffix = f"  [{g}]" if g else ""
        print(f"  {MARK[s]} {n:<8} {d}{suffix}", file=sys.stderr)
    print(f"  → overall: {overall}", file=sys.stderr)
    payload = {
        "overall": overall,
        "checks": {n: {"status": s, "gate": g, "detail": d}
                   for n, (s, g, d) in checks.items()},
    }
    print(json.dumps(payload, indent=2))
    sys.exit(1 if overall == "down" else 0)


if __name__ == "__main__":
    main()
```

#### `report.py` skeleton (only when artifact required)

Substitute `<<NAME>>`. Leave every `{ }` exactly as written — the `TEMPLATE`
string is itself fed to Python's `.format()` at runtime, so the doubled `{{ }}`
inside it are legitimate `.format()` escapes; they MUST be emitted as-is.

```python
#!/usr/bin/env python3
"""Render a JSON summary to one self-contained HTML file (spec A10).

I/O: stdin JSON | stdout HTML | --out PATH writes to file.
"""
import argparse, html, json, sys

TEMPLATE = """<!doctype html><meta charset='utf-8'><title>{title}</title>
<style>body{{font:14px/1.4 system-ui;max-width:760px;margin:2rem auto;padding:0 1rem}}</style>
<h1>{title}</h1><p><small>generated {date}</small></p><pre>{body}</pre>"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    args = ap.parse_args()
    data = json.load(sys.stdin)
    out = TEMPLATE.format(
        title=html.escape(data.get("title", "<<NAME>> report")),
        date=html.escape(data.get("date", "")),
        body=html.escape(json.dumps(data, indent=2)),
    )
    if args.out:
        open(args.out, "w").write(out)
    else:
        sys.stdout.write(out)


if __name__ == "__main__":
    main()
```

## Secrets — shared `.env` convention (when `needs_secrets`)

Do NOT create a per-skill `.env.example`. The convention (trendscan handoff
§3.3) is: edit the shared `~/.claude/skills/.env.example` and add a block:

```
# === Used by: <<NAME>> ===
# <<KEY_NAME>>
#   Used by: <<NAME>> (<<PURPOSE>>)
#   Get a key: <<KEY_URL_OR_BLANK>>
<<KEY_NAME>>=
```

The generator MUST print this block to the run summary in Step 7 so the user
can paste it into the shared file. It MUST NOT edit the shared file itself
(side-effects outside the new skill's folder = scope creep).

## After write — emit (Step 7)

Print exactly:

```
created tree:
  <out_dir>/<<NAME>>/
    SKILL.md
    README.md
    handoff.md
    references/.gitkeep
    [scripts/ if needs_scripts]

verdict: <line from Step 6 self-audit>

to publish this skill, run:
  echo '!/<<NAME>>/' >> ~/.claude/skills/.gitignore
  git -C ~/.claude/skills add <<NAME>> .gitignore
  git -C ~/.claude/skills commit -m "Add <<NAME>>"
```

(If `dry_run` was true: print everything above with the heading "DRY RUN —
no files written".)

## Non-goals (so the generator does not creep)

- Does NOT `git add` or commit anything.
- Does NOT edit `~/.claude/skills/skill-architecture.md` (reconcile.py flags
  drift; the human owns spec edits — DESIGN.md §5).
- Does NOT edit the shared `~/.claude/skills/.env.example` (prints the
  paste-ready block in the summary instead).
- Does NOT clobber an existing target directory.
- Does NOT invent frontmatter fields outside the live set from docs.py.
