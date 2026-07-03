import { Link } from "react-router-dom";
import type { JobPosting } from "../types";

export default function JobCard({
  job,
  score,
  verdict,
  reason,
  selected,
  onToggle,
}: {
  job: JobPosting;
  score?: number;
  verdict?: string;
  reason?: string;
  selected?: boolean;
  onToggle?: () => void;
}) {
  return (
    <div className={`card hover:border-accent transition-colors ${selected ? "border-accent" : ""}`}>
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={!!selected}
              onChange={onToggle}
              className="accent-teal-400"
            />
            <Link to={`/job/${job.id}`} className="font-semibold text-slate-100 hover:text-accent truncate">
              {job.title}
            </Link>
          </div>
          <div className="text-sm text-slate-400 mt-0.5">
            {job.company} · {job.location || (job.remote ? "Remote" : "—")}
          </div>
          <div className="mt-2 flex flex-wrap gap-1">
            <span className="tag">{job.source}</span>
            {job.remote && <span className="tag">remote</span>}
            {job.salary && <span className="tag">{job.salary}</span>}
            {verdict && <span className="tag">{verdict}</span>}
          </div>
          <p className="text-xs text-slate-400 mt-2 line-clamp-2">{job.description}</p>
          {reason && <p className="text-xs text-slate-300 mt-1 italic">“{reason}”</p>}
        </div>
        {score !== undefined && (
          <div className="text-right shrink-0">
            <div className="text-2xl font-bold text-accent leading-none">{score.toFixed(0)}</div>
            <div className="text-[10px] text-slate-400 uppercase">fit</div>
          </div>
        )}
      </div>
    </div>
  );
}
