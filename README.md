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
python -m pytest -q     # テスト16件
```

進め方（プロンプト指定）: F1→F2→F5→F3→F4。

## 予定フォルダ構成（実装時）

```
backend/{karte,assistant/rag,assistant/approval,reporting,index,db}
frontend/{advisor-console,client-portal}
slack_worker/ / seed/demo_clients/
tests/{test_approval_gate,test_citation_required,test_k_anonymity}
```
