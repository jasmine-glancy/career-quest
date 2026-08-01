import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import {
  analyzeFit,
  getApplications,
  getDashboard,
  getJob,
  getLatestAnalysis,
  getResumeVersions,
  getResumes,
  optimizeResume,
  updateApplicationStatus,
} from "./api";

function mockFetchOnce(response: Partial<Response> & { json?: () => Promise<unknown> }) {
  const fetchMock = vi.fn().mockResolvedValue(response as Response);
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}

describe("api client", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn());
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("getApplications requests the right URL and returns parsed JSON", async () => {
    const payload = [{ application_id: 1 }];
    const fetchMock = mockFetchOnce({ ok: true, json: async () => payload });

    const result = await getApplications(1);

    expect(fetchMock).toHaveBeenCalledWith(
      "http://localhost:8000/applications?user_id=1",
      expect.objectContaining({ cache: "no-store" }),
    );
    expect(result).toEqual(payload);
  });

  it("getApplications throws with the status code on a non-ok response", async () => {
    mockFetchOnce({ ok: false, status: 500 });

    await expect(getApplications(1)).rejects.toThrow("Failed to load applications (500)");
  });

  it("getResumes requests the right URL", async () => {
    const fetchMock = mockFetchOnce({ ok: true, json: async () => [] });

    await getResumes(1);

    expect(fetchMock).toHaveBeenCalledWith(
      "http://localhost:8000/resumes?user_id=1",
      expect.objectContaining({ cache: "no-store" }),
    );
  });

  it("getResumeVersions requests the resume-scoped URL", async () => {
    const fetchMock = mockFetchOnce({ ok: true, json: async () => [] });

    await getResumeVersions(5);

    expect(fetchMock).toHaveBeenCalledWith(
      "http://localhost:8000/resumes/5/versions",
      expect.objectContaining({ cache: "no-store" }),
    );
  });

  it("updateApplicationStatus PATCHes with the new status in the body", async () => {
    const fetchMock = mockFetchOnce({
      ok: true,
      json: async () => ({ status: "applied", applied_at: "2026-01-01T00:00:00Z" }),
    });

    const result = await updateApplicationStatus(3, "applied");

    expect(fetchMock).toHaveBeenCalledWith(
      "http://localhost:8000/applications/3/status",
      expect.objectContaining({
        method: "PATCH",
        body: JSON.stringify({ status: "applied" }),
      }),
    );
    expect(result.status).toBe("applied");
  });

  it("updateApplicationStatus surfaces the backend's detail message on failure", async () => {
    mockFetchOnce({
      ok: false,
      status: 409,
      json: async () => ({ detail: "Cannot transition application from 'offer' to 'rejected'" }),
    });

    await expect(updateApplicationStatus(3, "rejected")).rejects.toThrow(
      "Cannot transition application from 'offer' to 'rejected'",
    );
  });

  it("updateApplicationStatus falls back to a generic message if the error body isn't JSON", async () => {
    mockFetchOnce({
      ok: false,
      status: 500,
      json: async () => {
        throw new Error("not json");
      },
    });

    await expect(updateApplicationStatus(3, "rejected")).rejects.toThrow(
      "Failed to update status (500)",
    );
  });

  it("getJob requests the job-scoped URL", async () => {
    const fetchMock = mockFetchOnce({ ok: true, json: async () => ({ job_id: 9 }) });

    await getJob(9);

    expect(fetchMock).toHaveBeenCalledWith(
      "http://localhost:8000/jobs/9",
      expect.objectContaining({ cache: "no-store" }),
    );
  });

  it("getJob returns null on a 404 instead of throwing", async () => {
    mockFetchOnce({ ok: false, status: 404 });

    await expect(getJob(9)).resolves.toBeNull();
  });

  it("getJob throws on a non-404 error", async () => {
    mockFetchOnce({ ok: false, status: 500 });

    await expect(getJob(9)).rejects.toThrow("Failed to load job (500)");
  });

  it("getLatestAnalysis returns null on a 404 instead of throwing", async () => {
    mockFetchOnce({ ok: false, status: 404 });

    await expect(getLatestAnalysis(4)).resolves.toBeNull();
  });

  it("getLatestAnalysis returns parsed JSON on success", async () => {
    const payload = { analysis_id: 1, application_id: 4, match_score: 70 };
    const fetchMock = mockFetchOnce({ ok: true, json: async () => payload });

    const result = await getLatestAnalysis(4);

    expect(fetchMock).toHaveBeenCalledWith(
      "http://localhost:8000/applications/4/analysis",
      expect.objectContaining({ cache: "no-store" }),
    );
    expect(result).toEqual(payload);
  });

  it("getLatestAnalysis throws on a non-404 error", async () => {
    mockFetchOnce({ ok: false, status: 500 });

    await expect(getLatestAnalysis(4)).rejects.toThrow("Failed to load analysis (500)");
  });

  it("getDashboard requests the user-scoped URL", async () => {
    const payload = { total_analyzed: 0, strongest_skill: null, biggest_gap: null };
    const fetchMock = mockFetchOnce({ ok: true, json: async () => payload });

    const result = await getDashboard(1);

    expect(fetchMock).toHaveBeenCalledWith(
      "http://localhost:8000/dashboard?user_id=1",
      expect.objectContaining({ cache: "no-store" }),
    );
    expect(result).toEqual(payload);
  });

  it("getDashboard throws with the status code on a non-ok response", async () => {
    mockFetchOnce({ ok: false, status: 500 });

    await expect(getDashboard(1)).rejects.toThrow("Failed to load dashboard (500)");
  });

  it("analyzeFit POSTs the user/job/resume-version ids", async () => {
    const payload = { analysis_id: 1, match_score: 80 };
    const fetchMock = mockFetchOnce({ ok: true, json: async () => payload });

    const result = await analyzeFit(3, 7, 1);

    expect(fetchMock).toHaveBeenCalledWith(
      "http://localhost:8000/ai/analyze-fit",
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({ user_id: 3, job_id: 7, resume_version_id: 1 }),
      }),
    );
    expect(result).toEqual(payload);
  });

  it("analyzeFit surfaces the backend's detail message on failure", async () => {
    mockFetchOnce({
      ok: false,
      status: 400,
      json: async () => ({ detail: "Resume version 1 does not belong to user 3" }),
    });

    await expect(analyzeFit(3, 7, 1)).rejects.toThrow(
      "Resume version 1 does not belong to user 3",
    );
  });

  it("optimizeResume POSTs the user/resume-version/job ids", async () => {
    const payload = { summary: "ok", suggested_edits: [], missing_keywords: [] };
    const fetchMock = mockFetchOnce({ ok: true, json: async () => payload });

    const result = await optimizeResume(3, 2, 10);

    expect(fetchMock).toHaveBeenCalledWith(
      "http://localhost:8000/ai/optimize-resume",
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({ user_id: 3, resume_version_id: 2, job_id: 10 }),
      }),
    );
    expect(result).toEqual(payload);
  });

  it("optimizeResume surfaces the backend's detail message on failure", async () => {
    mockFetchOnce({
      ok: false,
      status: 404,
      json: async () => ({ detail: "Job 10 not found" }),
    });

    await expect(optimizeResume(3, 2, 10)).rejects.toThrow("Job 10 not found");
  });
});
