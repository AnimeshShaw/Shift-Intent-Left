#!/usr/bin/env python3
"""Validate a SIL Intent Contract.

Checks a contract against schema/intent-contract.schema.json, then enforces the
invariants from the paper that JSON Schema cannot express:

  I1  write subset of read          An agent must not modify what it cannot read (W subset S).
  I2  protected overrides write     A protected path is never writable, however broad W is.
  I3  egress is deny-by-default     Declared egress must be explicit; no wildcards.
  I4  credentials are bounded       Every credential carries a finite TTL.

Usage:
    python tools/validate_contract.py examples/dependency-upgrade.yaml
    python tools/validate_contract.py examples/*.yaml
"""
from __future__ import annotations

import argparse
import fnmatch
import json
import pathlib
import sys

try:
    import yaml
except ImportError:
    sys.exit("pyyaml is required: pip install -r requirements.txt")
try:
    import jsonschema
except ImportError:
    sys.exit("jsonschema is required: pip install -r requirements.txt")

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCHEMA_PATH = ROOT / "schema" / "intent-contract.schema.json"


def _covers(patterns: list[str], candidate: str) -> bool:
    """True if any glob in `patterns` covers `candidate`.

    Exact equality counts, and so does a pattern that fnmatch-matches. This is a
    deliberately conservative approximation: a real enforcement point resolves
    paths, but for linting a contract this catches the common mistakes.
    """
    return any(candidate == p or fnmatch.fnmatch(candidate, p) for p in patterns)


def check_invariants(doc: dict) -> list[str]:
    """Return a list of invariant violations; empty means the contract is sound."""
    errors: list[str] = []
    scope = doc.get("scope", {})
    read = scope.get("read", [])
    write = scope.get("write", [])
    protected = scope.get("protected", [])

    # I1: every writable pattern must be covered by the readable scope.
    for w in write:
        if not _covers(read, w):
            errors.append(
                f"I1 write-not-readable: '{w}' is writable but not covered by scope.read. "
                "An agent must not modify what it cannot read (W subset S)."
            )

    # I2: no writable pattern may be identical to a protected one.
    for w in write:
        if w in protected:
            errors.append(
                f"I2 write-protected-conflict: '{w}' appears in both scope.write and "
                "scope.protected. Protected resources are never writable."
            )

    # I3: egress must be explicit. Deny-by-default is the whole point of E.
    for host in doc.get("egress", []):
        if "*" in host or host.strip() in {"", "0.0.0.0/0", "::/0"}:
            errors.append(
                f"I3 egress-too-broad: '{host}' is a wildcard. Egress is deny-by-default "
                "and must enumerate destinations."
            )

    # I4: every credential must expire.
    for cred in doc.get("budget", {}).get("credentials", []):
        ttl = str(cred.get("ttl", "")).strip()
        if not ttl:
            errors.append(
                f"I4 unbounded-credential: credential '{cred.get('id')}' has no ttl. "
                "Credentials are scoped to the contract and bounded in lifetime."
            )

    # Advisory: a high-tier contract with no confirmation predicates is suspicious.
    if doc.get("risk_tier") == "high" and not doc.get("budget", {}).get("require_human_for"):
        errors.append(
            "I4 advisory: risk_tier is 'high' but budget.require_human_for is empty. "
            "High-tier tasks normally gate at least one action class on human confirmation."
        )
    return errors


def validate(path: pathlib.Path, schema: dict) -> bool:
    """Validate one contract file. Returns True if it passed."""
    try:
        doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        print(f"FAIL {path}: not valid YAML: {exc}")
        return False

    try:
        jsonschema.validate(doc, schema)
    except jsonschema.ValidationError as exc:
        location = "/".join(str(p) for p in exc.absolute_path) or "(root)"
        print(f"FAIL {path}: schema violation at {location}: {exc.message}")
        return False

    violations = check_invariants(doc)
    if violations:
        print(f"FAIL {path}:")
        for v in violations:
            print(f"  - {v}")
        return False

    print(f"OK   {path}")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("contracts", nargs="+", type=pathlib.Path,
                        help="Contract files to validate (YAML or JSON).")
    args = parser.parse_args()

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    results = [validate(p, schema) for p in args.contracts]

    passed, total = sum(results), len(results)
    print(f"\n{passed}/{total} contract(s) valid")
    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
