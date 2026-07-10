# Recoverable Setup Gates — registry and walkthroughs

Loaded by `SKILL.md` when a gate fires (preflight reports `gated`, or a source
emits a gate trigger mid-run). The 4-part gate anatomy is summarized in
SKILL.md; this file holds the full anatomy plus the per-gate walkthroughs.

## The four required parts (spec A7)

1. **Unambiguous trigger** — a specific signal that means *recoverable setup gap*,
   distinct from a genuine empty result or a transient error. Never gate on a vague
   failure (e.g. a timeout) — that would nag the user for no reason.
2. **`--agent` bypass** — if `--agent` is set, do **not** prompt. Take the documented
   fallback and note it in the stats block. A human-in-the-loop gate must never hang
   an unattended run.
3. **Ask, don't degrade** — in interactive runs, stop *before* the fallback and ask
   the user (use the interactive question UI) with exactly three choices:
   - **Fix it for me** — run the gate's fix command yourself, wait for it to finish,
     then re-run the source command and use the real result.
   - **I'll do it myself** — print the exact fix command, pause, and wait for the user
     to confirm they're done; then re-run the source command.
   - **Skip it** — take the documented fallback for this source now.
4. **Graceful dead-end** — if the chosen fix fails or times out, fall back anyway and
   note it. A gate never blocks the rest of the run.

## Registered gates

### X/Twitter — `x.py` not authenticated

- **Trigger:** `x.py` prints `[]` on stdout **and** its stderr contains the literal
  token `NO_SESSION`. (`[]` with stderr `TIMEOUT`, or `[]` with no marker, is **not**
  this gate — skip X and take the web fallback without prompting.)
- **Fix it for me:** not applicable — cookies can't be read from your browser
  automatically (and X blocks automated logins).
- **I'll do it myself:** tell the user to add `X_AUTH_TOKEN` and `X_CT0` to
  `~/.claude/skills/.env` — copy `auth_token`/`ct0` from a logged-in x.com tab
  (DevTools → Application/Storage → Cookies → x.com). `chmod 600` the file. (Or, if
  they can complete it, `python3 scripts/x.py --login` for the profile path.) Wait
  for their go-ahead, then re-run `python3 scripts/x.py "{TOPIC}" --days={DAYS}`.
- **Skip / fix failed / `--agent`:** run
  `python3 scripts/web.py "{TOPIC}" XFALLBACK --days={DAYS}`, tag results as X/Twitter,
  and render the stats line as `|- X/Twitter (via web): {N} pages`.

### Web — no search-provider key

- **Trigger:** `preflight.py` reports Web `status:"gated"`, `gate:"web_key"` (no
  `TAVILY_API_KEY` or `EXA_API_KEY` found).
- **Fix it for me:** not applicable — an API key can't be provisioned automatically.
- **I'll do it myself:** tell the user to add one line to `~/.claude/.env` (create it,
  then `chmod 600 ~/.claude/.env`): `TAVILY_API_KEY=...` (free tier at tavily.com) or
  `EXA_API_KEY=...` (exa.ai). Then re-run `python3 scripts/preflight.py` to confirm `ready`.
- **Skip / `--agent`:** proceed on DuckDuckGo; mark Web `degraded` in the stats block.
  If DDG is also blocked in this environment, Web is `down` — omit it.
