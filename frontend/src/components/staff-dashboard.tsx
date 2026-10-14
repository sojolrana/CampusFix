
"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { SignOutButton } from "@/components/sign-out-button";

type StaffUser = {
  full_name: string;
  email: string;
};

type Issue = {
  id: string;
  title: string;
  description: string;
  category: string;
  location: string;
  status: string;
  priority: string;
  reporter_id: string;
  assigned_staff_id: string | null;
  created_at: string;
  updated_at: string;
};

type ApiError = {
  detail?: unknown;
};

const categories = [
  "electrical",
  "facilities",
  "cleanliness",
  "network",
  "plumbing",
  "safety",
  "other",
];

const statuses = [
  "submitted",
  "acknowledged",
  "in_progress",
  "resolved",
  "rejected",
];

const priorities = ["low", "normal", "high", "urgent"];

const statusStyles: Record<string, string> = {
  submitted: "bg-blue-100 text-blue-800",
  acknowledged: "bg-indigo-100 text-indigo-800",
  in_progress: "bg-amber-100 text-amber-800",
  resolved: "bg-green-100 text-green-800",
  rejected: "bg-red-100 text-red-800",
};

/** Format an enum value for readable display. */
function formatLabel(value: string): string {
  return value
    .replaceAll("_", " ")
    .replace(/\b\w/g, (character) => character.toUpperCase());
}

/** Format a timestamp using the visitor's local timezone. */
function formatDate(value: string): string {
  const date = new Date(value);

  return Number.isNaN(date.getTime())
    ? "Unknown date"
    : date.toLocaleString();
}

/** Extract a readable message from an API error response. */
function responseMessage(
  data: ApiError,
  fallback: string,
): string {
  if (typeof data.detail === "string") {
    return data.detail;
  }

  if (Array.isArray(data.detail)) {
    const messages = data.detail
      .map((item: unknown) => {
        if (
          typeof item === "object" &&
          item !== null &&
          "msg" in item &&
          typeof item.msg === "string"
        ) {
          return item.msg;
        }

        return "";
      })
      .filter(Boolean);

    return messages.length > 0 ? messages.join(" ") : fallback;
  }

  return fallback;
}

/** Render assigned issues with filters, sorting, and pagination. */
export function StaffDashboard({
  user,
}: {
  user: StaffUser;
}) {
  const [issues, setIssues] = useState<Issue[]>([]);

  const [statusFilter, setStatusFilter] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("");
  const [priorityFilter, setPriorityFilter] = useState("");
  const [sortOrder, setSortOrder] = useState("newest");

  const [skip, setSkip] = useState(0);
  const [refreshKey, setRefreshKey] = useState(0);

  const limit = 10;

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;

    /** Fetch the assigned issue page using the selected filters. */
    async function fetchAssignedIssues(): Promise<void> {
      try {
        const params = new URLSearchParams({
          skip: String(skip),
          limit: String(limit),
          sort_order: sortOrder,
          _refresh: String(refreshKey),
        });

        if (statusFilter) {
          params.set("status", statusFilter);
        }

        if (categoryFilter) {
          params.set("category", categoryFilter);
        }

        if (priorityFilter) {
          params.set("priority", priorityFilter);
        }

        const response = await fetch(
          `/api/issues?${params.toString()}`,
          { cache: "no-store" },
        );

        const data: unknown = await response.json().catch(() => ({}));

        if (!response.ok) {
          throw new Error(
            responseMessage(
              data as ApiError,
              "Unable to load assigned issues.",
            ),
          );
        }

        if (!Array.isArray(data)) {
          throw new Error(
            "The server returned an invalid issue list.",
          );
        }

        if (cancelled) {
          return;
        }

        setIssues(data as Issue[]);
        setError("");
      } catch (caught: unknown) {
        if (cancelled) {
          return;
        }

        setIssues([]);

        setError(
          caught instanceof Error
            ? caught.message
            : "Unable to load assigned issues.",
        );
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    void fetchAssignedIssues();

    return () => {
      cancelled = true;
    };
  }, [
    skip,
    limit,
    sortOrder,
    statusFilter,
    categoryFilter,
    priorityFilter,
    refreshKey,
  ]);

  /** Reset all filters and return to the first page. */
  function resetFilters(): void {
    setLoading(true);
    setStatusFilter("");
    setCategoryFilter("");
    setPriorityFilter("");
    setSortOrder("newest");
    setSkip(0);
    setRefreshKey((previous) => previous + 1);
  }

  /** Refresh the assigned issue list from the backend. */
  function refreshIssues(): void {
    setLoading(true);
    setRefreshKey((previous) => previous + 1);
  }

  /** Navigate to the previous page of assigned issues. */
  function goToPreviousPage(): void {
    setLoading(true);
    setSkip((current) => Math.max(0, current - limit));
  }

  /** Navigate to the next page of assigned issues. */
  function goToNextPage(): void {
    setLoading(true);
    setSkip((current) => current + limit);
  }

  const selectClass =
    "w-full rounded-lg border border-slate-300 bg-white px-3 py-2.5 text-slate-900";

  const labelClass =
    "mb-1 block text-xs font-medium text-slate-700";

  return (
    <main className="min-h-screen bg-slate-50 px-4 py-6 sm:px-8 sm:py-10">
      <div className="mx-auto max-w-6xl">
        <header className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <Link href="/" className="font-semibold text-blue-700">
              CampusFix
            </Link>

            <h1 className="mt-3 text-3xl font-bold tracking-tight text-slate-900">
              Staff dashboard
            </h1>

            <p className="mt-2 text-slate-600">
              Welcome, {user.full_name}
            </p>

            <p className="mt-1 text-sm text-slate-500">
              View and manage issues assigned to you.
            </p>
          </div>

          <SignOutButton />
        </header>

        <section className="mt-8 rounded-2xl border border-slate-200 bg-white p-5 sm:p-6">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <h2 className="text-xl font-semibold text-slate-900">
                Assigned issues
              </h2>

              <p className="mt-1 text-sm text-slate-600">
                Review reports, update progress, and communicate with reporters.
              </p>
            </div>

            <button
              type="button"
              onClick={refreshIssues}
              disabled={loading}
              className="rounded-lg border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-100 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {loading ? "Refreshing..." : "Refresh"}
            </button>
          </div>

          <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <div>
              <label htmlFor="staff-filter-status" className={labelClass}>
                Status
              </label>

              <select
                id="staff-filter-status"
                value={statusFilter}
                onChange={(event) => {
                  setLoading(true);
                  setStatusFilter(event.target.value);
                  setSkip(0);
                }}
                className={selectClass}
              >
                <option value="">All statuses</option>

                {statuses.map((value) => (
                  <option key={value} value={value}>
                    {formatLabel(value)}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label htmlFor="staff-filter-category" className={labelClass}>
                Category
              </label>

              <select
                id="staff-filter-category"
                value={categoryFilter}
                onChange={(event) => {
                  setLoading(true);
                  setCategoryFilter(event.target.value);
                  setSkip(0);
                }}
                className={selectClass}
              >
                <option value="">All categories</option>

                {categories.map((value) => (
                  <option key={value} value={value}>
                    {formatLabel(value)}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label htmlFor="staff-filter-priority" className={labelClass}>
                Priority
              </label>

              <select
                id="staff-filter-priority"
                value={priorityFilter}
                onChange={(event) => {
                  setLoading(true);
                  setPriorityFilter(event.target.value);
                  setSkip(0);
                }}
                className={selectClass}
              >
                <option value="">All priorities</option>

                {priorities.map((value) => (
                  <option key={value} value={value}>
                    {formatLabel(value)}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label htmlFor="staff-filter-sort" className={labelClass}>
                Sort by
              </label>

              <select
                id="staff-filter-sort"
                value={sortOrder}
                onChange={(event) => {
                  setLoading(true);
                  setSortOrder(event.target.value);
                  setSkip(0);
                }}
                className={selectClass}
              >
                <option value="newest">Newest first</option>
                <option value="oldest">Oldest first</option>
              </select>
            </div>
          </div>

          <button
            type="button"
            onClick={resetFilters}
            className="mt-4 text-sm font-medium text-blue-700 hover:underline"
          >
            Reset filters
          </button>

          {error && (
            <p
              role="alert"
              className="mt-5 rounded-lg bg-red-50 p-3 text-sm text-red-700"
            >
              {error}
            </p>
          )}

          {loading ? (
            <p
              role="status"
              className="py-16 text-center text-slate-600"
            >
              Loading assigned issues...
            </p>
          ) : issues.length === 0 ? (
            <div className="mt-5 rounded-xl border border-dashed border-slate-300 px-4 py-12 text-center">
              <h3 className="font-semibold text-slate-800">
                No assigned issues found
              </h3>

              <p className="mt-2 text-sm text-slate-600">
                Try different filters or check again after an administrator
                assigns an issue to you.
              </p>
            </div>
          ) : (
            <div className="mt-5 space-y-3">
              {issues.map((issue) => (
                <article
                  key={issue.id}
                  className="rounded-xl border border-slate-200 p-4 transition hover:border-blue-300"
                >
                  <div className="flex flex-wrap items-start justify-between gap-3">
                    <div className="min-w-0">
                      <h3 className="font-semibold text-slate-900">
                        {issue.title}
                      </h3>

                      <p className="mt-1 text-sm text-slate-600">
                        {issue.location}
                      </p>
                    </div>

                    <span
                      className={`rounded-full px-3 py-1 text-xs font-medium ${
                        statusStyles[issue.status] ??
                        "bg-slate-100 text-slate-700"
                      }`}
                    >
                      {formatLabel(issue.status)}
                    </span>
                  </div>

                  <p className="mt-3 line-clamp-2 text-sm leading-6 text-slate-600">
                    {issue.description}
                  </p>

                  <div className="mt-3 flex flex-wrap gap-x-4 gap-y-1 text-xs text-slate-600">
                    <span>{formatLabel(issue.category)}</span>
                    <span>{formatLabel(issue.priority)} priority</span>
                    <span>Reported: {formatDate(issue.created_at)}</span>
                  </div>

                  <div className="mt-4 border-t border-slate-100 pt-3 text-right">
                    <Link
                      href={`/dashboard/staff/issues/${issue.id}`}
                      className="text-sm font-semibold text-blue-700 hover:underline"
                    >
                      Manage issue →
                    </Link>
                  </div>
                </article>
              ))}
            </div>
          )}

          <div className="mt-5 flex items-center justify-between border-t border-slate-100 pt-4">
            <button
              type="button"
              onClick={goToPreviousPage}
              disabled={skip === 0 || loading}
              className="rounded-lg border border-slate-300 px-3 py-2 text-sm font-medium text-slate-700 disabled:cursor-not-allowed disabled:opacity-40"
            >
              Previous
            </button>

            <span className="text-xs text-slate-600">
              {issues.length === 0
                ? "No items"
                : `Items ${skip + 1}–${skip + issues.length}`}
            </span>

            <button
              type="button"
              onClick={goToNextPage}
              disabled={loading || issues.length < limit}
              className="rounded-lg border border-slate-300 px-3 py-2 text-sm font-medium text-slate-700 disabled:cursor-not-allowed disabled:opacity-40"
            >
              Next
            </button>
          </div>
        </section>

        <footer className="mt-6 text-sm text-slate-600">
          Signed in as {user.email}
        </footer>
      </div>
    </main>
  );
}
