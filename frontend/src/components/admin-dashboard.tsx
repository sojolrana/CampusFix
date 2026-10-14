
"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { SignOutButton } from "@/components/sign-out-button";

type AdminUser = {
  id: string;
  full_name: string;
  email: string;
  role: string;
  is_active?: boolean;
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

const statuses = [
  "submitted",
  "acknowledged",
  "in_progress",
  "resolved",
  "rejected",
];

const categories = [
  "electrical",
  "facilities",
  "cleanliness",
  "network",
  "plumbing",
  "safety",
  "other",
];

const statusStyles: Record<string, string> = {
  submitted: "bg-blue-100 text-blue-800",
  acknowledged: "bg-indigo-100 text-indigo-800",
  in_progress: "bg-amber-100 text-amber-800",
  resolved: "bg-green-100 text-green-800",
  rejected: "bg-red-100 text-red-800",
};

/** Format enum values for readable display. */
function formatLabel(value: string): string {
  return value
    .replaceAll("_", " ")
    .replace(/\b\w/g, (character) => character.toUpperCase());
}

/** Format timestamps in the visitor's local timezone. */
function formatDate(value: string): string {
  const date = new Date(value);

  return Number.isNaN(date.getTime())
    ? "Unknown date"
    : date.toLocaleString();
}

/** Extract a useful error message from an API response. */
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

/** Accept either a direct list or a paginated list returned by an API. */
function extractList<T>(data: unknown): T[] {
  if (Array.isArray(data)) {
    return data as T[];
  }

  if (
    typeof data === "object" &&
    data !== null &&
    "items" in data &&
    Array.isArray(data.items)
  ) {
    return data.items as T[];
  }

  return [];
}

/** Render the admin dashboard, user directory, and issue assignment tools. */
export function AdminDashboard({
  user,
}: {
  user: {
    full_name: string;
    email: string;
  };
}) {
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [issues, setIssues] = useState<Issue[]>([]);

  const [statusFilter, setStatusFilter] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("");
  const [userSearch, setUserSearch] = useState("");
  const [issueSearch, setIssueSearch] = useState("");

  const [loading, setLoading] = useState(true);
  const [refreshKey, setRefreshKey] = useState(0);
  const [assignments, setAssignments] = useState<Record<string, string>>({});
  const [assigningIssueId, setAssigningIssueId] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  useEffect(() => {
    let cancelled = false;

    /** Fetch users and issues using the current admin session. */
    async function loadAdminData(): Promise<void> {
      try {
        const issueParams = new URLSearchParams({
          skip: "0",
          limit: "100",
          sort_order: "newest",
          _refresh: String(refreshKey),
        });

        const [usersResponse, issuesResponse] = await Promise.all([
          fetch(
            `/api/admin/users?_refresh=${refreshKey}`,
            { cache: "no-store" },
          ),
          fetch(
            `/api/issues?${issueParams.toString()}`,
            { cache: "no-store" },
          ),
        ]);

        const [usersData, issuesData] = await Promise.all([
          usersResponse.json().catch(() => ({})),
          issuesResponse.json().catch(() => ({})),
        ]);

        if (!usersResponse.ok) {
          throw new Error(
            responseMessage(
              usersData as ApiError,
              "Unable to load users.",
            ),
          );
        }

        if (!issuesResponse.ok) {
          throw new Error(
            responseMessage(
              issuesData as ApiError,
              "Unable to load issues.",
            ),
          );
        }

        const loadedUsers = extractList<AdminUser>(usersData);
        const loadedIssues = extractList<Issue>(issuesData);

        if (cancelled) {
          return;
        }

        setUsers(loadedUsers);
        setIssues(loadedIssues);
        setError("");
      } catch (caught: unknown) {
        if (cancelled) {
          return;
        }

        setError(
          caught instanceof Error
            ? caught.message
            : "Unable to load administrator data.",
        );
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    void loadAdminData();

    return () => {
      cancelled = true;
    };
  }, [refreshKey]);

  const staffUsers = users.filter(
    (account) =>
      account.role.toLowerCase() === "staff" &&
      account.is_active !== false,
  );

  const activeIssues = issues.filter(
    (issue) =>
      !["resolved", "rejected"].includes(issue.status),
  );

  const resolvedIssues = issues.filter(
    (issue) => issue.status === "resolved",
  );

  const filteredIssues = issues.filter((issue) => {
    const matchesStatus =
      !statusFilter || issue.status === statusFilter;

    const matchesCategory =
      !categoryFilter || issue.category === categoryFilter;

    const searchText = issueSearch.trim().toLowerCase();

    const matchesSearch =
      !searchText ||
      issue.title.toLowerCase().includes(searchText) ||
      issue.location.toLowerCase().includes(searchText) ||
      issue.description.toLowerCase().includes(searchText);

    return matchesStatus && matchesCategory && matchesSearch;
  });

  const filteredUsers = users.filter((account) => {
    const searchText = userSearch.trim().toLowerCase();

    return (
      !searchText ||
      account.full_name.toLowerCase().includes(searchText) ||
      account.email.toLowerCase().includes(searchText) ||
      account.role.toLowerCase().includes(searchText)
    );
  });

  /** Refresh the user and issue information from the backend. */
  function refreshDashboard(): void {
    setLoading(true);
    setError("");
    setSuccess("");
    setRefreshKey((previous) => previous + 1);
  }

  /** Assign an issue to the selected staff member. */
  async function handleAssignment(
    issueId: string,
  ): Promise<void> {
    const staffId = assignments[issueId];

    if (!staffId) {
      setError("Select a staff member before assigning the issue.");
      setSuccess("");
      return;
    }

    setAssigningIssueId(issueId);
    setError("");
    setSuccess("");

    try {
      const response = await fetch(
        `/api/issues/${encodeURIComponent(issueId)}/assign`,
        {
          method: "PATCH",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            staff_id: staffId,
          }),
        },
      );

      const data: unknown = await response.json().catch(() => ({}));

      if (!response.ok) {
        throw new Error(
          responseMessage(
            data as ApiError,
            "Unable to assign this issue.",
          ),
        );
      }

      setSuccess("Issue assigned successfully.");
      setLoading(true);
      setRefreshKey((previous) => previous + 1);
    } catch (caught: unknown) {
      setError(
        caught instanceof Error
          ? caught.message
          : "Unable to assign this issue.",
      );
    } finally {
      setAssigningIssueId("");
    }
  }

  const inputClass =
    "w-full rounded-lg border border-slate-300 bg-white px-3 py-2.5 text-slate-900 placeholder:text-slate-400 outline-none focus:border-blue-600 focus:ring-2 focus:ring-blue-100";

  const labelClass =
    "mb-1 block text-sm font-medium text-slate-700";

  return (
    <main className="min-h-screen bg-slate-50 px-4 py-6 sm:px-8 sm:py-10">
      <div className="mx-auto max-w-7xl">
        <header className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <Link href="/" className="font-semibold text-blue-700">
              CampusFix
            </Link>

            <h1 className="mt-3 text-3xl font-bold tracking-tight text-slate-900">
              Admin dashboard
            </h1>

            <p className="mt-2 text-slate-600">
              Welcome, {user.full_name}
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <button
              type="button"
              onClick={refreshDashboard}
              disabled={loading}
              className="rounded-lg border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-100 disabled:opacity-50"
            >
              {loading ? "Refreshing..." : "Refresh data"}
            </button>
            <SignOutButton />
          </div>
        </header>

        {error && (
          <p
            role="alert"
            className="mt-6 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700"
          >
            {error}
          </p>
        )}

        {success && (
          <p
            role="status"
            className="mt-6 rounded-lg border border-green-200 bg-green-50 p-3 text-sm text-green-800"
          >
            {success}
          </p>
        )}

        <section className="mt-8 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          <article className="rounded-2xl border border-slate-200 bg-white p-5">
            <p className="text-sm text-slate-600">Users returned</p>
            <p className="mt-2 text-3xl font-bold text-slate-900">
              {users.length}
            </p>
            <p className="mt-1 text-xs text-slate-500">
              From the admin users endpoint
            </p>
          </article>

          <article className="rounded-2xl border border-slate-200 bg-white p-5">
            <p className="text-sm text-slate-600">Issues loaded</p>
            <p className="mt-2 text-3xl font-bold text-slate-900">
              {issues.length}
            </p>
            <p className="mt-1 text-xs text-slate-500">
              Most recent 100 issues maximum
            </p>
          </article>

          <article className="rounded-2xl border border-slate-200 bg-white p-5">
            <p className="text-sm text-slate-600">Open issues loaded</p>
            <p className="mt-2 text-3xl font-bold text-amber-700">
              {activeIssues.length}
            </p>
            <p className="mt-1 text-xs text-slate-500">
              Not yet resolved or rejected
            </p>
          </article>

          <article className="rounded-2xl border border-slate-200 bg-white p-5">
            <p className="text-sm text-slate-600">Resolved issues loaded</p>
            <p className="mt-2 text-3xl font-bold text-green-700">
              {resolvedIssues.length}
            </p>
            <p className="mt-1 text-xs text-slate-500">
              Among the issues currently loaded
            </p>
          </article>
        </section>

        <section className="mt-8 rounded-2xl border border-slate-200 bg-white p-5 sm:p-6">
          <h2 className="text-xl font-semibold text-slate-900">
            Issue management
          </h2>

          <p className="mt-1 text-sm text-slate-600">
            Review reports and assign them to an active staff account.
          </p>

          <div className="mt-5 grid gap-4 md:grid-cols-3">
            <div>
              <label htmlFor="admin-issue-search" className={labelClass}>
                Search issues
              </label>
              <input
                id="admin-issue-search"
                value={issueSearch}
                onChange={(event) => setIssueSearch(event.target.value)}
                placeholder="Title, location, or description"
                className={inputClass}
              />
            </div>

            <div>
              <label htmlFor="admin-issue-status" className={labelClass}>
                Status
              </label>
              <select
                id="admin-issue-status"
                value={statusFilter}
                onChange={(event) => setStatusFilter(event.target.value)}
                className={inputClass}
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
              <label htmlFor="admin-issue-category" className={labelClass}>
                Category
              </label>
              <select
                id="admin-issue-category"
                value={categoryFilter}
                onChange={(event) => setCategoryFilter(event.target.value)}
                className={inputClass}
              >
                <option value="">All categories</option>
                {categories.map((value) => (
                  <option key={value} value={value}>
                    {formatLabel(value)}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {loading ? (
            <p role="status" className="py-12 text-center text-slate-600">
              Loading administrative data...
            </p>
          ) : filteredIssues.length === 0 ? (
            <p className="py-12 text-center text-slate-600">
              No matching issues were found.
            </p>
          ) : (
            <div className="mt-5 space-y-4">
              {filteredIssues.map((issue) => (
                <article
                  key={issue.id}
                  className="rounded-xl border border-slate-200 p-4"
                >
                  <div className="flex flex-wrap items-start justify-between gap-3">
                    <div className="min-w-0 flex-1">
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

                  <p className="mt-3 line-clamp-2 text-sm text-slate-600">
                    {issue.description}
                  </p>

                  <div className="mt-3 flex flex-wrap gap-x-4 gap-y-1 text-xs text-slate-600">
                    <span>{formatLabel(issue.category)}</span>
                    <span>{formatLabel(issue.priority)} priority</span>
                    <span>Reported: {formatDate(issue.created_at)}</span>
                  </div>

                  <div className="mt-4 grid gap-3 border-t border-slate-100 pt-4 sm:grid-cols-[minmax(0,1fr)_auto] sm:items-end">
                    <div>
                      <label
                        htmlFor={`staff-${issue.id}`}
                        className={labelClass}
                      >
                        Assign to staff
                      </label>

                      <select
                        id={`staff-${issue.id}`}
                        value={
                          assignments[issue.id] ??
                          issue.assigned_staff_id ??
                          ""
                        }
                        onChange={(event) =>
                          setAssignments((previous) => ({
                            ...previous,
                            [issue.id]: event.target.value,
                          }))
                        }
                        className={inputClass}
                      >
                        <option value="">
                          Select a staff member
                        </option>

                        {staffUsers.map((account) => (
                          <option key={account.id} value={account.id}>
                            {account.full_name} ({account.email})
                          </option>
                        ))}
                      </select>

                      {issue.assigned_staff_id && (
                        <p className="mt-1 text-xs text-slate-500">
                          Current staff ID: {issue.assigned_staff_id}
                        </p>
                      )}
                    </div>

                    <button
                      type="button"
                      onClick={() => void handleAssignment(issue.id)}
                      disabled={
                        assigningIssueId === issue.id ||
                        loading ||
                        staffUsers.length === 0
                      }
                      className="rounded-lg bg-blue-700 px-4 py-2.5 text-sm font-semibold text-white hover:bg-blue-800 disabled:cursor-not-allowed disabled:opacity-50"
                    >
                      {assigningIssueId === issue.id
                        ? "Assigning..."
                        : "Save assignment"}
                    </button>
                  </div>

                  <div className="mt-3 text-right">
                    <Link
                      href={`/dashboard/admin/issues/${issue.id}`}
                      className="text-sm font-semibold text-blue-700 hover:underline"
                    >
                      View issue →
                    </Link>
                  </div>
                </article>
              ))}
            </div>
          )}
        </section>

        <section className="mt-8 rounded-2xl border border-slate-200 bg-white p-5 sm:p-6">
          <h2 className="text-xl font-semibold text-slate-900">
            User directory
          </h2>

          <p className="mt-1 text-sm text-slate-600">
            View registered user accounts and their roles.
          </p>

          <div className="mt-5">
            <label htmlFor="admin-user-search" className={labelClass}>
              Search users
            </label>
            <input
              id="admin-user-search"
              value={userSearch}
              onChange={(event) => setUserSearch(event.target.value)}
              placeholder="Search name, email, or role"
              className={inputClass}
            />
          </div>

          {loading ? (
            <p className="py-8 text-center text-slate-600">
              Loading users...
            </p>
          ) : filteredUsers.length === 0 ? (
            <p className="py-8 text-center text-slate-600">
              No matching user accounts were found.
            </p>
          ) : (
            <div className="mt-5 overflow-x-auto">
              <table className="w-full min-w-[640px] text-left text-sm">
                <thead>
                  <tr className="border-b border-slate-200 text-xs uppercase tracking-wide text-slate-600">
                    <th className="px-3 py-3 font-medium">Name</th>
                    <th className="px-3 py-3 font-medium">Email</th>
                    <th className="px-3 py-3 font-medium">Role</th>
                    <th className="px-3 py-3 font-medium">Account status</th>
                  </tr>
                </thead>

                <tbody>
                  {filteredUsers.map((account) => (
                    <tr
                      key={account.id}
                      className="border-b border-slate-100 last:border-b-0"
                    >
                      <td className="px-3 py-3 font-medium text-slate-900">
                        {account.full_name}
                      </td>
                      <td className="px-3 py-3 text-slate-700">
                        {account.email}
                      </td>
                      <td className="px-3 py-3 text-slate-700">
                        {formatLabel(account.role)}
                      </td>
                      <td className="px-3 py-3">
                        {account.is_active === false ? (
                          <span className="rounded-full bg-red-100 px-2.5 py-1 text-xs font-medium text-red-800">
                            Inactive
                          </span>
                        ) : (
                          <span className="rounded-full bg-green-100 px-2.5 py-1 text-xs font-medium text-green-800">
                            Active
                          </span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>

        <footer className="mt-6 text-sm text-slate-600">
          Signed in as {user.email}
        </footer>
      </div>
    </main>
  );
}
