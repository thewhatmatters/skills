#!/usr/bin/env python3
"""Readiness check for summarize-yt (spec A6).

Reports which tiers of the capability ladder are reachable, as a 4-state status
per check plus an overall. Only a true dead-end (no network at all) is `down`;
a missing yt-dlp is a recoverable *gate* (offer install), a missing Gemini key
or ffmpeg is a *degrade* (a tier is unavailable, the skill still works).

I/O: stdout JSON {overall, checks, summary} · stderr human board · exit 1 only on `down`.
States per check: ready | degraded | gated | down  (with a gate id).
"""
import argparse
import json
import socket
import sys

import _env
import _tools

MARK = {"ready": "✅", "degraded": "⚠ ", "gated": "🔒", "down": "⛔"}
RANK = {"ready": 0, "degraded": 1, "gated": 2, "down": 3}


def check_ytdlp():
    cmd, src = _tools.resolve_ytdlp()
    if cmd:
        return ("ready", None, f"yt-dlp via {src}: {' '.join(cmd)}")
    # Recoverable: installing yt-dlp (or uv/pipx) restores the keyless path.
    return ("gated", "YTDLP_MISSING",
            "yt-dlp not reachable (no binary, no uvx/pipx) — offer install")


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
        return ("ready", None, "Gemini key present — watch tier available")
    return ("degraded", "GEMINI_KEY_ABSENT",
            "no Gemini key — visual watch tier off, captions still work")


def check_ffmpeg():
    if _tools.resolve_ffmpeg():
        return ("ready", None, "ffmpeg present — frame-sampling tier available")
    return ("degraded", "FFMPEG_MISSING", "no ffmpeg — frame-sampling tier off")


def check_network(timeout=4):
    for host in ("www.youtube.com", "generativelanguage.googleapis.com"):
        try:
            socket.create_connection((host, 443), timeout=timeout).close()
            return ("ready", None, f"network ok ({host} reachable)")
        except OSError:
            continue
    return ("down", "NETWORK_DOWN", "cannot reach YouTube or Gemini")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--agent", action="store_true")
    ap.parse_args()

    checks = {
        "network": check_network(),
        "ytdlp": check_ytdlp(),
        "transcript_api": check_transcript_api(),
        "gemini_key": check_gemini_key(),
        "ffmpeg": check_ffmpeg(),
    }

    # If the network is up, a missing yt-dlp is still only a gate (recoverable),
    # never down — captions can resume once it's installed, and the watch tier
    # (if keyed) needs no yt-dlp at all.
    overall = "ready"
    for s, _g, _d in checks.values():
        if RANK[s] > RANK[overall]:
            overall = s

    print("summarize-yt readiness", file=sys.stderr)
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
