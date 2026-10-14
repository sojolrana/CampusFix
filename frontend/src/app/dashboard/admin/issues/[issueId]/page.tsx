
import { Suspense } from "react";
import { requireRole } from "@/lib/server-auth";
import { StaffIssueDetail } from "@/components/staff-issue-detail";

type PageProps = {
  params: Promise<{
    issueId: string;
  }>;
};

/** Verify the administrator's role before showing issue details. */
async function AdminIssueDetailContent({ params }: PageProps) {
  await requireRole(["admin"]);

  const { issueId } = await params;

  return (
    <StaffIssueDetail
      issueId={issueId}
      backHref="/dashboard/admin"
      backLabel="Back to admin dashboard"
    />
  );
}

/** Render an issue with a fallback during authentication checks. */
export default function AdminIssueDetailPage(props: PageProps) {
  return (
    <Suspense
      fallback={
        <main className="p-8 text-sm text-slate-600">
          Loading issue...
        </main>
      }
    >
      <AdminIssueDetailContent params={props.params} />
    </Suspense>
  );
}
