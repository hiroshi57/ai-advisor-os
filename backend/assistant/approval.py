"""一次回答ボットの顧問承認フロー(差別化).

ボットは直接返信せず、出典つきドラフトを顧問レビューに回す。
出典がなければドラフトを出さない(創作しない)。顧問承認まで送信されない。
"""
from __future__ import annotations

import itertools
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class Citation:
    source_type: str    # karte / knowledge
    ref_id: str


@dataclass
class Draft:
    id: str
    question: str
    answer: str
    citations: List[Citation]
    status: str          # pending_review / no_answer / sent / handled_by_advisor
    edited: bool = False

    def as_dict(self):
        return {"id": self.id, "question": self.question, "answer": self.answer,
                "citations": [c.__dict__ for c in self.citations],
                "status": self.status, "edited": self.edited}


class ApprovalFlowError(Exception):
    pass


class AssistantApprovalFlow:
    """状態遷移: (draft) -> pending_review / no_answer -> sent / handled."""

    def __init__(self, audit_log: Optional[List] = None) -> None:
        self._items: Dict[str, Draft] = {}
        self._seq = itertools.count(1)
        self.audit_log: List[dict] = audit_log if audit_log is not None else []

    def draft(self, question: str, answer: str, citations: List[Citation]) -> Draft:
        did = f"D-{next(self._seq):04d}"
        # 出典必須: 引用がなければ no_answer(創作しない)
        if not citations:
            d = Draft(did, question, "", [], status="no_answer")
        else:
            d = Draft(did, question, answer, citations, status="pending_review")
        self._items[did] = d
        self._audit("system", "draft.created", {"id": did, "status": d.status})
        return d

    def approve_and_send(self, draft_id: str, advisor: str) -> Draft:
        d = self._require(draft_id)
        self._ensure_reviewable(d)
        d.status = "sent"
        self._audit(advisor, "draft.approved_sent", {"id": draft_id})
        return d

    def edit_and_send(self, draft_id: str, advisor: str, new_answer: str) -> Draft:
        d = self._require(draft_id)
        self._ensure_reviewable(d)
        d.answer = new_answer
        d.edited = True
        d.status = "sent"
        self._audit(advisor, "draft.edited_sent", {"id": draft_id})
        return d

    def handle_by_advisor(self, draft_id: str, advisor: str) -> Draft:
        d = self._require(draft_id)
        d.status = "handled_by_advisor"
        self._audit(advisor, "draft.handled", {"id": draft_id})
        return d

    def is_sent_to_client(self, draft_id: str) -> bool:
        return self._require(draft_id).status == "sent"

    # --- internal ---
    def _ensure_reviewable(self, d: Draft) -> None:
        if d.status != "pending_review":
            raise ApprovalFlowError(
                f"{d.id} は pending_review でないため送信できません(現在: {d.status})")

    def _require(self, draft_id: str) -> Draft:
        if draft_id not in self._items:
            raise KeyError(f"ドラフトが見つかりません: {draft_id}")
        return self._items[draft_id]

    def _audit(self, actor: str, action: str, detail: dict) -> None:
        self.audit_log.append({"actor": actor, "action": action, **detail})
