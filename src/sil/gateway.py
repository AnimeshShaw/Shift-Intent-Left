"""The tool gateway: the policy enforcement point (PEP) of the reference architecture.

Every side-effecting call is mediated here (property P1). The gateway evaluates
adm(a, I), enforces the step ceiling, and appends every *attempted* action, with
its decision, to the trace, including blocked ones. Drift is measured over
attempts, not over what executed.

Two modes:

* ``enforce``  - inadmissible actions are blocked.
* ``observe``  - everything runs, violations are only recorded. This is the
  permissive counterfactual used by H2 to establish when an attack *would have*
  succeeded, against which the lead time of the drift signal is measured.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Optional

from .admissibility import DataClassifier, admissible
from .contract import Contract
from .drift import WEIGHT_POLICIES
from .model import Action, Decision
from .trace import TraceWriter


@dataclass(frozen=True)
class Verdict:
    execute: bool          # may the caller run the action?
    decision: Decision     # the pure adm(a, I) result
    reason: str            # "ok" | "violation" | "step_ceiling" | "observed_violation"


class Gateway:
    def __init__(self, contract: Contract, trace: TraceWriter, mode: str = "enforce",
                 weights: str = "severity", classifier: DataClassifier = DataClassifier(),
                 run_id: str = "") -> None:
        if mode not in ("enforce", "observe"):
            raise ValueError("mode must be 'enforce' or 'observe'")
        if weights not in WEIGHT_POLICIES:
            raise ValueError("unknown weighting: %s" % weights)
        self.contract = contract
        self.trace = trace
        self.mode = mode
        self.classifier = classifier
        self.weights_name = weights
        self._weight = WEIGHT_POLICIES[weights](contract, classifier)
        self._steps = 0
        self.trace.write("start", {"run_id": run_id, "contract_digest": contract.digest,
                                   "mode": mode, "weights": weights,
                                   "max_steps": contract.max_steps})

    def checkpoint(self) -> None:
        """A human checkpoint: resets the autonomous step counter (n_max)."""
        self._steps = 0
        self.trace.write("checkpoint", {})

    def mediate(self, action: Action) -> Verdict:
        decision = admissible(action, self.contract, self.classifier)
        ceiling_hit = self._steps >= self.contract.max_steps

        if self.mode == "observe":
            execute = True
            reason = "ok" if decision.admissible else "observed_violation"
        elif not decision.admissible:
            execute, reason = False, "violation"
        elif ceiling_hit:
            execute, reason = False, "step_ceiling"
        else:
            execute, reason = True, "ok"

        self.trace.write("action", {
            "action": action.as_dict(),
            "adm": decision.admissible,
            "failed": list(decision.failed),
            "weight": self._weight(action),
            "executed": execute,
            "reason": reason,
        })
        if execute:
            self._steps += 1
        return Verdict(execute=execute, decision=decision, reason=reason)

    def run(self, action: Action, executor: Callable[[Action], Any]) -> Optional[Any]:
        """Mediate, then execute only if permitted. Returns the executor's result or None."""
        verdict = self.mediate(action)
        return executor(action) if verdict.execute else None
