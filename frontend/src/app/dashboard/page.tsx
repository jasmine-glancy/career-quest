import Link from "next/link";

import { getDashboard } from "@/lib/api";
import { DEV_USER_ID } from "@/lib/config";

export default async function DashboardPage() {
  const dashboard = await getDashboard(DEV_USER_ID);

  return (
    <div className="flex flex-col gap-4">
      <h1 className="text-2xl font-semibold">Dashboard</h1>

      {dashboard.total_analyzed === 0 ? (
        <p className="text-ink-secondary">
          No insights yet.{" "}
          <Link href="/applications" className="text-accent hover:underline">
            Analyze a job&apos;s fit
          </Link>{" "}
          against one of your resumes to see insights here.
        </p>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2">
          <div className="rounded-lg border border-border bg-surface p-4">
            <h2 className="text-sm font-medium text-ink-secondary">Strongest skill area</h2>
            {dashboard.strongest_skill ? (
              <p className="mt-1 text-lg font-semibold">
                {dashboard.strongest_skill.skill}{" "}
                <span className="text-sm font-normal text-ink-muted">
                  ({dashboard.strongest_skill.count}/{dashboard.strongest_skill.total_analyzed} roles
                  matched)
                </span>
              </p>
            ) : (
              <p className="mt-1 text-sm text-ink-muted">No matched skills yet.</p>
            )}
          </div>

          <div className="rounded-lg border border-border bg-surface p-4">
            <h2 className="text-sm font-medium text-ink-secondary">Biggest gap</h2>
            {dashboard.biggest_gap ? (
              <p className="mt-1 text-lg font-semibold">
                {dashboard.biggest_gap.skill}{" "}
                <span className="text-sm font-normal text-ink-muted">
                  (missing from {dashboard.biggest_gap.count}/{dashboard.biggest_gap.total_analyzed}{" "}
                  roles)
                </span>
              </p>
            ) : (
              <p className="mt-1 text-sm text-ink-muted">No skill gaps identified yet.</p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
