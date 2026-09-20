import json

import pytest

from sil import (Action, Gateway, TraceWriter, contract_from_dict, intent_drift,
                 read_trace, verify_trace)
from sil.trace import action_from_record
from conftest import run_a


def make(contract, tmp_path, mode="enforce", **kw):
    path = tmp_path / "trace.jsonl"
    return Gateway(contract, TraceWriter(path), mode=mode, **kw), path


def actions_of(path):
    return [r for r in read_trace(path) if r["type"] == "action"]


# --- trace integrity ----------------------------------------------------------------------

def test_chain_verifies_and_is_tamper_evident(contract, tmp_path):
    gw, path = make(contract, tmp_path)
    for a in run_a():
        gw.mediate(a)
    assert verify_trace(path) == (True, None)

    lines = path.read_text(encoding="utf-8").splitlines()
    rec = json.loads(lines[5])
    rec["adm"] = True                                   # hide a violation
    lines[5] = json.dumps(rec, sort_keys=True, separators=(",", ":"))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    ok, bad = verify_trace(path)
    assert not ok and bad == 5


def test_deleting_or_reordering_a_record_is_detected(contract, tmp_path):
    gw, path = make(contract, tmp_path)
    for a in run_a():
        gw.mediate(a)
    lines = path.read_text(encoding="utf-8").splitlines()
    path.write_text("\n".join(lines[:3] + lines[4:]) + "\n", encoding="utf-8")
    assert verify_trace(path)[0] is False


def test_chain_resumes_across_writers(contract, tmp_path):
    path = tmp_path / "t.jsonl"
    w1 = TraceWriter(path)
    w1.write("start", {})
    w2 = TraceWriter(path)
    w2.write("action", {"x": 1})
    assert verify_trace(path) == (True, None)
    assert [r["seq"] for r in read_trace(path)] == [0, 1]


def test_every_trace_names_exactly_one_contract_digest(contract, tmp_path):
    gw, path = make(contract, tmp_path)
    assert read_trace(path)[0]["contract_digest"] == contract.digest
    assert contract.digest.startswith("sha256:")


# --- enforcement --------------------------------------------------------------------------

def test_enforce_blocks_violations_but_records_them(contract, tmp_path):
    gw, path = make(contract, tmp_path)
    ran = []
    for a in run_a():
        gw.run(a, ran.append)
    assert len(ran) == 7                                 # 3 of the 10 were blocked
    recs = actions_of(path)
    assert len(recs) == 10                               # ...but all 10 attempts are in the trace
    assert [r["executed"] for r in recs].count(False) == 3


def test_blocked_attempts_still_count_toward_drift(contract, tmp_path):
    gw, path = make(contract, tmp_path)
    for a in run_a():
        gw.mediate(a)
    recs = actions_of(path)
    d = intent_drift((r["weight"], r["adm"]) for r in recs)
    assert d == pytest.approx(22 / 31)


def test_failed_conditions_are_recorded(contract, tmp_path):
    gw, path = make(contract, tmp_path)
    gw.mediate(Action("http", "connect", "paste.example.net"))
    assert actions_of(path)[0]["failed"] == ["C1", "C4"]


def test_trace_round_trips_to_actions(contract, tmp_path):
    gw, path = make(contract, tmp_path)
    original = run_a()
    for a in original:
        gw.mediate(a)
    assert [action_from_record(r) for r in actions_of(path)] == original


# --- observe mode (the permissive counterfactual) ----------------------------------------

def test_observe_mode_executes_everything_and_flags_violations(contract, tmp_path):
    gw, path = make(contract, tmp_path, mode="observe")
    ran = []
    for a in run_a():
        gw.run(a, ran.append)
    assert len(ran) == 10
    recs = actions_of(path)
    assert [r["reason"] for r in recs].count("observed_violation") == 3
    assert sum(1 for r in recs if not r["adm"]) == 3


def test_enforce_and_observe_agree_on_admissibility(contract, tmp_path):
    a_gw, a_path = make(contract, tmp_path / "a")
    b_gw, b_path = make(contract, tmp_path / "b", mode="observe")
    for a in run_a():
        a_gw.mediate(a)
        b_gw.mediate(a)
    assert [r["adm"] for r in actions_of(a_path)] == [r["adm"] for r in actions_of(b_path)]


# --- step ceiling -------------------------------------------------------------------------

def tiny_contract(contract, steps):
    raw = dict(contract.raw)
    raw["budget"] = {**raw["budget"], "max_autonomous_steps": steps}
    return contract_from_dict(raw)


def test_step_ceiling_blocks_until_a_human_checkpoint(contract, tmp_path):
    gw, path = make(tiny_contract(contract, 2), tmp_path)
    ok = Action("shell", "read", "requirements.txt")
    assert gw.mediate(ok).execute
    assert gw.mediate(ok).execute
    v = gw.mediate(ok)
    assert not v.execute and v.reason == "step_ceiling"
    assert v.decision.admissible                         # the action itself was fine
    gw.checkpoint()
    assert gw.mediate(ok).execute


def test_ceiling_denial_is_not_counted_as_drift(contract, tmp_path):
    """The ceiling bounds autonomy; it is not part of adm(a, I) and so not of D."""
    gw, path = make(tiny_contract(contract, 1), tmp_path)
    ok = Action("shell", "read", "requirements.txt")
    gw.mediate(ok)
    gw.mediate(ok)
    recs = actions_of(path)
    assert recs[1]["reason"] == "step_ceiling"
    assert intent_drift((r["weight"], r["adm"]) for r in recs) == 0.0


def test_invalid_mode_and_weighting_rejected(contract, tmp_path):
    with pytest.raises(ValueError):
        Gateway(contract, TraceWriter(tmp_path / "x.jsonl"), mode="yolo")
    with pytest.raises(ValueError):
        Gateway(contract, TraceWriter(tmp_path / "y.jsonl"), weights="vibes")
