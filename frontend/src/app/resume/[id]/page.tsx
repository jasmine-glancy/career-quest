import { notFound } from "next/navigation";

import { getApplications, getResumeVersions, getResumes } from "@/lib/api";
import { DEV_USER_ID } from "@/lib/config";
import { ResumeOptimizer } from "./ResumeOptimizer";

function formatDate(value: string): string {
  return new Date(value).toLocaleDateString();
}

export default async function ResumeEditorPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const resumeId = Number(id);
  if (!Number.isInteger(resumeId)) {
    notFound();
  }

  const [resumes, applications] = await Promise.all([
    getResumes(DEV_USER_ID),
    getApplications(DEV_USER_ID),
  ]);
  const resume = resumes.find((r) => r.resume_id === resumeId) ?? null;
  if (resume === null) {
    notFound();
  }

  const versions = await getResumeVersions(resumeId);
  const versionOptions = versions.map((version) => ({
    resume_version_id: version.resume_version_id,
    label: `Version from ${formatDate(version.created_at)}`,
  }));

  const seenJobIds = new Set<number>();
  const jobOptions = applications
    .filter((application) => {
      if (seenJobIds.has(application.job_id)) return false;
      seenJobIds.add(application.job_id);
      return true;
    })
    .map((application) => ({
      job_id: application.job_id,
      label: `${application.job_title} — ${application.company_name}`,
    }));

  return (
    <div className="flex flex-col gap-4">
      <h1 className="text-2xl font-semibold">{resume.title}</h1>
      <p className="text-sm text-ink-muted">Created {formatDate(resume.created_at)}</p>

      <ResumeOptimizer userId={DEV_USER_ID} versionOptions={versionOptions} jobOptions={jobOptions} />
    </div>
  );
}
