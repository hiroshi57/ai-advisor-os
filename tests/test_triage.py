import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.triage import TriageEngine, ClientSignal  # noqa: E402


def _signals():
    return [
        ClientSignal("c1", "安定商事", index_score=75, index_delta=2, mrr_yen=300000,
                     days_since_contact=5, contract_days_left=200),
        ClientSignal("c2", "危険製作所", index_score=30, index_delta=-10, mrr_yen=400000,
                     days_since_contact=40, contract_days_left=20),
        ClientSignal("c3", "中堅広告", index_score=55, index_delta=-2, mrr_yen=200000,
                     days_since_contact=25, contract_days_left=90),
    ]


def test_high_risk_high_value_ranked_first():
    items = TriageEngine().triage(_signals())
    assert items[0].client_id == "c2"        # 低スコア×悪化×放置×更新間近×高額
    assert items[-1].client_id == "c1"       # 安定


def test_reasons_and_action_present():
    items = TriageEngine().triage(_signals())
    top = items[0]
    assert top.reasons
    assert "更新" in top.recommended_action   # 更新20日 -> 更新面談


def test_top_n_limit():
    assert len(TriageEngine().triage(_signals(), top_n=2)) == 2


def test_stable_client_low_priority():
    stable = ClientSignal("s", "安定", 80, 3, 100000, 3, 300)
    item = TriageEngine().triage([stable])[0]
    assert item.priority < 20
    assert "安定" in item.reasons[0]


def test_priority_scales_with_value():
    low = ClientSignal("l", "小口", 30, -10, 50000, 40, 20)
    high = ClientSignal("h", "大口", 30, -10, 500000, 40, 20)
    items = {i.client_id: i for i in TriageEngine().triage([low, high])}
    assert items["h"].priority > items["l"].priority   # 同リスクなら高額が上位
