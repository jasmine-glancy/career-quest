"use client";

import { useState } from "react";

import { optimizeResume } from "@/lib/api";
import type { OptimizeResumeResult } from "@/lib/types";

interface VersionOption {
  resume_version_id: number;
  label: string;
}

interface JobOption {
  job_id: number;
  label: string;
}

export function ResumeOptimizer({
  userId,
  versionOptions,
  jobOptions,
}: {
  userId: number;
  versionOptions: VersionOption[];
  jobOptions: JobOption[];
}) {
  const [selectedVersionId, setSelectedVersionId] = useState<number | null>(
    versionOptions[versionOptions.length - 1]?.resume_version_id ?? null,
  );
  const [selectedJobId, setSelectedJobId] = useState<number | null>(jobOptions[0]?.job_id ?? null);
  const [result, setResult] = useState<OptimizeResumeResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleOptimize() {
    if (selectedVersionId === null || selectedJobId === null) return;
    setLoading(true);
    setError(null);
    try {
      const response = await optimizeResume(userId, selectedVersionId, selectedJobId);
      setResult(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to optimize resume");
    } finally {
      setLoading(false);
    }
  }

  if (versionOptions.length === 0) {
    return <p className="text-sm text-ink-secondary">This resume has no versions yet.</p>;
  }

  if (jobOptions.length === 0) {
    return (
      <p className="text-sm text-ink-secondary">
        Track a job from its detail page first, then come back here to optimize this resume for it.
      </p>
    );
  }

  return (
    <div className="flex flex-col gap-4 rounded-lg border border-border bg-surface p-4">
      <div className="flex flex-wrap items-center gap-3">
        <label className="text-sm text-ink-secondary" htmlFor="resume-optimize-version-select">
          Version
        </label>
        <select
          id="resume-optimize-version-select"
          className="rounded-md border border-border bg-card px-2 py-1 text-sm"
          value={selectedVersionId ?? ""}
          onChange={(event) => setSelectedVersionId(Number(event.target.value))}
        >
          {versionOptions.map((option) => (
            <option key={option.resume_version_id} value={option.resume_version_id}>
              {option.label}
            </option>
          ))}
        </select>

        <label className="text-sm text-ink-secondary" htmlFor="resume-optimize-job-select">
          Job
        </label>
        <select
          id="resume-optimize-job-select"
          className="rounded-md border border-border bg-card px-2 py-1 text-sm"
          value={selectedJobId ?? ""}
          onChange={(event) => setSelectedJobId(Number(event.target.value))}
        >
          {jobOptions.map((option) => (
            <option key={option.job_id} value={option.job_id}>
              {option.label}
            </option>
          ))}
        </select>

        <button
          type="button"
          onClick={handleOptimize}
          disabled={loading || selectedVersionId === null || selectedJobId === null}
          className="rounded-md bg-accent-solid px-3 py-1.5 text-sm font-medium text-white disabled:opacity-50"
        >
          {loading ? "Optimizing…" : "Optimize for this job"}
        </button>
      </div>

      {error && (
        <p className="rounded-md border border-error-border bg-error-bg px-3 py-2 text-sm text-error-text">
          {error}
        </p>
      )}

      {result && (
        <div className="flex flex-col gap-3 border-t border-border pt-4">
          <p className="text-sm text-ink-secondary">{result.summary}</p>

          <div>
            <h3 className="text-sm font-medium text-ink-secondary">Suggested edits</h3>
            <ul className="mt-1 flex flex-col gap-2 text-sm">
              {result.suggested_edits.map((edit, index) => (
                <li key={index} className="rounded-md border border-border bg-card p-2">
                  <span className="font-medium">{edit.section}: </span>
                  {edit.suggestion}
                </li>
              ))}
            </ul>
          </div>

          {result.missing_keywords.length > 0 && (
            <div>
              <h3 className="text-sm font-medium text-ink-secondary">Missing keywords</h3>
              <div className="mt-1 flex flex-wrap gap-2">
                {result.missing_keywords.map((keyword) => (
                  <span
                    key={keyword}
                    className="rounded-full border border-border bg-card px-2 py-0.5 text-xs"
                  >
                    {keyword}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
