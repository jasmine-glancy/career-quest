"use client";

import { useState } from "react";

import { analyzeFit } from "@/lib/api";
import type { AIAnalysis } from "@/lib/types";

interface ResumeVersionOption {
  resume_version_id: number;
  label: string;
}

export function JobFitAnalyzer({
  jobId,
  userId,
  resumeVersionOptions,
  initialResumeVersionId,
  initialAnalysis,
}: {
  jobId: number;
  userId: number;
  resumeVersionOptions: ResumeVersionOption[];
  initialResumeVersionId: number | null;
  initialAnalysis: AIAnalysis | null;
}) {
  const [selectedResumeVersionId, setSelectedResumeVersionId] = useState<number | null>(
    initialResumeVersionId ?? resumeVersionOptions[0]?.resume_version_id ?? null,
  );
  const [analysis, setAnalysis] = useState<AIAnalysis | null>(initialAnalysis);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleAnalyze() {
    if (selectedResumeVersionId === null) return;
    setLoading(true);
    setError(null);
    try {
      const result = await analyzeFit(userId, jobId, selectedResumeVersionId);
      setAnalysis(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to analyze fit");
    } finally {
      setLoading(false);
    }
  }

  if (resumeVersionOptions.length === 0) {
    return (
      <p className="text-sm text-ink-secondary">
        Create a resume before analyzing fit against this job.
      </p>
    );
  }

  return (
    <div className="flex flex-col gap-4 rounded-lg border border-border bg-surface p-4">
      <div className="flex flex-wrap items-center gap-3">
        <label className="text-sm text-ink-secondary" htmlFor="resume-version-select">
          Resume version
        </label>
        <select
          id="resume-version-select"
          className="rounded-md border border-border bg-card px-2 py-1 text-sm"
          value={selectedResumeVersionId ?? ""}
          onChange={(event) => setSelectedResumeVersionId(Number(event.target.value))}
        >
          {resumeVersionOptions.map((option) => (
            <option key={option.resume_version_id} value={option.resume_version_id}>
              {option.label}
            </option>
          ))}
        </select>
        <button
          type="button"
          onClick={handleAnalyze}
          disabled={loading || selectedResumeVersionId === null}
          className="rounded-md bg-accent-solid px-3 py-1.5 text-sm font-medium text-white disabled:opacity-50"
        >
          {loading ? "Analyzing…" : "Analyze Fit"}
        </button>
      </div>

      <p className="text-xs text-ink-muted">
        Analyzing sends this resume&apos;s content and the job description to OpenAI for
        processing. Don&apos;t analyze against a resume containing information you don&apos;t
        want shared with a third party.
      </p>

      {error && (
        <p className="rounded-md border border-error-border bg-error-bg px-3 py-2 text-sm text-error-text">
          {error}
        </p>
      )}

      {analysis && (
        <div className="flex flex-col gap-3 border-t border-border pt-4">
          <p className="text-lg font-semibold">Match score: {analysis.match_score}%</p>

          <div>
            <h3 className="text-sm font-medium text-ink-secondary">Strengths</h3>
            <ul className="mt-1 list-disc pl-5 text-sm">
              {analysis.strengths_json.map((strength, index) => (
                <li key={index}>{strength}</li>
              ))}
            </ul>
          </div>

          <div>
            <h3 className="text-sm font-medium text-ink-secondary">Gaps</h3>
            <ul className="mt-1 list-disc pl-5 text-sm">
              {analysis.gaps_json.map((gap, index) => (
                <li key={index}>{gap}</li>
              ))}
            </ul>
          </div>

          <div>
            <h3 className="text-sm font-medium text-ink-secondary">Recommendations</h3>
            <ul className="mt-1 list-disc pl-5 text-sm">
              {analysis.recommendations_json.map((recommendation, index) => (
                <li key={index}>{recommendation}</li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
}
