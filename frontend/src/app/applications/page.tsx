import { getApplications } from "@/lib/api";
import { DEV_USER_ID } from "@/lib/config";
import { STATUS_DOT_CLASS, STATUS_LABELS } from "@/lib/statusColor";

function formatDate(value: string | null): string {
  if (!value) return "—";
  return new Date(value).toLocaleDateString();
}

export default async function ApplicationsPage() {
  const applications = await getApplications(DEV_USER_ID);

  return (
    <div className="flex flex-col gap-4">
      <h1 className="text-2xl font-semibold">Applications</h1>

      {applications.length === 0 ? (
        <p className="text-ink-secondary">
          No applications yet. Track a job to see it here.
        </p>
      ) : (
        <table className="w-full border-collapse text-left text-sm">
          <thead>
            <tr className="border-b border-border text-ink-muted">
              <th className="py-2 pr-4 font-medium">Job</th>
              <th className="py-2 pr-4 font-medium">Company</th>
              <th className="py-2 pr-4 font-medium">Status</th>
              <th className="py-2 pr-4 font-medium">Applied</th>
              <th className="py-2 pr-4 font-medium">Created</th>
            </tr>
          </thead>
          <tbody>
            {applications.map((application) => (
              <tr key={application.application_id} className="border-b border-border">
                <td className="py-2 pr-4">{application.job_title}</td>
                <td className="py-2 pr-4">{application.company_name}</td>
                <td className="py-2 pr-4">
                  <span className="inline-flex items-center gap-2">
                    <span
                      className={`h-2 w-2 rounded-full ${STATUS_DOT_CLASS[application.status]}`}
                    />
                    {STATUS_LABELS[application.status]}
                  </span>
                </td>
                <td className="py-2 pr-4">{formatDate(application.applied_at)}</td>
                <td className="py-2 pr-4">{formatDate(application.created_at)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
