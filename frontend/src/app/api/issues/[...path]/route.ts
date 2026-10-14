
import { NextRequest } from "next/server";
import { forwardToFastAPI } from "@/lib/fastapi-proxy";

type RouteContext = {
  params: Promise<{
    path: string[];
  }>;
};

/** Forward an issue-related request, preserving its path and query string. */
async function proxyIssueRequest(
  request: NextRequest,
  context: RouteContext,
  method: "GET" | "POST" | "PATCH",
) {
  const { path } = await context.params;

  const issuePath = path.map((segment) =>
    encodeURIComponent(segment),
  ).join("/");

  const query = request.nextUrl.searchParams.toString();
  const targetPath = `/issues/${issuePath}${query ? `?${query}` : ""}`;

  const body =
    method === "GET" ? undefined : await request.text();

  return forwardToFastAPI(targetPath, {
    method,
    ...(body
      ? {
          headers: {
            "Content-Type": "application/json",
          },
          body,
        }
      : {}),
  });
}

/** Retrieve issue details, comments, or status history. */
export async function GET(
  request: NextRequest,
  context: RouteContext,
) {
  return proxyIssueRequest(request, context, "GET");
}

/** Add a comment to an issue through FastAPI. */
export async function POST(
  request: NextRequest,
  context: RouteContext,
) {
  return proxyIssueRequest(request, context, "POST");
}

/** Forward permitted issue status updates to FastAPI. */
export async function PATCH(
  request: NextRequest,
  context: RouteContext,
) {
  return proxyIssueRequest(request, context, "PATCH");
}
