# Career Copilot — desktop app

A local Electron desktop app that wraps the [`career-ai-assistant`](https://github.com/dikshant1103-beep/career-ai-assistant) RAG backend with:

1. **Drop-in resume upload** → embedded into Chroma instantly
2. **Auto job search** across Adzuna + Remotive + Greenhouse + Lever in parallel
3. **AI ranks each job** against your profile (Claude + local TF-IDF sanity score)
4. **Click a job** → instant JD analysis, tailored resume PDF, cover letter
5. **"I submitted ✓"** → tracks the application in SQLite

Because of how job platforms (LinkedIn / Indeed / Naukri) lock down automated form submission, this is a **co-pilot**: the AI prepares everything, you click submit. That's the legitimate way to do this without getting your accounts banned.

---

## 1. One-time install

```bash
# Pre-requisites: Node ≥ 18, Python ≥ 3.10
# This app depends on its sibling project, cloned NEXT TO it (same parent dir):
git clone https://github.com/dikshant1103-beep/career-ai-assistant.git
git clone https://github.com/dikshant1103-beep/career-copilot.git
cd career-ai-assistant && python3 -m venv .venv && .venv/bin/pip install -r requirements.txt && cd ..

cd career-copilot
bash install.sh             # creates venv, installs backend + frontend deps
cp .env.example .env
# If the sibling is NOT at ~/Desktop/career_ai_assistant, set CAREER_AI_PATH in .env
# Edit .env:
#   ANTHROPIC_API_KEY=sk-ant-…            (from console.anthropic.com)
#   ADZUNA_APP_ID=… ADZUNA_APP_KEY=…       (from developer.adzuna.com)
```

> Adzuna is optional — without keys, search still works against Remotive + Greenhouse + Lever.
> The Claude API key is **required**.

---

## 2. Run it

```bash
bash start.sh
```

This launches:
- the FastAPI backend on `http://127.0.0.1:8765`
- Vite dev server on `http://localhost:5173`
- the Electron window that loads it

Ctrl-C in the terminal stops everything.

---

## 3. Daily flow

1. **Upload resume** (Page 1) — drag your PDF/DOCX in, click *Ingest*. Repeat for thesis / SOP / papers if you want richer ranking.
2. **Search jobs** (Page 2) — type a query ("battery ML engineer"), location, country. Click *Search*. Tick the jobs you care about, click *AI rank*. Best fits float to the top.
3. **Click a job** — opens the detail page with three buttons:
   - **Analyze JD** → fit score, ATS score, matched/missing skills
   - **Tailor resume → PDF** → ATS-optimised PDF saved to `exports/copilot/<company>__<title>/resume_tailored.pdf`. Click *Download PDF*.
   - **Cover letter** → generated text + saved to disk
4. Click **Open posting ↗** — the original JD opens in your default browser.
5. Upload the tailored PDF + paste the cover letter into the actual application form on the company's site.
6. Click **I submitted ✓** — the status flips to *applied* in the tracker.
7. **Tracker** (Page 3) — change statuses (applied → interview → offer / rejected), filter, delete.

---

## 4. Architecture

```
┌──────────────────────────────┐         REST / JSON         ┌──────────────────────────────────┐
│  Electron + React + Vite     │ ───────────────────────────▶│  FastAPI backend  (port 8765)    │
│  (frontend/)                 │                              │  (backend/)                      │
│                              │ ◀───────────────────────────│   ├── routes/                    │
└──────────────────────────────┘                              │   │   ├── resume.py (upload)    │
                                                              │   │   ├── jobs.py   (search,    │
                                                              │   │   │              rank)      │
                                                              │   │   ├── apply.py  (tailor,    │
                                                              │   │   │              cover,     │
                                                              │   │   │              mark)      │
                                                              │   │   ├── tracker.py            │
                                                              │   │   └── status.py             │
                                                              │   ├── sources/                  │
                                                              │   │   ├── adzuna.py             │
                                                              │   │   ├── remotive.py           │
                                                              │   │   ├── greenhouse.py         │
                                                              │   │   └── lever.py              │
                                                              │   └── pipeline.py  ─── imports ─┐
                                                              └──────────────────────────────────┘
                                                                                                │
                                                                                                ▼
                                                                              ~/Desktop/career_ai_assistant
                                                                              (RAG · Chroma · Claude · PDF)
```

The backend imports the existing `career_ai_assistant` package via `sys.path` (see `backend/path_bootstrap.py`). No code duplication, single source of truth for the RAG pipeline.

---

## 5. Folder layout

```
career_copilot/
├── backend/
│   ├── app.py                # FastAPI entrypoint
│   ├── pipeline.py           # singletons + wrappers around career_ai_assistant
│   ├── path_bootstrap.py     # sys.path hack to import the sibling project
│   ├── schemas.py            # Pydantic request/response models
│   ├── routes/               # REST endpoints
│   ├── sources/              # adzuna, remotive, greenhouse, lever, aggregator
│   └── requirements.txt      # extra deps on top of career_ai_assistant
├── frontend/
│   ├── electron/             # main + preload (CommonJS)
│   ├── src/                  # React + Vite renderer (TS + Tailwind)
│   │   ├── pages/            # Upload, Search, JobDetail, Tracker
│   │   └── components/       # Layout, JobCard, Spinner
│   ├── package.json
│   ├── vite.config.ts
│   └── tailwind.config.js
├── install.sh
├── start.sh
├── .env.example
└── README.md
```

---

## 6. Job sources

| Source        | Auth needed?                    | Notes                                                |
|---------------|---------------------------------|------------------------------------------------------|
| Adzuna        | yes — `ADZUNA_APP_ID/KEY`       | free 1000/month; best general coverage in IN/US/UK  |
| Remotive      | none                            | remote roles only                                    |
| Greenhouse    | none                            | iterates over `backend/sources/companies.py`         |
| Lever         | none                            | iterates over `backend/sources/companies.py`         |

Edit `backend/sources/companies.py` to add/remove the company slugs that Greenhouse and Lever crawl (the URL slug each company uses for its public board).

---

## 7. Troubleshooting

| Symptom                                                                   | Fix                                                                                                                                |
|---------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------|
| Sidebar shows "Backend offline"                                          | The FastAPI process didn't start. Run `bash start.sh` again and check the terminal logs.                                           |
| Sidebar shows `API key: missing`                                          | Edit `.env`, set `ANTHROPIC_API_KEY=sk-ant-…`, restart `start.sh`.                                                                  |
| Sidebar shows `adzuna: no key`                                            | Optional — leave it; or get free keys at developer.adzuna.com and add `ADZUNA_APP_ID/KEY` to `.env`.                              |
| `RuntimeError: career_ai_assistant not found`                             | Clone [career-ai-assistant](https://github.com/dikshant1103-beep/career-ai-assistant) and/or set `CAREER_AI_PATH=/path/to/career_ai_assistant` in `.env`.  |
| Search returns 0 jobs from `greenhouse`/`lever` for a niche query         | They only cover ~50 companies (see `backend/sources/companies.py`). Add more slugs or rely on Adzuna for breadth.                  |
| `npm install` fails with `EACCES` / permission errors                     | You're running it as root; re-run as your normal user, or `chown -R "$USER" .` in this folder.                                     |
| Electron window stays blank                                               | The Vite dev server isn't up yet on first run. Wait ~10 sec, or open `http://localhost:5173` in a browser to confirm it's live.    |
| `"Claude did not return valid JSON"` on JD analyze                        | Sometimes Claude returns prose. Retry — or lower `CLAUDE_TEMPERATURE` in the `career_ai_assistant` `.env`.                         |
| Tailored PDF won't download                                               | Make sure the backend is on the same port (`8765`) the UI expects, and the file path under `exports/copilot/` exists on disk.       |

Logs: backend writes to its terminal; frontend errors live in the Electron DevTools (opens automatically in dev mode).

---

## 8. What is NOT included (and why)

- **Automatic form submission** to LinkedIn / Indeed / Naukri / Workday — these are protected by CAPTCHA, 2FA, rate limits and ToS that ban automated apply. The "auto-apply" tools you've seen get accounts banned regularly. Our **co-pilot** model is what serious applicants actually use.
- **Web scraping of LinkedIn / Indeed listings** — same reason. Use the API-based sources (Adzuna covers most of them legally).
- **A real "fill the form for me" agent** — possible later via Playwright on a small set of well-known ATS systems (Greenhouse, Lever, Ashby) where they expose a stable form. Out of scope for this MVP.

---

## 9. Roadmap

- Saved-search profiles (re-run a query daily, push notifications)
- Multi-resume support (one tailored PDF per role family)
- Playwright assistant that pre-fills Greenhouse/Lever forms in a controlled browser
- Bulk "tailor all top-N" mode
- Local-LLM (Ollama) fallback to make this fully offline

---

## 10. License

Personal-use starter. No warranty.
