"""The Intent Contract as an immutable in-memory object.

Mirrors the tuple I = (G, S, Theta, Delta, E, W, Pi, X, beta, sigma) from the paper.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
from dataclasses import dataclass
from typing import Any, Mapping, Optional, Tuple

import yaml


@dataclass(frozen=True)
class ToolGrant:
    """One entry of Theta: a tool with its permitted operations and refinements."""
    name: str
    ops: frozenset
    allow_cmds: Tuple[str, ...] = ()
    registries: Tuple[str, ...] = ()


@dataclass(frozen=True)
class Contract:
    goal: str
    risk_tier: str
    read: Tuple[str, ...]                        # S
    write: Tuple[str, ...]                       # W
    protected: Tuple[str, ...]                   # Pi
    data_classes: frozenset                      # Delta
    tools: Tuple[ToolGrant, ...]                 # Theta
    egress: frozenset                            # E (lower-cased hostnames)
    require_human_for: frozenset                 # H
    max_steps: int                               # n_max
    credentials: Tuple[Mapping[str, Any], ...]   # C
    exit_criteria: Tuple[str, ...]               # X
    approval: Mapping[str, Any]                  # sigma
    raw: Mapping[str, Any]

    @property
    def theta(self) -> frozenset:
        """The set of permitted (tool, operation) pairs."""
        return frozenset((t.name, op) for t in self.tools for op in t.ops)

    def tool(self, name: str) -> Optional[ToolGrant]:
        return next((t for t in self.tools if t.name == name), None)

    @property
    def digest(self) -> str:
        """Content digest binding actions and artifacts to exactly one contract (property P4)."""
        canonical = json.dumps(self.raw, sort_keys=True, separators=(",", ":"), default=str)
        return "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def contract_from_dict(doc: Mapping[str, Any]) -> Contract:
    """Build a Contract from an already schema-validated mapping."""
    scope = doc["scope"]
    budget = doc.get("budget", {})
    tools = tuple(
        ToolGrant(
            name=t["name"],
            ops=frozenset(t["ops"]),
            allow_cmds=tuple(t.get("allow_cmds", ())),
            registries=tuple(t.get("registries", ())),
        )
        for t in doc["tools"]
    )
    return Contract(
        goal=doc["goal"],
        risk_tier=doc["risk_tier"],
        read=tuple(scope["read"]),
        write=tuple(scope["write"]),
        protected=tuple(scope["protected"]),
        data_classes=frozenset(scope["data_classes"]),
        tools=tools,
        egress=frozenset(h.lower() for h in doc.get("egress", ())),
        require_human_for=frozenset(budget.get("require_human_for", ())),
        max_steps=int(budget["max_autonomous_steps"]),
        credentials=tuple(budget.get("credentials", ())),
        exit_criteria=tuple(doc.get("exit_criteria", ())),
        approval=dict(doc.get("approval", {})),
        raw=dict(doc),
    )


def load_contract(path) -> Contract:
    return contract_from_dict(yaml.safe_load(pathlib.Path(path).read_text(encoding="utf-8")))
