import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("@/lib/api", () => ({
  analyzeFit: vi.fn(),
}));

import { analyzeFit } from "@/lib/api";
import { JobFitAnalyzer } from "./JobFitAnalyzer";

const analyzeFitMock = vi.mocked(analyzeFit);

const resumeVersionOptions = [
  { resume_version_id: 1, label: "Resume A — 1/1/2026" },
  { resume_version_id: 2, label: "Resume B — 1/2/2026" },
];

describe("JobFitAnalyzer", () => {
  beforeEach(() => {
    analyzeFitMock.mockReset();
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it("shows a message when there are no resume versions to analyze against", () => {
    render(
      <JobFitAnalyzer
        jobId={1}
        userId={1}
        resumeVersionOptions={[]}
        initialResumeVersionId={null}
        initialAnalysis={null}
      />,
    );

    expect(screen.getByText(/create a resume/i)).toBeInTheDocument();
  });

  it("renders a pre-loaded analysis without calling analyzeFit", () => {
    render(
      <JobFitAnalyzer
        jobId={1}
        userId={1}
        resumeVersionOptions={resumeVersionOptions}
        initialResumeVersionId={1}
        initialAnalysis={{
          analysis_id: 1,
          application_id: 1,
          match_score: 80,
          strengths_json: ["Strong SQL"],
          gaps_json: ["No AWS"],
          recommendations_json: ["Add AWS"],
          matched_skills_json: ["SQL"],
          missing_skills_json: ["AWS"],
          created_at: "2026-01-01T00:00:00Z",
        }}
      />,
    );

    expect(screen.getByText("Match score: 80%")).toBeInTheDocument();
    expect(screen.getByText("Strong SQL")).toBeInTheDocument();
    expect(analyzeFitMock).not.toHaveBeenCalled();
  });

  it("clicking Analyze Fit calls analyzeFit with the selected resume version and renders the result", async () => {
    analyzeFitMock.mockResolvedValue({
      analysis_id: 2,
      application_id: 5,
      match_score: 65,
      strengths_json: ["Python"],
      gaps_json: ["Cloud"],
      recommendations_json: ["Learn AWS"],
      matched_skills_json: ["Python"],
      missing_skills_json: ["Cloud"],
      created_at: "2026-01-01T00:00:00Z",
    });
    const user = userEvent.setup();
    render(
      <JobFitAnalyzer
        jobId={7}
        userId={3}
        resumeVersionOptions={resumeVersionOptions}
        initialResumeVersionId={null}
        initialAnalysis={null}
      />,
    );

    await user.click(screen.getByRole("button", { name: "Analyze Fit" }));

    expect(analyzeFitMock).toHaveBeenCalledWith(3, 7, 1);
    expect(await screen.findByText("Match score: 65%")).toBeInTheDocument();
  });

  it("shows an error message when analyzeFit rejects", async () => {
    analyzeFitMock.mockRejectedValue(new Error("Resume version 1 does not belong to user 3"));
    const user = userEvent.setup();
    render(
      <JobFitAnalyzer
        jobId={7}
        userId={3}
        resumeVersionOptions={resumeVersionOptions}
        initialResumeVersionId={null}
        initialAnalysis={null}
      />,
    );

    await user.click(screen.getByRole("button", { name: "Analyze Fit" }));

    expect(await screen.findByText("Resume version 1 does not belong to user 3")).toBeInTheDocument();
  });
});
