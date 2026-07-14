"use client";

/**
 * Gramática/Gramàtica — la lista de capítulos, ordenada por score: los calientes arriba,
 * la referencia en desplegables tranquilos. Textos de lib/strings (es/ca).
 * El orden de los clusters viene del backend (por idioma) — aquí solo se agrupa.
 */

import { useEffect, useState } from "react";
import Link from "next/link";
import { apiFetch, STATE_LABEL, STATE_STYLE } from "@/lib/api";
import { S } from "@/lib/strings";

type ConceptRow = {
  slug: string;
  label: string;
  ctype: string;
  cefr: string | null;
  state: string;
  need_count: number;
  priority: number;
  reviewed: boolean;
  category: string;
};

function Row({ c }: { c: ConceptRow }) {
  const active = c.priority > 0;
  return (
    <Link
      href={`/gramatica/${c.slug}`}
      className={`flex items-center justify-between gap-3 p-3.5 active:bg-stone-50 ${
        active ? "" : "opacity-80"
      }`}
    >
      <div className="min-w-0">
        <p className="truncate font-medium">{c.label}</p>
        <p className="mt-0.5 flex items-center gap-1.5 text-xs text-stone-400">
          {c.cefr && <span>{c.cefr}</span>}
          {c.state !== "sin_ver" && (
            <span className={`rounded-full px-1.5 py-px ${STATE_STYLE[c.state]}`}>
              {STATE_LABEL[c.state]}
            </span>
          )}
          {!c.reviewed && <span className="text-stone-300">{S.draft}</span>}
        </p>
      </div>
      <span className="shrink-0 text-stone-300">→</span>
    </Link>
  );
}

export default function Gramatica() {
  const [rows, setRows] = useState<ConceptRow[] | null>(null);

  useEffect(() => {
    apiFetch(`/concepts`)
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then(setRows)
      .catch(() => setRows([]));
  }, []);

  if (rows === null) return <p className="text-sm text-stone-400">{S.loading}</p>;

  const hot = rows.filter((r) => r.priority > 0 || r.state === "aprendiendo");
  const quiet = rows.filter((r) => !hot.includes(r));

  const touched = rows.filter((r) => r.state !== "sin_ver").length;
  const dominated = rows.filter((r) => r.state === "dominado").length;

  // Cluster-Reihenfolge: wie sie (score-sortiert) vom Backend kommen, Kategorien dedupliziert
  const categories: string[] = [];
  for (const r of quiet) if (!categories.includes(r.category)) categories.push(r.category);
  const clusters = categories.map((cat) => ({
    cat,
    items: quiet.filter((r) => r.category === cat),
  }));

  return (
    <>
      <h1 className="mb-1 text-2xl font-bold">{S.gramaticaTitle}</h1>
      <p className="mb-4 text-xs text-stone-400">
        {S.summary(rows.length, touched, hot.length, dominated)}
      </p>

      {hot.length > 0 && (
        <section className="mb-6">
          <h2 className="mb-2 text-sm font-semibold uppercase tracking-wide text-stone-500">
            {S.yoursNow}
          </h2>
          <div className="divide-y divide-stone-100 rounded-xl border border-accent-200 bg-white">
            {hot.map((c) => <Row key={c.slug} c={c} />)}
          </div>
        </section>
      )}

      {clusters.map(({ cat, items }) => (
        <details key={cat} className="group mb-2 rounded-xl border border-stone-200 bg-white">
          <summary className="flex cursor-pointer select-none items-center justify-between p-3.5 text-sm font-semibold uppercase tracking-wide text-stone-500 [&::-webkit-details-marker]:hidden">
            <span>
              {cat} <span className="font-normal text-stone-300">· {items.length}</span>
            </span>
            <span className="text-stone-300 transition-transform group-open:rotate-90">›</span>
          </summary>
          <div className="divide-y divide-stone-100 border-t border-stone-100">
            {items.map((c) => <Row key={c.slug} c={c} />)}
          </div>
        </details>
      ))}
    </>
  );
}
