"""永続化層(SQLite, 標準ライブラリ). テナント分離 + AI-Adoption Index の月次保存."""
from __future__ import annotations

import json
import sqlite3
from typing import Dict, List, Optional

SCHEMA = """
CREATE TABLE IF NOT EXISTS clients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id TEXT NOT NULL,
    company TEXT NOT NULL,
    industry TEXT DEFAULT ''
);
CREATE TABLE IF NOT EXISTS index_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id TEXT NOT NULL,
    client_id INTEGER NOT NULL,
    month TEXT NOT NULL,
    score REAL NOT NULL,
    version TEXT NOT NULL,
    factors TEXT NOT NULL
);
"""


class Database:
    def __init__(self, path: str = ":memory:") -> None:
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    def add_client(self, tenant_id: str, company: str, industry: str = "") -> int:
        cur = self.conn.execute(
            "INSERT INTO clients(tenant_id, company, industry) VALUES (?, ?, ?)",
            (tenant_id, company, industry))
        self.conn.commit()
        return cur.lastrowid

    def get_client(self, tenant_id: str, client_id: int) -> Optional[Dict]:
        row = self.conn.execute(
            "SELECT id, company, industry FROM clients WHERE id=? AND tenant_id=?",
            (client_id, tenant_id)).fetchone()
        return dict(row) if row else None

    def list_clients(self, tenant_id: str) -> List[Dict]:
        rows = self.conn.execute(
            "SELECT id, company, industry FROM clients WHERE tenant_id=?", (tenant_id,)).fetchall()
        return [dict(r) for r in rows]

    def add_index(self, tenant_id: str, client_id: int, month: str,
                  score: float, version: str, factors: Dict) -> int:
        cur = self.conn.execute(
            "INSERT INTO index_records(tenant_id, client_id, month, score, version, factors) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (tenant_id, client_id, month, score, version, json.dumps(factors, ensure_ascii=False)))
        self.conn.commit()
        return cur.lastrowid

    def list_index(self, tenant_id: str, client_id: int) -> List[Dict]:
        rows = self.conn.execute(
            "SELECT month, score, version, factors FROM index_records "
            "WHERE tenant_id=? AND client_id=? ORDER BY month", (tenant_id, client_id)).fetchall()
        return [{"month": r["month"], "score": r["score"], "version": r["version"],
                 "factors": json.loads(r["factors"])} for r in rows]

    def segment_scores(self, tenant_id: str, industry: str) -> List[float]:
        """同業界の最新スコア群(ベンチマーク用). ※デモは同一テナント内で集計."""
        rows = self.conn.execute(
            "SELECT ir.score FROM index_records ir JOIN clients c ON ir.client_id=c.id "
            "WHERE ir.tenant_id=? AND c.industry=?", (tenant_id, industry)).fetchall()
        return [r["score"] for r in rows]

    def close(self) -> None:
        self.conn.close()
