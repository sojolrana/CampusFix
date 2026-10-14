
import { Suspense } from "react";
import { redirect } from "next/navigation";
import { getCurrentUser } from "@/lib/server-auth";

/** Resolve the user's role and redirect to the corresponding dashboard. */
async function DashboardRedirect() {
  const user = await getCurrentUser();

  if (!user || user.is_active === false) {
    redirect("/login");
  }

  switch (user.role.toLowerCase()) {
    case "student":
      redirect("/dashboard/student");

    case "staff":
      redirect("/dashboard/staff");

    case "admin":
      redirect("/dashboard/admin");

    default:
      redirect("/login");
  }

  // Unreachable during normal execution; provides a valid React return type.
  return null;
}

/** Render the dashboard redirect inside a Suspense boundary. */
export default function DashboardPage() {
  return (
    <Suspense
      fallback={
        <main className="p-8 text-sm text-slate-600">
          Loading your dashboard...
        </main>
      }
    >
      <DashboardRedirect />
    </Suspense>
  );
}
