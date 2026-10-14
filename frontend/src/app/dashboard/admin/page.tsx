
import { Suspense } from "react";
import { requireRole } from "@/lib/server-auth";
import { SignOutButton } from "@/components/sign-out-button";

/** Render the admin dashboard after verifying the user's session and role. */
async function AdminDashboardContent() {
  const user = await requireRole(["admin"]);

  return (
    <main className="min-h-screen bg-slate-50 p-6 sm:p-10">
      <div className="mx-auto max-w-5xl">
        <header className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <p className="font-semibold text-blue-700">CampusFix</p>
            <h1 className="mt-3 text-3xl font-bold text-slate-900">
              Admin dashboard
            </h1>
          </div>

          <SignOutButton />
        </header>

        <section className="mt-8 rounded-2xl border border-slate-200 bg-white p-6">
          <h2 className="text-xl font-semibold text-slate-900">
            Welcome, {user.full_name}
          </h2>

          <p className="mt-2 text-slate-600">
            Oversee campus issue resolution and administrative activities.
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
            User management, issue assignment, and system-wide
            analytics will be integrated in Milestone 11.
          </p>
        </section>
      </div>
    </main>
  );
}

/** Provide a fallback while the admin session is being verified. */
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
