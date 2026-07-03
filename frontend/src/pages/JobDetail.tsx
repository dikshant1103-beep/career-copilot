import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { api, http } from "../api";
import Spinner from "../components/Spinner";
import type { JDAnalysis, JobPosting, TailorResponse } from "../types";

export default function JobDetail() {
  const { id } = useParams();
  const [job, setJob] = useState<JobPosting | null>(null);
  const [analysis, setAnalysis] = useState<JDAnalysis | null>(null);
  const [tailored, setTailored] = useState<TailorResponse | null>(null);
  const [coverLetter, setCoverLetter] = useState<{ text: string; path: string } | null>(null);
  const [busy, setBusy] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Candidate identity used in PDF
  const [candidateName, setCandidateName] = useState("Your Name");
  const [contactLine, setContactLine] = useState(
    "you@example.com  |  linkedin.com/in/you  |  github.com/you"
  );

  useEffect(() => {
    if (!id) return;
    http.get<JobPosting>(`/jobs/${id}`).then((r) => setJob(r.data)).catch((e) => {
      setError(e?.response?.data?.detail || e.message);
    });
  }, [id]);

  async function doAnalyze() {
    if (!id) return;
    setBusy("Analyzing JD…"); setError(null);
    try {
      const r = await api.analyze(id);
      setAnalysis(r);
    } catch (e: any) { setError(e?.response?.data?.detail || e.message); }
    finally { setBusy(null); }
  }

  async function doTailor() {
    if (!id) return;
    setBusy("Tailoring resume + generating PDF…"); setError(null);
    try {
      const r = await api.tailor(id, candidateName, contactLine);
      setTailored(r);
    } catch (e: any) { setError(e?.response?.data?.detail || e.message); }
    finally { setBusy(null); }
  }

  async function doCover() {
    if (!id) return;
    setBusy("Drafting cover letter…"); setError(null);
    try {
      const r = await api.coverLetter(id);
      setCoverLetter({ text: r.text, path: r.path });
    } catch (e: any) { setError(e?.response?.data?.detail || e.message); }
    finally { setBusy(null); }
  }

  async function openExternal(url: string) {
    if (window.copilot?.openExternal) await window.copilot.openExternal(url);
    else window.open(url, "_blank");
  }

  async function markApplied() {
    if (!id) return;
    await api.markApplied(id);
    alert("Marked as applied — see Tracker.");
  }

  if (error) return <div className="p-8 text-rose-300">{error}</div>;
  if (!job) return <div className="p-8"><Spinner label="Loading job…" /></div>;

  return (
    <div className="p-8 max-w-5xl mx-auto space-y-5">
      <header>
        <div className="flex items-start justify-between gap-3">
          <div>
            <h1 className="text-2xl font-bold">{job.title}</h1>
            <div className="text-slate-400">{job.company} · {job.location || (job.remote ? "Remote" : "—")}</div>
            <div className="mt-1 text-xs flex gap-2">
              <span className="tag">{job.source}</span>
              {job.salary && <span className="tag">{job.salary}</span>}
              {job.posted_at && <span className="tag">posted {String(job.posted_at).slice(0, 10)}</span>}
            </div>
          </div>
          <div className="flex flex-col gap-2 shrink-0">
            <button className="btn-secondary" onClick={() => openExternal(job.url)}>Open posting ↗</button>
            <button className="btn-primary" onClick={markApplied}>I submitted ✓</button>
          </div>
        </div>
      </header>

      <div className="card">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          <button className="btn-primary" onClick={doAnalyze} disabled={!!busy}>1. Analyze JD</button>
          <button className="btn-primary" onClick={doTailor} disabled={!!busy}>2. Tailor resume → PDF</button>
          <button className="btn-primary" onClick={doCover} disabled={!!busy}>3. Cover letter</button>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mt-3">
          <div>
            <label className="text-xs text-slate-400">Name on PDF</label>
            <input className="input" value={candidateName} onChange={(e) => setCandidateName(e.target.value)} />
          </div>
          <div>
            <label className="text-xs text-slate-400">Contact line</label>
            <input className="input" value={contactLine} onChange={(e) => setContactLine(e.target.value)} />
          </div>
        </div>
        {busy && <div className="mt-3"><Spinner label={busy} /></div>}
      </div>

      <details className="card">
        <summary className="cursor-pointer text-slate-300">Show full JD</summary>
        <pre className="whitespace-pre-wrap text-sm text-slate-300 mt-2">{job.description}</pre>
      </details>

      {analysis && (
        <div className="card space-y-2">
          <h2 className="text-lg font-semibold">JD Analysis</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-center">
            <div className="bg-panel2 rounded-lg p-3"><div className="text-3xl text-accent font-bold">{analysis.compatibility_score}</div><div className="text-xs text-slate-400">Compatibility</div></div>
            <div className="bg-panel2 rounded-lg p-3"><div className="text-3xl text-accent font-bold">{analysis.ats_score}</div><div className="text-xs text-slate-400">ATS</div></div>
            <div className="bg-panel2 rounded-lg p-3"><div className="text-3xl text-accent2 font-bold">{(analysis.local_cosine_match * 100).toFixed(0)}</div><div className="text-xs text-slate-400">TF-IDF</div></div>
            <div className="bg-panel2 rounded-lg p-3"><div className="text-3xl font-bold capitalize">{analysis.seniority}</div><div className="text-xs text-slate-400">Seniority</div></div>
          </div>
          <p className="text-sm text-slate-300">{analysis.summary}</p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <Block title="Matched skills" items={analysis.candidate_matched_skills} color="text-emerald-300" />
            <Block title="Missing skills" items={analysis.candidate_missing_skills} color="text-rose-300" />
            <Block title="Strengths" items={analysis.strengths} color="text-slate-200" />
            <Block title="Weaknesses" items={analysis.weaknesses} color="text-amber-300" />
            <Block title="ATS keywords" items={analysis.ats_keywords} color="text-slate-300" />
            <Block title="Improvement suggestions" items={analysis.improvement_suggestions} color="text-slate-200" />
          </div>
        </div>
      )}

      {tailored && (
        <div className="card space-y-3">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold">Tailored resume</h2>
            <a className="btn-primary" href={api.downloadUrl(tailored.pdf_path)} target="_blank">Download PDF ↓</a>
          </div>
          <div className="text-sm text-slate-300"><b>Headline:</b> {tailored.headline}</div>
          <div className="text-sm text-slate-300"><b>Summary:</b> {tailored.summary}</div>
          <div className="text-sm"><b>Core skills:</b> <span className="text-slate-300">{tailored.core_skills.join(" · ")}</span></div>
          <div>
            <div className="text-sm font-semibold mb-1">Bullets</div>
            <ul className="space-y-1 text-sm">
              {tailored.bullets.map((b, i) => (
                <li key={i} className="border-l-2 border-accent pl-2">
                  <div className="text-xs text-slate-400">{b.section} · {b.title}</div>
                  <div>{b.rewritten_bullet}</div>
                </li>
              ))}
            </ul>
          </div>
          {tailored.cover_letter_hook && (
            <div className="text-sm text-slate-300 italic">Hook: "{tailored.cover_letter_hook}"</div>
          )}
        </div>
      )}

      {coverLetter && (
        <div className="card">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold">Cover letter</h2>
            <span className="text-xs text-slate-400">{coverLetter.path}</span>
          </div>
          <pre className="whitespace-pre-wrap text-sm text-slate-300 mt-2">{coverLetter.text}</pre>
        </div>
      )}
    </div>
  );
}

function Block({ title, items, color }: { title: string; items: string[]; color?: string }) {
  if (!items || items.length === 0) return null;
  return (
    <div className="bg-panel2 rounded-lg p-3">
      <div className="text-xs uppercase text-slate-400 mb-1">{title}</div>
      <ul className={`text-sm space-y-0.5 ${color || ""}`}>
        {items.map((x, i) => <li key={i}>• {x}</li>)}
      </ul>
    </div>
  );
}
