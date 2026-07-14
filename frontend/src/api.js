const BASE = import.meta.env?.VITE_API || "http://localhost:8000";
const h = (t) => ({ "Content-Type": "application/json", "X-Tenant-Id": t });

export async function listClients(t) {
  return (await fetch(`${BASE}/v1/clients`, { headers: h(t) })).json();
}
export async function addIndex(t, rec) {
  return (await fetch(`${BASE}/v1/index`, { method: "POST", headers: h(t), body: JSON.stringify(rec) })).json();
}
export function reportUrl(clientId) { return `${BASE}/v1/report/${clientId}`; }
