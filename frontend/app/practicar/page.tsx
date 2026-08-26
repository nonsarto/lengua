"use client";

/**
 * Practicar — DIE Übungszentrale: Mix (→ /sesion) · Vocabulario (SRS) ·
 * Gramática (Fehlersätze + Server-Übungen) · Escucha.
 * Azulejo-Motion (Konzept 05): Vokabeln als Karten-Deck mit 3D-Flip; Urteil =
 * grüner Wash / Shake; Shuffle rechts=gewusst, links=nicht gewusst; Übungen mit
 * gezeichnetem Häkchen. Durchlauf überlebt Reload (sessionStorage).
 */

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { apiFetch } from "@/lib/api";
import { S } from "@/lib/strings";
import { IconCheckDraw, IconHeadphones } from "@/components/icons";
import {
  DeChip, EmptyState, ErrorState, Finale, PageHead, Progress,
  btnGhost, btnPrimaryFull, btnVerdictNo, btnVerdictSi, cardLift, cardQuiet,
} from "@/components/ui";

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
  } catch { /* privater Modus o.ä. */ }
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

const reducedMotion = () =>
  typeof window !== "undefined" && matchMedia("(prefers-reduced-motion: reduce)").matches;

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
  // Motion-Phase der Vokabelkarte: hit-good/hit-bad → out-good/out-bad → snap
  const [anim, setAnim] = useState<"" | "hit-good" | "hit-bad" | "out-good" | "out-bad" | "snap">("");
  const timers = useRef<ReturnType<typeof setTimeout>[]>([]);

  useEffect(() => {
    const s = loadState();
    if (s) {
      setTipo(s.tipo);
      setCards(s.cards);
      setIdx(s.idx);
      setTally(s.tally);
    }
    return () => timers.current.forEach(clearTimeout);
  }, []);

  const later = (ms: number, fn: () => void) => {
    timers.current.push(setTimeout(fn, reducedMotion() ? 0 : ms));
  };

  function start(t: string) {
    setTipo(t);
    setCards(null);
    setIdx(0);
    setTally({ bien: 0, mal: 0 });
    setLoadFailed(false);
    setRevealed(false);
    setVerdict(null);
    setAnswer("");
    setAnim("");
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
      saveState(null);
    }
  }

  /** Vokabel-Urteil mit Shuffle-Choreografie: Wash/Shake → rausfliegen → nachrücken. */
  async function gradeVocab(correct: boolean) {
    const card = cards![idx];
    if (card.type !== "vocab" || grading) return;
    const t = correct ? { ...tally, bien: tally.bien + 1 } : { ...tally, mal: tally.mal + 1 };
    setTally(t);
    setGrading(true);
    apiFetch(`/practicar/grade`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ vocab_id: card.vocab_id, correct }),
    }).catch(() => { /* la nota se pierde en silencio — la tarjeta volverá */ });

    setAnim(correct ? "hit-good" : "hit-bad");
    later(correct ? 380 : 420, () => {
      setAnim(correct ? "out-good" : "out-bad");
      later(430, () => {
        setAnim("snap");
        setGrading(false);
        next(t);
        requestAnimationFrame(() => setAnim(""));
      });
    });
  }

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
        <PageHead title={S.practicarTitle} />
        <div className="space-y-2">
          <Link
            href="/sesion"
            className={`${cardLift} block w-full p-4 text-left active:scale-[0.99] transition-transform`}
          >
            <p className="font-semibold">{S.practicarMixTitle}</p>
            <p className="mt-0.5 text-sm text-accent-200">{S.practicarMixDesc}</p>
          </Link>
          <button
            onClick={() => start("vocabulario")}
            className={`${cardQuiet} block w-full p-4 text-left active:scale-[0.99] transition-transform`}
          >
            <p className="font-semibold">{S.practicarVocabTitle}</p>
            <p className="mt-0.5 text-sm text-stone-500">{S.practicarVocabDesc}</p>
          </button>
          <button
            onClick={() => start("gramatica")}
            className={`${cardQuiet} block w-full p-4 text-left active:scale-[0.99] transition-transform`}
          >
            <p className="font-semibold">{S.practicarGramTitle}</p>
            <p className="mt-0.5 text-sm text-stone-500">{S.practicarGramDesc}</p>
          </button>
          <Link
            href="/practicar/escucha"
            className={`${cardQuiet} block w-full p-4 text-left active:scale-[0.99] transition-transform`}
          >
            <p className="flex items-center gap-2 font-semibold">
              <IconHeadphones className="h-4 w-4 text-stone-400" />
              {S.escuchaBtn}
            </p>
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
        <PageHead title={S.practicarTitle} />
        {loadFailed
          ? <ErrorState text={S.sessionLoadFailed} onRetry={() => start(tipo)} />
          : <EmptyState title={S.nothingPending} />}
        <p className="mt-3 text-center">
          <button onClick={reset} className={btnGhost}>{S.chooseOther}</button>
        </p>
      </>
    );

  // ---------- fin de sesión ----------
  if (idx >= cards.length) {
    const graded = tally.bien + tally.mal;
    return (
      <>
        <PageHead title={S.practicarTitle} />
        <Finale>
          <p className="font-display text-xl font-semibold">{S.sessionDone}</p>
          <p className="mt-1 text-sm text-stone-500">{S.cardsReviewed(cards.length)}</p>
          {graded > 0 && (
            <p className="mt-2 text-sm tabular-nums">
              <span className="font-semibold text-green-700">{tally.bien} {S.tallyGood}</span>
              {" · "}
              <span className="font-semibold text-red-600">{tally.mal} {S.tallyBad}</span>
              {" · "}
              <span className="text-stone-500">{Math.round((tally.bien / graded) * 100)}%</span>
            </p>
          )}
          <div className="mt-5 flex justify-center gap-5 text-sm">
            <button onClick={reset} className={btnGhost}>{S.anotherSession}</button>
            <Link href="/" className={btnGhost}>{S.toInicio}</Link>
          </div>
        </Finale>
      </>
    );
  }

  const card = cards[idx];
  const deckLeft = cards.length - idx;

  return (
    <>
      <PageHead backHref="/practicar" backLabel={S.practicarTitle}
                counter={`${idx + 1} / ${cards.length}`} />
      <Progress value={idx} total={cards.length} />

      {/* ---------- vocab: Karten-Deck mit Flip + Shuffle ---------- */}
      {card.type === "vocab" && (
        <div className="flip-scene relative" style={{ height: 260 }}>
          {/* der Stapel dahinter */}
          {deckLeft > 2 && (
            <div className={`${cardQuiet} absolute inset-0 translate-y-3 scale-[.93] opacity-60`} aria-hidden="true" />
          )}
          {deckLeft > 1 && (
            <div className={`${cardQuiet} absolute inset-0 translate-y-1.5 scale-[.965]`} aria-hidden="true" />
          )}
          <div
            className={`flip-card absolute inset-0 ${revealed ? "flipped" : ""} ${
              anim === "hit-good" ? "verdict-good" : anim === "hit-bad" ? "verdict-bad" : ""
            } ${anim === "out-good" ? "out-good" : ""} ${anim === "out-bad" ? "out-bad" : ""} ${
              anim === "snap" ? "snap" : ""
            }`}
          >
            {/* Vorderseite */}
            <div className={`flip-face ${cardQuiet} absolute inset-0 flex flex-col justify-between p-5`}>
              <p className="text-xs uppercase tracking-[.12em] text-stone-400">
                {card.is_phrase ? S.howToSayPhrase : S.howToSay}
              </p>
              <p className="font-display text-2xl font-semibold">
                <DeChip />{card.prompt}
              </p>
              <button onClick={() => setRevealed(true)} className={btnPrimaryFull}>
                {S.showBtn}
              </button>
            </div>
            {/* Rückseite */}
            <div className={`flip-face flip-back ${cardQuiet} absolute inset-0 flex flex-col justify-between p-5`}>
              <p className="text-xs uppercase tracking-[.12em] text-stone-400">{S.exSolution}</p>
              <div>
                <p className="text-sm text-stone-500"><DeChip />{card.prompt}</p>
                <p className="mt-1 font-display text-2xl font-semibold text-green-700">{card.answer}</p>
              </div>
              <div className="flex gap-3">
                <button onClick={() => gradeVocab(false)} disabled={grading} className={btnVerdictNo}>
                  {S.tallyBad}
                </button>
                <button onClick={() => gradeVocab(true)} disabled={grading} className={btnVerdictSi}>
                  {S.tallyGood}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ---------- fix: tu frase real — ansehen, weiter (zählt nicht in den Tally) ---------- */}
      {card.type === "fix" && (
        <div className={`${cardQuiet} p-5`}>
          <p className="text-xs uppercase tracking-[.12em] text-stone-400">
            {S.fixYourSentence} · {card.concept_label}
          </p>
          <p className="mt-2 font-display text-xl font-medium text-red-600">{card.prompt}</p>
          {revealed && (
            <p className="mt-4 border-t border-stone-100 pt-4 font-display text-xl font-semibold text-green-700">
              {card.answer}
            </p>
          )}
          <button
            onClick={() => (revealed ? next() : setRevealed(true))}
            className={`mt-5 ${btnPrimaryFull}`}
          >
            {revealed ? S.sessionNext : S.showBtn}
          </button>
          {revealed && (
            <p className="mt-3 text-right">
              <Link href={`/gramatica/${card.concept_slug}`} className={`${btnGhost} text-xs`}>
                {S.seeLesson}
              </Link>
            </p>
          )}
        </div>
      )}

      {/* ---------- exercise: mcq / cloze — corrige el backend ---------- */}
      {card.type === "exercise" && (
        <div className={`${cardQuiet} p-5 ${verdict ? (verdict.correct ? "verdict-good" : "verdict-bad") : ""}`}>
          <p className="mb-1 text-xs uppercase tracking-[.12em] text-stone-400">
            {card.concept_label}
          </p>
          <p className="mb-4 font-display text-lg">{card.prompt}</p>

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
                    className={`flex w-full items-center justify-between rounded-xl border p-3 text-left text-base transition-colors active:scale-[0.99] ${
                      isSolution
                        ? "border-green-600 bg-green-50 font-medium text-green-800"
                        : chosen
                          ? "border-red-400 bg-red-50 text-red-700 line-through"
                          : "border-stone-200 bg-white disabled:opacity-50"
                    }`}
                  >
                    {o}
                    {isSolution && <IconCheckDraw className="check-draw h-4 w-4 shrink-0 text-green-700" />}
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
                className="w-full rounded-xl border border-stone-300 p-3 text-base outline-none focus:border-accent-500"
              />
              <button type="submit" disabled={grading || !answer.trim()}
                      className="shrink-0 rounded-xl bg-accent-600 px-4 py-2 text-sm font-semibold text-white disabled:opacity-40 active:scale-[.97]">
                {S.exCheck}
              </button>
            </form>
          )}

          {verdict && (
            <>
              <div className={`mt-4 rounded-xl p-3 ${verdict.correct ? "bg-green-50" : "bg-red-50"}`}>
                {verdict.correct ? (
                  <p className="flex items-center gap-2 font-medium text-green-800">
                    <IconCheckDraw className="check-draw h-4 w-4" />{S.exCorrect.replace("✓ ", "")}
                  </p>
                ) : (
                  <p className="font-medium text-red-700">
                    {S.exSolution} <span className="text-green-800">{verdict.solution}</span>
                  </p>
                )}
                <p className="mt-1 text-sm text-stone-600">{verdict.explanation}</p>
              </div>
              <button onClick={() => next()} autoFocus className={`mt-3 ${btnPrimaryFull}`}>
                {S.exNext.replace(" →", "")}
              </button>
            </>
          )}
        </div>
      )}
    </>
  );
}
