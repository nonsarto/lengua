import { S } from "@/lib/strings";

/** Una sola fuente para la URL del backend: env explícita o el mismo host en el puerto 8000
 *  (funciona en localhost Y desde el iPhone en la red local sin configurar nada). */
export const API =
  process.env.NEXT_PUBLIC_API_URL ??
  (typeof window !== "undefined" ? `http://${window.location.hostname}:8000` : "http://localhost:8000");

// ---------- auth ----------
export type User = {
  user_id: string;
  username: string;
  display_name: string;
  is_admin: boolean;
  onboarded: boolean;
  level_estimate: string | null;
};

export function getToken(): string | null {
  return typeof window === "undefined" ? null : localStorage.getItem("lengua_token");
}

export function getUser(): User | null {
  if (typeof window === "undefined") return null;
  const raw = localStorage.getItem("lengua_user");
  return raw ? (JSON.parse(raw) as User) : null;
}

export function setAuth(token: string, user: User) {
  localStorage.setItem("lengua_token", token);
  localStorage.setItem("lengua_user", JSON.stringify(user));
}

export function updateStoredUser(patch: Partial<User>) {
  const u = getUser();
  if (u) localStorage.setItem("lengua_user", JSON.stringify({ ...u, ...patch }));
}

export function clearAuth() {
  localStorage.removeItem("lengua_token");
  localStorage.removeItem("lengua_user");
}

/** fetch con Bearer-Token; un 401 manda de vuelta al login (sesión caducada). */
export async function apiFetch(path: string, init?: RequestInit): Promise<Response> {
  const token = getToken();
  const res = await fetch(`${API}${path}`, {
    ...init,
    headers: {
      ...(init?.headers ?? {}),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
  });
  if (res.status === 401 && typeof window !== "undefined" &&
      !window.location.pathname.startsWith("/login")) {
    clearAuth();
    window.location.href = "/login";
  }
  return res;
}

// ---------- estados de concepto ----------
// Labels aus dem Sprachpaket; die Werte selbst sind sprachneutrale Identifier.
export const STATE_LABEL: Record<string, string> = S.stateLabels;

export const STATE_STYLE: Record<string, string> = {
  aprendiendo: "bg-accent-100 text-accent-800",
  flojo: "bg-orange-50 text-orange-700",
  visto: "bg-stone-100 text-stone-500",
  dominado: "bg-green-50 text-green-700",
  sin_ver: "bg-stone-50 text-stone-400",
};
