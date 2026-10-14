
import { NextRequest, NextResponse } from "next/server";

/** Forward a new student registration to the FastAPI users endpoint. */
export async function POST(request: NextRequest) {
  const apiBase = process.env.FASTAPI_API_URL;

  if (!apiBase) {
    return NextResponse.json(
      { detail: "The API connection is not configured." },
      { status: 500 },
    );
  }

  try {
    const input = await request.json();

    const upstream = await fetch(
      `${apiBase.replace(/\/$/, "")}/api/v1/users`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          full_name: input.full_name,
          email: input.email,
          password: input.password,
        }),
        cache: "no-store",
      },
    );

    const text = await upstream.text();
    let payload: unknown;

    try {
      payload = JSON.parse(text);
    } catch {
      payload = {
        detail: "The API returned an unexpected response.",
      };
    }

    return NextResponse.json(payload, {
      status: upstream.status,
    });
  } catch {
    return NextResponse.json(
      { detail: "Could not connect to the registration service." },
      { status: 502 },
    );
  }
}
