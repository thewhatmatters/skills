"""Internal helper: layered external-binary resolution (spec A11).

Not a standalone script — imported by preflight.py and fetch_transcript.py.
One concern: turn "is yt-dlp/ffmpeg usable here?" into a concrete command list
without ever installing anything. Ephemeral runners (uvx / pipx run) let the
keyless path work with no global install.

Resolution for yt-dlp, first hit wins:
  $YT_DLP_BIN  →  yt-dlp on PATH  →  uvx yt-dlp  →  pipx run yt-dlp  →  None
ffmpeg:
  $FFMPEG_BIN  →  ffmpeg on PATH  →  None
"""
import os
import shutil

INSTALL_HINT = (
    "pipx install yt-dlp      # isolated, recommended\n"
    "# or: uv tool install yt-dlp\n"
    "# or: brew install yt-dlp"
)


def resolve_ytdlp():
    """Return (cmd_list, source_label) or (None, None) if unreachable.

    cmd_list is the argv prefix to which yt-dlp args are appended, e.g.
    ["uvx", "yt-dlp"]. source_label is one of: override|path|uvx|pipx.
    """
    override = os.environ.get("YT_DLP_BIN")
    if override and (shutil.which(override) or os.path.exists(override)):
        return ([override], "override")
    if shutil.which("yt-dlp"):
        return (["yt-dlp"], "path")
    if shutil.which("uvx"):
        return (["uvx", "yt-dlp"], "uvx")
    if shutil.which("pipx"):
        return (["pipx", "run", "yt-dlp"], "pipx")
    return (None, None)


def resolve_ffmpeg():
    """Return the ffmpeg binary path (or None)."""
    override = os.environ.get("FFMPEG_BIN")
    if override and (shutil.which(override) or os.path.exists(override)):
        return override
    return shutil.which("ffmpeg")
