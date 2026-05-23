#!/usr/bin/env python3
"""Render a Mermaid diagram through a graceful degraded ladder (spec A3/A10/A11).

One concern: take Mermaid source and emit it as a fenced Markdown block, a
rendered SVG/PNG (via the `mmdc` CLI — preferring a global binary, then
`npx @mermaid-js/mermaid-cli`), a network-rendered image (Kroki, opt-in), or a
self-contained HTML page that renders client-side with mermaid.js. Pure
stdlib; Node and the network are OPTIONAL capabilities, never hard
requirements — the fenced block always works.

USAGE
    python3 scripts/diagram.py [INPUT] [--format=mermaid|svg|png|html]
        [--render=auto|mmdc|kroki|none] [--theme=brand|default]
        [--out=PATH] [--title=STR] [--no-network]

    INPUT          Mermaid source file; if omitted, read from stdin.
    --format       mermaid (default) | svg | png | html
    --render       raster engine for svg/png: auto (default) | mmdc | kroki | none
    --theme        brand (ivory/clay, matches render-html) | default
    --out          output path; default derives from INPUT, else stdout
    --title        diagram name / HTML <title>
    --no-network   forbid Kroki egress (offline-safe)
    --agent        accepted for flag consistency; this renderer never prompts

I/O CONTRACT
    stdin  : Mermaid source (when no INPUT)
    stdout : the artifact (no --out) or a "wrote <path>" line (with --out)
    stderr : human diagnostics + capability / degradation notices
    exit   : 0 on success (including degraded fallbacks);
             1 on empty input, write failure, or an explicitly-requested
             engine that is unavailable (--render=mmdc/kroki with no capability)

LADDER (spec A3)
    format=mermaid  -> fenced ```mermaid block (zero dependency, always works)
    format=html     -> self-contained HTML embedding mermaid.js (CDN)
    format=svg|png  -> render=auto: mmdc (global -> npx) -> Kroki (if network)
                       -> degrade to a fenced block with a notice.
                       render=mmdc|kroki: forced; error if that engine is absent.

NODE / NETWORK ARE OPTIONAL (spec A11 layered resolution)
    mmdc binary: $MMDC_BIN -> `mmdc` on PATH -> `npx -y @mermaid-js/mermaid-cli`.
    The first npx run downloads mermaid-cli + a Puppeteer Chromium (one-time).
"""

import argparse
import html
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

# Diagram-type keywords mermaid accepts as the first significant token.
# Keep in sync with references/diagram-types.md. Unknown types only WARN (the
# experimental long tail is intentionally not all listed), so this set covers
# the well-established keywords to keep the warning honest, not exhaustive.
SUPPORTED_TYPES = {
    "graph", "flowchart", "sequenceDiagram", "classDiagram", "stateDiagram",
    "stateDiagram-v2", "erDiagram", "gantt", "journey", "gitGraph", "pie",
    "mindmap", "timeline", "quadrantChart", "requirementDiagram", "sankey-beta",
    "block-beta", "architecture-beta", "xychart-beta", "radar", "kanban",
    "packet-beta", "packet", "treemap",
    "C4Context", "C4Container", "C4Component", "C4Dynamic", "C4Deployment",
}

KROKI_URL = "https://kroki.io/mermaid/{fmt}"

# Brand theme matching render-html (ivory/clay). Applied as a one-line
# %%{init}%% directive so mmdc, Kroki, and the browser all honor it identically.
BRAND_INIT = (
    '%%{init: {"theme":"base","themeVariables":{'
    '"primaryColor":"#F7F6F2","primaryTextColor":"#191917",'
    '"primaryBorderColor":"#CC785C","lineColor":"#B0613F",'
    '"secondaryColor":"#E7E4D8","tertiaryColor":"#F0EEE6",'
    '"fontFamily":"ui-sans-serif, system-ui, -apple-system, Segoe UI, '
    'Helvetica, Arial, sans-serif"}} }%%'
)
BRAND_BG = "#F0EEE6"


def log(msg):
    print(msg, file=sys.stderr)


def detect_type(text):
    """First significant token = the diagram type (skip %%{init}%% directives)."""
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("%%"):
            continue
        return line.split()[0].split(":")[0]
    return ""


def validate(text):
    """Return a list of non-fatal warnings; the renderer still proceeds."""
    warns = []
    dtype = detect_type(text)
    if dtype and dtype not in SUPPORTED_TYPES:
        warns.append(f"diagram type '{dtype}' is not in the known-supported set "
                     f"(may still render if your mermaid version supports it)")
    # The bare word `end` as a node id breaks flowcharts (mermaid gotcha) — but
    # `end` alone is the legitimate `subgraph` terminator, so only warn when it
    # appears as a token on an edge line (e.g. `A --> end`).
    EDGE_MARKS = ("-->", "---", "==>", "-.-", "==", "--")
    for raw in text.splitlines():
        if raw.strip() == "end":  # subgraph closer — valid, skip
            continue
        if not any(m in raw for m in EDGE_MARKS):
            continue
        toks = (raw.replace("[", " ").replace("(", " ").replace("{", " ")
                .replace("|", " ").split())
        if "end" in toks:
            warns.append("a bare 'end' token in an edge can break flowcharts — "
                         "wrap it (e.g. [\"end\"]) if it's a node label")
            break
    return warns


def apply_theme(text, theme):
    """Prepend the brand init directive unless the source already has one."""
    if theme != "brand":
        return text
    if "%%{init" in text:
        return text  # respect an author-supplied directive
    return BRAND_INIT + "\n" + text


# --- renderers --------------------------------------------------------------
def mmdc_command():
    """Layered resolution (spec A11): $MMDC_BIN -> mmdc -> npx fallback."""
    import os
    override = os.environ.get("MMDC_BIN")
    if override:
        return [override]
    if shutil.which("mmdc"):
        return ["mmdc"]
    if shutil.which("npx"):
        return ["npx", "-y", "@mermaid-js/mermaid-cli"]
    return None


def render_mmdc(text, fmt, theme):
    """Render via the mmdc CLI. Returns bytes. Raises RuntimeError if no engine."""
    cmd = mmdc_command()
    if cmd is None:
        raise RuntimeError("no mmdc and no npx/node available")
    with tempfile.TemporaryDirectory() as td:
        src = Path(td) / "in.mmd"
        out = Path(td) / f"out.{fmt}"
        src.write_text(text, "utf-8")
        args = cmd + ["-i", str(src), "-o", str(out), "-e", fmt]
        if theme == "brand":
            args += ["-b", BRAND_BG]
        try:
            proc = subprocess.run(args, capture_output=True, timeout=180)
        except (OSError, subprocess.TimeoutExpired) as e:
            raise RuntimeError(f"mmdc invocation failed ({e.__class__.__name__}: {e})")
        if proc.returncode != 0 or not out.exists():
            err = proc.stderr.decode("utf-8", "replace")[-500:]
            raise RuntimeError(f"mmdc exited {proc.returncode}: {err}")
        return out.read_bytes()


def render_kroki(text, fmt, no_network):
    """Render via the Kroki HTTP service. Returns bytes. Honors --no-network."""
    if no_network:
        raise RuntimeError("network rendering disabled (--no-network)")
    url = KROKI_URL.format(fmt=fmt)
    req = urllib.request.Request(
        url, data=text.encode("utf-8"),
        headers={"Content-Type": "text/plain", "Accept": "image/svg+xml"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.read()
    except (OSError, ValueError) as e:
        raise RuntimeError(f"Kroki request failed ({e.__class__.__name__}: {e})")


# --- emitters ---------------------------------------------------------------
def emit_mermaid_block(text):
    return f"```mermaid\n{text.rstrip()}\n```\n"


HTML_TEMPLATE = """<!doctype html>
<html lang="en">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
  body {{ background: {bg}; margin: 0; padding: 2rem;
    font-family: ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif; }}
  .mermaid {{ display: flex; justify-content: center; }}
</style>
<pre class="mermaid">
{body}
</pre>
<script type="module">
  import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs";
  mermaid.initialize({{ startOnLoad: true }});
</script>
"""


def build_html(text, title, theme):
    bg = BRAND_BG if theme == "brand" else "#ffffff"
    return HTML_TEMPLATE.format(
        title=html.escape(title or "Diagram"),
        bg=bg,
        body=html.escape(text.rstrip()),
    )


def write_out(data, out, label):
    """Write bytes/str to --out or stdout."""
    if out:
        target = Path(out).expanduser()
        try:
            if isinstance(data, bytes):
                target.write_bytes(data)
            else:
                target.write_text(data, "utf-8")
        except OSError as e:
            log(f"FATAL: write failed ({e.__class__.__name__}: {e})")
            sys.exit(1)
        print(f"wrote {target}")
    else:
        if isinstance(data, bytes):
            sys.stdout.buffer.write(data)
        else:
            sys.stdout.write(data)


def derive_out(args, fmt, ext):
    if args.out:
        return args.out
    if args.input:
        return str(Path(args.input).expanduser().with_suffix(ext))
    return None  # stdout


def main():
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("input", nargs="?", help="Mermaid source file (default: stdin)")
    ap.add_argument("--format", choices=["mermaid", "svg", "png", "html"],
                    default="mermaid")
    ap.add_argument("--render", choices=["auto", "mmdc", "kroki", "none"],
                    default="auto")
    ap.add_argument("--theme", choices=["brand", "default"], default="default")
    ap.add_argument("--out")
    ap.add_argument("--title")
    ap.add_argument("--no-network", action="store_true")
    ap.add_argument("--agent", action="store_true",
                    help="accepted for consistency; this renderer never prompts")
    args = ap.parse_args()

    text = (Path(args.input).expanduser().read_text("utf-8")
            if args.input else sys.stdin.read())
    if not text.strip():
        log("FATAL: empty Mermaid input")
        sys.exit(1)

    for w in validate(text):
        log(f"warning: {w}")
    text = apply_theme(text, args.theme)

    # --- text formats ------------------------------------------------------
    if args.format == "mermaid":
        write_out(emit_mermaid_block(text), derive_out(args, "mermaid", ".md"),
                  "mermaid")
        return
    if args.format == "html":
        write_out(build_html(text, args.title, args.theme),
                  derive_out(args, "html", ".html"), "html")
        return

    # --- raster formats (svg/png): the render ladder -----------------------
    fmt = args.format
    out = derive_out(args, fmt, f".{fmt}")
    if fmt == "png" and not out:
        log("FATAL: --out is required for png (binary output)")
        sys.exit(1)

    engines = {
        "auto": ["mmdc", "kroki"],
        "mmdc": ["mmdc"],
        "kroki": ["kroki"],
        "none": [],
    }[args.render]

    last_err = None
    for eng in engines:
        try:
            if eng == "mmdc":
                data = render_mmdc(text, fmt, args.theme)
            else:
                data = render_kroki(text, fmt, args.no_network)
            write_out(data, out, fmt)
            return
        except RuntimeError as e:
            last_err = e
            log(f"notice: {eng} unavailable — {e}")

    # Explicitly-requested engine failed → hard error (honest, spec A12).
    if args.render in ("mmdc", "kroki"):
        log(f"FATAL: --render={args.render} requested but it could not render "
            f"({last_err})")
        sys.exit(1)

    # auto/none → degrade to the always-works fenced block.
    log("notice: no raster engine available — emitting a fenced ```mermaid "
        "block instead (open it anywhere mermaid renders)")
    write_out(emit_mermaid_block(text),
              str(Path(out).with_suffix(".md")) if out else None, "mermaid")


if __name__ == "__main__":
    main()
