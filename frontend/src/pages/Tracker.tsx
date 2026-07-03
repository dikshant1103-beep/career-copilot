import { useEffect, useState } from "react";
import { api } from "../api";
import Spinner from "../components/Spinner";
import type { TrackedJob } from "../types";

const STATUSES = ["saved", "tailored", "applied", "interview", "offer", "rejected", "analyzed"];

export default function Tracker() {
  const [rows, setRows] = useState<TrackedJob[] | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<string>("");

  async function load() {
    setBusy(true);
    setError(null);
    try {
      const r = await api.tracker();
      setRows(r);
    } catch (e: any) {
      setError(e?.response?.data?.detail || e.message);
    } finally {
      setBusy(false);
    }
  }

  useEffect(() => { load(); }, []);

  async function changeStatus(id: number, status: string) {
    await api.updateTracked(id, { status });
    await load();
  }
  async function remove(id: number) {
    if (!confirm("Delete this tracked job?")) return;
    await api.deleteTracked(id);
    await load();
  }

  if (busy && !rows) return <div className="p-8"><Spinner label="Loading tracker…" /></div>;

  const filtered = (rows || []).filter((r) => !filter || r.status === filter);

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-4">
      <header className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Application tracker</h1>
          <p className="text-slate-400 text-sm">{rows?.length ?? 0} total · stored locally in SQLite</p>
        </div>
        <div className="flex items-center gap-2">
          <select className="input w-40" value={filter} onChange={(e) => setFilter(e.target.value)}>
            <option value="">All statuses</option>
            {STATUSES.map((s) => <option key={s} value={s}>{s}</option>)}
          </select>
          <button className="btn-secondary" onClick={load}>Refresh</button>
        </div>
      </header>

      {error && <div className="card border-rose-400 text-rose-300">{error}</div>}

      <div className="card overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="text-left text-xs uppercase text-slate-400 border-b border-line">
            <tr>
              <th className="py-2 pr-2">#</th>
              <th className="py-2 pr-2">Title</th>
              <th className="py-2 pr-2">Company</th>
              <th className="py-2 pr-2">Status</th>
              <th className="py-2 pr-2 text-right">Fit</th>
              <th className="py-2 pr-2 text-right">ATS</th>
              <th className="py-2 pr-2">Updated</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((r) => (
              <tr key={r.id} className="border-b border-line/50 hover:bg-panel2">
                <td className="py-2 pr-2 text-slate-500">{r.id}</td>
                <td className="py-2 pr-2">{r.title}</td>
                <td className="py-2 pr-2 text-slate-400">{r.company}</td>
                <td className="py-2 pr-2">
                  <select
                    className="bg-panel border border-line rounded px-1 py-0.5 text-xs"
                    value={r.status}
                    onChange={(e) => changeStatus(r.id, e.target.value)}
                  >
                    {STATUSES.map((s) => <option key={s} value={s}>{s}</option>)}
                  </select>
                </td>
                <td className="py-2 pr-2 text-right">{r.score != null ? r.score.toFixed(0) : "—"}</td>
                <td className="py-2 pr-2 text-right">{r.ats_score != null ? r.ats_score.toFixed(0) : "—"}</td>
                <td className="py-2 pr-2 text-xs text-slate-500">{r.updated_at.slice(0, 16).replace("T", " ")}</td>
                <td className="py-2"><button className="text-rose-400 text-xs" onClick={() => remove(r.id)}>delete</button></td>
              </tr>
            ))}
            {filtered.length === 0 && (
              <tr><td colSpan={8} className="py-6 text-center text-slate-500">No applications yet.</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
