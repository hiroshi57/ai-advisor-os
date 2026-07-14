"""AI顧問 月次HTMLレポート(標準ライブラリのみ)."""
from __future__ import annotations

import html
from typing import Dict, List, Optional


def _bar(v: float, mx: float = 100, width: int = 160) -> str:
    w = int(max(0, min(1, v / mx)) * width)
    return (f'<div style="background:#e4e7ee;border-radius:4px;width:{width}px;height:12px">'
            f'<div style="background:#6a4c93;height:12px;border-radius:4px;width:{w}px"></div></div>')


def build_html_report(company: str, records: List[Dict],
                      recommended_actions: Optional[List[Dict]] = None,
                      benchmark: Optional[Dict] = None) -> str:
    company = html.escape(company)
    recommended_actions = recommended_actions or []
    latest = records[-1] if records else {"score": 0, "version": "-", "factors": {}, "month": "-"}
    prev = records[-2] if len(records) >= 2 else None
    delta = (latest["score"] - prev["score"]) if prev else 0.0

    trend = "".join(f'<tr><td>{html.escape(r["month"])}</td><td>{r["score"]:.1f}</td></tr>' for r in records)
    factors = "".join(
        f'<tr><td>{html.escape(k)}</td><td>{v:.1f}</td><td>{_bar(v)}</td></tr>'
        for k, v in latest["factors"].items())
    acts = "".join(
        f'<li>[{html.escape(a.get("id",""))}] {html.escape(a.get("name",""))} '
        f'({html.escape(a.get("target",""))})</li>' for a in recommended_actions) or "<li>該当施策なし</li>"

    bench_html = ""
    if benchmark and benchmark.get("available"):
        bench_html = (f'<h2>業界ベンチマーク</h2><p>中央値 {benchmark["median"]:.1f} / '
                      f'あなたは上位 {benchmark.get("percentile_of","-")}%（n={benchmark["n"]}）</p>')
    elif benchmark is not None:
        bench_html = f'<h2>業界ベンチマーク</h2><p>{html.escape(benchmark.get("reason","非表示"))}</p>'

    return f"""<!DOCTYPE html><html lang="ja"><head><meta charset="UTF-8">
<title>AI顧問 月次レポート - {company}</title>
<style>body{{font-family:system-ui,sans-serif;margin:24px;color:#1a1a2e}}
h1{{color:#6a4c93}} table{{border-collapse:collapse;margin:8px 0}}
th,td{{border:1px solid #dde;padding:6px 10px}} th{{background:#f0ecf7}}
.big{{font-size:40px;color:#6a4c93;font-weight:bold}}</style></head><body>
<h1>AI顧問 月次レポート</h1>
<p>企業: <b>{company}</b> / 対象月: {html.escape(latest["month"])} / 算出版: {html.escape(latest["version"])}</p>
<p>AI-Adoption Index: <span class="big">{latest["score"]:.1f}</span> / 100 (前月比 {delta:+.1f})</p>
<h2>4因子内訳</h2>
<table><tr><th>因子</th><th>スコア</th><th></th></tr>{factors}</table>
<h2>スコア推移</h2><table><tr><th>月</th><th>スコア</th></tr>{trend}</table>
{bench_html}
<h2>来月の推奨アクション</h2><ul>{acts}</ul>
</body></html>"""
