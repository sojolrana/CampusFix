
import { NextRequest } from "next/server";
import { forwardToFastAPI } from "@/lib/fastapi-proxy";

/** Retrieve issues using the current user's permissions and query filters. */
export async function GET(request: NextRequest) {
  const query = request.nextUrl.searchParams.toString();
  const path = query ? `/issues?${query}` : "/issues";

  return forwardToFastAPI(path);
}

/** Submit a new issue through the existing FastAPI endpoint. */
export async function POST(request: NextRequest) {
  const body = await request.text();

  return forwardToFastAPI("/issues", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body,
  });
}
