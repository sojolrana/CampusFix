
import { Suspense } from "react";
import { requireRole } from "@/lib/server-auth";
import { StaffDashboard } from "@/components/staff-dashboard";

/** Render the staff dashboard after verifying the authenticated user's role. */
async function StaffDashboardContent() {
  const user = await requireRole(["staff"]);

  return (
    <StaffDashboard
      user={{
        full_name: user.full_name,
        email: user.email,
      }}
    />
  );
}

/** Render the staff dashboard with a request-time loading fallback. */
export default function StaffDashboardPage() {
  return (
    <Suspense
      fallback={
        <main className="p-8 text-sm text-slate-600">
          Loading staff dashboard...
        </main>
      }
    >
      <StaffDashboardContent />
    </Suspense>
  );
}
