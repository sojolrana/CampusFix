
import { Suspense } from "react";
import { requireRole } from "@/lib/server-auth";
import { AdminDashboard } from "@/components/admin-dashboard";

/** Render the admin dashboard after verifying the user's role. */
async function AdminDashboardContent() {
  const user = await requireRole(["admin"]);

  return (
    <AdminDashboard
      user={{
        full_name: user.full_name,
        email: user.email,
      }}
    />
  );
}

/** Render the admin dashboard with a request-time loading fallback. */
export default function AdminDashboardPage() {
  return (
    <Suspense
      fallback={
        <main className="p-8 text-sm text-slate-600">
          Loading admin dashboard...
        </main>
      }
    >
      <AdminDashboardContent />
    </Suspense>
  );
}
