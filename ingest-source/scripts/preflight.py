#!/usr/bin/env python3
"""Readiness check for ingest-source (spec A6).

Reports which acquisition paths are reachable, as a 4-state status per check
plus an overall. Nothing here is ever `down`: local files (PDF / image /
document) ingest with no network and no binaries, so even a fully offline
machine is only `degraded` (URL sources unavailable). A missing yt-dlp is a
recoverable *gate* (offer install); a missing Gemini key, ffmpeg, or rich
fetch transport is a *degrade* (one tier unavailable, the skill still works).

I/O: stdout JSON {overall, checks, summary} · stderr human board · exit 1 only on `down`.
States per check: ready | degraded | gated | down  (with a gate id).
"""
import argparse
import json
import shutil
import socket
import sys

import _env
import _tools

MARK = {"ready": "✅", "degraded": "⚠ ", "gated": "🔒", "down": "⛔"}
RANK = {"ready": 0, "degraded": 1, "gated": 2, "down": 3}


def check_network(timeout=4):
    for host in ("www.youtube.com", "generativelanguage.googleapis.com",
                 "www.google.com"):
        try:
            socket.create_connection((host, 443), timeout=timeout).close()
            return ("ready", None, f"network ok ({host} reachable)")
        except OSError:
            continue
    # Offline is NOT down for this skill: local PDF/image/document ingestion
    # needs no network at all.
    return ("degraded", "NETWORK_OFFLINE",
            "offline — URL sources (YouTube/web) unavailable; local files still ingest")


def check_fetch_transport():
    """Webpage tier transport ladder: requests → urllib → curl.

    macOS stdlib Python often lacks a CA bundle, so urllib-only HTTPS can fail
    with CERTIFICATE_VERIFY_FAILED; `requests` (certifi) or `curl` avoids that.
    """
    try:
        import requests  # noqa: F401
        return ("ready", None, "web fetch via requests (certifi CA bundle)")
    except Exception:
        pass
    if shutil.which("curl"):
        return ("ready", None, "web fetch via urllib with curl fallback")
    return ("degraded", "FETCH_URLLIB_ONLY",
            "urllib only — HTTPS may fail without a CA bundle (no requests, no curl)")


def check_ytdlp():
    cmd, src = _tools.resolve_ytdlp()
    if cmd:
        return ("ready", None, f"yt-dlp via {src}: {' '.join(cmd)}")
    # Recoverable: installing yt-dlp (or uv/pipx) restores the keyless YouTube path.
    return ("gated", "YTDLP_MISSING",
            "yt-dlp not reachable (no binary, no uvx/pipx) — offer install (YouTube only)")


def check_transcript_api():
    try:
        import youtube_transcript_api  # noqa: F401
        return ("ready", None, "youtube-transcript-api importable (fallback)")
    except Exception:
        # Not a problem — it's only the lighter fallback for the yt-dlp tier.
        return ("degraded", None, "youtube-transcript-api absent (optional fallback)")


def check_gemini_key():
    key = _env.get("GOOGLE_API_KEY") or _env.get("GEMINI_API_KEY")
    if key:
        return ("ready", None, "Gemini key present — YouTube watch tier available")
    return ("degraded", "GEMINI_KEY_ABSENT",
            "no Gemini key — visual watch tier off, captions still work")


def check_ffmpeg():
    if _tools.resolve_ffmpeg():
        return ("ready", None, "ffmpeg present — frame-sampling tier available")
    return ("degraded", "FFMPEG_MISSING", "no ffmpeg — frame-sampling tier off")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--agent", action="store_true")
    ap.parse_args()

    checks = {
        "network": check_network(),
        "fetch": check_fetch_transport(),
        "ytdlp": check_ytdlp(),
        "transcript_api": check_transcript_api(),
        "gemini_key": check_gemini_key(),
        "ffmpeg": check_ffmpeg(),
    }

    overall = "ready"
    for s, _g, _d in checks.values():
        if RANK[s] > RANK[overall]:
            overall = s

    print("ingest-source readiness", file=sys.stderr)
    for n, (s, g, d) in checks.items():
        suffix = f"  [{g}]" if g else ""
        print(f"  {MARK[s]} {n:<15} {d}{suffix}", file=sys.stderr)
    for w in _env.perm_warnings():
        print(f"  ⚠  {w}", file=sys.stderr)
    print(f"  → overall: {overall}", file=sys.stderr)

    payload = {
        "overall": overall,
        "checks": {n: {"status": s, "gate": g, "detail": d}
                   for n, (s, g, d) in checks.items()},
        "summary": "overall=%s; " % overall + ", ".join(
            f"{n}={s}" for n, (s, _g, _d) in checks.items()),
    }
    print(json.dumps(payload, indent=2))
    sys.exit(1 if overall == "down" else 0)


if __name__ == "__main__":
    main()
