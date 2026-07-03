import axios from "axios";
import type {
  AppStatus,
  JDAnalysis,
  JobPosting,
  RankResponse,
  SearchResponse,
  TailorResponse,
  TrackedJob,
} from "./types";

const BASE = (import.meta as any).env?.VITE_API_BASE || "http://127.0.0.1:8765";

// 5-min timeout — Claude calls with retrieval + JSON-mode can take 60-180 s
// on cold start (embedder + first Claude call), well past axios' default 0.
export const http = axios.create({ baseURL: BASE, timeout: 300_000 });

export const api = {
  status: () => http.get<AppStatus>("/status").then((r) => r.data),

  uploadResume: (file: File, category = "resume") => {
    const fd = new FormData();
    fd.append("file", file);
    fd.append("category", category);
    return http.post("/resume/upload", fd, {
      headers: { "Content-Type": "multipart/form-data" },
    }).then((r) => r.data);
  },

  search: (body: {
    query: string;
    location?: string;
    country?: string;
    remote_only?: boolean;
    sources?: string[];
    limit_per_source?: number;
  }) => http.post<SearchResponse>("/jobs/search", body).then((r) => r.data),

  analyze: (jobId: string) =>
    http.post<JDAnalysis>(`/jobs/${jobId}/analyze`).then((r) => r.data),

  rank: (jobs: JobPosting[]) =>
    http.post<RankResponse>("/jobs/rank", {
      job_ids: jobs.map((j) => j.id),
      jobs,
    }).then((r) => r.data),

  tailor: (jobId: string, candidate_name: string, contact_line: string) =>
    http.post<TailorResponse>(
      `/apply/${jobId}/tailor`,
      null,
      { params: { candidate_name, contact_line } }
    ).then((r) => r.data),

  coverLetter: (jobId: string) =>
    http.post(`/apply/${jobId}/cover-letter`).then((r) => r.data),

  markApplied: (jobId: string) =>
    http.post(`/apply/${jobId}/mark-applied`).then((r) => r.data),

  downloadUrl: (path: string) =>
    `${BASE}/apply/download?path=${encodeURIComponent(path)}`,

  tracker: () => http.get<TrackedJob[]>("/tracker/").then((r) => r.data),

  updateTracked: (id: number, body: { status?: string; notes?: string }) =>
    http.patch<TrackedJob>(`/tracker/${id}`, body).then((r) => r.data),

  deleteTracked: (id: number) =>
    http.delete(`/tracker/${id}`).then((r) => r.data),
};
