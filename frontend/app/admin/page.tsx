"use client";

/** Panel de uso (solo admin) — wer nutzt die App: última actividad, Aktivität
 *  7/30 Tage und LLM-Verbrauch 30 Tage (llm_usage, Migration 016). Verlinkt
 *  aus Perfil → Usuarios. */

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { apiFetch, getUser } from "@/lib/api";
import { S } from "@/lib/strings";
import { PageHead, cardQuiet } from "@/components/ui";

type StatRow = {
  user_id: string;
  username: string | null;
  display_name: string | null;
  is_admin: boolean;
  last_active: string | null;
  sessions_7d: number;
  sessions_30d: number;
  exercises_7d: number;
  exercises_30d: number;
  captures_7d: number;
  captures_30d: number;
  voices_7d: number;
  voices_30d: number;
  voice_min_30d: number;
  tokens_in_30d: number;
  tokens_out_30d: number;
  tokens_cache_30d: number;
  audio_sec_30d: number;
  cost_usd_30d: number;
  cost_partial: boolean;
};

/** 1234 → "1,2k", 2345678 → "2,3M" — Tokens kompakt, wie man sie liest. */
function fmtTokens(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1).replace(".", ",")}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1).replace(".", ",")}k`;
  return String(n);
}

function fmtAgo(iso: string | null): string {
  if (!iso) return S.usoNever;
  const mins = Math.max(0, Math.floor((Date.now() - new Date(iso).getTime()) / 60000));
  if (mins < 60) return S.usoAgo(mins, S.usoUnits.min);
  if (mins < 48 * 60) return S.usoAgo(Math.floor(mins / 60), S.usoUnits.h);
  const days = Math.floor(mins / (24 * 60));
  return S.usoAgo(days, days === 1 ? S.usoUnits.d1 : S.usoUnits.d);
}

export default function Uso() {
  const router = useRouter();
  const [rows, setRows] = useState<StatRow[] | null>(null);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    const me = getUser();
    if (me && !me.is_admin) {
      router.replace("/perfil");
      return;
    }
    apiFetch("/admin/stats")
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then((data) => setRows(data.users))
      .catch(() => setFailed(true));
  }, [router]);

  const totalCost = (rows ?? []).reduce((sum, r) => sum + r.cost_usd_30d, 0);
  const anyPartial = (rows ?? []).some((r) => r.cost_partial);

  return (
    <>
      <PageHead title={S.usoTitle} />

      {failed && <p className="text-sm text-stone-500">{S.usoFailed}</p>}
      {rows && rows.length === 0 && <p className="text-sm text-stone-500">{S.usoEmpty}</p>}

      {rows && rows.length > 0 && (
        <>
          <div className={`${cardQuiet} mb-4 p-3 text-sm text-stone-600`}>
            {S.usoTokens}: {fmtTokens(rows.reduce((s, r) => s + r.tokens_in_30d, 0))} /{" "}
            {fmtTokens(rows.reduce((s, r) => s + r.tokens_out_30d, 0))} ·{" "}
            {S.usoCost(totalCost.toFixed(2).replace(".", ","))}
            {anyPartial ? ` ${S.usoCostPartial}` : ""}
          </div>

          <div className={`${cardQuiet} divide-y divide-stone-100`}>
            {rows.map((r) => (
              <div key={r.user_id} className="p-3">
                <div className="flex items-baseline justify-between gap-2">
                  <p className="truncate font-medium">
                    {r.display_name}{" "}
                    {r.is_admin && <span className="text-xs text-accent-700">{S.adminTag}</span>}
                  </p>
                  <p className="shrink-0 text-xs text-stone-400">
                    {S.usoLastActive}: {fmtAgo(r.last_active)}
                  </p>
                </div>
                <p className="mt-0.5 text-xs text-stone-400">@{r.username}</p>

                <div className="mt-2 grid grid-cols-2 gap-x-4 gap-y-1 text-sm text-stone-600">
                  <span>
                    {S.usoExercises}: {r.exercises_7d} / {r.exercises_30d}
                    <span className="text-xs text-stone-400"> ({S.usoWindow7}/{S.usoWindow30})</span>
                  </span>
                  <span>{S.usoSessions}: {r.sessions_7d} / {r.sessions_30d}</span>
                  <span>{S.usoCaptures}: {r.captures_7d} / {r.captures_30d}</span>
                  <span>
                    {S.usoVoices}: {r.voices_7d} / {r.voices_30d}
                    {r.voice_min_30d > 0 ? ` · ${r.voice_min_30d} min` : ""}
                  </span>
                </div>

                <p className="mt-2 text-xs text-stone-500">
                  {S.usoTokens}: {S.usoTokensInOut(fmtTokens(r.tokens_in_30d), fmtTokens(r.tokens_out_30d))}
                  {r.audio_sec_30d > 0 ? ` · ${S.usoAudioMin(Math.round(r.audio_sec_30d / 60))}` : ""}
                  {" · "}
                  <span className="text-accent-700">
                    {S.usoCost(r.cost_usd_30d.toFixed(2).replace(".", ","))}
                    {r.cost_partial ? ` ${S.usoCostPartial}` : ""}
                  </span>
                </p>
              </div>
            ))}
          </div>
        </>
      )}
    </>
  );
}
