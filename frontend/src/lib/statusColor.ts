import type { ApplicationStatus } from "./types";

export const STATUS_LABELS: Record<ApplicationStatus, string> = {
  saved: "Saved",
  applied: "Applied",
  interviewing: "Interviewing",
  offer: "Offer",
  rejected: "Rejected",
};

// Tailwind can't resolve dynamically-built class names, so each variant is
// spelled out in full rather than templated from the status string.
export const STATUS_DOT_CLASS: Record<ApplicationStatus, string> = {
  saved: "bg-stage-saved",
  applied: "bg-stage-applied",
  interviewing: "bg-stage-interviewing",
  offer: "bg-stage-offer",
  rejected: "bg-stage-rejected",
};

// For inline styles (e.g. border-left-color) where a Tailwind utility class
// would risk losing to another border-color utility on the same element
// depending on generated stylesheet order.
export const STATUS_ACCENT_VAR: Record<ApplicationStatus, string> = {
  saved: "var(--stage-saved)",
  applied: "var(--stage-applied)",
  interviewing: "var(--stage-interviewing)",
  offer: "var(--stage-offer)",
  rejected: "var(--stage-rejected)",
};
