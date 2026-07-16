"""顧問トリアージエンジン(尖った武器). 50社を1人で回すための優先順位付け.

各クライアントを「離脱リスク × 契約価値 × 放置期間」でスコア化し、
顧問が今日対応すべき順にランキングする(next-best-action)。
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ClientSignal:
    client_id: str
    company: str
    index_score: float          # 直近のAI-Adoption Index (0-100)
    index_delta: float          # 前月比(負=悪化)
    mrr_yen: float              # 月額(契約価値)
    days_since_contact: int     # 最終接触からの日数
    contract_days_left: int     # 契約更新までの残日数


@dataclass
class TriageItem:
    client_id: str
    company: str
    priority: float
    reasons: List[str]
    recommended_action: str

    def as_dict(self):
        return {"client_id": self.client_id, "company": self.company,
                "priority": round(self.priority, 1), "reasons": self.reasons,
                "recommended_action": self.recommended_action}


class TriageEngine:
    def __init__(self, mrr_cap_yen: float = 500000) -> None:
        self.mrr_cap = mrr_cap_yen

    def _score(self, s: ClientSignal) -> TriageItem:
        reasons: List[str] = []
        # 離脱リスク(0-1): 低スコア/悪化/長期放置
        risk = 0.0
        if s.index_score < 40:
            risk += 0.4; reasons.append("Index<40(低定着)")
        if s.index_delta < -5:
            risk += 0.3; reasons.append(f"前月比{s.index_delta:.0f}(悪化)")
        if s.days_since_contact > 21:
            risk += 0.2; reasons.append(f"{s.days_since_contact}日未接触")
        if s.contract_days_left <= 30:
            risk += 0.3; reasons.append(f"更新まで{s.contract_days_left}日")
        risk = min(1.0, risk)
        # 契約価値(0-1)
        value = min(1.0, s.mrr_yen / self.mrr_cap)
        # 優先度 = リスク×価値を主に、リスク単独も加味
        priority = (0.7 * risk * value + 0.3 * risk) * 100
        action = self._action(s, risk)
        if not reasons:
            reasons.append("安定(定期フォローで可)")
        return TriageItem(s.client_id, s.company, priority, reasons, action)

    def _action(self, s: ClientSignal, risk: float) -> str:
        if s.contract_days_left <= 30:
            return "更新面談を設定(契約リスク)"
        if s.index_score < 40:
            return "定着テコ入れ: 基礎研修+活用WSを提案"
        if s.index_delta < -5:
            return "スコア低下の要因ヒアリング"
        if s.days_since_contact > 21:
            return "定期チェックイン連絡"
        return "月次レポート送付のみ"

    def triage(self, signals: List[ClientSignal], top_n: Optional[int] = None) -> List[TriageItem]:
        items = [self._score(s) for s in signals]
        items.sort(key=lambda x: x.priority, reverse=True)
        return items[:top_n] if top_n else items
