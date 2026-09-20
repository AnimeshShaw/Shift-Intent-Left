"""The admissibility predicate adm(a, I): Definition 4 of the paper.

Six conditions, all of which must hold. Identifiers are stable so a trace can
record which condition failed:

    C1  (tool, op) in Theta   [refined by allow_cmds for execute, registries for install]
    C2  target in S           [path resources]
    C3  writes stay in W and outside Pi   [path resources]
    C4  connect targets are in E          [host resources]
    C5  class(target) in Delta            [path resources]
    C6  a matching confirmation predicate has a recorded human confirmation
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Sequence, Tuple

from .contract import Contract
from .globs import any_match, normalize
from .model import Action, Decision

DEFAULT_SECRET_PATTERNS: Tuple[str, ...] = (
    ".env*", "*.pem", "*.key", "id_rsa*", "**/secrets/**", "**/.ssh/**", "**/credentials*",
)


@dataclass(frozen=True)
class DataClassifier:
    """Maps a path to a data classification. Secret patterns match at any depth."""
    secret_patterns: Tuple[str, ...] = DEFAULT_SECRET_PATTERNS
    default_class: str = "source_code"

    def classify(self, path: Optional[str]) -> str:
        if path is not None and any_match(self.secret_patterns, path, anywhere=True):
            return "secrets"
        return self.default_class


def _command_allowed(cmd: str, allowed: Sequence[str]) -> bool:
    """A command is allowed if it equals an entry or extends it by whole arguments."""
    c = " ".join(cmd.split())
    return any(c == a or c.startswith(a + " ") for a in allowed)


def admissible(action: Action, contract: Contract,
               classifier: DataClassifier = DataClassifier()) -> Decision:
    failed = []

    # C1: the (tool, op) pair is permitted, refined by the tool's own allowlists.
    grant = contract.tool(action.tool)
    if grant is None or action.op not in grant.ops:
        failed.append("C1")
    elif action.op == "execute" and grant.allow_cmds and not _command_allowed(action.target, grant.allow_cmds):
        failed.append("C1")
    elif action.op == "install" and grant.registries and action.registry not in grant.registries:
        failed.append("C1")

    if action.kind == "path":
        path = normalize(action.target)
        # C2: readable scope. Permitting sets are anchored, so anywhere=False.
        if not any_match(contract.read, path):
            failed.append("C2")
        # C3: a write must be inside W and outside Pi. Pi is restricting, so anywhere=True.
        if action.op == "write":
            if not any_match(contract.write, path) or any_match(contract.protected, path, anywhere=True):
                failed.append("C3")
        # C5: the data class of the target must be permitted.
        if classifier.classify(path) not in contract.data_classes:
            failed.append("C5")
    elif action.kind == "host":
        # C4: egress is deny-by-default, matched exactly and case-insensitively.
        if action.op == "connect" and action.target.lower() not in contract.egress:
            failed.append("C4")

    # C6: a matching confirmation predicate needs a recorded human confirmation.
    if any(t in contract.require_human_for for t in action.tags) and not action.confirmation:
        failed.append("C6")

    return Decision(admissible=not failed, failed=tuple(failed))
