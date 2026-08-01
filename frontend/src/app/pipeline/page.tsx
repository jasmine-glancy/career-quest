import { getApplications } from "@/lib/api";
import { DEV_USER_ID } from "@/lib/config";
import { KanbanBoardClientOnly } from "./KanbanBoardLoader";

export default async function PipelinePage() {
  const applications = await getApplications(DEV_USER_ID);

  return (
    <div className="flex flex-col gap-4">
      <h1 className="text-2xl font-semibold">Pipeline</h1>
      <p className="text-sm text-ink-secondary">
        Drag a card to move it forward, or reject it. Offer and Rejected are
        final — cards there can&apos;t be moved again.
      </p>
      <KanbanBoardClientOnly initialApplications={applications} />
    </div>
  );
}
