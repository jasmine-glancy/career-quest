import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("@/lib/api", () => ({
  optimizeResume: vi.fn(),
}));

import { optimizeResume } from "@/lib/api";
import { ResumeOptimizer } from "./ResumeOptimizer";

const optimizeResumeMock = vi.mocked(optimizeResume);

const versionOptions = [
  { resume_version_id: 1, label: "Version from 1/1/2026" },
  { resume_version_id: 2, label: "Version from 1/2/2026" },
];

const jobOptions = [
  { job_id: 10, label: "Data Analyst — Acme Corp" },
  { job_id: 11, label: "BI Engineer — Other Co" },
];

describe("ResumeOptimizer", () => {
  beforeEach(() => {
    optimizeResumeMock.mockReset();
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it("shows a message when the resume has no versions", () => {
    render(<ResumeOptimizer userId={3} versionOptions={[]} jobOptions={jobOptions} />);

    expect(screen.getByText(/no versions yet/i)).toBeInTheDocument();
  });

  it("shows a message prompting to track a job when there are none", () => {
    render(<ResumeOptimizer userId={3} versionOptions={versionOptions} jobOptions={[]} />);

    expect(screen.getByText(/track a job from its detail page first/i)).toBeInTheDocument();
  });

  it("defaults to the latest version and clicking Optimize calls optimizeResume", async () => {
    optimizeResumeMock.mockResolvedValue({
      summary: "Good alignment overall.",
      suggested_edits: [{ section: "Experience", suggestion: "Add metrics to bullet 2." }],
      missing_keywords: ["dbt"],
    });
    const user = userEvent.setup();
    render(<ResumeOptimizer userId={3} versionOptions={versionOptions} jobOptions={jobOptions} />);

    await user.click(screen.getByRole("button", { name: "Optimize for this job" }));

    expect(optimizeResumeMock).toHaveBeenCalledWith(3, 2, 10);
    expect(await screen.findByText("Good alignment overall.")).toBeInTheDocument();
    expect(screen.getByText(/Add metrics to bullet 2\./)).toBeInTheDocument();
    expect(screen.getByText("dbt")).toBeInTheDocument();
  });

  it("shows an error message when optimizeResume rejects", async () => {
    optimizeResumeMock.mockRejectedValue(new Error("Job 10 not found"));
    const user = userEvent.setup();
    render(<ResumeOptimizer userId={3} versionOptions={versionOptions} jobOptions={jobOptions} />);

    await user.click(screen.getByRole("button", { name: "Optimize for this job" }));

    expect(await screen.findByText("Job 10 not found")).toBeInTheDocument();
  });
});
