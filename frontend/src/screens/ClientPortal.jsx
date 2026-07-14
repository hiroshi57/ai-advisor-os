import React from "react";

// クライアントポータル: 自社のAI-Adoption Index + 業界ベンチマーク位置。
export default function ClientPortal({ company, score, factors, benchmark }) {
  return (
    <div className="card">
      <h2>{company} の AI活用状況</h2>
      <div className="big">{score?.toFixed(1) ?? "-"} <small>/ 100（AI-Adoption Index）</small></div>
      <h3>4因子</h3>
      <ul>{Object.entries(factors || {}).map(([k, v]) => <li key={k}>{k}: {v.toFixed(0)}</li>)}</ul>
      <h3>業界ベンチマーク</h3>
      {benchmark?.available
        ? <p>中央値 {benchmark.median} / あなたは上位 <b>{benchmark.percentile_of}%</b>（n={benchmark.n}）</p>
        : <p>{benchmark?.reason || "同業界5社未満のため非表示（k-匿名性）"}</p>}
    </div>
  );
}
