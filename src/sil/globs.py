"""Path normalisation and glob matching.

Two deliberate choices, both documented in docs/SPEC-NOTES.md:

* Paths that escape the workspace (absolute, drive-lettered, or containing a
  leading ``..`` after normalisation) normalise to ``None`` and are never in
  any permitting set.
* A pattern with no ``/`` matches at any depth only when used as a *restricting*
  set (protected paths, secret classifiers). As a *permitting* set (read/write
  scope) it is anchored to the workspace root, so a bare ``requirements*.txt``
  in ``write`` does not silently authorise ``vendor/deep/requirements.txt``.
  Permitting sets err narrow; restricting sets err broad.
"""
from __future__ import annotations

import posixpath
import re
from functools import lru_cache
from typing import Iterable, Optional


def normalize(path: str) -> Optional[str]:
    """Return a workspace-relative POSIX path, or None if it escapes the workspace."""
    p = path.replace("\\", "/")
    if p.startswith("/") or re.match(r"^[A-Za-z]:/", p):
        return None
    n = posixpath.normpath(p)
    if n == ".":
        return ""
    if n == ".." or n.startswith("../"):
        return None
    return n


@lru_cache(maxsize=None)
def _compile(pattern: str, anywhere: bool) -> "re.Pattern[str]":
    out: list[str] = []
    i = 0
    while i < len(pattern):
        c = pattern[i]
        if c == "*":
            if pattern.startswith("**/", i):
                out.append("(?:.*/)?")
                i += 3
                continue
            if pattern.startswith("**", i):
                out.append(".*")
                i += 2
                continue
            out.append("[^/]*")
        elif c == "?":
            out.append("[^/]")
        else:
            out.append(re.escape(c))
        i += 1
    body = "".join(out)
    if anywhere and "/" not in pattern:
        body = "(?:.*/)?" + body
    return re.compile("^" + body + "$")


def glob_match(pattern: str, path: str, anywhere: bool = False) -> bool:
    """True if ``path`` (already normalised) matches ``pattern``."""
    return _compile(pattern, anywhere).match(path) is not None


def any_match(patterns: Iterable[str], path: Optional[str], anywhere: bool = False) -> bool:
    """True if any pattern matches. A path that escapes the workspace matches nothing."""
    if path is None:
        return False
    return any(glob_match(p, path, anywhere) for p in patterns)
