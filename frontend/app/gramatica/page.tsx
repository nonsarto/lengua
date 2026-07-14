"use client";

/**
 * Gramática — la lista de capítulos, ordenada por score: los calientes arriba,
 * los dominados y nunca-tocados abajo, como referencia tranquila.
 */

import { useEffect, useState } from "react";
import Link from "next/link";
import { API, STATE_LABEL, STATE_STYLE } from "@/lib/api";

type ConceptRow = {
  slug: string;
  label: string;
  ctype: string;
  cefr: string | null;
  state: string;
  need_count: number;
  priority: number;
  reviewed: boolean;
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
          {!c.reviewed && <span className="text-stone-300">borrador</span>}
        </p>
      </div>
      <span className="shrink-0 text-stone-300">→</span>
    </Link>
  );
}

export default function Gramatica() {
  const [rows, setRows] = useState<ConceptRow[] | null>(null);

  useEffect(() => {
    fetch(`${API}/concepts`)
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then(setRows)
      .catch(() => setRows([]));
  }, []);

  if (rows === null) return <p className="text-sm text-stone-400">cargando…</p>;

  const hot = rows.filter((r) => r.priority > 0 || r.state === "aprendiendo");
  const quiet = rows.filter((r) => !hot.includes(r));

  return (
    <>
      <h1 className="mb-4 text-2xl font-bold">Gramática</h1>

      {hot.length > 0 && (
        <section className="mb-6">
          <h2 className="mb-2 text-sm font-semibold uppercase tracking-wide text-stone-500">
            Lo tuyo ahora
          </h2>
          <div className="divide-y divide-stone-100 rounded-xl border border-amber-200 bg-white">
            {hot.map((c) => <Row key={c.slug} c={c} />)}
          </div>
        </section>
      )}

      <section>
        <h2 className="mb-2 text-sm font-semibold uppercase tracking-wide text-stone-500">
          Referencia
        </h2>
        <div className="divide-y divide-stone-100 rounded-xl border border-stone-200 bg-white">
          {quiet.map((c) => <Row key={c.slug} c={c} />)}
        </div>
      </section>
    </>
  );
}
