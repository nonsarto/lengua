"use client";

/** Perfil — quién eres, salir, y (solo admin) gestión de usuarios:
 *  contraseña · Telegram-Pairing-Link (Speaking Bot) · eliminar. */

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { apiFetch, clearAuth, getUser, type User } from "@/lib/api";
import { S } from "@/lib/strings";
import { PageHead, btnGhost, btnPrimary, btnSecondary, cardQuiet } from "@/components/ui";

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
  // localStorage erst nach dem Mount lesen — direkt im Render bricht die Hydration
  const [me, setMe] = useState<User | null>(null);
  const [users, setUsers] = useState<Row[]>([]);
  const [newUser, setNewUser] = useState({ username: "", display_name: "", password: "" });
  const [msg, setMsg] = useState<string | null>(null);
  const [tgLink, setTgLink] = useState<{ username: string; link: string } | null>(null);
  const [copied, setCopied] = useState(false);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    setMe(getUser());
  }, []);

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
        setMsg(data.detail ?? S.somethingFailed);
        return;
      }
      setMsg(S.userCreated(data.username));
      setNewUser({ username: "", display_name: "", password: "" });
      const list = await apiFetch("/admin/users");
      if (list.ok) setUsers(await list.json());
    } finally {
      setBusy(false);
    }
  }

  async function resetPassword(u: Row) {
    const pw = window.prompt(S.newPassPrompt(u.username ?? "?"));
    if (!pw) return;
    const res = await apiFetch(`/admin/users/${u.user_id}/password`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ password: pw }),
    });
    const data = await res.json().catch(() => ({}));
    setMsg(res.ok ? S.passChanged(u.username ?? "?") : (data.detail ?? S.somethingFailed));
  }

  async function deleteUser(u: Row) {
    if (!window.confirm(S.adminDeleteConfirm(u.username ?? "?"))) return;
    const res = await apiFetch(`/admin/users/${u.user_id}`, { method: "DELETE" });
    const data = await res.json().catch(() => ({}));
    if (res.ok) {
      setMsg(S.adminDeleted(u.username ?? "?"));
      setUsers((rows) => rows.filter((r) => r.user_id !== u.user_id));
    } else {
      setMsg(data.detail ?? S.somethingFailed);
    }
  }

  async function telegramLink(u: Row) {
    setMsg(null);
    setTgLink(null);
    setCopied(false);
    try {
      const res = await apiFetch(`/admin/users/${u.user_id}/telegram-link`, { method: "POST" });
      if (!res.ok) throw new Error();
      const data = await res.json();
      setTgLink({ username: u.username ?? "?", link: data.link });
    } catch {
      setMsg(S.adminTelegramFailed);
    }
  }

  async function copyLink() {
    if (!tgLink) return;
    try {
      await navigator.clipboard.writeText(tgLink.link);
      setCopied(true);
    } catch {
      /* Clipboard nicht verfügbar — der Link ist markierbar */
    }
  }

  return (
    <>
      <PageHead title={S.perfilTitle} />

      <div className={`${cardQuiet} mb-6 p-4`}>
        <p className="font-medium">{me?.display_name ?? "—"}</p>
        <p className="mt-0.5 text-sm text-stone-500">
          @{me?.username}
          {me?.level_estimate ? ` · ${S.levelPrefix}${me.level_estimate}` : ""}
          {me?.is_admin ? ` · ${S.adminTag}` : ""}
        </p>
        <button onClick={logout} className={`mt-3 ${btnSecondary}`}>
          {S.logoutBtn}
        </button>
      </div>

      {me?.is_admin && (
        <section>
          <h2 className="mb-2 text-xs font-semibold uppercase tracking-[.12em] text-stone-400">
            {S.usersTitle}
          </h2>

          <div className={`${cardQuiet} mb-3 divide-y divide-stone-100`}>
            {users.map((u) => (
              <div key={u.user_id} className="p-3">
                <div className="flex items-center justify-between gap-2">
                  <div className="min-w-0">
                    <p className="truncate font-medium">
                      {u.display_name}{" "}
                      {u.is_admin && <span className="text-xs text-accent-700">{S.adminTag}</span>}
                    </p>
                    <p className="text-xs text-stone-400">
                      @{u.username}
                      {u.level_estimate ? ` · ~${u.level_estimate}` : ""}
                      {!u.onboarded_at ? ` · ${S.testPending}` : ""}
                    </p>
                  </div>
                </div>
                <p className="mt-1.5 flex gap-4 text-xs">
                  <button onClick={() => resetPassword(u)} className={`${btnGhost} text-xs`}>
                    {S.passwordBtn}
                  </button>
                  <button onClick={() => telegramLink(u)} className={`${btnGhost} text-xs text-accent-700`}>
                    {S.adminTelegramBtn}
                  </button>
                  {u.user_id !== me?.user_id && (
                    <button onClick={() => deleteUser(u)} className={`${btnGhost} text-xs text-red-600`}>
                      {S.adminDeleteBtn}
                    </button>
                  )}
                </p>
              </div>
            ))}
          </div>

          {tgLink && (
            <div className={`${cardQuiet} mb-3 p-3`}>
              <p className="text-xs text-stone-500">{S.adminTelegramLink(tgLink.username)}</p>
              <p className="mt-1 break-all font-mono text-sm text-accent-700 select-all">{tgLink.link}</p>
              <button onClick={copyLink} className={`mt-2 ${btnSecondary} text-xs`}>
                {copied ? S.adminTelegramCopied : S.adminTelegramCopy}
              </button>
            </div>
          )}

          <form onSubmit={createUser} className={`${cardQuiet} p-4`}>
            <p className="mb-2 text-sm font-semibold">{S.newUserTitle}</p>
            <div className="space-y-2">
              <input
                value={newUser.username}
                onChange={(e) => setNewUser({ ...newUser, username: e.target.value })}
                placeholder={S.userPlaceholder}
                autoCapitalize="none"
                className="w-full rounded-xl border border-stone-300 px-3 py-2 text-sm outline-none focus:border-accent-500"
              />
              <input
                value={newUser.display_name}
                onChange={(e) => setNewUser({ ...newUser, display_name: e.target.value })}
                placeholder={S.namePlaceholder}
                className="w-full rounded-xl border border-stone-300 px-3 py-2 text-sm outline-none focus:border-accent-500"
              />
              <input
                value={newUser.password}
                onChange={(e) => setNewUser({ ...newUser, password: e.target.value })}
                placeholder={S.passPlaceholder}
                type="password"
                className="w-full rounded-xl border border-stone-300 px-3 py-2 text-sm outline-none focus:border-accent-500"
              />
              <button type="submit" disabled={busy || !newUser.username || newUser.password.length < 8}
                      className={btnPrimary}>
                {S.createBtn}
              </button>
            </div>
          </form>

          {msg && <p className="mt-3 text-sm text-stone-600">{msg}</p>}
        </section>
      )}
    </>
  );
}
