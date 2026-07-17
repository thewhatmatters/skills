"""Shared HTTP helper for extract-docs scripts: verified TLS with a CA ladder.

macOS framework Python ships no local issuer bundle, so plain urllib fails
CERTIFICATE_VERIFY_FAILED where curl (system keychain) works. Ladder
(spec A11): certifi if importable → /etc/ssl/cert.pem (macOS LibreSSL
bundle) → interpreter default. Verification is never disabled.

get(url, timeout=15, method="GET") → (status:int, body:str)
  status 0 = network/SSL failure; body "" on any failure. Never raises.
"""
import os
import ssl
import sys
import urllib.error
import urllib.request

UA = {"User-Agent": "extract-docs/1.0 (+local documentation mirror)"}


def _context():
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        pass
    if os.path.exists("/etc/ssl/cert.pem"):
        return ssl.create_default_context(cafile="/etc/ssl/cert.pem")
    return ssl.create_default_context()


_CTX = _context()


def get(url, timeout=15, method="GET", max_bytes=8_000_000):
    try:
        req = urllib.request.Request(url, headers=UA, method=method)
        with urllib.request.urlopen(req, timeout=timeout, context=_CTX) as r:
            body = "" if method == "HEAD" else r.read(max_bytes).decode(
                "utf-8", errors="replace")
            return r.status, body
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception as e:
        print(f"  fetch error {url}: {e.__class__.__name__}", file=sys.stderr)
        return 0, ""
