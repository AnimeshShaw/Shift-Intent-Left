"""Actions and admissibility decisions."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Tuple

_KIND_BY_OP = {"read": "path", "write": "path", "connect": "host",
               "install": "package", "execute": "command"}


@dataclass(frozen=True)
class Action:
    """One attempted tool call, a = (t, op, r, e).

    ``kind`` types the resource r (path / host / package / command). The paper
    treats R as one flat set; an enforcement point cannot, because the scope
    conditions are only meaningful for paths and the egress condition only for
    hosts. See docs/SPEC-NOTES.md.
    """
    tool: str
    op: str
    target: str
    kind: str = ""
    registry: Optional[str] = None       # for install
    tags: Tuple[str, ...] = ()           # names of confirmation predicates this action matches
    confirmation: bool = False           # a valid human confirmation is recorded

    def __post_init__(self) -> None:
        if not self.kind:
            object.__setattr__(self, "kind", _KIND_BY_OP.get(self.op, "path"))

    @property
    def modifies_state(self) -> bool:
        return self.op in ("write", "install")

    def as_dict(self) -> dict:
        return {"tool": self.tool, "op": self.op, "target": self.target, "kind": self.kind,
                "registry": self.registry, "tags": list(self.tags),
                "confirmation": self.confirmation}


@dataclass(frozen=True)
class Decision:
    """Result of evaluating adm(a, I). ``failed`` lists the failing conditions C1..C6."""
    admissible: bool
    failed: Tuple[str, ...] = field(default_factory=tuple)
