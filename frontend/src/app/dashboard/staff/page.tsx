
import { Suspense } from "react";
import { requireRole } from "@/lib/server-auth";
import { SignOutButton } from "@/components/sign-out-button";

/** Render the staff dashboard after verifying the user's session and role. */
async function StaffDashboardContent() {
  const user = await requireRole(["staff"]);

  return (
    <main className="min-h-screen bg-slate-50 p-6 sm:p-10">
      <div className="mx-auto max-w-5xl">
        <header className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <p className="font-semibold text-blue-700">CampusFix</p>
            <h1 className="mt-3 text-3xl font-bold text-slate-900">
              Staff dashboard
            </h1>
          </div>

          <SignOutButton />
        </header>

        <section className="mt-8 rounded-2xl border border-slate-200 bg-white p-6">
          <h2 className="text-xl font-semibold text-slate-900">
            Welcome, {user.full_name}
          </h2>

          <p className="mt-2 text-slate-600">
            Manage assigned campus issues and track their progress.
          </p>

          <p className="mt-4 text-sm text-slate-500">
            {user.email}
          </p>
        </section>

        <section className="mt-6 rounded-xl border border-dashed border-slate-300 bg-white p-6">
          <h2 className="font-semibold text-slate-900">
            Coming next
          </h2>

          <p className="mt-2 text-sm text-slate-600">
            Your assigned issue queue, issue details, comments, and
            status update controls will be added in Milestone 10.
          </p>
        </section>
      </div>
    </main>
  );
}

/** Provide a fallback while the staff session is being verified. */
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
