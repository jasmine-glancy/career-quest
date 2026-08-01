import { describe, expect, it } from "vitest";

import { STATUS_ACCENT_VAR, STATUS_DOT_CLASS, STATUS_LABELS } from "./statusColor";
import type { ApplicationStatus } from "./types";

const ALL_STATUSES: ApplicationStatus[] = [
  "saved",
  "applied",
  "interviewing",
  "offer",
  "rejected",
];

describe("statusColor", () => {
  it("has a label for every status", () => {
    for (const status of ALL_STATUSES) {
      expect(STATUS_LABELS[status]).toBeTruthy();
    }
  });

  it("has a dot class for every status", () => {
    for (const status of ALL_STATUSES) {
      expect(STATUS_DOT_CLASS[status]).toMatch(/^bg-stage-/);
    }
  });

  it("has a CSS variable reference for every status", () => {
    for (const status of ALL_STATUSES) {
      expect(STATUS_ACCENT_VAR[status]).toMatch(/^var\(--stage-/);
    }
  });

  it("labels read as capitalized English, not the raw enum value", () => {
    expect(STATUS_LABELS.interviewing).toBe("Interviewing");
    expect(STATUS_LABELS.saved).not.toBe("saved");
  });
});
