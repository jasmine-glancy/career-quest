export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

// No auth layer yet (see docs/RUNBOOK.md) — every page acts as this dev user.
export const DEV_USER_ID = 1;
