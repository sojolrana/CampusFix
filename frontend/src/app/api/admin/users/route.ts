import { NextRequest } from "next/server";
import { forwardToFastAPI } from "@/lib/fastapi-proxy";

/** Retrieve users through the authenticated FastAPI admin endpoint. */
export async function GET(request: NextRequest) {
  const query = request.nextUrl.searchParams.toString();
  const path = query ? `/admin/users?${query}` : "/admin/users";

  return forwardToFastAPI(path);
}