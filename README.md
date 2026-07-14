# ai-advisor-os

AI顧問オペレーションOS: 月額制AI顧問サービスの運営基盤。顧問業務の8割（状況把握・月次レポート・
ナレッジ回答）を自動化し、**顧問1人あたり20社→50社**を目指す。

## 差別化ポイント

1. **顧問承認フロー** — ボットは直接返信せず、顧問がワンクリック承認してから送信。
   承認済み回答がナレッジ化し精度が向上する。
2. **全社横断の匿名化ベンチマーク**（AI-Adoption Index）— 単独コンサルには作れない構造的差別化。

## ステータス

🟢 **全機能拡張中**（F1カルテ / F2承認フロー / F3月次レポート / Index+k匿名ベンチ）

- [docs/index_spec.md](docs/index_spec.md) / [docs/approval_flow.md](docs/approval_flow.md) — 仕様
- `backend/index/` — AI-Adoption Index(formula.yamlでバージョン管理) + k匿名ベンチマーク
- `backend/assistant/approval.py` — 顧問承認フロー(出典必須/未承認は未送信)
- `backend/karte/` — F1 クライアントカルテ(相談履歴/決定事項の追記)
- `backend/reporting/` — F3 月次レポート(action_catalogから条件マッチ選定=**創作しない**, 全推奨に施策ID)

```bash
python demo.py          # Index算出 + k匿名ベンチ + 承認フロー
python -m pytest -q     # テスト21件(DB/テナント分離/HTMLレポート/API E2E含む)
```

## 本番構成（SQLite + HTMLレポート + Vite 2画面）

- **DB**: `backend/db/`（SQLite）。クライアント＋Index月次記録、全クエリ tenant_id 強制フィルタ＝**テナント分離**
- **API**: `backend/api/main.py`（FastAPI）。clients / index(算出) / report(HTML, 業界ベンチマーク付き)
- **HTMLレポート**: `backend/report/builder.py`（Index＋4因子＋推移＋推奨施策＋k匿名ベンチマーク、XSSエスケープ）
- **フロント**: `frontend/`（React+Vite）。**顧問コンソール**＋**クライアントポータル**の2画面。ビルド不要は `frontend/standalone.html`
- **CI**: `.github/workflows/ci.yml`

```bash
uvicorn backend.api.main:app --reload
cd frontend && npm install && npm run dev     # or: open frontend/standalone.html
```

## 予定フォルダ構成（実装時）

```
backend/{karte,assistant/rag,assistant/approval,reporting,index,db}
frontend/{advisor-console,client-portal}
slack_worker/ / seed/demo_clients/
tests/{test_approval_gate,test_citation_required,test_k_anonymity}
```
