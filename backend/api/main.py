"""AI顧問OS API(FastAPI). Index記録 -> ベンチマーク -> 月次レポート. テナント分離.
`uvicorn backend.api.main:app --reload`
"""
from ..db import Database
from ..index import IndexCalculator, AdoptionInput, BenchmarkService, load_formula
from ..reporting import MonthlyReportGenerator, load_catalog
from ..report import build_html_report

FORMULA = load_formula()
DB = Database(":memory:")
CALC = IndexCalculator(FORMULA)
BENCH = BenchmarkService(k_anonymity=FORMULA.get("k_anonymity", 5))
REPORTER = MonthlyReportGenerator(load_catalog())


def record_index(tenant: str, client_id: int, month: str, x: AdoptionInput) -> dict:
    r = CALC.compute(x)
    DB.add_index(tenant, client_id, month, r.score, r.version, r.factors)
    return {"month": month, "score": r.score, "version": r.version, "factors": r.factors}


def create_app():  # pragma: no cover
    from fastapi import Depends, FastAPI, Header, HTTPException
    from fastapi.responses import HTMLResponse
    from pydantic import BaseModel

    app = FastAPI(title="AI Advisor OS", version="1.0.0")

    def tenant(x_tenant_id: str = Header(...)) -> str:
        if not x_tenant_id:
            raise HTTPException(401, "tenant required")
        return x_tenant_id

    class ClientIn(BaseModel):
        company: str
        industry: str = ""

    class IndexIn(BaseModel):
        client_id: int
        month: str
        wau: int = 0
        target_users: int = 1
        active_departments: int = 0
        total_departments: int = 1
        usage_stage_avg: float = 1.0
        governance_checklist_ratio: float = 0.0

    @app.post("/v1/clients")
    def create_client(body: ClientIn, t: str = Depends(tenant)):
        return {"client_id": DB.add_client(t, body.company, body.industry)}

    @app.get("/v1/clients")
    def list_clients(t: str = Depends(tenant)):
        return {"clients": DB.list_clients(t)}

    @app.post("/v1/index")
    def add_index(body: IndexIn, t: str = Depends(tenant)):
        if DB.get_client(t, body.client_id) is None:
            raise HTTPException(404, "client not found")
        x = AdoptionInput(body.wau, body.target_users, body.active_departments,
                          body.total_departments, body.usage_stage_avg,
                          body.governance_checklist_ratio)
        return record_index(t, body.client_id, body.month, x)

    @app.get("/v1/report/{client_id}", response_class=HTMLResponse)
    def report(client_id: int, t: str = Depends(tenant)):
        client = DB.get_client(t, client_id)
        if client is None:
            raise HTTPException(404, "client not found")
        records = DB.list_index(t, client_id)
        acts, bench = [], None
        if records:
            latest = records[-1]
            rep = REPORTER.generate(client["company"], latest["score"], 0.0, latest["factors"], [])
            acts = [{"id": a.catalog_id, "name": a.name, "target": a.target}
                    for a in rep.recommended_actions]
            seg = DB.segment_scores(t, client["industry"])
            bench = BENCH.segment_benchmark(seg, own_score=latest["score"]).as_dict()
        return build_html_report(client["company"], records, acts, bench)

    @app.get("/healthz")
    def healthz():
        return {"status": "ok"}

    return app


try:  # pragma: no cover
    app = create_app()
except Exception:
    app = None
