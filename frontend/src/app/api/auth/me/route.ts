
import { cookies } from "next/headers";
import { NextResponse } from "next/server";

/** Return the authenticated user's profile without exposing the token. */
export async function GET() {
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

  try {
    const upstream = await fetch(
      `${apiBase.replace(/\/$/, "")}/api/v1/auth/me`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
        cache: "no-store",
      },
    );

    const payload = await upstream.json().catch(() => ({}));
    const response = NextResponse.json(payload, {
      status: upstream.status,
    });

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
      { detail: "Could not connect to the user service." },
      { status: 502 },
    );
  }
}
