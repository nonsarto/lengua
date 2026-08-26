"use client";

/**
 * Hablar — Übersicht des Speaking Bots: Fehler-Top-3 als Metrik-Kacheln,
 * darunter die Sessions als bordered rows (keine Cards). ES-only-Feature.
 */

import { useEffect, useState } from "react";
import Link from "next/link";
import { apiFetch } from "@/lib/api";
import { S } from "@/lib/strings";
import { IconChevronRight } from "@/components/icons";

type Overview = {
  top_errors: { error_type: string; count: number }[];
  open_chunks: number;
  sessions: {
    id: string;
    created_at: string;
    duration_sec: number | null;
    snippet: string;
    error_count: number;
    chunk_count: number;
  }[];
};

function fmtDate(iso: string) {
  return new Date(iso).toLocaleDateString("es-ES", {
    weekday: "short", day: "numeric", month: "short",
  });
}

function fmtDuration(sec: number | null) {
  if (!sec) return "";
  const m = Math.floor(sec / 60);
  return `${m}:${String(sec % 60).padStart(2, "0")}`;
}

export default function Hablar() {
  const [data, setData] = useState<Overview | null>(null);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    apiFetch(`/hablar`)
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then(setData)
      .catch(() => setFailed(true));
  }, []);

  if (failed) return <p className="text-sm text-stone-400">{S.loadFailed}</p>;
  if (data === null) return <p className="text-sm text-stone-400">{S.loading}</p>;

  return (
    <>
      <h1 className="mb-1 font-display text-2xl font-bold">{S.hablarTitle}</h1>
      <p className="mb-4 text-xs text-stone-400">
        {data.open_chunks} {S.hablarOpenChunks}
      </p>

      {data.top_errors.length > 0 && (
        <div className="mb-6 grid grid-cols-3 gap-2">
          {data.top_errors.map((t) => (
            <div key={t.error_type} className="rounded-2xl border border-stone-200 bg-white p-3">
              <p className="text-2xl font-bold text-accent-700">{t.count}</p>
              <p className="mt-0.5 truncate text-xs text-stone-500">
                {S.errorTypeLabels[t.error_type] ?? t.error_type}
              </p>
              <p className="text-[10px] uppercase tracking-wide text-stone-300">
                {S.hablarErrors14d}
              </p>
            </div>
          ))}
        </div>
      )}

      {data.sessions.length === 0 ? (
        <p className="text-sm text-stone-400">{S.hablarEmpty}</p>
      ) : (
        <div className="rounded-2xl border border-stone-200 bg-white">
          <div className="divide-y divide-stone-100">
            {data.sessions.map((s) => (
              <Link
                key={s.id}
                href={`/hablar/${s.id}`}
                className="flex items-center justify-between gap-3 p-3.5 active:bg-stone-50"
              >
                <div className="min-w-0">
                  <p className="flex items-center gap-2 text-sm font-medium">
                    {fmtDate(s.created_at)}
                    <span className="font-normal text-stone-400">{fmtDuration(s.duration_sec)}</span>
                  </p>
                  <p className="mt-0.5 truncate text-xs text-stone-400">{s.snippet}…</p>
                  <p className="mt-0.5 text-xs text-stone-400">
                    {S.hablarSessionErrors(s.error_count)} · {S.hablarSessionChunks(s.chunk_count)}
                  </p>
                </div>
                <IconChevronRight className="h-4 w-4 shrink-0 text-stone-300" />
              </Link>
            ))}
          </div>
        </div>
      )}
    </>
  );
}
