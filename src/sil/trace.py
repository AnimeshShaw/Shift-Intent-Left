"""A tamper-evident action trace.

Each record commits to the previous one, so altering, removing or reordering any
record breaks every hash after it. This detects tampering; it does not prevent
it. True append-only storage is an operational property of the deployment (the
paper's trust assumption), not something a Python file can provide.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import time
from typing import Any, Callable, Dict, List, Optional, Tuple

from .model import Action

GENESIS = "0" * 64


def _canonical(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _hash(prev: str, body: Dict[str, Any]) -> str:
    return hashlib.sha256((prev + _canonical(body)).encode("utf-8")).hexdigest()


class TraceWriter:
    """Appends hash-chained JSON lines. Resumes the chain if the file already exists."""

    def __init__(self, path, clock: Callable[[], float] = time.time) -> None:
        self.path = pathlib.Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._clock = clock
        self._seq = 0
        self._prev = GENESIS
        if self.path.exists() and self.path.stat().st_size > 0:
            last = read_trace(self.path)[-1]
            self._seq = last["seq"] + 1
            self._prev = last["hash"]

    def write(self, rtype: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        body = {"seq": self._seq, "ts": self._clock(), "type": rtype, **payload}
        digest = _hash(self._prev, body)
        record = {**body, "prev": self._prev, "hash": digest}
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(_canonical(record) + "\n")
            fh.flush()
        self._seq += 1
        self._prev = digest
        return record


def read_trace(path) -> List[Dict[str, Any]]:
    with pathlib.Path(path).open(encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def verify_trace(path) -> Tuple[bool, Optional[int]]:
    """Recompute the chain. Returns (True, None), or (False, seq of the first bad record)."""
    prev = GENESIS
    for i, rec in enumerate(read_trace(path)):
        body = {k: v for k, v in rec.items() if k not in ("prev", "hash")}
        if rec.get("prev") != prev or rec.get("seq") != i or _hash(prev, body) != rec.get("hash"):
            return False, i
        prev = rec["hash"]
    return True, None


def action_from_record(rec: Dict[str, Any]) -> Action:
    a = rec["action"]
    return Action(tool=a["tool"], op=a["op"], target=a["target"], kind=a["kind"],
                  registry=a.get("registry"), tags=tuple(a.get("tags", ())),
                  confirmation=bool(a.get("confirmation", False)))
