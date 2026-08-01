export type ApplicationStatus =
  | "saved"
  | "applied"
  | "interviewing"
  | "offer"
  | "rejected";

export interface Resume {
  resume_id: number;
  user_id: number;
  title: string;
  created_at: string;
}

export interface ResumeVersion {
  resume_version_id: number;
  resume_id: number;
  snapshot_json: Record<string, unknown>;
  created_at: string;
}

export interface ApplicationListItem {
  application_id: number;
  job_id: number;
  job_title: string;
  company_name: string;
  resume_version_id: number | null;
  status: ApplicationStatus;
  applied_at: string | null;
  created_at: string;
}

export interface Job {
  job_id: number;
  company_id: number;
  company_name: string;
  title: string;
  description: string | null;
  url: string | null;
  location: string | null;
  created_at: string;
}

export interface AIAnalysis {
  analysis_id: number;
  application_id: number;
  match_score: number;
  strengths_json: string[];
  gaps_json: string[];
  recommendations_json: string[];
  created_at: string;
}

export interface ResumeEdit {
  section: string;
  suggestion: string;
}

export interface OptimizeResumeResult {
  summary: string;
  suggested_edits: ResumeEdit[];
  missing_keywords: string[];
}
