"use client";

/**
 * Practicar — tres tipos de drill, UNA sesión. La selección es determinista y tira
 * exactamente de donde cojea tu scoring: vocabulario SRS vencido, TUS frases mal dichas
 * (no ejercicios genéricos), y conjugación de los patrones flojos.
 * Solo el vocabulario mueve el SRS (bien/mal); fix y conjugación son auto-chequeo.
 */

import { useEffect, useState } from "react";
import Link from "next/link";
import { API } from "@/lib/api";

type Card =
  | { type: "vocab"; vocab_id: string; prompt: string; answer: string; register: string; is_phrase: boolean }
  | { type: "fix"; prompt: string; answer: string; concept_slug: string; concept_label: string }
  | { type: "conj"; verb: string; verb_de: string; tense: string; person: string | null; answer: string; pattern: string };

export default function Practicar() {
  const [cards, setCards] = useState<Card[] | null>(null);
  const [idx, setIdx] = useState(0);
  const [revealed, setRevealed] = useState(false);
  const [grading, setGrading] = useState(false);

  useEffect(() => {
    fetch(`${API}/practicar/session`)
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then((d) => setCards(d.items))
      .catch(() => setCards([]));
  }, []);

  function next() {
    setRevealed(false);
    setIdx((i) => i + 1);
  }

  async function grade(correct: boolean) {
    const card = cards![idx];
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

  if (cards === null) return <p className="text-sm text-stone-400">cargando…</p>;

  if (cards.length === 0)
    return (
      <>
        <h1 className="mb-4 text-2xl font-bold">Practicar</h1>
        <p className="text-sm text-stone-500">
          Nada que practicar todavía — captura algo de tu día con el botón{" "}
          <span className="font-semibold text-amber-600">+</span> y vuelve.
        </p>
      </>
    );

  if (idx >= cards.length)
    return (
      <>
        <h1 className="mb-4 text-2xl font-bold">Practicar</h1>
        <div className="rounded-xl border border-green-200 bg-green-50/60 p-6 text-center">
          <p className="text-lg font-semibold text-green-800">Sesión terminada ✓</p>
          <p className="mt-1 text-sm text-stone-600">{cards.length} tarjetas repasadas.</p>
          <Link href="/" className="mt-3 inline-block text-sm text-stone-500 underline-offset-2 hover:underline">
            → volver a Inicio
          </Link>
        </div>
      </>
    );

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
          ) : card.type === "vocab" ? (
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
          ) : (
            <button
              onClick={next}
              className="w-full rounded-lg bg-stone-900 py-2.5 text-sm font-semibold text-white active:scale-[0.98]"
            >
              siguiente
            </button>
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
