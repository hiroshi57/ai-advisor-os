import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest  # noqa: E402

from backend.karte import KarteStore  # noqa: E402
from backend.reporting import MonthlyReportGenerator, load_catalog  # noqa: E402


# --- F1 カルテ ---
def test_karte_append_history_and_decisions():
    store = KarteStore(now_fn=lambda: "T")
    store.create("c1", "ACME", tools=["ChatGPT"], monthly_goal="活用率向上")
    store.append_consultation("c1", "議事録AIの相談")
    store.append_decision("c1", "来月から全社展開")
    k = store.get("c1")
    assert len(k.history) == 1 and len(k.decisions) == 1
    assert k.tools == ["ChatGPT"]


def test_karte_missing_raises():
    with pytest.raises(KeyError):
        KarteStore().get("nope")


# --- F3 月次レポート ---
def test_report_recommends_from_catalog_with_ids():
    gen = MonthlyReportGenerator(load_catalog())
    rep = gen.generate("ACME", index_score=35, index_delta=5,
                       factors={"utilization": 30, "breadth": 30, "depth": 40, "ability": 40, "governance": 40},
                       topics=["議事録AI", "広告レポート自動化"])
    assert rep.recommended_actions
    # すべての推奨に施策カタログIDがひも付く(創作なし)
    catalog_ids = {a["id"] for a in load_catalog()["actions"]}
    for a in rep.recommended_actions:
        assert a.catalog_id in catalog_ids


def test_low_index_triggers_basic_training():
    gen = MonthlyReportGenerator(load_catalog())
    rep = gen.generate("ACME", index_score=30, index_delta=0,
                       factors={"utilization": 50, "breadth": 50, "depth": 50, "ability": 50, "governance": 50},
                       topics=[])
    ids = {a.catalog_id for a in rep.recommended_actions}
    assert "ACT-001" in ids     # index<40 -> 基礎研修


def test_report_caps_actions():
    gen = MonthlyReportGenerator(load_catalog())
    rep = gen.generate("ACME", index_score=20, index_delta=0,
                       factors={"utilization": 10, "breadth": 10, "depth": 10, "ability": 10, "governance": 10},
                       topics=[], max_actions=2)
    assert len(rep.recommended_actions) <= 2


def test_no_matching_actions_returns_empty():
    gen = MonthlyReportGenerator(load_catalog())
    rep = gen.generate("ACME", index_score=95, index_delta=0,
                       factors={"utilization": 90, "breadth": 90, "depth": 90, "ability": 90, "governance": 90},
                       topics=[])
    assert rep.recommended_actions == []   # 高スコアは該当施策なし(創作しない)
