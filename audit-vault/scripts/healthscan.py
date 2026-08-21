#!/usr/bin/env python3
"""Read-only metrics engine for audit-vault (spec A4, A10).

Walks the OKF vault (READ-ONLY: vault files are only ever opened for
reading), computes health metrics, diffs against the newest prior snapshot,
records a new snapshot in the state dir (outside the vault), and emits one
JSON payload.

I/O: stdout JSON | stderr diagnostics | exit 0 on success, 1 on fatal.
Args:
  --vault PATH        vault root (required)
  --verify PATH       optional verify_bundle JSON (adds conformance section)
  --folder SUB        scope report metrics to one vault-relative folder
                      (link graph is still computed vault-wide)
  --state-dir PATH    snapshot dir (default ~/.cursor/cache/audit-vault)
  --no-snapshot       do not record this run
  --deep-candidates N size of the deep_candidates list (default 10)

Writes ONLY to --state-dir. Never writes under --vault.
"""
import argparse
import datetime
import json
import os
import re
import sys

# Lowercase set, matched case-insensitively — APFS casing variance means
# handoff.md/HANDOFF.md are the same file on disk but not to a str compare.
RESERVED = {"index.md", "log.md", "claude.md", "handoff.md"}
# Regenerable mirror shelf + frozen archive: counted in totals, but excluded
# from hub rankings, deep candidates, and groom suggestions (they would
# dominate every score while representing zero curation debt).
EXEMPT_SHELVES = {"documentation", "archive"}
LINK_RE = re.compile(r"\]\(([^)#\s]+\.md)\)")
DATE_HEAD_RE = re.compile(r"^## (\d{4}-\d{2}-\d{2})\s*$", re.M)
AGE_BUCKETS = ((30, "under_30d"), (90, "30_90d"), (180, "90_180d"))


def log(msg):
    print(msg, file=sys.stderr)


def parse_frontmatter(text):
    """Lenient key: value frontmatter parse (no YAML dep). Returns dict."""
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end < 0:
        return {}
    fm = {}
    for line in text[3:end].splitlines():
        m = re.match(r"^(\w[\w-]*):\s*(.*)$", line)
        if m:
            fm[m.group(1)] = m.group(2).strip().strip('"').strip("'")
    return fm


def walk_vault(vault):
    """Yield (relpath, text) for every non-reserved .md concept file."""
    for root, dirs, files in os.walk(vault):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for f in files:
            if not f.endswith(".md") or f.lower() in RESERVED:
                continue
            rel = os.path.relpath(os.path.join(root, f), vault)
            try:
                with open(os.path.join(root, f), encoding="utf-8") as fh:
                    yield rel, fh.read()
            except OSError as e:
                log(f"  ! unreadable: {rel}: {e}")


def resolve_link(target, source_rel):
    if target.startswith("/"):
        return target.lstrip("/")
    return os.path.normpath(os.path.join(os.path.dirname(source_rel), target))


def age_days(ts, today):
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})", ts or "")
    if not m:
        return None
    try:
        d = datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    except ValueError:
        return None
    return (today - d).days


def bucket(days):
    for limit, name in AGE_BUCKETS:
        if days < limit:
            return name
    return "over_180d"


def top_folder(rel):
    return rel.split(os.sep)[0] if os.sep in rel else "(root)"


def median(xs):
    if not xs:
        return None
    xs = sorted(xs)
    return xs[len(xs) // 2]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vault", required=True)
    ap.add_argument("--verify")
    ap.add_argument("--folder")
    ap.add_argument("--state-dir",
                    default=os.path.expanduser("~/.cursor/cache/audit-vault"))
    ap.add_argument("--no-snapshot", action="store_true")
    ap.add_argument("--deep-candidates", type=int, default=10)
    args = ap.parse_args()

    vault = os.path.expanduser(args.vault)
    if not os.path.isdir(vault):
        print(json.dumps({"error": f"vault not found: {vault}"}))
        sys.exit(1)
    today = datetime.date.today()

    # ---- walk: concepts, links, per-folder stats -------------------------
    concepts = {}          # rel -> {type, timestamp, has_citations, out_links}
    for rel, text in walk_vault(vault):
        fm = parse_frontmatter(text)
        concepts[rel] = {
            "type": fm.get("type") or "(none)",
            "timestamp": fm.get("timestamp", ""),
            "created": fm.get("created", ""),
            "has_citations": "# Citations" in text,
            "out_links": [resolve_link(t, rel) for t in LINK_RE.findall(text)
                          if not t.startswith(("http://", "https://"))],
        }
    log(f"  scanned {len(concepts)} concepts")

    inbound = {rel: 0 for rel in concepts}
    for rel, c in concepts.items():
        for t in c["out_links"]:
            if t in inbound and t != rel:
                inbound[t] += 1

    # ---- index coverage (reserved index.md files, read-only) ------------
    index_listed = set()
    for root, dirs, files in os.walk(vault):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        if "index.md" in files:
            rel_dir = os.path.relpath(root, vault)
            try:
                with open(os.path.join(root, "index.md"), encoding="utf-8") as fh:
                    for t in LINK_RE.findall(fh.read()):
                        tgt = (t.lstrip("/") if t.startswith("/") else
                               os.path.normpath(os.path.join(
                                   "" if rel_dir == "." else rel_dir, t)))
                        index_listed.add(tgt)
            except OSError as e:
                log(f"  ! index unreadable in {rel_dir}: {e}")

    # ---- scope filter for reported metrics -------------------------------
    scope = (lambda rel: rel.startswith(args.folder.rstrip("/") + os.sep)
             or rel == args.folder) if args.folder else (lambda rel: True)
    scoped = {rel: c for rel, c in concepts.items() if scope(rel)}

    # ---- per-folder staleness / orphans / coverage -----------------------
    folders = {}
    for rel, c in scoped.items():
        f = folders.setdefault(top_folder(rel), {
            "concepts": 0, "ages": [], "doc_ages": [], "no_timestamp": 0,
            "with_created": 0, "orphans": 0,
            "unindexed": 0, "with_citations": 0,
            "by_bucket": {n: 0 for _, n in AGE_BUCKETS} | {"over_180d": 0},
        })
        f["concepts"] += 1
        d = age_days(c["timestamp"], today)
        if d is None:
            f["no_timestamp"] += 1
        else:
            f["ages"].append(d)
            f["by_bucket"][bucket(d)] += 1
        # created (house extension) = document age; timestamp = freshness
        dc = age_days(c["created"], today)
        if dc is not None:
            f["with_created"] += 1
            f["doc_ages"].append(dc)
        if inbound.get(rel, 0) == 0:
            f["orphans"] += 1
        if rel not in index_listed:
            f["unindexed"] += 1
        if c["has_citations"]:
            f["with_citations"] += 1
    for f in folders.values():
        ages = f.pop("ages")
        doc_ages = f.pop("doc_ages")
        f["median_age_days"] = median(ages)
        f["median_doc_age_days"] = median(doc_ages)
        f["pct_over_180d"] = (round(100 * f["by_bucket"]["over_180d"] /
                                    len(ages)) if ages else None)

    # ---- link graph ------------------------------------------------------
    curated = lambda rel: top_folder(rel) not in EXEMPT_SHELVES
    hubs = sorted(((n, rel) for rel, n in inbound.items()
                   if scope(rel) and curated(rel) and n > 0),
                  reverse=True)[:10]
    isolates = sorted(rel for rel, c in scoped.items()
                      if curated(rel) and inbound.get(rel, 0) == 0
                      and not c["out_links"])

    # ---- log cadence -----------------------------------------------------
    cadence = {"entries_last_30d": None, "last_entry": None}
    log_path = os.path.join(vault, "log.md")
    if os.path.isfile(log_path):
        with open(log_path, encoding="utf-8") as fh:
            log_text = fh.read()
        dates = DATE_HEAD_RE.findall(log_text)
        cadence["last_entry"] = dates[0] if dates else None

        def within_30d(d):
            a = age_days(d, today)
            return a is not None and a <= 30
        recent = [d for d in dates if within_30d(d)]
        # count bullet lines under recent headings, cheap approximation:
        cadence["entries_last_30d"] = sum(
            len(re.findall(r"^\* \*\*", sect, re.M))
            for d, sect in zip(dates, re.split(DATE_HEAD_RE, log_text)[2::2])
            if within_30d(d)) or len(recent)

    # ---- conformance (verify_bundle JSON, optional) ----------------------
    conformance = None
    if args.verify and os.path.isfile(args.verify):
        try:
            with open(args.verify, encoding="utf-8") as fh:
                v = json.load(fh)
            broken = v.get("broken_links", [])
            conformance = {
                "errors": len(v.get("errors", [])),
                "error_samples": v.get("errors", [])[:10],
                "broken_links": len(broken),
                "broken_samples": broken[:10],
            }
        except (OSError, ValueError) as e:
            log(f"  ! verify JSON unreadable ({e}) — conformance unmeasured")

    # ---- growth vs snapshots ---------------------------------------------
    by_type = {}
    for c in scoped.values():
        by_type[c["type"]] = by_type.get(c["type"], 0) + 1
    snapshot = {
        "date": today.isoformat(),
        "total": len(scoped),
        "by_type": by_type,
        "by_folder": {k: v["concepts"] for k, v in folders.items()},
        "scoped_to": args.folder,
    }
    growth = None
    snap_dir = os.path.join(os.path.expanduser(args.state_dir), "snapshots")
    try:
        os.makedirs(snap_dir, exist_ok=True)
        prior = sorted(f for f in os.listdir(snap_dir) if f.endswith(".json"))
        # compare against the newest prior snapshot with the same scope
        for name in reversed(prior):
            try:
                with open(os.path.join(snap_dir, name), encoding="utf-8") as fh:
                    p = json.load(fh)
            except (OSError, ValueError) as e:
                log(f"  ! snapshot {name} unreadable ({e}) — skipped")
                continue
            if p.get("scoped_to") == args.folder:
                growth = {
                    "since": p["date"],
                    "total_delta": snapshot["total"] - p["total"],
                    "by_folder_delta": {
                        k: snapshot["by_folder"].get(k, 0) - p["by_folder"].get(k, 0)
                        for k in set(snapshot["by_folder"]) | set(p["by_folder"])
                        if snapshot["by_folder"].get(k, 0) != p["by_folder"].get(k, 0)},
                }
                break
        if not args.no_snapshot:
            out = os.path.join(snap_dir, f"{today.isoformat()}.json")
            tmp = out + ".tmp"
            with open(tmp, "w", encoding="utf-8") as fh:
                json.dump(snapshot, fh, indent=2)
            os.replace(tmp, out)   # atomic: an interrupted cron run never
                                   # leaves a half-written snapshot behind
    except OSError as e:
        log(f"  ! state dir unwritable, no deltas persisted: {e}")

    # ---- deep candidates + groom suggestions -----------------------------
    def suspicion(rel):
        d = age_days(concepts[rel]["timestamp"], today) or 0
        return d * (1 + inbound.get(rel, 0))   # old AND load-bearing first
    deep_candidates = sorted((r for r in scoped if curated(r)),
                             key=suspicion,
                             reverse=True)[:args.deep_candidates]

    def badness(name, f):
        return (f["orphans"] + f["unindexed"]
                + (f["by_bucket"]["over_180d"] or 0))
    worst = sorted(((badness(k, v), k) for k, v in folders.items()
                    if k not in EXEMPT_SHELVES and v["concepts"] >= 3),
                   reverse=True)[:3]
    suggestions = [f"run /curate-vault --groom={name}/"
                   for score, name in worst if score > 0]

    print(json.dumps({
        "generated": today.isoformat(),
        "vault": vault,
        "scoped_to": args.folder,
        "totals": {"concepts": len(scoped), "by_type": by_type},
        "conformance": conformance,
        "folders": folders,
        "link_graph": {"top_hubs": [{"inbound": n, "concept": r}
                                    for n, r in hubs],
                       "isolates": isolates[:20],
                       "isolate_count": len(isolates)},
        "log_cadence": cadence,
        "growth": growth,
        "deep_candidates": deep_candidates,
        "suggestions": suggestions,
    }, indent=2))


if __name__ == "__main__":
    main()
