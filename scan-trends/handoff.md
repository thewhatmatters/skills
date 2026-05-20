# scan-trends — Handoff & Skill Architecture

Living record of what scan-trends is, the reusable patterns it established, why
decisions were made, and a rubric usable by a future **generate-skill** and
**audit-skill**.

Last updated: 2026-05-18.

---

## 1. What scan-trends is

A Claude Code skill that researches any topic across a recent, configurable
window and synthesizes a grounded, cited report + a self-contained HTML file.

- **Sources (6, final):** Reddit, X/Twitter, YouTube, Hacker News, Polymarket, Web.
  (Bluesky and TikTok were removed — see Decision Log.)
- **Two execution modes:** `SCRIPTS` (Python scrapers/APIs, preferred) and
  `NATIVE` (built-in `web_search` fallback), chosen by a Step 0 probe.
- **Install:** symlink `~/.claude/skills/scan-trends` → `~/Downloads/scan-trends`
  (edit the working copy; live via symlink; skill registry hot-reloads).

## 2. File inventory

```
SKILL.md                     # lean core instructions (loaded every run)
references/output-patterns.md# COMPARISON/RECOMMENDATIONS/PROMPTING templates (progressive disclosure)
scripts/
  reddit.py                  # reddit.com search JSON
  x.py                       # X/Twitter — cookie auth (primary) or persistent profile
  youtube.py                 # Playwright (YouTube)
  hackernews.py              # HN Algolia API
  polymarket.py              # Polymarket gamma API
  web.py                     # Tavily → Exa → DuckDuckGo (provider-pluggable)
  _env.py                    # shared key loader (NOT a source)
  preflight.py               # readiness check (NOT a source)
  report.py                  # JSON → self-contained results.html (NOT a source)
handoff.md                   # this file
```
Key store: `~/.claude/.env` and/or `~/.claude/skills/.env` (the latter is canonical;
`.env.example` is the committable template). `chmod 600`.

## 3. Reusable patterns (the transferable IP)

These are the generalizable conventions any skill in this family should follow.

1. **Dual-mode + Step 0 probe.** Detect environment once; pick SCRIPTS vs NATIVE;
   announce the mode. Every capability has a degraded-but-functional NATIVE path.
2. **One concern per script.** Each source/function is its own file with a
   docstring stating its I/O contract; stdout = JSON payload, stderr = diagnostics.
   This keeps failures isolated and the pieces independently testable.
3. **Shared key loader (`_env.py`).** Precedence: real env → `~/.claude/.env` →
   `~/.claude/skills/.env`. Empty values skipped (a placeholder never shadows a
   real key). Keys sent in **headers only**, never URLs/logs. `chmod 600`; warn
   on looser perms. No `python-dotenv` dependency.
4. **Preflight readiness check.** A `preflight.py` probes every dependency before
   the expensive run and emits a human board (stderr) + machine JSON (stdout):
   `status ∈ {ready, degraded, gated, down}` + a `gate` id. Verify the
   unreliable things for real (don't trust file-presence heuristics).
5. **Recoverable Setup Gates** (the crown-jewel pattern). A *one-time setup gap*
   (no key, not logged in) is NOT a transient error — do not silently degrade.
   A gate has four required parts:
   - **Unambiguous trigger** distinct from transient failures (e.g. a literal
     `NO_SESSION` stderr token vs `TIMEOUT`).
   - **`--agent` bypass** — never prompt in unattended runs; take the fallback.
   - **Ask, don't degrade** — interactive: stop and offer
     *Fix it for me / I'll do it myself / Skip it*.
   - **Graceful dead-end** — if the fix fails, fall back anyway; never block.
6. **Source/scope picker.** Default interactive runs let the user choose which
   sources run (multi-select annotated with live preflight status). Selecting a
   not-ready source fires its gate; deselecting skips it silently (only nag for
   what the user wants). Bypass: `--agent`, `--sources=a,b,c`, `--all`.
7. **Consistent flags.** `--days=N` (window, default 30), `--agent`
   (non-interactive, no prompts/pauses), `--out=PATH` (artifact location),
   `--sources=`/`--all`. `--quick`/`--deep` reserved (documented, not yet impl).
8. **Self-contained artifact.** A `report.py` turns a JSON summary into one
   dependency-free HTML file (inline CSS, light/dark, escaped) that records the
   original prompt, request date, and findings. Runs in both modes and `--agent`.
9. **Progressive disclosure.** SKILL.md stays lean (loaded every run); bulky or
   occasional detail lives in `references/` and is pulled in only when relevant.
10. **Honest verification & memory discipline.** Distinguish code-verified vs
    live-verified; report partial/degraded runs explicitly; never write secret
    values to memory/logs; record non-obvious decisions so they aren't
    re-litigated.

## 4. Conventions & audit rubric

A skill in this family passes if:

- [ ] `SKILL.md` has YAML frontmatter (`name`, trigger-rich `description`); core
      stays lean; bulky detail in `references/`.
- [ ] Environment/deps documented; a Step 0 mode probe exists with a NATIVE path.
- [ ] Every external dependency is covered by **preflight** with a 4-state status.
- [ ] Secrets only via the shared `_env.py` convention; header-only; `chmod 600`;
      never logged; `.env.example` committed, `.env` gitignored.
- [ ] Recoverable setup gaps use the **Setup Gate** pattern (4 parts); transient
      errors do NOT trigger gates; `--agent` bypasses all prompts.
- [ ] Each script: single concern, docstring I/O contract, JSON-stdout /
      diagnostics-stderr, graceful failure (never hangs the run).
- [ ] Standard flags present and consistent (`--days`, `--agent`, `--out`, …).
- [ ] Produces a self-contained artifact recording prompt + date + results.
- [ ] No hard-coded environment paths without fallback (e.g. browser binary
      resolution: override → sandbox → bundled).
- [ ] Honest fallbacks; partial runs disclosed; "fire on all cylinders" verified
      by preflight, not assumed.

## 5. Decision log (the "why")

- **`/last30days` → `/scan-trends`** + `--days=N`: a fixed "30 days" in the name
  made no sense when the window is parameterizable.
- **Bluesky removed:** `public.api.bsky.app` 403'd from the dev machine; user
  opted to remove rather than keep (recommendation was to keep — it was an IP
  block, not an API failure — but user chose removal; executed cleanly).
- **`bird` CLI → `x.py`:** bird unmaintained/broken. Chose Playwright persistent
  profile (A) + web `site:x.com` fallback (D).
- **x.py → cookie injection (primary):** X blocks automated logins and the
  isolated profile can't use the user's normal browser session; cookie
  injection (`X_AUTH_TOKEN`/`X_CT0` from `.env`) reuses an existing session with
  no login flow to block. Persistent profile/`--login` kept as fallback.
- **Brave → Tavily → Exa → DuckDuckGo:** moved off Brave to LLM-native search
  with precise recency (`topic=news`+`days` / exact published-date range) and
  inline content (killed the fragile separate page-fetch + DDG-redirect bug).
- **TikTok removed:** chronically bot-blocks headless; it was the only
  perpetually-degraded source. `tiktok.com` stays in web.py SKIP so its junk
  can't resurface via web search.
- **Recoverable Setup Gates added:** user wanted human-in-the-loop on
  recoverable gaps instead of silent degradation.
- **Shared `.env` convention:** user works across machines and wants one key
  file usable by many skills.
- **Source picker (default on):** control which sources run per scan.
- **Flat script names kept:** prefixing is redundant with the `scan-trends/scripts/`
  namespace and hyphens break `import _env`/`import x`. Do not re-propose.

## 6. Known limitations / environment caveats

- Dev machine IP-blocks the DuckDuckGo HTML endpoint (202 challenge) and
  `public.api.bsky.app` (403) — keyless web path can't be live-tested there;
  Tavily path IS live-verified.
- `datetime.utcnow()` DeprecationWarning across several scripts (Python 3.13,
  stderr-only, harmless) — deferred, not fixed.
- `--quick` / `--deep` documented but unimplemented.
- SKILL.md error-matrix has minor mismatches (youtube no-retry; DDG no
  alt-phrasing) — deferred by user.
- AskUserQuestion UI caps options at 4 → the 6-source picker is two grouped
  multi-selects, and there are no pre-checked defaults (user ticks each run).

## 7. Operational runbook

- Run: `/scan-trends <topic> [--days=N] [--sources=a,b,c|--all] [--agent] [--out=PATH]`
- One-time setup: put `TAVILY_API_KEY` (and optionally `EXA_API_KEY`,
  `X_AUTH_TOKEN`/`X_CT0`) in `~/.claude/skills/.env` (`chmod 600`).
- Health check anytime: `python3 scripts/preflight.py`.
- Editing the skill: edit `~/Downloads/scan-trends/*`; live via symlink; SKILL.md
  body reloads per invocation (registry/description at session start).
