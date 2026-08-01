"use client";

import { useState } from "react";
import {
  DndContext,
  type DragEndEvent,
  KeyboardSensor,
  PointerSensor,
  useDraggable,
  useDroppable,
  useSensor,
  useSensors,
} from "@dnd-kit/core";

import { updateApplicationStatus } from "@/lib/api";
import { STATUS_ACCENT_VAR, STATUS_DOT_CLASS, STATUS_LABELS } from "@/lib/statusColor";
import type { ApplicationListItem, ApplicationStatus } from "@/lib/types";

const COLUMNS: ApplicationStatus[] = ["saved", "applied", "interviewing", "offer", "rejected"];

function isTerminal(status: ApplicationStatus): boolean {
  return status === "offer" || status === "rejected";
}

function Card({ application }: { application: ApplicationListItem }) {
  const { attributes, listeners, setNodeRef, transform, isDragging } = useDraggable({
    id: String(application.application_id),
    disabled: isTerminal(application.status),
  });

  const dragTransform = transform
    ? `translate3d(${transform.x}px, ${transform.y}px, 0)`
    : undefined;
  const dragClass = isDragging ? "opacity-50" : "";
  const cursorClass = isTerminal(application.status) ? "cursor-default" : "cursor-grab";

  // Offer is a solid celebratory fill; every other stage (including
  // Rejected) is a quiet left-border card, so a run of rejections doesn't
  // read as a wall of alarm blocks.
  if (application.status === "offer") {
    return (
      <div
        ref={setNodeRef}
        style={{ transform: dragTransform }}
        {...listeners}
        {...attributes}
        className={`rounded-md bg-stage-offer p-3 text-sm text-white shadow-sm ${dragClass} ${cursorClass}`}
      >
        <p className="font-medium">
          <span className="mr-1">✓</span>
          {application.job_title}
        </p>
        <p className="text-white/80">{application.company_name}</p>
      </div>
    );
  }

  return (
    <div
      ref={setNodeRef}
      style={{
        transform: dragTransform,
        borderLeftWidth: "3px",
        borderLeftColor: STATUS_ACCENT_VAR[application.status],
      }}
      {...listeners}
      {...attributes}
      className={`rounded-md border border-border bg-card p-3 text-sm shadow-sm ${dragClass} ${cursorClass}`}
    >
      <p className="font-medium">
        {application.status === "rejected" && (
          <span className="mr-1 font-bold text-stage-rejected">✕</span>
        )}
        {application.job_title}
      </p>
      <p className="text-ink-muted">{application.company_name}</p>
    </div>
  );
}

function Column({
  status,
  applications,
}: {
  status: ApplicationStatus;
  applications: ApplicationListItem[];
}) {
  const { setNodeRef, isOver } = useDroppable({ id: status });

  return (
    <div
      ref={setNodeRef}
      className={`flex min-h-[200px] flex-col gap-2 rounded-lg border border-border p-3 ${
        isOver ? "bg-surface" : ""
      }`}
    >
      <h2 className="flex items-center gap-2 text-sm font-semibold text-ink-secondary">
        <span className={`h-2 w-2 rounded-full ${STATUS_DOT_CLASS[status]}`} />
        {STATUS_LABELS[status]} ({applications.length})
      </h2>
      {applications.map((application) => (
        <Card key={application.application_id} application={application} />
      ))}
    </div>
  );
}

export function KanbanBoard({
  initialApplications,
}: {
  initialApplications: ApplicationListItem[];
}) {
  const [applications, setApplications] = useState(initialApplications);
  const [error, setError] = useState<string | null>(null);
  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 5 } }),
    useSensor(KeyboardSensor),
  );

  async function handleDragEnd(event: DragEndEvent) {
    const { active, over } = event;
    if (!over) return;

    const applicationId = Number(active.id);
    const newStatus = over.id as ApplicationStatus;
    const current = applications.find((a) => a.application_id === applicationId);
    if (!current || current.status === newStatus) return;

    const previousStatus = current.status;
    setError(null);
    setApplications((prev) =>
      prev.map((a) =>
        a.application_id === applicationId ? { ...a, status: newStatus } : a,
      ),
    );

    try {
      const updated = await updateApplicationStatus(applicationId, newStatus);
      setApplications((prev) =>
        prev.map((a) =>
          a.application_id === applicationId
            ? { ...a, status: updated.status, applied_at: updated.applied_at }
            : a,
        ),
      );
    } catch (err) {
      setApplications((prev) =>
        prev.map((a) =>
          a.application_id === applicationId ? { ...a, status: previousStatus } : a,
        ),
      );
      setError(err instanceof Error ? err.message : "Failed to update status");
    }
  }

  return (
    <div className="flex flex-col gap-3">
      {error && (
        <p className="rounded-md border border-error-border bg-error-bg px-3 py-2 text-sm text-error-text">
          {error}
        </p>
      )}
      <DndContext sensors={sensors} onDragEnd={handleDragEnd}>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-5">
          {COLUMNS.map((status) => (
            <Column
              key={status}
              status={status}
              applications={applications.filter((a) => a.status === status)}
            />
          ))}
        </div>
      </DndContext>
    </div>
  );
}
