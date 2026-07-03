import { NavLink, Outlet } from "react-router-dom";
import { useEffect, useState } from "react";
import { api } from "../api";
import type { AppStatus } from "../types";

export default function Layout() {
  const [status, setStatus] = useState<AppStatus | null>(null);

  useEffect(() => {
    api.status().then(setStatus).catch(() => setStatus(null));
    const id = setInterval(() => api.status().then(setStatus).catch(() => null), 8000);
    return () => clearInterval(id);
  }, []);

  const navItem = ({ isActive }: { isActive: boolean }) =>
    `block px-3 py-2 rounded-lg text-sm transition-colors ${
      isActive ? "bg-accent text-ink font-semibold" : "text-slate-300 hover:bg-panel2"
    }`;

  return (
    <div className="h-full flex">
      <aside className="w-64 bg-panel border-r border-line flex flex-col">
        <div className="px-4 py-4 border-b border-line">
          <div className="text-lg font-bold text-accent">Career Copilot</div>
          <div className="text-xs text-slate-400">v0.1.0</div>
        </div>
        <nav className="p-3 space-y-1 flex-1">
          <NavLink to="/" end className={navItem}>1. Upload resume</NavLink>
          <NavLink to="/search" className={navItem}>2. Search jobs</NavLink>
          <NavLink to="/tracker" className={navItem}>3. Tracker</NavLink>
        </nav>
        <div className="p-3 border-t border-line text-xs text-slate-400 space-y-1">
          {status ? (
            <>
              <div>API key: {status.api_key_set ? <span className="text-emerald-400">set</span> : <span className="text-rose-400">missing</span>}</div>
              <div>Model: <span className="text-slate-200">{status.claude_model}</span></div>
              <div>Vector chunks: <span className="text-slate-200">{status.chunks_stored}</span></div>
              <div className="pt-2 border-t border-line">
                <div>Sources:</div>
                {Object.entries(status.sources_available).map(([k, v]) => (
                  <div key={k} className="ml-2">{k}: {v ? <span className="text-emerald-400">ok</span> : <span className="text-amber-400">no key</span>}</div>
                ))}
              </div>
            </>
          ) : (
            <div className="text-rose-400">Backend offline</div>
          )}
        </div>
      </aside>

      <main className="flex-1 overflow-y-auto">
        <Outlet />
      </main>
    </div>
  );
}
