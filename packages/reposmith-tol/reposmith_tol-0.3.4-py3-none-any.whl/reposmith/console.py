from __future__ import annotations

import io
import locale
import os
import sys
from typing import TextIO

def _try_reconfigure(stream: TextIO, *, encoding: str = "utf-8", errors: str = "replace") -> bool:
    """
    Try to reconfigure a TextIO stream with a new encoding (Python 3.7+).

    Args:
        stream (TextIO): Stream to reconfigure (e.g., sys.stdout).
        encoding (str): Encoding to apply. Default is 'utf-8'.
        errors (str): Error handling mode. Default is 'replace'.

    Returns:
        bool: True if reconfiguration was successful, False otherwise.
    """
    if hasattr(stream, "reconfigure"):
        try:
            stream.reconfigure(encoding=encoding, errors=errors)  # type: ignore[attr-defined]
            return True
        except Exception:
            return False
    return False

def _wrap_buffer(stream: TextIO, *, encoding: str = "utf-8", errors: str = "replace") -> bool:
    """
    Wrap the buffer of a TextIO stream with a TextIOWrapper if reconfigure is unavailable.

    Args:
        stream (TextIO): Stream to wrap (e.g., sys.stdout).
        encoding (str): Encoding to apply. Default is 'utf-8'.
        errors (str): Error handling mode. Default is 'replace'.

    Returns:
        bool: True if wrapping was successful, False otherwise.
    """
    buf = getattr(stream, "buffer", None)
    if buf is None:
        return False
    try:
        wrapper = io.TextIOWrapper(buf, encoding=encoding, errors=errors, line_buffering=True)
        if stream is sys.stdout:
            sys.stdout = wrapper  # type: ignore[assignment]
        elif stream is sys.stderr:
            sys.stderr = wrapper  # type: ignore[assignment]
        else:
            return False
        return True
    except Exception:
        return False

def enable_utf8_console() -> bool:
    """
    Ensure stdout and stderr support UTF-8 encoding without crashing on unsupported symbols.

    Returns:
        bool: True if both stdout and stderr were updated successfully.
    """
    preferred = (locale.getpreferredencoding(False) or "").lower()
    target_enc = "utf-8" if "utf" in preferred else (os.environ.get("PYTHONIOENCODING") or "utf-8")

    ok_out = _try_reconfigure(sys.stdout, encoding=target_enc, errors="replace") or \
             _wrap_buffer(sys.stdout, encoding=target_enc, errors="replace")
    ok_err = _try_reconfigure(sys.stderr, encoding=target_enc, errors="replace") or \
             _wrap_buffer(sys.stderr, encoding=target_enc, errors="replace")

    return ok_out and ok_err

def sanitize_text(s: str) -> str:
    """
    Ensure text is printable on the current encoding without raising UnicodeEncodeError.

    Args:
        s (str): Input string to sanitize.

    Returns:
        str: Safe-to-print string using current stdout encoding.
    """
    enc = getattr(sys.stdout, "encoding", None) or locale.getpreferredencoding(False) or "utf-8"
    try:
        s.encode(enc)
        return s
    except UnicodeEncodeError:
        return s.encode(enc, errors="replace").decode(enc, errors="replace")

def maybe_strip_emoji(s: str) -> str:
    """
    Optionally remove emojis from a string based on the REPOSMITH_NO_EMOJI environment variable.

    Args:
        s (str): Input string potentially containing emojis.

    Returns:
        str: Modified string with emojis replaced if REPOSMITH_NO_EMOJI=1.
    """
    if os.environ.get("REPOSMITH_NO_EMOJI") == "1":
        return s.encode("ascii", "replace").decode("ascii")
    return s
