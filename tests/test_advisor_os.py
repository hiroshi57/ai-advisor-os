import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest  # noqa: E402

from backend.index import IndexCalculator, AdoptionInput, BenchmarkService, load_formula  # noqa: E402
from backend.assistant import AssistantApprovalFlow, Citation, ApprovalFlowError  # noqa: E402


# --- AI-Adoption Index ---
def test_index_within_bounds_and_versioned():
    r = IndexCalculator().compute(AdoptionInput(60, 100, 4, 8, 2.1, 0.7))
    assert 0 <= r.score <= 100
    assert r.version == "v1.0"


def test_index_monotonic_in_utilization():
    calc = IndexCalculator()
    low = calc.compute(AdoptionInput(20, 100, 4, 8, 2.0, 0.5)).score
    high = calc.compute(AdoptionInput(90, 100, 4, 8, 2.0, 0.5)).score
    assert high > low


def test_formula_versioning_switch():
    f = load_formula()
    f2 = {"version": "v2.0", "weights": {"utilization": 1.0, "breadth": 0, "depth": 0, "governance": 0},
          "k_anonymity": 5}
    r1 = IndexCalculator(f).compute(AdoptionInput(50, 100, 8, 8, 3.0, 1.0))
    r2 = IndexCalculator(f2).compute(AdoptionInput(50, 100, 8, 8, 3.0, 1.0))
    assert r1.version != r2.version
    assert r2.score == 50.0     # 利用率のみ重み1.0 -> 50%


# --- k-匿名ベンチマーク ---
def test_benchmark_hidden_below_k():
    b = BenchmarkService(k_anonymity=5).segment_benchmark([55, 60, 62])
    assert b.available is False
    assert b.n == 3


def test_benchmark_shown_at_or_above_k():
    b = BenchmarkService(k_anonymity=5).segment_benchmark([40, 55, 60, 62, 70], own_score=60)
    assert b.available is True
    assert b.median > 0
    assert b.percentile_of is not None


# --- 顧問承認フロー ---
def test_citation_required_no_answer():
    flow = AssistantApprovalFlow()
    d = flow.draft("Q", "A", citations=[])
    assert d.status == "no_answer"
    assert d.answer == ""


def test_unapproved_not_sent():
    flow = AssistantApprovalFlow()
    d = flow.draft("Q", "A", [Citation("karte", "C-1")])
    assert flow.is_sent_to_client(d.id) is False    # 承認前は未送信


def test_approve_sends_and_audits():
    flow = AssistantApprovalFlow()
    d = flow.draft("Q", "A", [Citation("knowledge", "K-9")])
    flow.approve_and_send(d.id, "adv01")
    assert flow.is_sent_to_client(d.id) is True
    actions = [e["action"] for e in flow.audit_log]
    assert "draft.approved_sent" in actions


def test_cannot_send_no_answer_draft():
    flow = AssistantApprovalFlow()
    d = flow.draft("Q", "A", [])       # no_answer
    with pytest.raises(ApprovalFlowError):
        flow.approve_and_send(d.id, "adv01")


def test_edit_and_send_marks_edited():
    flow = AssistantApprovalFlow()
    d = flow.draft("Q", "A", [Citation("karte", "C-2")])
    flow.edit_and_send(d.id, "adv01", "修正後の回答")
    assert d.edited is True and d.answer == "修正後の回答"
    assert flow.is_sent_to_client(d.id) is True
