
"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import type { FormEvent } from "react";

type Issue = {
  id: string;
  title: string;
  description: string;
  category: string;
  location: string;
  status: string;
  priority: string;
  created_at: string;
  updated_at: string;
};

type IssueComment = {
  id: string;
  issue_id: string;
  author_id: string;
  body: string;
  created_at: string;
  updated_at: string;
};

type StatusHistory = {
  id: string;
  issue_id: string;
  changed_by_id: string;
  old_status: string;
  new_status: string;
  changed_at: string;
};

type ApiError = {
  detail?: unknown;
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

/** Render issue details, status history, and the comment discussion. */
export function StudentIssueDetail({
  issueId,
}: {
  issueId: string;
}) {
  const [issue, setIssue] = useState<Issue | null>(null);
  const [comments, setComments] = useState<IssueComment[]>([]);
  const [history, setHistory] = useState<StatusHistory[]>([]);

  const [commentBody, setCommentBody] = useState("");
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    let cancelled = false;

    /** Fetch details, comments, and history for the selected issue. */
    async function fetchIssueData(): Promise<void> {
      try {
        const encodedId = encodeURIComponent(issueId);

        const responses = await Promise.all([
          fetch(`/api/issues/${encodedId}`, {
            cache: "no-store",
          }),
          fetch(`/api/issues/${encodedId}/comments`, {
            cache: "no-store",
          }),
          fetch(`/api/issues/${encodedId}/history`, {
            cache: "no-store",
          }),
        ]);

        const payloads: unknown[] = await Promise.all(
          responses.map((response) =>
            response.json().catch(() => ({})),
          ),
        );

        for (let index = 0; index < responses.length; index += 1) {
          if (!responses[index].ok) {
            throw new Error(
              responseMessage(
                payloads[index] as ApiError,
                "Unable to load issue information.",
              ),
            );
          }
        }

        if (cancelled) {
          return;
        }

        setIssue(payloads[0] as Issue);
        setComments(payloads[1] as IssueComment[]);
        setHistory(payloads[2] as StatusHistory[]);
        setError("");
      } catch (caught: unknown) {
        if (cancelled) {
          return;
        }

        setError(
          caught instanceof Error
            ? caught.message
            : "Unable to load issue information.",
        );
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    void fetchIssueData();

    return () => {
      cancelled = true;
    };
  }, [issueId, refreshKey]);

  /** Submit a comment to the selected issue. */
  async function handleCommentSubmit(
    event: FormEvent<HTMLFormElement>,
  ): Promise<void> {
    event.preventDefault();

    setSubmitting(true);
    setError("");
    setSuccess("");

    try {
      const response = await fetch(
        `/api/issues/${encodeURIComponent(issueId)}/comments`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            body: commentBody,
          }),
        },
      );

      const data: unknown = await response.json().catch(() => ({}));

      if (!response.ok) {
        throw new Error(
          responseMessage(
            data as ApiError,
            "Unable to post your comment.",
          ),
        );
      }

      setCommentBody("");
      setSuccess("Comment posted successfully.");
      setLoading(true);
      setRefreshKey((previous) => previous + 1);
    } catch (caught: unknown) {
      setError(
        caught instanceof Error
          ? caught.message
          : "Unable to post your comment.",
      );
    } finally {
      setSubmitting(false);
    }
  }

  const fieldLabelClass =
    "text-xs font-medium uppercase tracking-wide text-slate-600";

  const textAreaClass =
    "w-full rounded-lg border border-slate-300 bg-white px-3 py-2.5 text-slate-900 placeholder:text-slate-400 outline-none focus:border-blue-600 focus:ring-2 focus:ring-blue-100";

  if (loading && !issue) {
    return (
      <main className="mx-auto max-w-4xl p-8 text-slate-700">
        Loading issue details...
      </main>
    );
  }

  if (!issue) {
    return (
      <main className="mx-auto max-w-4xl p-8">
        <Link
          href="/dashboard/student"
          className="font-medium text-blue-700 hover:underline"
        >
          ← Back to dashboard
        </Link>

        <p role="alert" className="mt-6 text-red-600">
          {error || "Issue details could not be found."}
        </p>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-slate-50 px-4 py-8 sm:px-8">
      <div className="mx-auto max-w-4xl">
        <Link
          href="/dashboard/student"
          className="text-sm font-semibold text-blue-700 hover:underline"
        >
          ← Back to student dashboard
        </Link>

        <section className="mt-5 rounded-2xl border border-slate-200 bg-white p-6 sm:p-8">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div className="min-w-0">
              <p className="text-sm font-medium text-blue-700">
                {formatLabel(issue.category)}
              </p>

              <h1 className="mt-2 text-2xl font-bold text-slate-900 sm:text-3xl">
                {issue.title}
              </h1>
            </div>

            <span className="rounded-full bg-slate-100 px-3 py-1.5 text-sm font-medium text-slate-800">
              {formatLabel(issue.status)}
            </span>
          </div>

          <p className="mt-6 whitespace-pre-wrap leading-7 text-slate-700">
            {issue.description}
          </p>

          <dl className="mt-6 grid gap-4 border-t border-slate-100 pt-5 sm:grid-cols-2">
            <div>
              <dt className={fieldLabelClass}>Location</dt>
              <dd className="mt-1 text-sm text-slate-900">
                {issue.location}
              </dd>
            </div>

            <div>
              <dt className={fieldLabelClass}>Priority</dt>
              <dd className="mt-1 text-sm text-slate-900">
                {formatLabel(issue.priority)}
              </dd>
            </div>

            <div>
              <dt className={fieldLabelClass}>Reported</dt>
              <dd className="mt-1 text-sm text-slate-900">
                {formatDate(issue.created_at)}
              </dd>
            </div>

            <div>
              <dt className={fieldLabelClass}>Last updated</dt>
              <dd className="mt-1 text-sm text-slate-900">
                {formatDate(issue.updated_at)}
              </dd>
            </div>
          </dl>
        </section>

        <section className="mt-6 rounded-2xl border border-slate-200 bg-white p-6">
          <h2 className="text-xl font-semibold text-slate-900">
            Status timeline
          </h2>

          {loading && (
            <p role="status" className="mt-3 text-sm text-slate-600">
              Refreshing issue activity...
            </p>
          )}

          {history.length === 0 ? (
            <p className="mt-4 text-sm text-slate-600">
              No status changes have been recorded yet.
            </p>
          ) : (
            <ol className="mt-5 space-y-5">
              {history.map((entry) => (
                <li
                  key={entry.id}
                  className="border-l-2 border-blue-200 pl-4"
                >
                  <p className="font-medium text-slate-900">
                    {formatLabel(entry.old_status)} →{" "}
                    {formatLabel(entry.new_status)}
                  </p>

                  <p className="mt-1 text-sm text-slate-600">
                    {formatDate(entry.changed_at)}
                  </p>

                  <p className="mt-1 break-all text-xs text-slate-600">
                    Updated by account {entry.changed_by_id}
                  </p>
                </li>
              ))}
            </ol>
          )}
        </section>

        <section className="mt-6 rounded-2xl border border-slate-200 bg-white p-6">
          <h2 className="text-xl font-semibold text-slate-900">
            Discussion
          </h2>

          <p className="mt-1 text-sm text-slate-600">
            Add information or follow up on this issue.
          </p>

          <form onSubmit={handleCommentSubmit} className="mt-5 space-y-3">
            <label
              htmlFor="comment-body"
              className="block text-sm font-medium text-slate-700"
            >
              Your comment
            </label>

            <textarea
              id="comment-body"
              required
              minLength={1}
              maxLength={3000}
              rows={3}
              value={commentBody}
              onChange={(event) =>
                setCommentBody(event.target.value)
              }
              placeholder="Write an update or ask a question..."
              className={textAreaClass}
            />

            <button
              type="submit"
              disabled={submitting}
              className="rounded-lg bg-blue-700 px-4 py-2.5 font-semibold text-white hover:bg-blue-800 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {submitting ? "Posting..." : "Post comment"}
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

          <div className="mt-6 space-y-4 border-t border-slate-100 pt-5">
            {comments.length === 0 ? (
              <p className="text-sm text-slate-600">
                No comments yet. Start the discussion.
              </p>
            ) : (
              comments.map((comment) => (
                <article
                  key={comment.id}
                  className="rounded-xl bg-slate-50 p-4"
                >
                  <div className="flex flex-wrap justify-between gap-2">
                    <span className="break-all text-xs font-medium text-slate-600">
                      Account {comment.author_id}
                    </span>

                    <time className="text-xs text-slate-600">
                      {formatDate(comment.created_at)}
                    </time>
                  </div>

                  <p className="mt-3 whitespace-pre-wrap break-words text-sm leading-6 text-slate-800">
                    {comment.body}
                  </p>
                </article>
              ))
            )}
          </div>
        </section>
      </div>
    </main>
  );
}
