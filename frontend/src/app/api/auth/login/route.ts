
import { NextRequest, NextResponse } from "next/server";

/** Forward login credentials to FastAPI and create a session cookie. */
export async function POST(request: NextRequest) {
  const apiBase = process.env.FASTAPI_API_URL;

  if (!apiBase) {
    return NextResponse.json(
      { detail: "The API connection is not configured." },
      { status: 500 },
    );
  }

  try {
    const credentials = await request.json();
    const email =
      typeof credentials.email === "string"
        ? credentials.email.trim()
        : "";
    const password =
      typeof credentials.password === "string"
        ? credentials.password
        : "";

    if (!email || !password) {
      return NextResponse.json(
        { detail: "Email and password are required." },
        { status: 422 },
      );
    }

    const form = new URLSearchParams({
      username: email,
      password,
    });

    const upstream = await fetch(
      `${apiBase.replace(/\/$/, "")}/api/v1/auth/login`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: form.toString(),
        cache: "no-store",
      },
    );

    const payload = await upstream.json().catch(() => ({}));

    if (!upstream.ok) {
      return NextResponse.json(
        {
          detail:
            typeof payload.detail === "string"
              ? payload.detail
              : "Login failed. Check your credentials.",
        },
        { status: upstream.status },
      );
    }

    if (typeof payload.access_token !== "string") {
      return NextResponse.json(
        { detail: "The API returned an invalid login response." },
        { status: 502 },
      );
    }

    const response = NextResponse.json({
      message: "Login successful.",
    });

    response.cookies.set(
      "campusfix_access_token",
      payload.access_token,
      {
        httpOnly: true,
        secure: process.env.NODE_ENV === "production",
        sameSite: "lax",
        path: "/",
        // Match this to your backend's JWT expiration setting.
        maxAge: 30 * 60,
      },
    );

    return response;
  } catch {
    return NextResponse.json(
      { detail: "Could not connect to the authentication service." },
      { status: 502 },
    );
  }
}
