import { getResumes, getResumeVersions } from "@/lib/api";
import { DEV_USER_ID } from "@/lib/config";

function formatDate(value: string): string {
  return new Date(value).toLocaleDateString();
}

export default async function ResumesPage() {
  const resumes = await getResumes(DEV_USER_ID);
  const versionsByResume = await Promise.all(
    resumes.map((resume) => getResumeVersions(resume.resume_id)),
  );

  return (
    <div className="flex flex-col gap-4">
      <h1 className="text-2xl font-semibold">Resumes</h1>

      {resumes.length === 0 ? (
        <p className="text-ink-secondary">No resumes yet.</p>
      ) : (
        <ul className="flex flex-col gap-4">
          {resumes.map((resume, index) => {
            const versions = versionsByResume[index];
            return (
              <li key={resume.resume_id} className="rounded-lg border border-border bg-surface p-4">
                <div className="flex items-baseline justify-between">
                  <h2 className="font-medium">{resume.title}</h2>
                  <span className="text-sm text-ink-muted">
                    {versions.length} version{versions.length === 1 ? "" : "s"}
                  </span>
                </div>
                <p className="mt-1 text-sm text-ink-muted">
                  Created {formatDate(resume.created_at)}
                </p>
                {versions.length > 0 && (
                  <ul className="mt-3 flex flex-col gap-1 border-t border-border pt-3 text-sm text-ink-secondary">
                    {versions.map((version) => (
                      <li key={version.resume_version_id}>
                        Version from {formatDate(version.created_at)}
                      </li>
                    ))}
                  </ul>
                )}
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
