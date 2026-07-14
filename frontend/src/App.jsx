import React, { useState } from "react";
import AdvisorConsole from "./screens/AdvisorConsole.jsx";
import ClientPortal from "./screens/ClientPortal.jsx";
import { reportUrl } from "./api.js";

// デモデータ(バックエンド未起動でも画面確認可能)
const DEMO_CLIENTS = [
  { id: 1, company: "デモ商事", industry: "IT", score: 62.5 },
  { id: 2, company: "サンプル製作所", industry: "製造", score: 38.0 },
  { id: 3, company: "テスト広告", industry: "広告", score: 71.0 },
];
const DEMO_PORTAL = {
  company: "デモ商事", score: 62.5,
  factors: { utilization: 60, breadth: 50, depth: 70, governance: 70 },
  benchmark: { available: true, median: 55, percentile_of: 33.3, n: 6 },
};

export default function App() {
  const [tab, setTab] = useState("advisor");
  return (
    <div className="wrap">
      <h1>AI顧問オペレーションOS</h1>
      <nav>
        <button onClick={() => setTab("advisor")} disabled={tab === "advisor"}>顧問コンソール</button>
        <button onClick={() => setTab("client")} disabled={tab === "client"}>クライアントポータル</button>
      </nav>
      {tab === "advisor"
        ? <AdvisorConsole clients={DEMO_CLIENTS} onOpenReport={(id) => window.open(reportUrl(id), "_blank")} />
        : <ClientPortal {...DEMO_PORTAL} />}
    </div>
  );
}
