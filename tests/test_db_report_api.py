import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest  # noqa: E402

from backend.db import Database  # noqa: E402
from backend.report import build_html_report  # noqa: E402


def test_index_roundtrip_and_trend():
    db = Database(":memory:")
    cid = db.add_client("t-a", "ACME", "IT")
    db.add_index("t-a", cid, "2026-05", 55.0, "v1.0", {"utilization": 50})
    db.add_index("t-a", cid, "2026-06", 62.0, "v1.0", {"utilization": 60})
    recs = db.list_index("t-a", cid)
    assert [r["month"] for r in recs] == ["2026-05", "2026-06"]


def test_tenant_isolation():
    db = Database(":memory:")
    cid = db.add_client("t-a", "ACME")
    db.add_index("t-a", cid, "2026-06", 60.0, "v1.0", {})
    assert db.get_client("t-b", cid) is None
    assert db.list_index("t-b", cid) == []
    assert db.list_clients("t-b") == []


def test_segment_scores_by_industry():
    db = Database(":memory:")
    c1 = db.add_client("t-a", "A", "IT")
    c2 = db.add_client("t-a", "B", "IT")
    c3 = db.add_client("t-a", "C", "製造")
    db.add_index("t-a", c1, "2026-06", 60, "v1.0", {})
    db.add_index("t-a", c2, "2026-06", 70, "v1.0", {})
    db.add_index("t-a", c3, "2026-06", 50, "v1.0", {})
    it = db.segment_scores("t-a", "IT")
    assert sorted(it) == [60.0, 70.0]     # 業界IT のみ


def test_html_report_sections_and_escape():
    records = [{"month": "2026-05", "score": 55.0, "version": "v1.0", "factors": {"utilization": 50}},
               {"month": "2026-06", "score": 62.0, "version": "v1.0",
                "factors": {"utilization": 60, "depth": 64}}]
    acts = [{"id": "ACT-001", "name": "基礎研修", "target": "全社"}]
    html = build_html_report("ACME", records, acts, {"available": False, "reason": "5社未満"})
    assert "AI顧問 月次レポート" in html and "ACME" in html
    assert "4因子内訳" in html and "ACT-001" in html and "前月比 +7.0" in html
    assert "5社未満" in html
    assert "<b>x</b>" not in build_html_report("<b>x</b>", [], [])


def test_api_e2e_and_tenant_isolation():
    pytest.importorskip("fastapi")
    pytest.importorskip("httpx")
    from fastapi.testclient import TestClient
    from backend.api.main import create_app
    c = TestClient(create_app())
    ha, hb = {"X-Tenant-Id": "t-a"}, {"X-Tenant-Id": "t-b"}
    cid = c.post("/v1/clients", json={"company": "ACME", "industry": "IT"}, headers=ha).json()["client_id"]
    idx = c.post("/v1/index", json={"client_id": cid, "month": "2026-06", "wau": 60,
                                    "target_users": 100, "active_departments": 4,
                                    "total_departments": 8, "usage_stage_avg": 2.1,
                                    "governance_checklist_ratio": 0.7}, headers=ha).json()
    assert 0 <= idx["score"] <= 100
    assert c.get(f"/v1/report/{cid}", headers=hb).status_code == 404
    r = c.get(f"/v1/report/{cid}", headers=ha)
    assert r.status_code == 200 and "AI顧問 月次レポート" in r.text
