import { useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";
import Spinner from "../components/Spinner";

const CATEGORIES = ["resume", "thesis", "paper", "sop", "linkedin", "other"];

export default function Upload() {
  const [files, setFiles] = useState<File[]>([]);
  const [category, setCategory] = useState("resume");
  const [busy, setBusy] = useState(false);
  const [log, setLog] = useState<string[]>([]);
  const [totalChunks, setTotalChunks] = useState<number | null>(null);

  function onDrop(e: React.DragEvent<HTMLDivElement>) {
    e.preventDefault();
    const dropped = Array.from(e.dataTransfer.files);
    setFiles((prev) => [...prev, ...dropped]);
  }

  async function uploadAll() {
    if (!files.length) return;
    setBusy(true);
    setLog([]);
    for (const f of files) {
      try {
        const r = await api.uploadResume(f, category);
        setLog((l) => [...l, `✔ ${f.name} → +${r.chunks_added} chunks (total ${r.total_chunks})`]);
        setTotalChunks(r.total_chunks);
      } catch (err: any) {
        setLog((l) => [...l, `✘ ${f.name} → ${err.message}`]);
      }
    }
    setFiles([]);
    setBusy(false);
  }

  return (
    <div className="p-8 max-w-3xl mx-auto space-y-6">
      <header>
        <h1 className="text-2xl font-bold">Upload your documents</h1>
        <p className="text-slate-400 text-sm mt-1">
          Drop your resume, thesis, papers, SOP, LinkedIn export. Files are indexed
          locally into the vector store — nothing is uploaded to the cloud except
          the eventual Claude prompts that quote from them.
        </p>
      </header>

      <div className="card">
        <label className="block text-sm text-slate-300 mb-1">Category</label>
        <select
          className="input mb-3"
          value={category}
          onChange={(e) => setCategory(e.target.value)}
        >
          {CATEGORIES.map((c) => (
            <option key={c} value={c}>{c}</option>
          ))}
        </select>

        <div
          onDragOver={(e) => e.preventDefault()}
          onDrop={onDrop}
          className="border-2 border-dashed border-line rounded-xl p-8 text-center text-slate-400 hover:border-accent transition-colors"
        >
          <div className="text-lg">Drag & drop files here</div>
          <div className="text-xs mt-1">or</div>
          <label className="btn-secondary mt-3 cursor-pointer inline-block">
            Choose files…
            <input
              type="file"
              multiple
              accept=".pdf,.docx,.md,.markdown,.txt"
              className="hidden"
              onChange={(e) => setFiles(Array.from(e.target.files || []))}
            />
          </label>
          <div className="text-xs mt-2">PDF · DOCX · MD · TXT</div>
        </div>

        {files.length > 0 && (
          <div className="mt-4">
            <div className="text-sm text-slate-300 mb-2">Queued:</div>
            <ul className="text-sm space-y-1">
              {files.map((f, i) => (
                <li key={i} className="flex justify-between">
                  <span className="truncate">{f.name}</span>
                  <span className="text-slate-500">{(f.size / 1024).toFixed(1)} KB</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        <div className="mt-4 flex items-center gap-3">
          <button className="btn-primary" disabled={!files.length || busy} onClick={uploadAll}>
            {busy ? "Uploading…" : `Ingest ${files.length || ""} file(s)`}
          </button>
          {busy && <Spinner label="Embedding & storing…" />}
        </div>
      </div>

      {log.length > 0 && (
        <div className="card text-sm font-mono whitespace-pre-wrap">
          {log.join("\n")}
        </div>
      )}

      {totalChunks !== null && (
        <div className="card bg-panel2">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-lg font-semibold">{totalChunks} chunks in vector store</div>
              <div className="text-xs text-slate-400">Ready to search & rank jobs.</div>
            </div>
            <Link to="/search" className="btn-primary">Search jobs →</Link>
          </div>
        </div>
      )}
    </div>
  );
}
