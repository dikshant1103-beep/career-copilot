import { useEffect, useMemo, useState } from "react";
import { api } from "../api";
import JobCard from "../components/JobCard";
import Spinner from "../components/Spinner";
import type { JobPosting, RankResponse, SearchResponse } from "../types";

const ALL_SOURCES = ["adzuna", "remotive", "greenhouse", "lever"];

export default function Search() {
  const [query, setQuery] = useState("battery ML engineer");
  const [location, setLocation] = useState("");
  const [country, setCountry] = useState("in");
  const [remoteOnly, setRemoteOnly] = useState(false);
  const [sources, setSources] = useState<string[]>(ALL_SOURCES);

  const [busy, setBusy] = useState(false);
  const [data, setData] = useState<SearchResponse | null>(null);
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [ranking, setRanking] = useState<RankResponse | null>(null);
  const [rankBusy, setRankBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Profile-driven query suggestions
  const [suggestions, setSuggestions] = useState<{
    queries: { query: string; rationale: string; suggested_location: string; remote_friendly: boolean }[];
    suggested_role_titles: string[];
    core_keywords: string[];
    summary: string;
  } | null>(null);
  const [suggestBusy, setSuggestBusy] = useState(false);

  async function doSuggest() {
    setSuggestBusy(true);
    setError(null);
    try {
      const r = await api.suggestQueries();
      setSuggestions(r);
    } catch (err: any) {
      setError(err?.response?.data?.detail || err.message);
    } finally {
      setSuggestBusy(false);
    }
  }

  function applySuggestion(q: { query: string; suggested_location: string; remote_friendly: boolean }) {
    setQuery(q.query);
    if (q.suggested_location) setLocation(q.suggested_location);
    if (q.remote_friendly) setRemoteOnly(true);
  }

  async function doSearch() {
    setBusy(true);
    setError(null);
    setRanking(null);
    setSelected(new Set());
    try {
      const r = await api.search({ query, location, country, remote_only: remoteOnly, sources });
      setData(r);
    } catch (err: any) {
      setError(err?.response?.data?.detail || err.message);
    } finally {
      setBusy(false);
    }
  }

  function toggle(id: string) {
    setSelected((prev) => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  }

  function selectAll() {
    if (!data) return;
    setSelected(new Set(data.jobs.map((j) => j.id)));
  }
  function clearSel() { setSelected(new Set()); }

  async function doRank() {
    if (!data) return;
    const picks = data.jobs.filter((j) => selected.has(j.id));
    const list: JobPosting[] = picks.length ? picks : data.jobs.slice(0, 8);
    setRankBusy(true);
    try {
      const r = await api.rank(list);
      setRanking(r);
    } catch (err: any) {
      setError(err?.response?.data?.detail || err.message);
    } finally {
      setRankBusy(false);
    }
  }

  // Quick map for ranked overlay
  const rankMap = useMemo(() => {
    const m = new Map<string, { score: number; verdict: string; reason: string }>();
    ranking?.rankings.forEach((r) =>
      m.set(r.job.id, {
        score: r.overall_score,
        verdict: r.verdict,
        reason: r.one_line_reason,
      })
    );
    return m;
  }, [ranking]);

  const sortedJobs = useMemo(() => {
    if (!data) return [];
    if (!ranking) return data.jobs;
    const order = new Map(ranking.rankings.map((r, i) => [r.job.id, i]));
    return [...data.jobs].sort((a, b) => {
      const ai = order.has(a.id) ? order.get(a.id)! : 9999;
      const bi = order.has(b.id) ? order.get(b.id)! : 9999;
      return ai - bi;
    });
  }, [data, ranking]);

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-6">
      <header>
        <h1 className="text-2xl font-bold">Search jobs</h1>
        <p className="text-slate-400 text-sm mt-1">
          Queries fan out to Adzuna, Remotive, Greenhouse & Lever in parallel.
          Select the interesting ones, then let Claude rank them against your profile.
        </p>
      </header>

      <div className="card grid grid-cols-1 md:grid-cols-6 gap-3">
        <div className="md:col-span-3">
          <label className="text-xs text-slate-400">Query</label>
          <input className="input" value={query} onChange={(e) => setQuery(e.target.value)} />
        </div>
        <div className="md:col-span-2">
          <label className="text-xs text-slate-400">Location</label>
          <input className="input" placeholder="e.g. Bengaluru" value={location} onChange={(e) => setLocation(e.target.value)} />
        </div>
        <div>
          <label className="text-xs text-slate-400">Country</label>
          <input className="input" value={country} onChange={(e) => setCountry(e.target.value)} />
        </div>

        <div className="md:col-span-6 flex flex-wrap items-center gap-3">
          <label className="flex items-center gap-2 text-sm">
            <input type="checkbox" className="accent-teal-400" checked={remoteOnly} onChange={(e) => setRemoteOnly(e.target.checked)} />
            Remote only
          </label>
          <div className="flex flex-wrap items-center gap-3">
            <span className="text-xs text-slate-400">Sources:</span>
            {ALL_SOURCES.map((s) => (
              <label key={s} className="flex items-center gap-1 text-sm">
                <input
                  type="checkbox"
                  className="accent-teal-400"
                  checked={sources.includes(s)}
                  onChange={(e) =>
                    setSources((prev) =>
                      e.target.checked ? [...prev, s] : prev.filter((x) => x !== s)
                    )
                  }
                />
                {s}
              </label>
            ))}
          </div>
          <div className="ml-auto flex gap-2">
            <button className="btn-secondary" onClick={doSuggest} disabled={suggestBusy}>
              {suggestBusy ? "Reading your profile…" : "✨ Suggest from my profile"}
            </button>
            <button className="btn-primary" onClick={doSearch} disabled={busy}>
              {busy ? "Searching…" : "Search"}
            </button>
          </div>
        </div>
      </div>

      {error && <div className="card border-rose-400 text-rose-300">{error}</div>}
      {busy && <Spinner label="Querying job sources…" />}
      {suggestBusy && <Spinner label="Reading your profile + asking Claude…" />}

      {suggestions && (
        <div className="card space-y-3">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold">Suggested searches from your profile</h2>
            <button className="btn-ghost text-xs" onClick={() => setSuggestions(null)}>dismiss</button>
          </div>
          {suggestions.summary && <p className="text-sm text-slate-300">{suggestions.summary}</p>}
          <div className="space-y-2">
            {suggestions.queries.map((q, i) => (
              <div key={i} className="bg-panel2 rounded-lg p-3 flex items-start justify-between gap-3">
                <div className="flex-1 min-w-0">
                  <div className="font-semibold text-slate-100">{q.query}
                    {q.suggested_location && <span className="text-xs text-slate-400 ml-2">📍 {q.suggested_location}</span>}
                    {q.remote_friendly && <span className="tag ml-2">remote-friendly</span>}
                  </div>
                  <div className="text-xs text-slate-400 mt-0.5">{q.rationale}</div>
                </div>
                <div className="flex gap-2 shrink-0">
                  <button className="btn-ghost text-xs" onClick={() => applySuggestion(q)}>use</button>
                  <button className="btn-primary text-xs"
                          onClick={async () => { applySuggestion(q); setTimeout(doSearch, 50); }}>
                    use & search
                  </button>
                </div>
              </div>
            ))}
          </div>
          {suggestions.suggested_role_titles?.length > 0 && (
            <div>
              <div className="text-xs uppercase text-slate-400 mb-1">Role titles to watch</div>
              <div className="flex flex-wrap gap-1">
                {suggestions.suggested_role_titles.map((t, i) => (
                  <button key={i} className="tag hover:border-accent"
                          onClick={() => { setQuery(t); }}>
                    {t}
                  </button>
                ))}
              </div>
            </div>
          )}
          {suggestions.core_keywords?.length > 0 && (
            <div>
              <div className="text-xs uppercase text-slate-400 mb-1">Core keywords</div>
              <div className="flex flex-wrap gap-1">
                {suggestions.core_keywords.map((k, i) => <span key={i} className="tag">{k}</span>)}
              </div>
            </div>
          )}
        </div>
      )}

      {data && (
        <>
          <div className="flex items-center justify-between flex-wrap gap-2">
            <div className="text-sm text-slate-400">
              {data.jobs.length} jobs · {Object.entries(data.source_counts).map(([k, v]) => `${k}=${v}`).join(" · ")}
              {data.errors.length > 0 && (
                <span className="ml-2 text-amber-400">errors: {data.errors.join(" | ")}</span>
              )}
            </div>
            <div className="flex gap-2 items-center">
              <button className="btn-ghost" onClick={selectAll}>Select all</button>
              <button className="btn-ghost" onClick={clearSel}>Clear</button>
              <button className="btn-primary" onClick={doRank} disabled={!data.jobs.length || rankBusy}>
                {rankBusy ? "Ranking…" : `AI rank (${selected.size || "all"})`}
              </button>
            </div>
          </div>

          {ranking?.summary && (
            <div className="card bg-panel2">
              <div className="text-xs uppercase text-slate-400 mb-1">AI summary</div>
              <div className="text-sm">{ranking.summary}</div>
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {sortedJobs.map((j) => {
              const r = rankMap.get(j.id);
              return (
                <JobCard
                  key={j.id}
                  job={j}
                  selected={selected.has(j.id)}
                  onToggle={() => toggle(j.id)}
                  score={r?.score}
                  verdict={r?.verdict}
                  reason={r?.reason}
                />
              );
            })}
          </div>
        </>
      )}
    </div>
  );
}
