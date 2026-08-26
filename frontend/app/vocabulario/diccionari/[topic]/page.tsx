"use client";

/**
 * Un tema del Diccionari bàsic: paraules per freqüència, amb un toc per afegir-les
 * al teu repàs (SRS). Les que ja tens es mostren en calma.
 */

import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { apiFetch } from "@/lib/api";
import { S } from "@/lib/strings";
import { PageHead } from "@/components/ui";

type Word = {
  id: string;
  term: string;
  translation: string;
  register: string;
  freq_rank: number;
  cefr: string | null;
  is_phrase: boolean;
  note: string | null;
  added: boolean;
};

export default function DiccionariTema() {
  const { topic } = useParams<{ topic: string }>();
  const decoded = decodeURIComponent(topic);
  const [words, setWords] = useState<Word[] | null>(null);
  const [missing, setMissing] = useState(false);

  useEffect(() => {
    apiFetch(`/diccionari/${encodeURIComponent(decoded)}`)
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then((d) => setWords(d.words))
      .catch(() => setMissing(true));
  }, [decoded]);

  async function add(w: Word) {
    setWords((ws) => ws!.map((x) => (x.id === w.id ? { ...x, added: true } : x)));
    try {
      const res = await apiFetch(`/diccionari/${w.id}/add`, { method: "POST" });
      if (!res.ok) throw new Error();
    } catch {
      setWords((ws) => ws!.map((x) => (x.id === w.id ? { ...x, added: false } : x)));
    }
  }

  if (missing)
    return (
      <>
        <p className="text-sm text-stone-400">{S.situationMissing}</p>
        <p className="mt-4">
          <Link href="/vocabulario" className="text-sm text-stone-500 underline-offset-2 hover:underline">
            ← {S.vocabularioTitle}
          </Link>
        </p>
      </>
    );
  if (!words) return <p className="text-sm text-stone-400">{S.loading}</p>;

  return (
    <>
      <PageHead backHref="/vocabulario" backLabel={S.dictTitle} />
      <h1 className="mb-5 font-display text-2xl font-bold capitalize">{decoded}</h1>

      <ul className="divide-y divide-stone-100 rounded-2xl border border-stone-200 bg-white">
        {words.map((w) => (
          <li key={w.id} className="flex items-center justify-between gap-3 p-3">
            <div className="min-w-0">
              <p className="font-medium">
                {w.term}
                {w.is_phrase && <span className="ml-1.5 rounded-[5px] bg-stone-100 px-1.5 py-px text-[9px] font-semibold uppercase tracking-wide text-stone-500">frase</span>}
              </p>
              <p className="truncate text-sm text-stone-500">
                {w.translation}
                {w.register !== "neutral" ? ` · ${w.register}` : ""}
              </p>
              {w.note && <p className="truncate text-xs italic text-stone-400">{w.note}</p>}
            </div>
            {w.added ? (
              <span className="shrink-0 text-xs text-green-700">{S.dictAdded}</span>
            ) : (
              <button
                onClick={() => add(w)}
                className="shrink-0 rounded-lg border border-accent-300 px-3 py-1 text-xs font-semibold text-accent-700 active:scale-95 transition-transform"
              >
                + {S.dictAdd}
              </button>
            )}
          </li>
        ))}
      </ul>
    </>
  );
}
