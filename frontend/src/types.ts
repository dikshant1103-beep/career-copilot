export interface JobPosting {
  id: string;
  title: string;
  company: string;
  location: string;
  remote: boolean;
  url: string;
  description: string;
  source: string;
  posted_at?: string | null;
  salary?: string | null;
}

export interface SearchResponse {
  jobs: JobPosting[];
  source_counts: Record<string, number>;
  errors: string[];
}

export interface RankedJob {
  job: JobPosting;
  overall_score: number;
  skill_overlap_score: number;
  verdict: string;
  one_line_reason: string;
}

export interface RankResponse {
  rankings: RankedJob[];
  top_pick_id?: string | null;
  summary: string;
}

export interface JDAnalysis {
  job_title: string;
  company: string;
  seniority: string;
  required_skills: string[];
  preferred_skills: string[];
  responsibilities: string[];
  ats_keywords: string[];
  candidate_matched_skills: string[];
  candidate_missing_skills: string[];
  strengths: string[];
  weaknesses: string[];
  compatibility_score: number;
  ats_score: number;
  improvement_suggestions: string[];
  summary: string;
  local_cosine_match: number;
}

export interface TailoredBullet {
  section: string;
  title: string;
  rewritten_bullet: string;
}

export interface TailorResponse {
  summary: string;
  headline: string;
  core_skills: string[];
  bullets: TailoredBullet[];
  missing_tech_to_learn: string[];
  ats_keywords_embedded: string[];
  cover_letter_hook: string;
  pdf_path: string;
  json_path: string;
}

export interface TrackedJob {
  id: number;
  title: string;
  company: string;
  status: string;
  score?: number | null;
  ats_score?: number | null;
  keywords: string[];
  missing_skills: string[];
  notes: string;
  created_at: string;
  updated_at: string;
}

export interface AppStatus {
  api_key_set: boolean;
  claude_model: string;
  embedding_model: string;
  chunks_stored: number;
  sources_available: Record<string, boolean>;
  career_ai_path: string;
}

declare global {
  interface Window {
    copilot?: {
      openExternal: (url: string) => Promise<void>;
      version: () => string;
    };
  }
}
