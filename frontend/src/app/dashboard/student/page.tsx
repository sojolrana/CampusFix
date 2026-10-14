
import { Suspense } from "react";
import { requireRole } from "@/lib/server-auth";
import { StudentDashboard } from "@/components/student-dashboard";

/** Render the student dashboard after checking the user's session and role. */
async function StudentDashboardContent() {
  const user = await requireRole(["student"]);

  return (
    <StudentDashboard
      user={{
        full_name: user.full_name,
        email: user.email,
      }}
    />
  );
}

/** Render the student dashboard with a request-time loading fallback. */
export default function StudentDashboardPage() {
  return (
    <Suspense
      fallback={
        <main className="p-8 text-sm text-slate-600">
          Loading student dashboard...
        </main>
      }
    >
      <StudentDashboardContent />
    </Suspense>
  );
}
