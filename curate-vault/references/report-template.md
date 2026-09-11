# Vault health report — structure

Loaded by `references/audit.md` (spec A1). Every number comes from the
healthscan JSON (plus verify_bundle for conformance); a section whose input
was skipped or gated says "not measured — <reason>" instead of guessing
(spec A12).

```markdown
# Vault health — <date>

**<one-line verdict: healthy / drifting / needs grooming — with the single
biggest reason>**  ·  <N> concepts (<+/-delta> since <prior date>)

## Conformance
- Errors: <n> (samples if any) · Broken links: <n>
- (or: not measured — verify_bundle unavailable)
- Interpret broken links by SOURCE: links from `log.md`/`archive/` are
  historical records pointing at moved/archived targets — legal per OKF and
  not curation debt; broken links from live concept bodies ARE. Split the
  count when the samples show both.

## Staleness heat
| Folder | Concepts | Freshness (median, `timestamp`) | Doc age (median, `created`) | % >180d | Orphans | Unindexed |
|---|---|---|---|---|---|---|
(`created` adoption may be partial — when a folder's `with_created` count is
low, say "n/N have created" instead of implying a measured age)
(one row per top-level folder, worst first; note that `documentation/` is a
regenerable mirror shelf — flag it separately, don't let it dominate the
verdict)

## Link graph
- Top hubs: <top 3–5 with inbound counts — these are the load-bearing
  articles; stale hubs outrank stale leaves>
- Isolates (no links in OR out): <count> (list up to 5)

## Growth
- <total delta since prior snapshot; per-folder deltas worth naming>
- (first run: "no prior snapshot — deltas start next run")

## Activity
- Log: <entries in last 30d> entries; last entry <date>
- Citation coverage: <folders where it's notably low, if any>

## Claim spot-check   ← ONLY when --deep ran
- <per concept: verdict summary from its vault-verifier agent>

## Recommended grooms
1. `run /curate-vault --groom=<folder>/` — <one-line reason from the data>
2. ...
(and `--relink` when isolate/orphan counts dominate the badness score)
```

Rules:

- Verdict line first — the user should get the state of the vault in one
  glance without scrolling.
- Tables for the per-folder data; prose only where a number needs a why.
- Suggestions come verbatim from the engine's `suggestions` array; the model
  may add a reason per line but never invents new targets.
- Never propose an edit, merge, archive, or deletion — name the folder and
  hand it to `--groom` / `--relink` on this same skill.
