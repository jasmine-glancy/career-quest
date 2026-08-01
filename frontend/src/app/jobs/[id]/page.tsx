import { notFound } from "next/navigation";

import { getApplications, getJob, getLatestAnalysis, getResumeVersions, getResumes } from "@/lib/api";
import { DEV_USER_ID } from "@/lib/config";
import { JobFitAnalyzer } from "./JobFitAnalyzer";

function formatDate(value: string): string {
  return new Date(value).toLocaleDateString();
}

export default async function JobDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const jobId = Number(id);
  if (!Number.isInteger(jobId)) {
    notFound();
  }

  const job = await getJob(jobId);
  if (job === null) {
    notFound();
  }

  const [resumes, applications] = await Promise.all([
    getResumes(DEV_USER_ID),
    getApplications(DEV_USER_ID),
  ]);
  const versionsByResume = await Promise.all(resumes.map((resume) => getResumeVersions(resume.resume_id)));
  const resumeVersionOptions = resumes.flatMap((resume, index) =>
    versionsByResume[index].map((version) => ({
      resume_version_id: version.resume_version_id,
      label: `${resume.title} — ${formatDate(version.created_at)}`,
    })),
  );

  const existingApplication = applications.find((application) => application.job_id === jobId) ?? null;
  const initialAnalysis = existingApplication
    ? await getLatestAnalysis(existingApplication.application_id)
    : null;

  return (
    <div className="flex flex-col gap-4">
      <div>
        <h1 className="text-2xl font-semibold">{job.title}</h1>
        <p className="text-ink-secondary">
          {job.company_name}
          {job.location ? ` · ${job.location}` : ""}
        </p>
      </div>

      {job.description && (
        <p className="whitespace-pre-wrap rounded-lg border border-border bg-surface p-4 text-sm text-ink-secondary">
          {job.description}
        </p>
      )}

      <JobFitAnalyzer
        jobId={job.job_id}
        userId={DEV_USER_ID}
        resumeVersionOptions={resumeVersionOptions}
        initialResumeVersionId={existingApplication?.resume_version_id ?? null}
        initialAnalysis={initialAnalysis}
      />
    </div>
  );
}
