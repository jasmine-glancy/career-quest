import { act } from "react";
import { render, screen, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import type { ApplicationListItem } from "@/lib/types";

const { capturedOnDragEnd, useDraggableMock } = vi.hoisted(() => ({
  capturedOnDragEnd: { current: null as ((event: unknown) => void | Promise<void>) | null },
  // eslint-disable-next-line @typescript-eslint/no-unused-vars -- typed for call-shape checking below, body doesn't need it
  useDraggableMock: vi.fn((_args: { id: string; disabled?: boolean }) => ({
    attributes: {},
    listeners: {},
    setNodeRef: () => {},
    transform: null,
    isDragging: false,
  })),
}));

vi.mock("@dnd-kit/core", async () => {
  const actual = await vi.importActual<typeof import("@dnd-kit/core")>("@dnd-kit/core");
  return {
    ...actual,
    // Real DndContext requires a browser drag gesture to ever call
    // onDragEnd. Capturing it lets the test invoke the board's actual
    // handler directly, exercising the real optimistic-update/revert logic
    // without simulating pointer events dnd-kit needs real layout for.
    DndContext: ({
      children,
      onDragEnd,
    }: {
      children: React.ReactNode;
      onDragEnd: (event: unknown) => void | Promise<void>;
    }) => {
      capturedOnDragEnd.current = onDragEnd;
      return children;
    },
    useDraggable: useDraggableMock,
    useDroppable: () => ({ setNodeRef: () => {}, isOver: false }),
  };
});

vi.mock("@/lib/api", () => ({
  updateApplicationStatus: vi.fn(),
}));

import { updateApplicationStatus } from "@/lib/api";
import { KanbanBoard } from "./KanbanBoard";

const updateApplicationStatusMock = vi.mocked(updateApplicationStatus);

function application(overrides: Partial<ApplicationListItem>): ApplicationListItem {
  return {
    application_id: 1,
    job_id: 1,
    job_title: "Backend Engineer",
    company_name: "Acme Corp",
    resume_version_id: null,
    status: "saved",
    applied_at: null,
    created_at: "2026-01-01T00:00:00Z",
    ...overrides,
  };
}

async function dragEnd(activeId: number, overId: string) {
  await act(async () => {
    await capturedOnDragEnd.current?.({ active: { id: String(activeId) }, over: { id: overId } });
  });
}

describe("KanbanBoard", () => {
  beforeEach(() => {
    capturedOnDragEnd.current = null;
    updateApplicationStatusMock.mockReset();
    useDraggableMock.mockClear();
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it("groups cards into their status column", () => {
    render(
      <KanbanBoard
        initialApplications={[
          application({ application_id: 1, job_title: "Backend Engineer", status: "saved" }),
          application({ application_id: 2, job_title: "Frontend Engineer", status: "offer" }),
        ]}
      />,
    );

    expect(within(screen.getByText("Saved (1)").closest("div")!).getByText("Backend Engineer")).toBeInTheDocument();
    expect(within(screen.getByText("Offer (1)").closest("div")!).getByText("Frontend Engineer")).toBeInTheDocument();
  });

  it("marks offer and rejected cards as non-draggable", () => {
    render(
      <KanbanBoard
        initialApplications={[
          application({ application_id: 1, status: "saved" }),
          application({ application_id: 2, status: "offer" }),
          application({ application_id: 3, status: "rejected" }),
        ]}
      />,
    );

    const callFor = (id: number) =>
      useDraggableMock.mock.calls.find((call) => call[0].id === String(id))?.[0];

    expect(callFor(1)?.disabled).toBe(false);
    expect(callFor(2)?.disabled).toBe(true);
    expect(callFor(3)?.disabled).toBe(true);
  });

  it("optimistically moves a card and confirms it on a successful drop", async () => {
    updateApplicationStatusMock.mockResolvedValue({ status: "applied", applied_at: "2026-01-02T00:00:00Z" });
    render(
      <KanbanBoard
        initialApplications={[application({ application_id: 1, status: "saved" })]}
      />,
    );

    await dragEnd(1, "applied");

    expect(updateApplicationStatusMock).toHaveBeenCalledWith(1, "applied");
    expect(screen.getByText("Applied (1)")).toBeInTheDocument();
    expect(screen.getByText("Saved (0)")).toBeInTheDocument();
  });

  it("reverts the card and shows an error when the backend rejects the transition", async () => {
    updateApplicationStatusMock.mockRejectedValue(
      new Error("Cannot transition application from 'saved' to 'offer'"),
    );
    render(
      <KanbanBoard
        initialApplications={[application({ application_id: 1, status: "saved" })]}
      />,
    );

    await dragEnd(1, "offer");

    expect(screen.getByText("Cannot transition application from 'saved' to 'offer'")).toBeInTheDocument();
    expect(screen.getByText("Saved (1)")).toBeInTheDocument();
    expect(screen.getByText("Offer (0)")).toBeInTheDocument();
  });

  it("does nothing when a card is dropped back on its own column", async () => {
    render(
      <KanbanBoard
        initialApplications={[application({ application_id: 1, status: "saved" })]}
      />,
    );

    await dragEnd(1, "saved");

    expect(updateApplicationStatusMock).not.toHaveBeenCalled();
  });

  it("clears a previous error on the next drag attempt", async () => {
    updateApplicationStatusMock.mockRejectedValueOnce(new Error("first failure"));
    render(
      <KanbanBoard
        initialApplications={[
          application({ application_id: 1, status: "saved" }),
          application({ application_id: 2, status: "saved" }),
        ]}
      />,
    );

    await dragEnd(1, "offer");
    expect(screen.getByText("first failure")).toBeInTheDocument();

    updateApplicationStatusMock.mockResolvedValueOnce({ status: "applied", applied_at: null });
    await dragEnd(2, "applied");

    expect(screen.queryByText("first failure")).not.toBeInTheDocument();
  });
});
