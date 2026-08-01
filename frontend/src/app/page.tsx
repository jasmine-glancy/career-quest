import Link from "next/link";

const SECTIONS = [
  {
    href: "/applications",
    title: "Applications",
    description: "A table of every application you're tracking.",
  },
  {
    href: "/resumes",
    title: "Resumes",
    description: "Your saved resumes and their versions.",
  },
  {
    href: "/pipeline",
    title: "Pipeline",
    description: "A kanban board of your applications by status.",
  },
];

export default function Home() {
  return (
    <div className="flex flex-col gap-6">
      <h1 className="text-2xl font-semibold">Career Quest</h1>
      <div className="grid gap-4 sm:grid-cols-3">
        {SECTIONS.map((section) => (
          <Link
            key={section.href}
            href={section.href}
            className="rounded-lg border border-border bg-surface p-4 hover:border-accent"
          >
            <h2 className="font-medium">{section.title}</h2>
            <p className="mt-1 text-sm text-ink-secondary">{section.description}</p>
          </Link>
        ))}
      </div>
    </div>
  );
}
