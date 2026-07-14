"use client";

/** Entrar — el admin crea las cuentas, aquí solo se entra. Token: 30 días. */

import { useState } from "react";
import { useRouter } from "next/navigation";
import { apiFetch, setAuth, type User } from "@/lib/api";
import { S } from "@/lib/strings";

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
        setError(res.status === 401 ? S.loginWrong : S.loginFailed);
        return;
      }
      const data: { token: string; user: User } = await res.json();
      setAuth(data.token, data.user);
      router.push(data.user.onboarded ? "/" : "/nivel");
    } catch {
      setError(S.loginNoBackend);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="flex min-h-[70dvh] flex-col justify-center">
      <h1 className="mb-1 text-2xl font-bold">{S.loginHello}</h1>
      <p className="mb-6 text-sm text-stone-500">{S.loginSub}</p>

      <form onSubmit={submit} className="space-y-3">
        <input
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          placeholder={S.loginUser}
          autoCapitalize="none"
          autoCorrect="off"
          className="w-full rounded-xl border border-stone-300 bg-white px-4 py-3 text-base outline-none focus:border-accent-500"
        />
        <input
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder={S.loginPass}
          type="password"
          className="w-full rounded-xl border border-stone-300 bg-white px-4 py-3 text-base outline-none focus:border-accent-500"
        />
        <button
          type="submit"
          disabled={busy || !username || !password}
          className="w-full rounded-xl bg-accent-600 py-3 text-base font-semibold text-white disabled:opacity-40 active:scale-[0.99]"
        >
          {busy ? S.loggingIn : S.loginBtn}
        </button>
      </form>

      {error && <p className="mt-4 rounded-lg bg-red-50 p-3 text-sm text-red-700">{error}</p>}
    </div>
  );
}
