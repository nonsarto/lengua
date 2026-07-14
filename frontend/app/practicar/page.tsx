"use client";

/**
 * Practicar — tres tipos de drill, UNA fuente. Primero eliges el sabor de la sesión
 * (mix / palabras / frases / conjugación); la selección sigue siendo determinista y
 * tira exactamente de donde cojea tu scoring. Solo el vocabulario mueve el SRS.
 */

import { useState } from "react";
import Link from "next/link";
import { API } from "@/lib/api";

type Card =
  | { type: "vocab"; vocab_id: string; prompt: string; answer: string; register: string; is_phrase: boolean }
  | { type: "fix"; prompt: string; answer: string; concept_slug: string; concept_label: string }
  | { type: "conj"; verb: string; verb_de: string; tense: string; person: string | null; answer: string; pattern: string };

const MODES = [
  { tipo: "mix", label: "Mix", desc: "Un poco de todo — donde cojeas ahora" },
  { tipo: "palabras", label: "Palabras", desc: "Solo vocabulario (SRS)" },
  { tipo: "frases", label: "Frases", desc: "Frases con intención de tus preps" },
  { tipo: "conjugacion", label: "Conjugación", desc: "Verbo · tiempo · persona → forma" },
];

export default function Practicar() {
  const [tipo, setTipo] = useState<string | null>(null);
  const [cards, setCards] = useState<Card[] | null>(null);
  const [idx, setIdx] = useState(0);
  const [revealed, setRevealed] = useState(false);
  const [grading, setGrading] = useState(false);
  const [tally, setTally] = useState({ bien: 0, mal: 0 });
  const [loadFailed, setLoadFailed] = useState(false);

  function start(t: string) {
    setTipo(t);
    setCards(null);
    setIdx(0);
    setTally({ bien: 0, mal: 0 });
    setLoadFailed(false);
    fetch(`${API}/practicar/session?tipo=${t}`)
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then((d) => setCards(d.items))
      .catch(() => {
        setLoadFailed(true);
        setCards([]);
      });
  }

  function reset() {
    setTipo(null);
    setCards(null);
  }

  function next() {
    setRevealed(false);
    setIdx((i) => i + 1);
  }

  async function grade(correct: boolean) {
    const card = cards![idx];
    setTally((t) => (correct ? { ...t, bien: t.bien + 1 } : { ...t, mal: t.mal + 1 }));
    if (card.type !== "vocab") return next();
    setGrading(true);
    try {
      await fetch(`${API}/practicar/grade`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ vocab_id: card.vocab_id, correct }),
      });
    } catch {
      /* la nota se pierde en silencio — la tarjeta volverá */
    } finally {
      setGrading(false);
      next();
    }
  }

  // ---------- pantalla 1: elegir sesión ----------
  if (tipo === null) {
    return (
      <>
        <h1 className="mb-4 text-2xl font-bold">Practicar</h1>
        <div className="space-y-2">
          {MODES.map((m) => (
            <button
              key={m.tipo}
              onClick={() => start(m.tipo)}
              className="block w-full rounded-xl border border-stone-200 bg-white p-4 text-left active:scale-[0.99]"
            >
              <p className="font-semibold">{m.label}</p>
              <p className="mt-0.5 text-sm text-stone-500">{m.desc}</p>
            </button>
          ))}
        </div>
      </>
    );
  }

  if (cards === null) return <p className="text-sm text-stone-400">preparando sesión…</p>;

  // ---------- sin tarjetas ----------
  if (cards.length === 0)
    return (
      <>
        <h1 className="mb-4 text-2xl font-bold">Practicar</h1>
        <p className="text-sm text-stone-500">
          {loadFailed
            ? "No se pudo cargar la sesión — ¿backend corriendo?"
            : "Nada pendiente en esta categoría ahora mismo — captura más o prueba otro modo."}
        </p>
        <button onClick={reset} className="mt-3 text-sm text-stone-500 underline-offset-2 hover:underline">
          ← elegir otro modo
        </button>
      </>
    );

  // ---------- fin de sesión: la cuenta ----------
  if (idx >= cards.length) {
    const graded = tally.bien + tally.mal;
    return (
      <>
        <h1 className="mb-4 text-2xl font-bold">Practicar</h1>
        <div className="rounded-xl border border-green-200 bg-green-50/60 p-6 text-center">
          <p className="text-lg font-semibold text-green-800">Sesión terminada ✓</p>
          <p className="mt-1 text-sm text-stone-600">{cards.length} tarjetas repasadas.</p>
          {graded > 0 && (
            <p className="mt-2 text-sm">
              <span className="font-semibold text-green-700">{tally.bien} bien</span>
              {" · "}
              <span className="font-semibold text-red-600">{tally.mal} mal</span>
              {" · "}
              <span className="text-stone-500">{Math.round((tally.bien / graded) * 100)}%</span>
            </p>
          )}
          <div className="mt-4 flex justify-center gap-4 text-sm">
            <button onClick={reset} className="text-stone-600 underline-offset-2 hover:underline">
              otra sesión
            </button>
            <Link href="/" className="text-stone-500 underline-offset-2 hover:underline">
              → Inicio
            </Link>
          </div>
        </div>
      </>
    );
  }

  const card = cards[idx];

  return (
    <>
      <div className="mb-4 flex items-baseline justify-between">
        <h1 className="text-2xl font-bold">Practicar</h1>
        <span className="text-sm text-stone-400">{idx + 1} / {cards.length}</span>
      </div>

      {/* barra de progreso */}
      <div className="mb-5 h-1 rounded-full bg-stone-200">
        <div
          className="h-1 rounded-full bg-amber-600 transition-all"
          style={{ width: `${(idx / cards.length) * 100}%` }}
        />
      </div>

      <div className="rounded-xl border border-stone-200 bg-white p-5">
        {card.type === "vocab" && (
          <>
            <p className="text-xs uppercase tracking-wide text-stone-400">
              {card.is_phrase ? "¿Cómo se dice esta frase?" : "¿Cómo se dice?"}
            </p>
            <p className="mt-2 text-xl font-medium">🇩🇪 {card.prompt}</p>
          </>
        )}
        {card.type === "fix" && (
          <>
            <p className="text-xs uppercase tracking-wide text-stone-400">
              Corrige tu frase · {card.concept_label}
            </p>
            <p className="mt-2 text-xl font-medium text-red-700">{card.prompt}</p>
          </>
        )}
        {card.type === "conj" && (
          <>
            <p className="text-xs uppercase tracking-wide text-stone-400">Conjuga</p>
            <p className="mt-2 text-xl font-medium">
              {card.verb} <span className="text-sm text-stone-400">({card.verb_de})</span>
            </p>
            <p className="mt-1 text-base text-stone-600">
              {card.tense}{card.person ? ` · ${card.person}` : ""}
            </p>
          </>
        )}

        {revealed && (
          <p className="mt-4 border-t border-stone-100 pt-4 text-xl font-semibold text-green-700">
            {card.answer}
          </p>
        )}

        <div className="mt-5 flex gap-3">
          {!revealed ? (
            <button
              onClick={() => setRevealed(true)}
              className="w-full rounded-lg bg-stone-900 py-2.5 text-sm font-semibold text-white active:scale-[0.98]"
            >
              mostrar
            </button>
          ) : (
            <>
              <button
                onClick={() => grade(false)}
                disabled={grading}
                className="flex-1 rounded-lg border border-red-200 bg-red-50 py-2.5 text-sm font-semibold text-red-700 active:scale-[0.98] disabled:opacity-40"
              >
                mal
              </button>
              <button
                onClick={() => grade(true)}
                disabled={grading}
                className="flex-1 rounded-lg border border-green-200 bg-green-50 py-2.5 text-sm font-semibold text-green-700 active:scale-[0.98] disabled:opacity-40"
              >
                bien
              </button>
            </>
          )}
        </div>

        {card.type === "fix" && revealed && (
          <p className="mt-3 text-right">
            <Link
              href={`/gramatica/${card.concept_slug}`}
              className="text-xs text-stone-400 underline-offset-2 hover:underline"
            >
              → ver lección
            </Link>
          </p>
        )}
      </div>
    </>
  );
}
