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
