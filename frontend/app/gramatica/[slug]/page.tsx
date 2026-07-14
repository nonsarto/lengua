"use client";

/**
 * Un capítulo = dos capas.
 * MANTO personal (solo tuyo): si el concepto está promovido, el capítulo ABRE con tus
 * errores reales — "esto es lo que te pasa" — y la regla viene detrás, como explicación.
 * CUERPO compartido (congelado tras revisión): explicación, regla de oro, la trampa
 * alemana, paradigma, ejercicios. Un capítulo tranquilo muestra solo el cuerpo.
 */

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { API, STATE_LABEL, STATE_STYLE } from "@/lib/api";

type Detail = {
  slug: string;
  label: string;
  ctype: string;
  cefr: string | null;
  explanation: string | null;
  rule_of_thumb: string | null;
  german_pitfall: string | null;
  paradigm: Record<string, Record<string, string>> | null;
  member_verbs: string[] | null;
  default_exercises: { q: string; a: string }[] | null;
  reviewed: boolean;
  corrections: { wrong: string; correct: string; created_at: string }[];
  state: { state: string; need_count: number; success_count: number; priority: number };
};

const PERSONS = ["yo", "tu", "el", "nosotros", "vosotros", "ellos"];
const PERSON_LABEL: Record<string, string> = {
  yo: "yo", tu: "tú", el: "él/ella", nosotros: "nosotros", vosotros: "vosotros", ellos: "ellos/ellas",
};

export default function Capitulo() {
  const { slug } = useParams<{ slug: string }>();
  const [d, setD] = useState<Detail | null>(null);
  const [missing, setMissing] = useState(false);

  useEffect(() => {
    fetch(`${API}/concepts/${slug}`)
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then(setD)
      .catch(() => setMissing(true));
  }, [slug]);

  if (missing) return <p className="text-sm text-stone-400">Este capítulo no existe.</p>;
  if (!d) return <p className="text-sm text-stone-400">cargando…</p>;

  const promoted = d.state.state === "aprendiendo" || d.state.state === "flojo";

  return (
    <>
      <p className="mb-1 flex items-center gap-2 text-xs text-stone-400">
        {d.cefr && <span>{d.cefr}</span>}
        <span className={`rounded-full px-1.5 py-px ${STATE_STYLE[d.state.state]}`}>
          {STATE_LABEL[d.state.state]}
        </span>
        {!d.reviewed && <span className="text-stone-300">borrador — sin revisar</span>}
      </p>
      <h1 className="mb-4 text-2xl font-bold">{d.label}</h1>

      {/* EL MANTO — tus errores primero, si el capítulo está caliente */}
      {promoted && d.corrections.length > 0 && (
        <section className="mb-6 rounded-xl border border-amber-300 bg-amber-50/70 p-4">
          <h2 className="mb-2 text-sm font-semibold uppercase tracking-wide text-amber-800">
            Esto es lo que te pasa
          </h2>
          <ul className="space-y-2">
            {d.corrections.slice(0, 3).map((c, i) => (
              <li key={i}>
                <p className="text-sm text-red-700 line-through">{c.wrong}</p>
                <p className="font-medium text-green-800">{c.correct}</p>
              </li>
            ))}
          </ul>
          <p className="mt-2 text-xs text-amber-700">
            {d.state.need_count} {d.state.need_count === 1 ? "vez" : "veces"} capturado — la regla de abajo explica tu problema.
          </p>
        </section>
      )}

      {/* EL CUERPO — la referencia compartida */}
      {d.explanation && <p className="mb-4 text-base leading-relaxed">{d.explanation}</p>}

      {d.rule_of_thumb && (
        <div className="mb-4 rounded-xl border border-stone-200 bg-white p-4">
          <h3 className="mb-1 text-xs font-semibold uppercase tracking-wide text-stone-500">
            Regla de oro
          </h3>
          <p className="text-base">{d.rule_of_thumb}</p>
        </div>
      )}

      {d.german_pitfall && (
        <div className="mb-4 rounded-xl border border-orange-200 bg-orange-50/60 p-4">
          <h3 className="mb-1 text-xs font-semibold uppercase tracking-wide text-orange-700">
            ⚠️ La trampa alemana
          </h3>
          <p className="text-base">{d.german_pitfall}</p>
        </div>
      )}

      {d.paradigm && (
        <div className="mb-4 overflow-x-auto rounded-xl border border-stone-200 bg-white p-4">
          <h3 className="mb-2 text-xs font-semibold uppercase tracking-wide text-stone-500">
            Paradigma
          </h3>
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-xs text-stone-400">
                <th className="py-1 pr-3 font-normal"></th>
                {Object.keys(d.paradigm).map((g) => (
                  <th key={g} className="py-1 pr-3 font-semibold">-{g}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {PERSONS.map((p) => (
                <tr key={p} className="border-t border-stone-100">
                  <td className="py-1 pr-3 text-stone-400">{PERSON_LABEL[p]}</td>
                  {Object.keys(d.paradigm!).map((g) => (
                    <td key={g} className="py-1 pr-3">{d.paradigm![g][p]}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {d.member_verbs && d.member_verbs.length > 0 && (
        <div className="mb-4">
          <h3 className="mb-2 text-xs font-semibold uppercase tracking-wide text-stone-500">
            Verbos de este patrón
          </h3>
          <div className="flex flex-wrap gap-1.5">
            {d.member_verbs.map((v) => (
              <span key={v} className="rounded-full border border-stone-200 bg-white px-2.5 py-0.5 text-sm">
                {v}
              </span>
            ))}
          </div>
        </div>
      )}

      {d.default_exercises && d.default_exercises.length > 0 && (
        <div className="mb-4 rounded-xl border border-stone-200 bg-white p-4">
          <h3 className="mb-2 text-xs font-semibold uppercase tracking-wide text-stone-500">
            Para probar
          </h3>
          <ul className="space-y-2">
            {d.default_exercises.map((ex, i) => (
              <li key={i}>
                <details>
                  <summary className="cursor-pointer text-base">{ex.q}</summary>
                  <p className="mt-1 pl-4 font-medium text-green-700">{ex.a}</p>
                </details>
              </li>
            ))}
          </ul>
        </div>
      )}
    </>
  );
}
