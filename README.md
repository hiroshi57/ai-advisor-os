# ai-advisor-os

AI顧問オペレーションOS: 月額制AI顧問サービスの運営基盤。顧問業務の8割（状況把握・月次レポート・
ナレッジ回答）を自動化し、**顧問1人あたり20社→50社**を目指す。

## 差別化ポイント

1. **顧問承認フロー** — ボットは直接返信せず、顧問がワンクリック承認してから送信。
   承認済み回答がナレッジ化し精度が向上する。
2. **全社横断の匿名化ベンチマーク**（AI-Adoption Index）— 単独コンサルには作れない構造的差別化。

## ステータス

🟡 **仕様書ドラフト作成済み・承認待ち**（実装は未着手）

- [docs/index_spec.md](docs/index_spec.md) — AI-Adoption Index（4因子・k匿名ベンチマーク）
- [docs/approval_flow.md](docs/approval_flow.md) — 一次回答ボットの顧問承認フロー状態遷移

進め方（プロンプト指定）: 承認フロー＋Index仕様 → **承認** → 実装（F1→F2→F5→F3→F4）。

## 予定フォルダ構成（実装時）

```
backend/{karte,assistant/rag,assistant/approval,reporting,index,db}
frontend/{advisor-console,client-portal}
slack_worker/ / seed/demo_clients/
tests/{test_approval_gate,test_citation_required,test_k_anonymity}
```
