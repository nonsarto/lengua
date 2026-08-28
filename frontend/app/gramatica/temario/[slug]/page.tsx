"use client";

/**
 * Una lección del Temario: geteilte, eingefrorene Blöcke (LessonBlocks) + der Status aus
 * dem Connect Layer. Lernstand lebt NIE hier — der Link "tu capítulo conectado" führt zum
 * Konzept-Kapitel mit Manto (deine Fehler, Übungen, Dudas). Verlinken, nie kopieren.
 */

import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { apiFetch } from "@/lib/api";
import { S } from "@/lib/strings";
import { IconArrowLeft } from "@/components/icons";
import LessonBlocks, { Block } from "@/components/LessonBlocks";
import { NeedLine, StateDots, cardQuiet } from "@/components/ui";

type Detail = {
  slug: string;
  level: string;
  title_es: string;
  subtitle_de: string | null;
  lesson: { blocks: Block[]; version: number } | null;
  concept: { slug: string; label: string } | null;
  state: string;
  need_count: number;
};

export default function Tema() {
  const { slug } = useParams<{ slug: string }>();
  const [d, setD] = useState<Detail | null>(null);
  const [missing, setMissing] = useState(false);

  useEffect(() => {
    apiFetch(`/grammar/topics/${slug}`)
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then(setD)
      .catch(() => setMissing(true));
  }, [slug]);

  if (missing)
    return (
      <>
        <p className="text-sm text-stone-400">{S.temarioTopicMissing}</p>
        <p className="mt-4">
          <Link href="/gramatica/temario" className="text-sm text-stone-500 underline-offset-2 hover:underline">
            ← {S.temarioTitle}
          </Link>
        </p>
      </>
    );
  if (!d) return <p className="text-sm text-stone-400">{S.loading}</p>;

  return (
    <>
      <p className="mb-1 flex items-center gap-2 text-xs text-stone-400">
        <span>{d.level}</span>
        <StateDots state={d.state} />
        <NeedLine state={d.state} needCount={d.need_count} />
      </p>
      <h1 className="font-display text-2xl font-bold">{d.title_es}</h1>
      {d.subtitle_de && <p className="mb-4 mt-0.5 text-sm text-stone-400">{d.subtitle_de}</p>}

      {d.lesson ? (
        <LessonBlocks blocks={d.lesson.blocks} />
      ) : (
        <div className="mb-4 rounded-xl border border-dashed border-stone-300 bg-white p-5 text-center">
          <p className="text-sm text-stone-500">{S.temarioLessonPending}</p>
        </div>
      )}

      {/* El puente al Connect Layer: das Kapitel mit deinem Manto (Fehler, Übungen, Dudas) */}
      {d.concept && (
        <Link
          href={`/gramatica/${d.concept.slug}`}
          className={`mb-4 flex items-center justify-between gap-3 p-3.5 ${cardQuiet} active:bg-stone-50`}
        >
          <div className="min-w-0">
            <p className="text-xs font-semibold uppercase tracking-wide text-stone-500">
              {S.temarioConceptLink}
            </p>
            <p className="truncate font-medium">{d.concept.label}</p>
          </div>
          <span className="text-stone-300">›</span>
        </Link>
      )}

      <p className="mt-6">
        <Link href="/gramatica/temario" className="inline-flex items-center gap-1.5 text-sm text-stone-400 underline-offset-4 hover:underline">
          <IconArrowLeft className="h-3.5 w-3.5" />{S.temarioTitle}
        </Link>
      </p>
    </>
  );
}
