
import { Suspense } from "react";
import { requireRole } from "@/lib/server-auth";
import { StudentIssueDetail } from "@/components/student-issue-detail";

type PageProps = {
  params: Promise<{
    issueId: string;
  }>;
};

/** Verify the student's role before rendering issue details. */
async function StudentIssueDetailContent({ params }: PageProps) {
  await requireRole(["student"]);

  const { issueId } = await params;

  return <StudentIssueDetail issueId={issueId} />;
}

/** Render issue details with a fallback during session verification. */
export default function StudentIssueDetailPage(props: PageProps) {
  return (
    <Suspense
      fallback={
        <main className="p-8 text-sm text-slate-600">
          Loading issue...
        </main>
      }
    >
      <StudentIssueDetailContent params={props.params} />
    </Suspense>
  );
}
