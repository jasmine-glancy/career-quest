import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { getApplications, getResumeVersions, getResumes, updateApplicationStatus } from "./api";

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
});
