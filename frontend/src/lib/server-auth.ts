
import "server-only";

import { cookies } from "next/headers";
import { redirect } from "next/navigation";

export type CampusUser = {
  id: string;
  full_name: string;
  email: string;
  role: string;
  is_active?: boolean;
};

/** Retrieve the current user from FastAPI using the server-held cookie. */
export async function getCurrentUser(): Promise<CampusUser | null> {
  const apiBase = process.env.FASTAPI_API_URL;
  const cookieStore = await cookies();
  const token = cookieStore.get("campusfix_access_token")?.value;

  if (!apiBase || !token) {
    return null;
  }

  try {
    const response = await fetch(
      `${apiBase.replace(/\/$/, "")}/api/v1/auth/me`,
      {
        headers: { Authorization: `Bearer ${token}` },
        cache: "no-store",
      },
    );

    if (!response.ok) {
      return null;
    }

    const user = (await response.json()) as CampusUser;

    if (
      typeof user.id !== "string" ||
      typeof user.email !== "string" ||
      typeof user.role !== "string"
    ) {
      return null;
    }

    return user;
  } catch {
    return null;
  }
}

/** Require authentication and an allowed role for a dashboard page. */
export async function requireRole(
  allowedRoles: string[],
): Promise<CampusUser> {
  const user = await getCurrentUser();

  if (!user || user.is_active === false) {
    redirect("/login");
  }

  const actualRole = user.role.toLowerCase();
  const permittedRoles = allowedRoles.map((role) => role.toLowerCase());

  if (!permittedRoles.includes(actualRole)) {
    redirect("/dashboard");
  }

  return user;
}
