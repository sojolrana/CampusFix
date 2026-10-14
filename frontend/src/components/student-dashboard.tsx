
"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import { SignOutButton } from "@/components/sign-out-button";

type StudentUser = {
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

/** Extract a readable message from an API response. */
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

/** Render the student issue-reporting form and personal issue list. */
export function StudentDashboard({
  user,
}: {
  user: StudentUser;
}) {
  const [issues, setIssues] = useState<Issue[]>([]);

  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [category, setCategory] = useState("facilities");
  const [location, setLocation] = useState("");

  const [statusFilter, setStatusFilter] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("");
  const [priorityFilter, setPriorityFilter] = useState("");
  const [sortOrder, setSortOrder] = useState("newest");

  const [skip, setSkip] = useState(0);
  const [refreshKey, setRefreshKey] = useState(0);

  const limit = 10;

  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  useEffect(() => {
    let cancelled = false;

    /** Fetch the issue page using the current filters and pagination. */
    async function fetchIssues(): Promise<void> {
      try {
        const params = new URLSearchParams({
          skip: String(skip),
          limit: String(limit),
          sort_order: sortOrder,
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
              "Unable to load your issues.",
            ),
          );
        }

        if (!Array.isArray(data)) {
          throw new Error(
            "The server returned an unexpected issue list.",
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
            : "Unable to load your issues.",
        );
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    void fetchIssues();

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

  /** Submit a new campus issue through the authenticated API proxy. */
  async function handleCreateIssue(
    event: FormEvent<HTMLFormElement>,
  ): Promise<void> {
    event.preventDefault();

    setSubmitting(true);
    setError("");
    setSuccess("");

    try {
      const response = await fetch("/api/issues", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          title,
          description,
          category,
          location,
        }),
      });

      const data: unknown = await response.json().catch(() => ({}));

      if (!response.ok) {
        throw new Error(
          responseMessage(
            data as ApiError,
            "Unable to submit the issue.",
          ),
        );
      }

      setTitle("");
      setDescription("");
      setCategory("facilities");
      setLocation("");
      setSkip(0);
      setLoading(true);
      setSuccess("Your issue has been submitted successfully.");

      setRefreshKey((previous) => previous + 1);
    } catch (caught: unknown) {
      setError(
        caught instanceof Error
          ? caught.message
          : "Unable to submit the issue.",
      );
    } finally {
      setSubmitting(false);
    }
  }

  /** Reset all issue filters and refresh the first page. */
  function resetFilters(): void {
    setStatusFilter("");
    setCategoryFilter("");
    setPriorityFilter("");
    setSortOrder("newest");
    setSkip(0);
    setLoading(true);
    setSuccess("");
    setRefreshKey((previous) => previous + 1);
  }

  /** Change a filter while returning to the first result page. */
  function updateStatusFilter(value: string): void {
    setLoading(true);
    setStatusFilter(value);
    setSkip(0);
  }

  /** Change the category filter and reset pagination. */
  function updateCategoryFilter(value: string): void {
    setLoading(true);
    setCategoryFilter(value);
    setSkip(0);
  }

  /** Change the priority filter and reset pagination. */
  function updatePriorityFilter(value: string): void {
    setLoading(true);
    setPriorityFilter(value);
    setSkip(0);
  }

  /** Change the sorting order and reset pagination. */
  function updateSortOrder(value: string): void {
    setLoading(true);
    setSortOrder(value);
    setSkip(0);
  }

  /** Navigate to the previous issue page. */
  function goToPreviousPage(): void {
    setLoading(true);
    setSkip((current) => Math.max(0, current - limit));
  }

  /** Navigate to the next issue page. */
  function goToNextPage(): void {
    setLoading(true);
    setSkip((current) => current + limit);
  }

  const inputClass =
    "w-full rounded-lg border border-slate-300 bg-white px-3 py-2.5 text-slate-900 placeholder:text-slate-400 outline-none focus:border-blue-600 focus:ring-2 focus:ring-blue-100";

  const selectClass =
    "w-full rounded-lg border border-slate-300 bg-white px-3 py-2.5 text-slate-900";

  const labelClass =
    "mb-1 block text-sm font-medium text-slate-700";

  const filterLabelClass =
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
              Student dashboard
            </h1>

            <p className="mt-2 text-slate-600">
              Welcome, {user.full_name}
            </p>
          </div>

          <SignOutButton />
        </header>

        <section className="mt-8 grid gap-6 lg:grid-cols-[minmax(0,0.9fr)_minmax(0,1.1fr)]">
          <div className="rounded-2xl border border-slate-200 bg-white p-6">
            <h2 className="text-xl font-semibold text-slate-900">
              Report a campus issue
            </h2>

            <p className="mt-2 text-sm text-slate-600">
              Describe the problem and where it occurred.
            </p>

            <form onSubmit={handleCreateIssue} className="mt-6 space-y-4">
              <div>
                <label htmlFor="issue-title" className={labelClass}>
                  Title
                </label>

                <input
                  id="issue-title"
                  type="text"
                  required
                  minLength={5}
                  maxLength={150}
                  value={title}
                  onChange={(event) => setTitle(event.target.value)}
                  placeholder="e.g. Broken classroom light"
                  className={inputClass}
                />
              </div>

              <div>
                <label
                  htmlFor="issue-description"
                  className={labelClass}
                >
                  Description
                </label>

                <textarea
                  id="issue-description"
                  required
                  minLength={10}
                  maxLength={5000}
                  rows={4}
                  value={description}
                  onChange={(event) =>
                    setDescription(event.target.value)
                  }
                  placeholder="Explain what happened and why it needs attention."
                  className={inputClass}
                />
              </div>

              <div>
                <label htmlFor="issue-category" className={labelClass}>
                  Category
                </label>

                <select
                  id="issue-category"
                  required
                  value={category}
                  onChange={(event) => setCategory(event.target.value)}
                  className={selectClass}
                >
                  {categories.map((value) => (
                    <option key={value} value={value}>
                      {formatLabel(value)}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label htmlFor="issue-location" className={labelClass}>
                  Location
                </label>

                <input
                  id="issue-location"
                  type="text"
                  required
                  minLength={2}
                  maxLength={200}
                  value={location}
                  onChange={(event) => setLocation(event.target.value)}
                  placeholder="e.g. Building A, Room 204"
                  className={inputClass}
                />
              </div>

              <button
                type="submit"
                disabled={submitting}
                className="w-full rounded-lg bg-blue-700 px-4 py-3 font-semibold text-white hover:bg-blue-800 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {submitting ? "Submitting..." : "Submit issue"}
              </button>
            </form>

            {success && (
              <p role="status" className="mt-4 text-sm text-green-700">
                {success}
              </p>
            )}

            {error && (
              <p role="alert" className="mt-4 text-sm text-red-600">
                {error}
              </p>
            )}
          </div>

          <div className="min-w-0 rounded-2xl border border-slate-200 bg-white p-6">
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <h2 className="text-xl font-semibold text-slate-900">
                  My reported issues
                </h2>

                <p className="mt-1 text-sm text-slate-600">
                  Track the progress of your reports.
                </p>
              </div>

              <span className="rounded-full bg-slate-100 px-3 py-1 text-sm text-slate-700">
                {issues.length} on this page
              </span>
            </div>

            <div className="mt-5 grid gap-3 sm:grid-cols-2">
              <div>
                <label htmlFor="filter-status" className={filterLabelClass}>
                  Status
                </label>

                <select
                  id="filter-status"
                  value={statusFilter}
                  onChange={(event) =>
                    updateStatusFilter(event.target.value)
                  }
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
                <label
                  htmlFor="filter-category"
                  className={filterLabelClass}
                >
                  Category
                </label>

                <select
                  id="filter-category"
                  value={categoryFilter}
                  onChange={(event) =>
                    updateCategoryFilter(event.target.value)
                  }
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
                <label
                  htmlFor="filter-priority"
                  className={filterLabelClass}
                >
                  Priority
                </label>

                <select
                  id="filter-priority"
                  value={priorityFilter}
                  onChange={(event) =>
                    updatePriorityFilter(event.target.value)
                  }
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
                <label htmlFor="filter-sort" className={filterLabelClass}>
                  Sort by
                </label>

                <select
                  id="filter-sort"
                  value={sortOrder}
                  onChange={(event) =>
                    updateSortOrder(event.target.value)
                  }
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
              className="mt-3 text-sm font-medium text-blue-700 hover:underline"
            >
              Reset filters
            </button>

            {loading ? (
              <p
                role="status"
                className="py-12 text-center text-sm text-slate-600"
              >
                Loading issues...
              </p>
            ) : issues.length === 0 ? (
              <div className="mt-5 rounded-xl border border-dashed border-slate-300 px-4 py-10 text-center">
                <p className="font-medium text-slate-800">
                  No issues found
                </p>

                <p className="mt-2 text-sm text-slate-600">
                  Try changing your filters or submit your first report.
                </p>
              </div>
            ) : (
              <div className="mt-5 space-y-3">
                {issues.map((issue) => (
                  <article
                    key={issue.id}
                    className="rounded-xl border border-slate-200 p-4 transition hover:border-blue-300"
                  >
                    <div className="flex flex-wrap items-start justify-between gap-2">
                      <h3 className="font-semibold text-slate-900">
                        {issue.title}
                      </h3>

                      <span
                        className={`rounded-full px-2.5 py-1 text-xs font-medium ${
                          statusStyles[issue.status] ??
                          "bg-slate-100 text-slate-700"
                        }`}
                      >
                        {formatLabel(issue.status)}
                      </span>
                    </div>

                    <p className="mt-2 line-clamp-2 text-sm text-slate-600">
                      {issue.description}
                    </p>

                    <div className="mt-3 flex flex-wrap gap-x-4 gap-y-1 text-xs text-slate-600">
                      <span>{formatLabel(issue.category)}</span>
                      <span>
                        {formatLabel(issue.priority)} priority
                      </span>
                      <span>{issue.location}</span>
                    </div>

                    <div className="mt-4 flex flex-wrap items-center justify-between gap-2 border-t border-slate-100 pt-3">
                      <span className="text-xs text-slate-600">
                        {formatDate(issue.created_at)}
                      </span>

                      <Link
                        href={`/dashboard/student/issues/${issue.id}`}
                        className="text-sm font-semibold text-blue-700 hover:underline"
                      >
                        View details →
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
          </div>
        </section>

        <footer className="mt-8 text-sm text-slate-600">
          Signed in as {user.email}
        </footer>
      </div>
    </main>
  );
}
