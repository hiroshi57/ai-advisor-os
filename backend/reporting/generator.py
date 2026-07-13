"""F3 月次レポート自動ドラフト.

推奨アクションは action_catalog.yaml から条件マッチで選定する(カタログにない施策は創作しない)。
全推奨に施策IDがひも付く(受け入れ基準)。
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Dict, List

DEFAULT_CATALOG = {"actions": [
    {"id": "ACT-001", "name": "AI基礎研修(全社)", "when": {"index_below": 40}, "target": "全社"},
    {"id": "ACT-002", "name": "活用深化ワークショップ",
     "when": {"utilization_above": 60, "depth_below": 50}, "target": "推進部署"},
    {"id": "ACT-003", "name": "部署横展開キックオフ", "when": {"breadth_below": 40}, "target": "未導入部署"},
    {"id": "ACT-004", "name": "プロンプト作成トレーニング", "when": {"ability_below": 50}, "target": "実務担当"},
    {"id": "ACT-005", "name": "AI利用ガイドライン整備支援", "when": {"governance_below": 50}, "target": "管理部門"},
]}


def load_catalog(path: str = "") -> Dict:
    path = path or os.path.join(os.path.dirname(__file__), "action_catalog.yaml")
    try:
        import yaml
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception:
        return DEFAULT_CATALOG


def _matches(cond: Dict, factors: Dict, index: float) -> bool:
    ok = True
    for key, val in cond.items():
        metric, op = key.rsplit("_", 1)
        cur = index if metric == "index" else factors.get(metric, 0.0)
        if op == "below":
            ok = ok and cur < val
        elif op == "above":
            ok = ok and cur > val
    return ok


@dataclass
class RecommendedAction:
    catalog_id: str          # ★カタログID(必須・創作なし)
    name: str
    target: str


@dataclass
class MonthlyReport:
    company: str
    index_score: float
    index_delta: float
    topics: List[str]
    recommended_actions: List[RecommendedAction]

    def as_dict(self):
        return {"company": self.company, "index_score": round(self.index_score, 1),
                "index_delta": round(self.index_delta, 1), "topics": self.topics,
                "recommended_actions": [a.__dict__ for a in self.recommended_actions]}


class MonthlyReportGenerator:
    def __init__(self, catalog: Dict = None) -> None:
        self.catalog = catalog or DEFAULT_CATALOG

    def generate(self, company: str, index_score: float, index_delta: float,
                 factors: Dict, topics: List[str], max_actions: int = 3) -> MonthlyReport:
        recs: List[RecommendedAction] = []
        for act in self.catalog["actions"]:
            if _matches(act.get("when", {}), factors, index_score):
                recs.append(RecommendedAction(act["id"], act["name"], act.get("target", "")))
            if len(recs) >= max_actions:
                break
        return MonthlyReport(company=company, index_score=index_score, index_delta=index_delta,
                             topics=topics, recommended_actions=recs)
