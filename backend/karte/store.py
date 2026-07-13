"""F1 クライアントカルテ. 会社プロフィール・導入ツール・目標・相談履歴・決定事項を一元管理."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List


@dataclass
class KarteEntry:
    ts: str
    kind: str        # consultation / decision
    text: str


@dataclass
class ClientKarte:
    client_id: str
    company: str
    tools: List[str] = field(default_factory=list)
    monthly_goal: str = ""
    history: List[KarteEntry] = field(default_factory=list)
    decisions: List[KarteEntry] = field(default_factory=list)

    def as_dict(self):
        return {"client_id": self.client_id, "company": self.company,
                "tools": self.tools, "monthly_goal": self.monthly_goal,
                "history": [e.__dict__ for e in self.history],
                "decisions": [e.__dict__ for e in self.decisions]}


class KarteStore:
    def __init__(self, now_fn=None) -> None:
        self._karte: Dict[str, ClientKarte] = {}
        self._now = now_fn or (lambda: datetime.now(timezone.utc).isoformat())

    def create(self, client_id: str, company: str, tools=None, monthly_goal="") -> ClientKarte:
        k = ClientKarte(client_id=client_id, company=company,
                        tools=list(tools or []), monthly_goal=monthly_goal)
        self._karte[client_id] = k
        return k

    def get(self, client_id: str) -> ClientKarte:
        if client_id not in self._karte:
            raise KeyError(f"カルテが見つかりません: {client_id}")
        return self._karte[client_id]

    def append_consultation(self, client_id: str, summary: str) -> KarteEntry:
        e = KarteEntry(self._now(), "consultation", summary)
        self.get(client_id).history.append(e)
        return e

    def append_decision(self, client_id: str, text: str) -> KarteEntry:
        e = KarteEntry(self._now(), "decision", text)
        self.get(client_id).decisions.append(e)
        return e
