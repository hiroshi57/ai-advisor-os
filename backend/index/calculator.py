"""AI-Adoption Index 算出(0-100). formula.yaml のバージョンをスコアにひも付ける."""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Dict

DEFAULT_FORMULA = {
    "version": "v1.0",
    "weights": {"utilization": 0.35, "breadth": 0.20, "depth": 0.25, "governance": 0.20},
    "k_anonymity": 5,
}


def load_formula(path: str = "") -> Dict:
    path = path or os.path.join(os.path.dirname(__file__), "formula.yaml")
    try:
        import yaml
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception:
        return DEFAULT_FORMULA


@dataclass
class AdoptionInput:
    wau: int
    target_users: int
    active_departments: int
    total_departments: int
    usage_stage_avg: float       # 1.0-3.0 (定型文/分析/意思決定支援)
    governance_checklist_ratio: float  # 0-1


@dataclass
class IndexResult:
    score: float
    version: str
    factors: Dict[str, float]

    def as_dict(self):
        return {"score": round(self.score, 1), "version": self.version,
                "factors": {k: round(v, 1) for k, v in self.factors.items()}}


class IndexCalculator:
    def __init__(self, formula: Dict = None) -> None:
        self.formula = formula or DEFAULT_FORMULA

    def compute(self, x: AdoptionInput) -> IndexResult:
        util = _ratio(x.wau, x.target_users) * 100
        breadth = _ratio(x.active_departments, x.total_departments) * 100
        depth = min(max(x.usage_stage_avg, 0.0), 3.0) / 3 * 100
        gov = min(max(x.governance_checklist_ratio, 0.0), 1.0) * 100
        factors = {"utilization": util, "breadth": breadth, "depth": depth, "governance": gov}
        w = self.formula["weights"]
        total_w = sum(w.values()) or 1.0
        score = sum(factors[k] * w[k] for k in w) / total_w
        return IndexResult(score=score, version=self.formula.get("version", "?"), factors=factors)


def _ratio(a: int, b: int) -> float:
    return (a / b) if b else 0.0
