
import { cookies } from "next/headers";
import { NextResponse } from "next/server";

/** Forward an authenticated request to the FastAPI v1 API. */
export async function forwardToFastAPI(
  path: string,
  init: RequestInit = {},
): Promise<NextResponse> {
  const apiBase = process.env.FASTAPI_API_URL;
  const cookieStore = await cookies();
  const token = cookieStore.get("campusfix_access_token")?.value;

  if (!token) {
    return NextResponse.json(
      { detail: "Authentication required." },
      { status: 401 },
    );
  }

  if (!apiBase) {
    return NextResponse.json(
      { detail: "The API connection is not configured." },
      { status: 500 },
    );
  }

  const headers = new Headers(init.headers);
  headers.set("Authorization", `Bearer ${token}`);

  if (init.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  try {
    const upstream = await fetch(
      `${apiBase.replace(/\/$/, "")}/api/v1${path}`,
      {
        ...init,
        headers,
        cache: "no-store",
      },
    );

    const responseBody = await upstream.text();

    const response = new NextResponse(
      responseBody || null,
      {
        status: upstream.status,
        headers: {
          "Content-Type":
            upstream.headers.get("content-type") ??
            "application/json",
        },
      },
    );

    if (upstream.status === 401) {
      response.cookies.set("campusfix_access_token", "", {
        httpOnly: true,
        secure: process.env.NODE_ENV === "production",
        sameSite: "lax",
        path: "/",
        maxAge: 0,
      });
    }

    return response;
  } catch {
    return NextResponse.json(
      { detail: "Could not connect to the backend API." },
      { status: 502 },
    );
  }
}
