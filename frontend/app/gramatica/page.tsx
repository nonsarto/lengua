"use client";

/**
 * Gramática — la lista de capítulos, ordenada por score: los calientes arriba,
 * la referencia en desplegables tranquilos. Azulejo: Lernstand als Tinte (Dots),
 * nur "braucht dich" trägt Akzent. Geübt wird in Practicar — hier wird gelesen.
 */

import { useEffect, useState } from "react";
import Link from "next/link";
import { apiFetch } from "@/lib/api";
import { S } from "@/lib/strings";
import SubirMaterial from "@/components/SubirMaterial";
import { ErrorState, NeedLine, PageHead, StateDots, cardQuiet } from "@/components/ui";

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
  return (
    <Link
      href={`/gramatica/${c.slug}`}
      className="flex items-center justify-between gap-3 p-3.5 active:bg-stone-50"
    >
      <div className="min-w-0">
        <p className="truncate font-medium">{c.label}</p>
        <p className="mt-0.5 flex items-center gap-1.5 text-xs text-stone-400">
          <NeedLine state={c.state} needCount={c.need_count} />
          {c.state !== "flojo" && c.state !== "aprendiendo" && c.cefr && <span>{c.cefr}</span>}
          {!c.reviewed && <span className="text-stone-300">{S.draft}</span>}
        </p>
      </div>
      <StateDots state={c.state} />
    </Link>
  );
}

export default function Gramatica() {
  const [rows, setRows] = useState<ConceptRow[] | null>(null);
  const [failed, setFailed] = useState(false);

  function load() {
    setFailed(false);
    setRows(null);
    apiFetch(`/concepts`)
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then(setRows)
      .catch(() => setFailed(true));   // Fehler sichtbar machen, nie als leere Liste tarnen
  }

  useEffect(load, []);

  if (failed)
    return (
      <>
        <PageHead title={S.gramaticaTitle} serif />
        <ErrorState onRetry={load} />
      </>
    );
  if (rows === null) return <p className="text-sm text-stone-400">{S.loading}</p>;

  const hot = rows.filter((r) => r.priority > 0 || r.state === "aprendiendo");
  const quiet = rows.filter((r) => !hot.includes(r));

  const touched = rows.filter((r) => r.state !== "sin_ver").length;
  const dominated = rows.filter((r) => r.state === "dominado").length;

  const categories: string[] = [];
  for (const r of quiet) if (!categories.includes(r.category)) categories.push(r.category);
  const clusters = categories.map((cat) => ({
    cat,
    items: quiet.filter((r) => r.category === cat),
  }));

  return (
    <>
      <h1 className="mb-1 font-display text-2xl font-bold">{S.gramaticaTitle}</h1>
      <p className="mb-4 text-xs tabular-nums text-stone-400">
        {S.summary(rows.length, touched, hot.length, dominated)}
      </p>

      <SubirMaterial />

      {/* El Temario — das feste Curriculum A1-B2, komplementär zur Score-Liste hier */}
      <Link
        href="/gramatica/temario"
        className={`mb-6 flex items-center justify-between gap-3 p-3.5 ${cardQuiet} active:bg-stone-50`}
      >
        <div className="min-w-0">
          <p className="font-medium">{S.temarioLink}</p>
          <p className="mt-0.5 truncate text-xs text-stone-400">{S.temarioLinkDesc}</p>
        </div>
        <span className="text-stone-300">›</span>
      </Link>

      {/* Tus temas — offen, weil sie dich brauchen */}
      {hot.length > 0 && (
        <details open className={`group mb-6 ${cardQuiet}`}>
          <summary className="flex cursor-pointer select-none items-center justify-between p-3.5 text-xs font-semibold uppercase tracking-[.12em] text-stone-500 [&::-webkit-details-marker]:hidden">
            <span>
              {S.yoursNow} <span className="font-normal text-stone-300">· {hot.length}</span>
            </span>
            <span className="text-stone-300 transition-transform group-open:rotate-90">›</span>
          </summary>
          <div className="divide-y divide-stone-100 border-t border-stone-100">
            {hot.map((c) => <Row key={c.slug} c={c} />)}
          </div>
        </details>
      )}

      {clusters.map(({ cat, items }) => (
        <details key={cat} className={`group mb-2 ${cardQuiet}`}>
          <summary className="flex cursor-pointer select-none items-center justify-between p-3.5 text-xs font-semibold uppercase tracking-[.12em] text-stone-500 [&::-webkit-details-marker]:hidden">
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
