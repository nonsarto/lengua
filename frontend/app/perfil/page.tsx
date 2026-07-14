"use client";

/** Perfil — quién eres, salir, y (solo admin) gestión de usuarios:
 *  crear cuentas con usuario+contraseña y resetear contraseñas. */

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { apiFetch, clearAuth, getUser } from "@/lib/api";

type Row = {
  user_id: string;
  username: string | null;
  display_name: string | null;
  is_admin: boolean;
  level_estimate: string | null;
  onboarded_at: string | null;
  created_at: string;
};

export default function Perfil() {
  const router = useRouter();
  const me = getUser();
  const [users, setUsers] = useState<Row[]>([]);
  const [newUser, setNewUser] = useState({ username: "", display_name: "", password: "" });
  const [msg, setMsg] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (me?.is_admin) {
      apiFetch("/admin/users")
        .then((r) => (r.ok ? r.json() : []))
        .then(setUsers)
        .catch(() => {});
    }
  }, [me?.is_admin]);

  function logout() {
    clearAuth();
    router.push("/login");
  }

  async function createUser(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setMsg(null);
    try {
      const res = await apiFetch("/admin/users", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(newUser),
      });
      const data = await res.json();
      if (!res.ok) {
        setMsg(data.detail ?? "Algo falló.");
        return;
      }
      setMsg(`Usuario '${data.username}' creado ✓`);
      setNewUser({ username: "", display_name: "", password: "" });
      const list = await apiFetch("/admin/users");
      if (list.ok) setUsers(await list.json());
    } finally {
      setBusy(false);
    }
  }

  async function resetPassword(u: Row) {
    const pw = window.prompt(`Nueva contraseña para '${u.username}' (mín. 8):`);
    if (!pw) return;
    const res = await apiFetch(`/admin/users/${u.user_id}/password`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ password: pw }),
    });
    const data = await res.json().catch(() => ({}));
    setMsg(res.ok ? `Contraseña de '${u.username}' cambiada ✓` : (data.detail ?? "Algo falló."));
  }

  return (
    <>
      <h1 className="mb-4 text-2xl font-bold">Perfil</h1>

      <div className="mb-6 rounded-xl border border-stone-200 bg-white p-4">
        <p className="font-medium">{me?.display_name ?? "—"}</p>
        <p className="mt-0.5 text-sm text-stone-500">
          @{me?.username}
          {me?.level_estimate ? ` · nivel ~${me.level_estimate}` : ""}
          {me?.is_admin ? " · admin" : ""}
        </p>
        <button
          onClick={logout}
          className="mt-3 rounded-lg border border-stone-300 px-4 py-2 text-sm active:scale-95"
        >
          Salir
        </button>
      </div>

      {me?.is_admin && (
        <section>
          <h2 className="mb-2 text-sm font-semibold uppercase tracking-wide text-stone-500">
            Usuarios
          </h2>

          <div className="mb-3 divide-y divide-stone-100 rounded-xl border border-stone-200 bg-white">
            {users.map((u) => (
              <div key={u.user_id} className="flex items-center justify-between p-3">
                <div>
                  <p className="font-medium">
                    {u.display_name}{" "}
                    {u.is_admin && <span className="text-xs text-amber-700">admin</span>}
                  </p>
                  <p className="text-xs text-stone-400">
                    @{u.username}
                    {u.level_estimate ? ` · ~${u.level_estimate}` : ""}
                    {!u.onboarded_at ? " · test pendiente" : ""}
                  </p>
                </div>
                <button
                  onClick={() => resetPassword(u)}
                  className="text-xs text-stone-500 underline-offset-2 hover:underline"
                >
                  contraseña
                </button>
              </div>
            ))}
          </div>

          <form onSubmit={createUser} className="rounded-xl border border-stone-200 bg-white p-4">
            <p className="mb-2 text-sm font-semibold">Nuevo usuario</p>
            <div className="space-y-2">
              <input
                value={newUser.username}
                onChange={(e) => setNewUser({ ...newUser, username: e.target.value })}
                placeholder="usuario (solo letras/números)"
                autoCapitalize="none"
                className="w-full rounded-lg border border-stone-300 px-3 py-2 text-sm outline-none focus:border-amber-500"
              />
              <input
                value={newUser.display_name}
                onChange={(e) => setNewUser({ ...newUser, display_name: e.target.value })}
                placeholder="nombre visible"
                className="w-full rounded-lg border border-stone-300 px-3 py-2 text-sm outline-none focus:border-amber-500"
              />
              <input
                value={newUser.password}
                onChange={(e) => setNewUser({ ...newUser, password: e.target.value })}
                placeholder="contraseña (mín. 8)"
                type="password"
                className="w-full rounded-lg border border-stone-300 px-3 py-2 text-sm outline-none focus:border-amber-500"
              />
              <button
                type="submit"
                disabled={busy || !newUser.username || newUser.password.length < 8}
                className="rounded-lg bg-amber-600 px-4 py-2 text-sm font-semibold text-white disabled:opacity-40 active:scale-95"
              >
                crear
              </button>
            </div>
          </form>

          {msg && <p className="mt-3 text-sm text-stone-600">{msg}</p>}
        </section>
      )}
    </>
  );
}
