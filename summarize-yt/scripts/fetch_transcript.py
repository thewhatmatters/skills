#!/usr/bin/env python3
"""Keyless caption + metadata fetch for summarize-yt (Tiers 2–3, spec A4).

One concern: get a YouTube video's timestamped captions and basic metadata
without any API key, normalised to JSON the NATIVE summariser consumes.
Primary path is yt-dlp (resolved via _tools, never installed here); if it
yields no captions, falls back to the youtube-transcript-api library when
importable.

I/O: --url URL [--lang en] · stdout JSON · stderr diagnostics · never hangs
(all subprocesses are timeout-bounded). Exit 0 with captions, 1 if none found.

JSON shape:
  {"video": {"id","title","channel","duration","url"},
   "chapters": [{"t","title"}],
   "captions": [{"t","text"}],
   "source": "yt-dlp"|"youtube-transcript-api"|null,
   "error": "<reason>"|null}
"""
import argparse
import glob
import json
import os
import re
import subprocess
import sys
import tempfile

import _tools

_ID_RE = re.compile(
    r"(?:v=|/shorts/|/embed/|youtu\.be/)([A-Za-z0-9_-]{11})")
_SRT_TIME = re.compile(r"(\d\d):(\d\d):(\d\d)[,.](\d{3})\s*-->")


def video_id(url):
    m = _ID_RE.search(url)
    if m:
        return m.group(1)
    # bare id?
    if re.fullmatch(r"[A-Za-z0-9_-]{11}", url):
        return url
    return None


def _hms(total):
    total = int(total)
    h, rem = divmod(total, 3600)
    m, s = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


def _run(cmd, timeout):
    """Run cmd, return (stdout, ok). Diagnostics to stderr. Never raises."""
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        if p.returncode != 0:
            tail = (p.stderr or "").strip().splitlines()[-1:] or [""]
            print(f"  · {' '.join(cmd[:2])} rc={p.returncode}: {tail[0]}",
                  file=sys.stderr)
            return (p.stdout, False)
        return (p.stdout, True)
    except subprocess.TimeoutExpired:
        print(f"  · timeout: {' '.join(cmd[:2])}", file=sys.stderr)
        return ("", False)
    except (OSError, ValueError) as e:
        print(f"  · failed: {' '.join(cmd[:2])}: {e}", file=sys.stderr)
        return ("", False)


def parse_srt(text):
    """SRT → [{t, text}], dropping rolling-duplicate auto-caption lines."""
    out, last = [], None
    for block in re.split(r"\n\s*\n", text):
        mt = _SRT_TIME.search(block)
        if not mt:
            continue
        h, m, s, _ms = (int(x) for x in mt.groups())
        lines = block.splitlines()
        # text = everything after the timing line
        body = " ".join(l.strip() for l in lines[2:] if l.strip())
        body = re.sub(r"<[^>]+>", "", body).strip()
        if not body or body == last:
            continue
        out.append({"t": _hms(h * 3600 + m * 60 + s), "text": body})
        last = body
    return out


def metadata(ytdlp, url, timeout=60):
    out, ok = _run(ytdlp + ["-J", "--skip-download", "--no-warnings", url], timeout)
    if not ok or not out.strip():
        return ({"id": video_id(url), "title": None, "channel": None,
                 "duration": None, "url": url}, [])
    try:
        d = json.loads(out)
    except json.JSONDecodeError:
        return ({"id": video_id(url), "title": None, "channel": None,
                 "duration": None, "url": url}, [])
    chapters = [{"t": _hms(c.get("start_time", 0)), "title": c.get("title", "")}
                for c in (d.get("chapters") or [])]
    meta = {"id": d.get("id") or video_id(url),
            "title": d.get("title"),
            "channel": d.get("channel") or d.get("uploader"),
            "duration": _hms(d["duration"]) if d.get("duration") else None,
            "url": d.get("webpage_url") or url}
    return (meta, chapters)


def captions_via_ytdlp(ytdlp, url, lang, timeout=120):
    with tempfile.TemporaryDirectory() as tmp:
        out_tpl = os.path.join(tmp, "%(id)s")
        _run(ytdlp + ["--skip-download", "--write-auto-sub", "--write-sub",
                      "--sub-lang", f"{lang},en,en-orig", "--convert-subs", "srt",
                      "--no-warnings", "--output", out_tpl, url], timeout)
        srts = sorted(glob.glob(os.path.join(tmp, "*.srt")))
        # Prefer a manual sub for the requested lang; else first available.
        preferred = [p for p in srts if f".{lang}." in os.path.basename(p)]
        for path in (preferred + srts):
            try:
                with open(path, encoding="utf-8", errors="replace") as fh:
                    caps = parse_srt(fh.read())
                if caps:
                    return caps
            except OSError:
                continue
    return []


def captions_via_api(vid, lang):
    """Fallback library. Tolerates both old (get_transcript) and new (fetch) APIs."""
    try:
        from youtube_transcript_api import YouTubeTranscriptApi as Y
    except Exception:
        return []
    langs = [lang, "en"]
    raw = None
    try:  # older 0.6.x classmethod
        raw = Y.get_transcript(vid, languages=langs)
    except AttributeError:
        try:  # newer 1.x instance API
            raw = [{"text": s.text, "start": s.start} for s in Y().fetch(vid, languages=langs)]
        except Exception as e:
            print(f"  · transcript-api fetch failed: {e}", file=sys.stderr)
            return []
    except Exception as e:
        print(f"  · transcript-api failed: {e}", file=sys.stderr)
        return []
    out, last = [], None
    for s in raw or []:
        txt = (s.get("text") or "").strip().replace("\n", " ")
        if txt and txt != last:
            out.append({"t": _hms(s.get("start", 0)), "text": txt})
            last = txt
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True)
    ap.add_argument("--lang", default="en")
    ap.add_argument("--agent", action="store_true")
    args = ap.parse_args()

    vid = video_id(args.url)
    result = {"video": {"id": vid, "title": None, "channel": None,
                        "duration": None, "url": args.url},
              "chapters": [], "captions": [], "source": None, "error": None}

    ytdlp, src = _tools.resolve_ytdlp()
    print(f"summarize-yt fetch_transcript ({'yt-dlp:'+src if ytdlp else 'no yt-dlp'})",
          file=sys.stderr)

    caps = []
    if ytdlp:
        meta, chapters = metadata(ytdlp, args.url)
        result["video"], result["chapters"] = meta, chapters
        vid = meta.get("id") or vid
        caps = captions_via_ytdlp(ytdlp, args.url, args.lang)
        if caps:
            result["source"] = "yt-dlp"

    if not caps and vid:
        caps = captions_via_api(vid, args.lang)
        if caps:
            result["source"] = "youtube-transcript-api"

    result["captions"] = caps
    if not caps:
        result["error"] = ("no captions found (no yt-dlp and no transcript-api)"
                           if not ytdlp else "video has no usable caption track")
        print(f"  ⛔ {result['error']}", file=sys.stderr)
    else:
        print(f"  ✅ {len(caps)} caption lines via {result['source']}",
              file=sys.stderr)

    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(0 if caps else 1)


if __name__ == "__main__":
    main()
