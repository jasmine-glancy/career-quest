"use client";

import dynamic from "next/dynamic";

// @dnd-kit assigns its accessibility-description IDs from a module-level
// counter rather than React's SSR-safe useId(), so the count the server
// renders can drift from what the client computes (the dev server process
// keeps incrementing across requests; a fresh page load in the browser
// starts over) — a real hydration mismatch, not a false alarm. Loading the
// board client-only avoids ever rendering it on the server.
export const KanbanBoardClientOnly = dynamic(
  () => import("./KanbanBoard").then((mod) => mod.KanbanBoard),
  { ssr: false },
);
