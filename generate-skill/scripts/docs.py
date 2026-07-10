#!/usr/bin/env python3
"""Fetch, cache, and version-stamp the canonical Claude skill-authoring docs.

One concern: make Anthropic's *current* skill docs available locally so the
generator scaffolds against what Claude Code expects today — and say which
Claude Code version they reflect. It does NOT judge them against our in-house
spec (that is reconcile.py).

USAGE
    python3 scripts/docs.py [--refresh] [--agent]

    --refresh   ignore a fresh cache and re-fetch from the network now
    --agent     non-interactive; never prompts (this script never prompts
                anyway — the flag exists for a consistent CLI surface)

I/O CONTRACT
    stdout : a single JSON object (the manifest) — see KEYS below
    stderr : human-readable diagnostics, one line per step
    exit   : 0 whenever a usable doc set was produced (live, cache, OR the
             committed offline snapshot); 1 only if NOTHING is available
             (no network, no cache, no snapshot). Never hangs (timeouts).

JSON KEYS
    status               fresh     — cache used as-is, within freshness window
                         refreshed — live fetch succeeded (cache may also have
                                     been refreshed, or refresh skipped — see notes)
                         stale     — live failed; existing cache returned anyway
                         offline   — live failed AND no cache; snapshot returned
                         no-docs   — nothing available (exit 1)
    source               live | cache | snapshot | null   (null only with no-docs)
    claude_code_version  e.g. "2.1.144"  (parsed from changelog.md; may be null)
    fetched_at           ISO-8601 UTC of this run's content, or null
    cache_age_days       float age of the cache used, or null
    docs                 [{slug, filename, sha256, bytes, http_status}]
    notes                [str, ...]  human-relevant remarks

RESOLUTION ORDER (dual-mode, mirrors scan-trends SCRIPTS vs NATIVE)
    1. live fetch via stdlib urllib (keyless — no .env / API keys; SSL trust
       via certifi when present, else default verification)
    2. local .cache/docs/ if a live fetch fails, or if the cache is fresh
       and --refresh was not given
    3. committed references/claude-docs-snapshot/ if fully offline
"""

import argparse
import hashlib
import json
import re
import ssl
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
SNAPSHOT_DIR = SKILL_ROOT / "references" / "claude-docs-snapshot"
CACHE_DIR = SKILL_ROOT / ".cache" / "docs"
MANIFEST = CACHE_DIR / "manifest.json"

FRESHNESS_DAYS = 30
FETCH_TIMEOUT = 15  # seconds per doc; bounds total runtime, never hangs

# (slug, filename, url) — the pinned canonical docs (DESIGN.md §2).
DOCS = [
    ("skills", "skills.md",
     "https://code.claude.com/docs/en/skills.md"),
    ("changelog", "changelog.md",
     "https://code.claude.com/docs/en/changelog.md"),
    ("plugins-reference", "plugins-reference.md",
     "https://code.claude.com/docs/en/plugins-reference.md"),
    ("claude-directory", "claude-directory.md",
     "https://code.claude.com/docs/en/claude-directory.md"),
    ("agent-sdk-skills", "agent-sdk-skills.md",
     "https://code.claude.com/docs/en/agent-sdk/skills.md"),
]

_VERSION_RE = re.compile(r"\b\d+\.\d+\.\d+\b")


def log(msg):
    """Diagnostics go to stderr so stdout stays pure JSON."""
    print(msg, file=sys.stderr)


def now_utc():
    return datetime.now(timezone.utc)


def iso(dt):
    return dt.replace(microsecond=0).isoformat()


def sha256_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def parse_version(changelog_text):
    """First semver-looking token in the changelog = the current CC version."""
    if not changelog_text:
        return None
    m = _VERSION_RE.search(changelog_text)
    return m.group(0) if m else None


def load_manifest():
    try:
        return json.loads(MANIFEST.read_text("utf-8"))
    except (OSError, ValueError):
        return None


def cache_age_days(manifest):
    if not manifest or not manifest.get("fetched_at"):
        return None
    try:
        fetched = datetime.fromisoformat(manifest["fetched_at"])
    except ValueError:
        return None
    if fetched.tzinfo is None:
        fetched = fetched.replace(tzinfo=timezone.utc)
    return (now_utc() - fetched).total_seconds() / 86400.0


_SSL_CTX = "unset"


def ssl_context():
    """certifi-backed SSL context when available, else default verification.

    macOS python.org builds don't trust via the system keychain, so stdlib
    `urllib` fails cert verification while `curl` succeeds. `certifi` ships
    with `requests` (already used by scan-trends), so this adds no new
    dependency; absent it, fall back to the default context (works on Linux /
    system-trust). Layered resolution — spec pattern A11.
    """
    global _SSL_CTX
    if _SSL_CTX == "unset":
        try:
            import certifi
            _SSL_CTX = ssl.create_default_context(cafile=certifi.where())
        except Exception:  # noqa: BLE001 - any failure → default verification
            _SSL_CTX = None
    return _SSL_CTX


def fetch_url(url):
    """GET a URL with a timeout. Returns (http_status, text). Raises on error."""
    req = urllib.request.Request(
        url, headers={"User-Agent": "generate-skill-docs/1.0"}
    )
    with urllib.request.urlopen(
        req, timeout=FETCH_TIMEOUT, context=ssl_context()
    ) as resp:
        return resp.status, resp.read().decode("utf-8", "replace")


def read_dir(base):
    """Read all pinned docs from a directory. Returns {filename: text} or {}."""
    out = {}
    for _slug, filename, _url in DOCS:
        p = base / filename
        try:
            out[filename] = p.read_text("utf-8")
        except OSError:
            return {}  # incomplete set is unusable — treat as absent
    return out


def emit(payload, exit_code):
    print(json.dumps(payload, indent=2))
    sys.exit(exit_code)


def main():
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--refresh", action="store_true")
    ap.add_argument("--agent", action="store_true")
    args = ap.parse_args()

    manifest = load_manifest()
    age = cache_age_days(manifest)
    cache_fresh = age is not None and age <= FRESHNESS_DAYS

    notes = []

    # 1. Use a fresh cache as-is unless --refresh forces a network check.
    if cache_fresh and not args.refresh:
        cached = read_dir(CACHE_DIR)
        if cached:
            log(f"cache is fresh ({age:.1f}d ≤ {FRESHNESS_DAYS}d) — using it")
            emit({
                "status": "fresh",
                "source": "cache",
                "claude_code_version": manifest.get("claude_code_version"),
                "fetched_at": manifest.get("fetched_at"),
                "cache_age_days": round(age, 2),
                "docs": manifest.get("docs", []),
                "notes": ["cache within freshness window; pass --refresh to "
                          "force a live re-fetch"],
            }, 0)
        notes.append("manifest fresh but cache files unreadable — re-fetching")

    # 2. Attempt a live fetch of every pinned doc.
    log("fetching canonical docs from code.claude.com ...")
    fetched, docs_meta, failed = {}, [], []
    for slug, filename, url in DOCS:
        try:
            status, text = fetch_url(url)
            if status != 200 or not text.strip():
                raise urllib.error.URLError(f"http {status} / empty")
            fetched[filename] = text
            docs_meta.append({
                "slug": slug, "filename": filename,
                "sha256": sha256_text(text), "bytes": len(text.encode("utf-8")),
                "http_status": status,
            })
            log(f"  ok    {filename}  ({len(text.encode('utf-8'))} bytes)")
        except Exception as e:  # noqa: BLE001 - any failure → fall back
            failed.append(filename)
            log(f"  FAIL  {filename}  ({e.__class__.__name__}: {e})")

    if not failed:
        version = parse_version(fetched.get("changelog.md", ""))
        stamp = iso(now_utc())
        # The live content is in hand — never crash if persisting it fails
        # (read-only home, denied perms, full disk). Honest degrade: still
        # emit the manifest with a note that the cache wasn't updated.
        try:
            CACHE_DIR.mkdir(parents=True, exist_ok=True)
            for filename, text in fetched.items():
                (CACHE_DIR / filename).write_text(text, "utf-8")
            new_manifest = {
                "fetched_at": stamp,
                "claude_code_version": version,
                "source_urls": {f: u for _s, f, u in DOCS},
                "docs": docs_meta,
            }
            MANIFEST.write_text(json.dumps(new_manifest, indent=2), "utf-8")
            log(f"refreshed cache; Claude Code version = {version}")
        except OSError as e:
            notes.append(f"cache write failed ({e.__class__.__name__}: {e}); "
                         "live content used this run but not cached")
            log(f"cache write FAILED ({e}); live content used anyway")
        emit({
            "status": "refreshed",
            "source": "live",
            "claude_code_version": version,
            "fetched_at": stamp,
            "cache_age_days": 0.0,
            "docs": docs_meta,
            "notes": notes,
        }, 0)

    # 3. Live fetch incomplete → degrade. Prefer cache, then snapshot.
    notes.append(f"live fetch failed for: {', '.join(failed)}")
    cached = read_dir(CACHE_DIR)
    if cached:
        log("falling back to existing cache (stale-but-usable)")
        emit({
            "status": "stale",
            "source": "cache",
            "claude_code_version": (manifest or {}).get("claude_code_version"),
            "fetched_at": (manifest or {}).get("fetched_at"),
            "cache_age_days": round(age, 2) if age is not None else None,
            "docs": (manifest or {}).get("docs", []),
            "notes": notes + ["offline or partial fetch; cache may be stale — "
                              "run with --refresh when back online"],
        }, 0)

    snap = read_dir(SNAPSHOT_DIR)
    if snap:
        version = parse_version(snap.get("changelog.md", ""))
        log("falling back to committed offline snapshot")
        emit({
            "status": "offline",
            "source": "snapshot",
            "claude_code_version": version,
            "fetched_at": None,
            "cache_age_days": None,
            "docs": [{"slug": s, "filename": f,
                      "sha256": sha256_text(snap[f]),
                      "bytes": len(snap[f].encode("utf-8")),
                      "http_status": None}
                     for s, f, _u in DOCS],
            "notes": notes + ["using committed snapshot; it reflects the docs "
                              "as of the last snapshot commit, not live"],
        }, 0)

    log("FATAL: no live docs, no cache, no snapshot — cannot proceed")
    emit({
        "status": "no-docs", "source": None, "claude_code_version": None,
        "fetched_at": None, "cache_age_days": None, "docs": [],
        "notes": notes + ["no docs available by any path"],
    }, 1)


if __name__ == "__main__":
    main()
