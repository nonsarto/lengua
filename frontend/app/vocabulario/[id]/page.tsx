"use client";

/**
 * Un estante = una situación: vocabulario clave, frases con intención, y la gramática
 * que esto activa — ENLACES a los capítulos (con el porqué), nunca la explicación copiada.
 */

import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { apiFetch } from "@/lib/api";
import { S } from "@/lib/strings";

type Detail = {
  id: string;
  name: string;
  is_seed: boolean;
  words: { id: string; term: string; translation: string; register: string; region: string | null }[];
  phrases: { intent: string; es: string; de: string }[];
  concepts: { slug: string; label: string; cefr: string | null; why: string | null }[];
};

export default function Estante() {
  const { id } = useParams<{ id: string }>();
  const [d, setD] = useState<Detail | null>(null);
  const [missing, setMissing] = useState(false);

  useEffect(() => {
    apiFetch(`/situations/${id}`)
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then(setD)
      .catch(() => setMissing(true));
  }, [id]);

  if (missing) return <p className="text-sm text-stone-400">{S.situationMissing}</p>;
  if (!d) return <p className="text-sm text-stone-400">{S.loading}</p>;

  return (
    <>
      <p className="mb-1 text-xs text-stone-400">
        <Link href="/vocabulario" className="underline-offset-2 hover:underline">
          {S.vocabularioTitle}
        </Link>
        {" / "}{S.shelfCrumb}
      </p>
      <h1 className="mb-5 text-2xl font-bold">{d.name}</h1>

      {d.words.length > 0 && (
        <section className="mb-6">
          <h2 className="mb-2 text-sm font-semibold uppercase tracking-wide text-stone-500">
            {S.keyVocab}
          </h2>
          <ul className="divide-y divide-stone-100 rounded-xl border border-stone-200 bg-white">
            {d.words.map((w) => (
              <li key={w.id} className="flex items-baseline justify-between gap-3 p-3">
                <span className="font-medium">{w.term}</span>
                <span className="min-w-0 truncate text-right text-sm text-stone-500">
                  {w.translation}
                  {w.register !== "neutral" ? ` · ${w.register}` : ""}
                </span>
              </li>
            ))}
          </ul>
        </section>
      )}

      {d.phrases.length > 0 && (
        <section className="mb-6">
          <h2 className="mb-2 text-sm font-semibold uppercase tracking-wide text-stone-500">
            {S.intentPhrases}
          </h2>
          <ul className="space-y-2">
            {d.phrases.map((p, i) => (
              <li key={i} className="rounded-xl border border-stone-200 bg-white p-3.5">
                <p className="text-[11px] uppercase tracking-wide text-accent-700">{p.intent}</p>
                <p className="mt-1 text-base font-medium">{p.es}</p>
                <p className="mt-0.5 text-sm text-stone-500">{p.de}</p>
              </li>
            ))}
          </ul>
        </section>
      )}

      {d.concepts.length > 0 && (
        <section className="mb-6">
          <h2 className="mb-2 text-sm font-semibold uppercase tracking-wide text-stone-500">
            {S.activatedGrammar}
          </h2>
          <ul className="space-y-2">
            {d.concepts.map((c) => (
              <li key={c.slug}>
                <Link
                  href={`/gramatica/${c.slug}`}
                  className="block rounded-xl border border-accent-200 bg-accent-50/50 p-3.5 active:scale-[0.99]"
                >
                  <p className="flex items-center justify-between font-medium">
                    {c.label} <span className="text-stone-400">→</span>
                  </p>
                  {c.why && <p className="mt-0.5 text-sm text-stone-600">{c.why}</p>}
                </Link>
              </li>
            ))}
          </ul>
        </section>
      )}
    </>
  );
}
