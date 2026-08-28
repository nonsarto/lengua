"use client";

/**
 * Temario — el catálogo completo de gramática, nivel a nivel (A1-B2). Anders als
 * /gramatica (score-sortiert, deine Themen zuerst) ist das hier das Curriculum in
 * fester Reihenfolge. Die Dots rechts sind der Connect Layer: welche Themen dir in
 * deinen Captures schon begegnet sind, bevor du sie überhaupt gelernt hast.
 */

import { useEffect, useState } from "react";
import Link from "next/link";
import { apiFetch } from "@/lib/api";
import { S } from "@/lib/strings";
import { ErrorState, PageHead, StateDots, cardQuiet } from "@/components/ui";

type TopicRow = {
  slug: string;
  level: "A1" | "A2" | "B1" | "B2";
  title_es: string;
  subtitle_de: string | null;
  state: string;
  has_lesson: boolean;
};

const LEVELS: TopicRow["level"][] = ["A1", "A2", "B1", "B2"];

function Row({ t }: { t: TopicRow }) {
  return (
    <Link
      href={`/gramatica/temario/${t.slug}`}
      className="flex items-center justify-between gap-3 p-3.5 active:bg-stone-50"
    >
      <div className="min-w-0">
        <p className="truncate font-medium">{t.title_es}</p>
        <p className="mt-0.5 truncate text-xs text-stone-400">
          {t.subtitle_de}
          {!t.has_lesson && <span className="text-stone-300"> · {S.draft}</span>}
        </p>
      </div>
      <StateDots state={t.state} />
    </Link>
  );
}

export default function Temario() {
  const [rows, setRows] = useState<TopicRow[] | null>(null);
  const [failed, setFailed] = useState(false);

  function load() {
    setFailed(false);
    setRows(null);
    apiFetch(`/grammar/topics`)
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then(setRows)
      .catch(() => setFailed(true)); // Fehler sichtbar machen, nie als leere Liste tarnen
  }

  useEffect(load, []);

  if (failed)
    return (
      <>
        <PageHead backHref="/gramatica" backLabel={S.gramaticaTitle} title={S.temarioTitle} serif />
        <ErrorState onRetry={load} />
      </>
    );
  if (rows === null) return <p className="text-sm text-stone-400">{S.loading}</p>;

  return (
    <>
      <PageHead backHref="/gramatica" backLabel={S.gramaticaTitle} title={S.temarioTitle} serif />

      {LEVELS.map((level) => {
        const items = rows.filter((r) => r.level === level);
        if (items.length === 0) return null;
        return (
          <section key={level} className="mb-6">
            <h2 className="mb-2 flex items-baseline gap-2 text-xs font-semibold uppercase tracking-[.12em] text-stone-500">
              {level}
              <span className="font-normal text-stone-300">· {S.temarioCount(items.length)}</span>
            </h2>
            <div className={`divide-y divide-stone-100 ${cardQuiet}`}>
              {items.map((t) => <Row key={t.slug} t={t} />)}
            </div>
          </section>
        );
      })}
    </>
  );
}
