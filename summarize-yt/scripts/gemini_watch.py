#!/usr/bin/env python3
"""Watch tier for summarize-yt: hand a YouTube URL to the Gemini API (Tier 1, spec A4/A7).

One concern: ask Gemini to *watch* a public YouTube video (audio + visuals, ~1
fps) and return timestamped notes, using only the stdlib. Gemini accepts the URL
directly as a fileData part — nothing is downloaded locally. The summariser then
reshapes the notes per content type.

Secret hygiene (spec A7): the API key is read via the shared _env loader and sent
in the `x-goog-api-key` *header* — never in the URL or logs. Keyless callers must
not reach this script; preflight gates that.

I/O: --url URL [--format auto|tutorial|list|review|talk] [--model NAME]
     · stdout JSON {tier, model, text} · stderr diagnostics
     · exit 1 on any failure (caller drops to the caption tier). Network bounded.
"""
import argparse
import json
import sys
import urllib.error
import urllib.request

import _env

ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
DEFAULT_MODEL = "gemini-2.5-flash"
TIMEOUT = 180  # video processing can be slow; still bounded so we never hang

_SHAPES = {
    "tutorial": "an ordered, reproducible step list (each step: timestamp, action, any command shown on screen) plus a gotchas section",
    "list": "the ranked items in the video's own order (each: rank, item, timestamp, one-line why)",
    "review": "a verdict line, a pros/cons table, and notable moments (benchmarks, demos, price) — each with a timestamp",
    "talk": "the key points as timestamped bullets, plus one or two short quotable lines with timestamps",
    "auto": "the most fitting structure for this video's type (tutorial steps, ranked list, pros/cons, or key points)",
}


def build_prompt(fmt):
    shape = _SHAPES.get(fmt, _SHAPES["auto"])
    return (
        "Watch this YouTube video — both the spoken audio AND what is shown on "
        "screen (text overlays, demos, slides, on-screen items). Produce concise "
        "notes as " + shape + ". "
        "Prefix every point with its timestamp in [MM:SS] (use [H:MM:SS] past one "
        "hour). Capture on-screen-only information the narration doesn't say. "
        "Start with one tl;dr sentence. Use only timestamps that actually occur "
        "in the video; never invent them."
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True)
    ap.add_argument("--format", default="auto", choices=list(_SHAPES))
    ap.add_argument("--model", default=None)
    ap.add_argument("--agent", action="store_true")
    args = ap.parse_args()

    key = _env.get("GOOGLE_API_KEY") or _env.get("GEMINI_API_KEY")
    if not key:
        print("  ⛔ no GOOGLE_API_KEY / GEMINI_API_KEY — watch tier unavailable",
              file=sys.stderr)
        sys.exit(1)

    model = args.model or _env.get("GEMINI_MODEL") or DEFAULT_MODEL
    body = json.dumps({
        "contents": [{
            "parts": [
                {"text": build_prompt(args.format)},
                {"fileData": {"fileUri": args.url}},
            ]
        }]
    }).encode("utf-8")

    req = urllib.request.Request(
        ENDPOINT.format(model=model),
        data=body,
        method="POST",
        headers={"Content-Type": "application/json", "x-goog-api-key": key},
    )
    print(f"summarize-yt gemini_watch (model={model})", file=sys.stderr)
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detail = ""
        try:
            detail = json.loads(e.read().decode("utf-8")).get("error", {}).get("message", "")
        except Exception:
            pass
        print(f"  ⛔ Gemini HTTP {e.code}: {detail or e.reason}", file=sys.stderr)
        sys.exit(1)
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        print(f"  ⛔ Gemini request failed: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        parts = payload["candidates"][0]["content"]["parts"]
        text = "".join(p.get("text", "") for p in parts).strip()
    except (KeyError, IndexError):
        # Often a safety block or empty candidate — surface and degrade.
        fb = (payload.get("promptFeedback") or {}).get("blockReason")
        print(f"  ⛔ no usable candidate{' (blocked: ' + fb + ')' if fb else ''}",
              file=sys.stderr)
        sys.exit(1)

    if not text:
        print("  ⛔ empty response from Gemini", file=sys.stderr)
        sys.exit(1)

    print(f"  ✅ {len(text)} chars of timestamped notes", file=sys.stderr)
    print(json.dumps({"tier": "gemini-watch", "model": model, "text": text},
                     indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
