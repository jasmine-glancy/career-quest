import { API_BASE_URL } from "./config";
import type {
  AIAnalysis,
  ApplicationListItem,
  ApplicationStatus,
  Job,
  OptimizeResumeResult,
  Resume,
  ResumeVersion,
} from "./types";

export async function getApplications(userId: number): Promise<ApplicationListItem[]> {
  const res = await fetch(`${API_BASE_URL}/applications?user_id=${userId}`, {
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error(`Failed to load applications (${res.status})`);
  }
  return res.json();
}

export async function getResumes(userId: number): Promise<Resume[]> {
  const res = await fetch(`${API_BASE_URL}/resumes?user_id=${userId}`, {
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error(`Failed to load resumes (${res.status})`);
  }
  return res.json();
}

export async function getResumeVersions(resumeId: number): Promise<ResumeVersion[]> {
  const res = await fetch(`${API_BASE_URL}/resumes/${resumeId}/versions`, {
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error(`Failed to load resume versions (${res.status})`);
  }
  return res.json();
}

export async function getJob(jobId: number): Promise<Job> {
  const res = await fetch(`${API_BASE_URL}/jobs/${jobId}`, {
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error(`Failed to load job (${res.status})`);
  }
  return res.json();
}

export async function getLatestAnalysis(applicationId: number): Promise<AIAnalysis | null> {
  const res = await fetch(`${API_BASE_URL}/applications/${applicationId}/analysis`, {
    cache: "no-store",
  });
  if (res.status === 404) {
    return null;
  }
  if (!res.ok) {
    throw new Error(`Failed to load analysis (${res.status})`);
  }
  return res.json();
}

export async function analyzeFit(
  userId: number,
  jobId: number,
  resumeVersionId: number,
): Promise<AIAnalysis> {
  const res = await fetch(`${API_BASE_URL}/ai/analyze-fit`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_id: userId, job_id: jobId, resume_version_id: resumeVersionId }),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail ?? `Failed to analyze fit (${res.status})`);
  }
  return res.json();
}

export async function optimizeResume(
  userId: number,
  resumeVersionId: number,
  jobId: number,
): Promise<OptimizeResumeResult> {
  const res = await fetch(`${API_BASE_URL}/ai/optimize-resume`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_id: userId, resume_version_id: resumeVersionId, job_id: jobId }),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail ?? `Failed to optimize resume (${res.status})`);
  }
  return res.json();
}

export async function updateApplicationStatus(
  applicationId: number,
  status: ApplicationStatus,
): Promise<{ status: ApplicationStatus; applied_at: string | null }> {
  const res = await fetch(`${API_BASE_URL}/applications/${applicationId}/status`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ status }),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail ?? `Failed to update status (${res.status})`);
  }
  return res.json();
}
