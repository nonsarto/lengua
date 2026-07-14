"use client";

/** Entrar — el admin crea las cuentas, aquí solo se entra. El token vive 30 días. */

import { useState } from "react";
import { useRouter } from "next/navigation";
import { API, setAuth, type User } from "@/lib/api";

export default function Login() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      const res = await apiFetch(`/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });
      if (!res.ok) {
        setError(res.status === 401 ? "Usuario o contraseña incorrectos." : "Algo falló.");
        return;
      }
      const data: { token: string; user: User } = await res.json();
      setAuth(data.token, data.user);
      router.push(data.user.onboarded ? "/" : "/nivel");
    } catch {
      setError("No hay conexión con el backend.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="flex min-h-[70dvh] flex-col justify-center">
      <h1 className="mb-1 text-2xl font-bold">Hola 👋</h1>
      <p className="mb-6 text-sm text-stone-500">Entra para seguir aprendiendo.</p>

      <form onSubmit={submit} className="space-y-3">
        <input
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          placeholder="usuario"
          autoCapitalize="none"
          autoCorrect="off"
          className="w-full rounded-xl border border-stone-300 bg-white px-4 py-3 text-base outline-none focus:border-amber-500"
        />
        <input
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="contraseña"
          type="password"
          className="w-full rounded-xl border border-stone-300 bg-white px-4 py-3 text-base outline-none focus:border-amber-500"
        />
        <button
          type="submit"
          disabled={busy || !username || !password}
          className="w-full rounded-xl bg-amber-600 py-3 text-base font-semibold text-white disabled:opacity-40 active:scale-[0.99]"
        >
          {busy ? "entrando…" : "Entrar"}
        </button>
      </form>

      {error && <p className="mt-4 rounded-lg bg-red-50 p-3 text-sm text-red-700">{error}</p>}
    </div>
  );
}
