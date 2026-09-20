"""Shift Intent Left: reference enforcement point.

Implements the formal model from the paper: an Intent Contract, the
admissibility predicate adm(a, I), the severity-weighted Intent Drift D, and a
tamper-evident action trace, wired together in a mediating Gateway (the PEP).
"""
from .contract import Contract, ToolGrant, contract_from_dict, load_contract
from .model import Action, Decision
from .admissibility import DataClassifier, admissible
from .drift import (artifact_drift, intent_drift, prefix_series, severity_weights,
                    steep_weights, unit_weights)
from .trace import TraceWriter, read_trace, verify_trace
from .gateway import Gateway, Verdict

__all__ = [
    "Contract", "ToolGrant", "contract_from_dict", "load_contract",
    "Action", "Decision", "DataClassifier", "admissible",
    "intent_drift", "prefix_series", "artifact_drift",
    "unit_weights", "severity_weights", "steep_weights",
    "TraceWriter", "read_trace", "verify_trace", "Gateway", "Verdict",
]
