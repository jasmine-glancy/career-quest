import { API_BASE_URL } from "./config";
import type { ApplicationListItem, ApplicationStatus, Resume, ResumeVersion } from "./types";

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
