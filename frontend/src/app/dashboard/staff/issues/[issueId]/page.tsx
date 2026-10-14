
import { Suspense } from "react";
import { requireRole } from "@/lib/server-auth";
import { StaffIssueDetail } from "@/components/staff-issue-detail";

type PageProps = {
  params: Promise<{
    issueId: string;
  }>;
};

/** Verify the staff role before rendering the selected issue. */
async function StaffIssueDetailContent({ params }: PageProps) {
  await requireRole(["staff"]);

  const { issueId } = await params;

  return <StaffIssueDetail issueId={issueId} />;
}

/** Render issue details with a fallback during authentication checks. */
export default function StaffIssueDetailPage(props: PageProps) {
  return (
    <Suspense
      fallback={
        <main className="p-8 text-sm text-slate-600">
          Loading assigned issue...
        </main>
      }
    >
      <StaffIssueDetailContent params={props.params} />
    </Suspense>
  );
}
