import React from "react";

// 顧問コンソール: 担当クライアント一覧 + スコア + レポートリンク。
export default function AdvisorConsole({ clients, onOpenReport }) {
  return (
    <div className="card">
      <h2>担当クライアント（顧問1人で最大50社）</h2>
      <table>
        <thead><tr><th>企業</th><th>業界</th><th>Index</th><th>状態</th><th></th></tr></thead>
        <tbody>
          {clients.map((c) => (
            <tr key={c.id}>
              <td>{c.company}</td><td>{c.industry}</td>
              <td>{c.score?.toFixed(1) ?? "-"}</td>
              <td>{c.score >= 60 ? "🟢良好" : c.score >= 40 ? "🟡要注視" : "🔴要介入"}</td>
              <td><button onClick={() => onOpenReport(c.id)}>月次レポート</button></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
