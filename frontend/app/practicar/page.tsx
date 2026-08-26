"use client";

/**
 * Practicar — DIE Übungszentrale, drei Kacheln + Escucha:
 *   · Mix       → die 20-Minuten-Tages-Session (/sesion) — kein eigener Drill hier
 *   · Vocabulario → SRS-Recall (Wörter + Frasen), bewegt das SRS
 *   · Gramática   → eigene Fehlersätze + interaktive Übungen (Server-Grading über
 *                   /exercises/{id}/answer — bewegt den Konzept-Lernstand)
 *   · Escucha     → Hörverstehen (eigene Seite)
 * Kapitel in Gramática sind reine Referenz + Chat; geübt wird hier.
 * Der Durchlauf überlebt einen Reload (sessionStorage) — wie die Tages-Session,
 * nur clientseitig. Textos de lib/strings (es/ca).
 */

import { useEffect, useState } from "react";
import Link from "next/link";
import { apiFetch } from "@/lib/api";
import { S } from "@/lib/strings";

type Card =
  | { type: "vocab"; vocab_id: string; prompt: string; answer: string; register: string; is_phrase: boolean }
  | { type: "fix"; prompt: string; answer: string; concept_slug: string; concept_label: string }
  | { type: "exercise"; exercise_id: string; etype: "mcq" | "cloze"; prompt: string;
      options: string[] | null; concept_slug: string; concept_label: string };

type Verdict = { correct: boolean; solution: string; explanation: string };

const STORE_KEY = "lengua_practicar_v1";

type Stored = { tipo: string; cards: Card[]; idx: number; tally: { bien: number; mal: number } };

function saveState(s: Stored | null) {
  try {
    if (s) sessionStorage.setItem(STORE_KEY, JSON.stringify(s));
    else sessionStorage.removeItem(STORE_KEY);
  } catch { /* privater Modus o.ä. — dann eben ohne Persistenz */ }
}

function loadState(): Stored | null {
  try {
    const raw = sessionStorage.getItem(STORE_KEY);
    if (!raw) return null;
    const s = JSON.parse(raw) as Stored;
    return s.cards && s.idx < s.cards.length ? s : null;
  } catch {
    return null;
  }
}

export default function Practicar() {
  const [tipo, setTipo] = useState<string | null>(null);
  const [cards, setCards] = useState<Card[] | null>(null);
  const [idx, setIdx] = useState(0);
  const [revealed, setRevealed] = useState(false);
  const [answer, setAnswer] = useState("");
  const [verdict, setVerdict] = useState<Verdict | null>(null);
  const [grading, setGrading] = useState(false);
  const [tally, setTally] = useState({ bien: 0, mal: 0 });
  const [loadFailed, setLoadFailed] = useState(false);

  // Reload mitten im Drill → weitermachen, wo man war (B6)
  useEffect(() => {
    const s = loadState();
    if (s) {
      setTipo(s.tipo);
      setCards(s.cards);
      setIdx(s.idx);
      setTally(s.tally);
    }
  }, []);

  function start(t: string) {
    setTipo(t);
    setCards(null);
    setIdx(0);
    setTally({ bien: 0, mal: 0 });
    setLoadFailed(false);
    setRevealed(false);
    setVerdict(null);
    setAnswer("");
    apiFetch(`/practicar/session?tipo=${t}`)
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then((d) => {
        setCards(d.items);
        saveState({ tipo: t, cards: d.items, idx: 0, tally: { bien: 0, mal: 0 } });
      })
      .catch(() => {
        setLoadFailed(true);
        setCards([]);
      });
  }

  function reset() {
    setTipo(null);
    setCards(null);
    saveState(null);
  }

  function next(nextTally = tally) {
    setRevealed(false);
    setVerdict(null);
    setAnswer("");
    const nextIdx = idx + 1;
    setIdx(nextIdx);
    if (cards && nextIdx < cards.length && tipo) {
      saveState({ tipo, cards, idx: nextIdx, tally: nextTally });
    } else {
      saveState(null);   // fertig — nichts wiederaufnehmen
    }
  }

  // Vokabeln: Selbst-Grading bewegt das SRS
  async function gradeVocab(correct: boolean) {
    const card = cards![idx];
    if (card.type !== "vocab") return;
    const t = correct ? { ...tally, bien: tally.bien + 1 } : { ...tally, mal: tally.mal + 1 };
    setTally(t);
    setGrading(true);
    try {
      await apiFetch(`/practicar/grade`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ vocab_id: card.vocab_id, correct }),
      });
    } catch {
      /* la nota se pierde en silencio — la tarjeta volverá */
    } finally {
      setGrading(false);
      next(t);
    }
  }

  // Übungen: der Server bewertet und bewegt den Konzept-State
  async function submitExercise(a: string) {
    const card = cards![idx];
    if (card.type !== "exercise" || grading || verdict) return;
    setGrading(true);
    try {
      const res = await apiFetch(`/exercises/${card.exercise_id}/answer`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ answer: a }),
      });
      if (!res.ok) throw new Error();
      const v: Verdict = await res.json();
      setAnswer(a);
      setVerdict(v);
      setTally((t) => (v.correct ? { ...t, bien: t.bien + 1 } : { ...t, mal: t.mal + 1 }));
    } catch {
      /* si falla, deja reintentar */
    } finally {
      setGrading(false);
    }
  }

  // ---------- pantalla 1: elegir ----------
  if (tipo === null) {
    return (
      <>
        <h1 className="mb-4 text-2xl font-bold">{S.practicarTitle}</h1>
        <div className="space-y-2">
          {/* Mix = die Tages-Session — der Standardweg, deshalb oben und akzentuiert */}
          <Link
            href="/sesion"
            className="block w-full rounded-xl border border-accent-300 bg-accent-100/70 p-4 text-left active:scale-[0.99]"
          >
            <p className="font-semibold text-accent-800">{S.practicarMixTitle}</p>
            <p className="mt-0.5 text-sm text-stone-600">{S.practicarMixDesc}</p>
          </Link>
          <button
            onClick={() => start("vocabulario")}
            className="block w-full rounded-xl border border-stone-200 bg-white p-4 text-left active:scale-[0.99]"
          >
            <p className="font-semibold">{S.practicarVocabTitle}</p>
            <p className="mt-0.5 text-sm text-stone-500">{S.practicarVocabDesc}</p>
          </button>
          <button
            onClick={() => start("gramatica")}
            className="block w-full rounded-xl border border-stone-200 bg-white p-4 text-left active:scale-[0.99]"
          >
            <p className="font-semibold">{S.practicarGramTitle}</p>
            <p className="mt-0.5 text-sm text-stone-500">{S.practicarGramDesc}</p>
          </button>
          {/* Escucha — audio, propia pantalla (no es un drill de tarjetas) */}
          <Link
            href="/practicar/escucha"
            className="block w-full rounded-xl border border-stone-200 bg-white p-4 text-left active:scale-[0.99]"
          >
            <p className="font-semibold">{S.escuchaBtn}</p>
            <p className="mt-0.5 text-sm text-stone-500">{S.escuchaDesc}</p>
          </Link>
        </div>
      </>
    );
  }

  if (cards === null) return <p className="text-sm text-stone-400">{S.preparingSession}</p>;

  // ---------- sin tarjetas ----------
  if (cards.length === 0)
    return (
      <>
        <h1 className="mb-4 text-2xl font-bold">{S.practicarTitle}</h1>
        <p className="text-sm text-stone-500">
          {loadFailed ? S.sessionLoadFailed : S.nothingPending}
        </p>
        <button onClick={reset} className="mt-3 text-sm text-stone-500 underline-offset-2 hover:underline">
          {S.chooseOther}
        </button>
      </>
    );

  // ---------- fin de sesión: la cuenta ----------
  if (idx >= cards.length) {
    const graded = tally.bien + tally.mal;
    return (
      <>
        <h1 className="mb-4 text-2xl font-bold">{S.practicarTitle}</h1>
        <div className="rounded-xl border border-green-200 bg-green-50/60 p-6 text-center">
          <p className="text-lg font-semibold text-green-800">{S.sessionDone}</p>
          <p className="mt-1 text-sm text-stone-600">{S.cardsReviewed(cards.length)}</p>
          {graded > 0 && (
            <p className="mt-2 text-sm">
              <span className="font-semibold text-green-700">{tally.bien} {S.tallyGood}</span>
              {" · "}
              <span className="font-semibold text-red-600">{tally.mal} {S.tallyBad}</span>
              {" · "}
              <span className="text-stone-500">{Math.round((tally.bien / graded) * 100)}%</span>
            </p>
          )}
          <div className="mt-4 flex justify-center gap-4 text-sm">
            <button onClick={reset} className="text-stone-600 underline-offset-2 hover:underline">
              {S.anotherSession}
            </button>
            <Link href="/" className="text-stone-500 underline-offset-2 hover:underline">
              {S.toInicio}
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
        <h1 className="text-2xl font-bold">{S.practicarTitle}</h1>
        <span className="shrink-0 text-sm text-stone-400">{idx + 1} / {cards.length}</span>
      </div>

      {/* barra de progreso */}
      <div className="mb-5 h-1 rounded-full bg-stone-200">
        <div
          className="h-1 rounded-full bg-accent-600 transition-all"
          style={{ width: `${(idx / cards.length) * 100}%` }}
        />
      </div>

      <div className="rounded-xl border border-stone-200 bg-white p-5">
        {/* ---------- vocab: recall + Selbst-Grading (SRS) ---------- */}
        {card.type === "vocab" && (
          <>
            <p className="text-xs uppercase tracking-wide text-stone-400">
              {card.is_phrase ? S.howToSayPhrase : S.howToSay}
            </p>
            <p className="mt-2 text-xl font-medium">🇩🇪 {card.prompt}</p>
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
                  {S.showBtn}
                </button>
              ) : (
                <>
                  <button
                    onClick={() => gradeVocab(false)}
                    disabled={grading}
                    className="flex-1 rounded-lg border border-red-200 bg-red-50 py-2.5 text-sm font-semibold text-red-700 active:scale-[0.98] disabled:opacity-40"
                  >
                    {S.tallyBad}
                  </button>
                  <button
                    onClick={() => gradeVocab(true)}
                    disabled={grading}
                    className="flex-1 rounded-lg border border-green-200 bg-green-50 py-2.5 text-sm font-semibold text-green-700 active:scale-[0.98] disabled:opacity-40"
                  >
                    {S.tallyGood}
                  </button>
                </>
              )}
            </div>
          </>
        )}

        {/* ---------- fix: tu frase real — ansehen, weiter (zählt nicht in den Tally) ---------- */}
        {card.type === "fix" && (
          <>
            <p className="text-xs uppercase tracking-wide text-stone-400">
              {S.fixYourSentence} · {card.concept_label}
            </p>
            <p className="mt-2 text-xl font-medium text-red-700">{card.prompt}</p>
            {revealed && (
              <p className="mt-4 border-t border-stone-100 pt-4 text-xl font-semibold text-green-700">
                {card.answer}
              </p>
            )}
            <button
              onClick={() => (revealed ? next() : setRevealed(true))}
              className="mt-5 w-full rounded-lg bg-stone-900 py-2.5 text-sm font-semibold text-white active:scale-[0.98]"
            >
              {revealed ? S.sessionNext : S.showBtn}
            </button>
            {revealed && (
              <p className="mt-3 text-right">
                <Link
                  href={`/gramatica/${card.concept_slug}`}
                  className="text-xs text-stone-400 underline-offset-2 hover:underline"
                >
                  {S.seeLesson}
                </Link>
              </p>
            )}
          </>
        )}

        {/* ---------- exercise: mcq / cloze — corrige el backend (mueve el estado) ---------- */}
        {card.type === "exercise" && (
          <>
            <p className="mb-1 text-xs uppercase tracking-wide text-stone-400">
              {card.concept_label}
            </p>
            <p className="mb-4 text-lg">{card.prompt}</p>

            {card.etype === "mcq" && card.options && (
              <div className="space-y-2">
                {card.options.map((o) => {
                  const chosen = verdict && o === answer;
                  const isSolution = verdict && o === verdict.solution;
                  return (
                    <button
                      key={o}
                      onClick={() => submitExercise(o)}
                      disabled={grading || !!verdict}
                      className={`block w-full rounded-lg border p-3 text-left text-base active:scale-[0.99] ${
                        isSolution
                          ? "border-green-600 bg-green-50 font-medium text-green-800"
                          : chosen
                            ? "border-red-400 bg-red-50 text-red-700 line-through"
                            : "border-stone-200 bg-white disabled:opacity-60"
                      }`}
                    >
                      {o}
                    </button>
                  );
                })}
              </div>
            )}

            {card.etype === "cloze" && !verdict && (
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  if (answer.trim()) submitExercise(answer);
                }}
                className="flex gap-2"
              >
                <input
                  value={answer}
                  onChange={(e) => setAnswer(e.target.value)}
                  placeholder={S.exPlaceholder}
                  autoFocus
                  autoCapitalize="none"
                  autoCorrect="off"
                  className="w-full rounded-lg border border-stone-300 p-3 text-base outline-none focus:border-accent-500"
                />
                <button
                  type="submit"
                  disabled={grading || !answer.trim()}
                  className="shrink-0 rounded-lg bg-accent-600 px-4 py-2 text-sm font-semibold text-white disabled:opacity-40 active:scale-95"
                >
                  {S.exCheck}
                </button>
              </form>
            )}

            {verdict && (
              <>
                <div className={`mt-4 rounded-lg p-3 ${verdict.correct ? "bg-green-50" : "bg-red-50"}`}>
                  {verdict.correct ? (
                    <p className="font-medium text-green-800">{S.exCorrect}</p>
                  ) : (
                    <p className="font-medium text-red-700">
                      {S.exSolution} <span className="text-green-800">{verdict.solution}</span>
                    </p>
                  )}
                  <p className="mt-1 text-sm text-stone-600">{verdict.explanation}</p>
                </div>
                <button
                  onClick={() => next()}
                  autoFocus
                  className="mt-3 w-full rounded-lg bg-accent-600 py-2.5 text-sm font-semibold text-white active:scale-[0.98]"
                >
                  {S.exNext}
                </button>
              </>
            )}
          </>
        )}
      </div>
    </>
  );
}
