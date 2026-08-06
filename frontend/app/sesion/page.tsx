"use client";

/**
 * Sesión diaria — el arco de 15 min: entrada suave (vocabulario) → núcleo (UN concepto de
 * gramática: explicación + ejercicios de tus errores) → cierre (vocabulario de situación).
 * El plan viene congelado de GET /session/today; la corrección va por los caminos de siempre
 * (SRS / grading de ejercicios), así el aprendizaje se mueve igual que en Practicar/Capturar.
 * El progreso se guarda tras cada ítem → cortar y continuar. Textos de lib/strings (es/ca).
 */

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { apiFetch } from "@/lib/api";
import { S } from "@/lib/strings";

type Item =
  | { kind: "vocab"; vocab_id: string; prompt: string; answer: string; register: string; is_phrase: boolean }
  | { kind: "fix"; prompt: string; answer: string; concept_slug: string; concept_label: string }
  | { kind: "explain"; concept_slug: string; label: string; explanation: string; rule_of_thumb: string | null; german_pitfall: string | null }
  | { kind: "exercise"; exercise_id: string; etype: "mcq" | "cloze"; prompt: string; options: string[] | null; concept_slug: string; concept_label: string };

type Session = {
  id: string;
  status: "active" | "completed";
  headline: string;
  budget_seconds: number;
  cursor: number;
  progress: { index: number; correct?: boolean }[];
  items: Item[];
};

type Verdict = { correct: boolean; solution: string; explanation: string };

export default function Sesion() {
  const [session, setSession] = useState<Session | null>(null);
  const [failed, setFailed] = useState(false);
  const [idx, setIdx] = useState(0);
  const [progress, setProgress] = useState<{ index: number; correct?: boolean }[]>([]);
  const [done, setDone] = useState(false);
  const [busy, setBusy] = useState(false);

  // Estado por ítem
  const [revealed, setRevealed] = useState(false);
  const [answer, setAnswer] = useState("");
  const [verdict, setVerdict] = useState<Verdict | null>(null);

  const load = useCallback((data: Session) => {
    setSession(data);
    setProgress(data.progress || []);
    setIdx(data.status === "completed" ? data.items.length : data.cursor);
    setDone(data.status === "completed");
    setRevealed(false);
    setAnswer("");
    setVerdict(null);
  }, []);

  useEffect(() => {
    apiFetch(`/session/today`)
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then(load)
      .catch(() => setFailed(true));
  }, [load]);

  function resetItem() {
    setRevealed(false);
    setAnswer("");
    setVerdict(null);
  }

  async function complete(id: string) {
    setDone(true);
    try {
      await apiFetch(`/session/${id}/complete`, { method: "POST" });
    } catch {
      /* la marca se reintenta al reabrir */
    }
  }

  // Avanza un ítem, guarda el progreso (cortar → continuar), cierra al final.
  function advance(correct?: boolean) {
    if (!session) return;
    const nextIdx = idx + 1;
    const nextProgress = [...progress, { index: idx, ...(correct !== undefined ? { correct } : {}) }];
    setProgress(nextProgress);
    setIdx(nextIdx);
    resetItem();
    apiFetch(`/session/${session.id}/progress`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ cursor: nextIdx, progress: nextProgress }),
    }).catch(() => {});
    if (nextIdx >= session.items.length) complete(session.id);
  }

  async function gradeVocab(correct: boolean) {
    const item = session!.items[idx];
    if (item.kind !== "vocab") return;
    setBusy(true);
    try {
      await apiFetch(`/practicar/grade`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ vocab_id: item.vocab_id, correct }),
      });
    } catch {
      /* la nota se pierde en silencio — la tarjeta volverá otro día */
    } finally {
      setBusy(false);
      advance(correct);
    }
  }

  async function submitExercise(a: string) {
    const item = session!.items[idx];
    if (item.kind !== "exercise" || busy || verdict) return;
    setBusy(true);
    try {
      const res = await apiFetch(`/exercises/${item.exercise_id}/answer`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ answer: a }),
      });
      if (!res.ok) throw new Error();
      const v: Verdict = await res.json();
      setAnswer(a);
      setVerdict(v);
    } catch {
      /* si falla, deja reintentar */
    } finally {
      setBusy(false);
    }
  }

  async function reroll() {
    setSession(null);
    setDone(false);
    try {
      const res = await apiFetch(`/session/reroll`, { method: "POST" });
      if (!res.ok) throw new Error();
      load(await res.json());
    } catch {
      setFailed(true);
    }
  }

  if (failed) return <p className="text-sm text-stone-400">{S.sessionError}</p>;
  if (!session) return <p className="text-sm text-stone-400">{S.sessionPreparing}</p>;

  const total = session.items.length;

  // ---------- cierre: confirmación tranquila, sin ofrecer ya lo siguiente ----------
  if (done || idx >= total) {
    return (
      <div className="rounded-2xl border border-green-200 bg-green-50/60 p-8 text-center">
        <p className="text-2xl font-bold text-green-800">{S.sessionDoneToday} ✓</p>
        <p className="mt-2 text-sm text-stone-600">{S.sessionDoneSub}</p>
        <p className="mt-6">
          <Link href="/" className="text-sm text-stone-500 underline-offset-2 hover:underline">
            {S.sessionToInicio}
          </Link>
        </p>
      </div>
    );
  }

  const item = session.items[idx];

  return (
    <>
      <div className="mb-4 flex items-baseline justify-between">
        <h1 className="text-xl font-bold">{session.headline || S.sessionVocabLabel}</h1>
        <span className="text-sm text-stone-400">{idx + 1} / {total}</span>
      </div>

      {/* progreso */}
      <div className="mb-5 h-1 rounded-full bg-stone-200">
        <div className="h-1 rounded-full bg-accent-600 transition-all" style={{ width: `${(idx / total) * 100}%` }} />
      </div>

      <div className="rounded-xl border border-stone-200 bg-white p-5">
        {/* ---------- vocab: recall (mueve SRS) ---------- */}
        {item.kind === "vocab" && (
          <>
            <p className="text-xs uppercase tracking-wide text-stone-400">{S.sessionSaidWord}</p>
            <p className="mt-2 text-xl font-medium">🇩🇪 {item.prompt}</p>
            {revealed && (
              <p className="mt-4 border-t border-stone-100 pt-4 text-xl font-semibold text-green-700">
                {item.answer}
              </p>
            )}
            <div className="mt-5 flex gap-3">
              {!revealed ? (
                <button
                  onClick={() => setRevealed(true)}
                  className="w-full rounded-lg bg-stone-900 py-2.5 text-sm font-semibold text-white active:scale-[0.98]"
                >
                  {S.sessionReveal}
                </button>
              ) : (
                <>
                  <button
                    onClick={() => gradeVocab(false)}
                    disabled={busy}
                    className="flex-1 rounded-lg border border-red-200 bg-red-50 py-2.5 text-sm font-semibold text-red-700 active:scale-[0.98] disabled:opacity-40"
                  >
                    {S.sessionBad}
                  </button>
                  <button
                    onClick={() => gradeVocab(true)}
                    disabled={busy}
                    className="flex-1 rounded-lg border border-green-200 bg-green-50 py-2.5 text-sm font-semibold text-green-700 active:scale-[0.98] disabled:opacity-40"
                  >
                    {S.sessionGood}
                  </button>
                </>
              )}
            </div>
          </>
        )}

        {/* ---------- explain: el núcleo, la regla detrás de tu error ---------- */}
        {item.kind === "explain" && (
          <>
            <p className="text-xs uppercase tracking-wide text-accent-600">{item.label}</p>
            <p className="mt-2 text-base text-stone-800">{item.explanation}</p>
            {item.rule_of_thumb && (
              <p className="mt-3 rounded-lg bg-stone-50 p-3 text-sm text-stone-700">
                <span className="font-semibold">{S.sessionRule}:</span> {item.rule_of_thumb}
              </p>
            )}
            {item.german_pitfall && (
              <p className="mt-2 rounded-lg bg-amber-50 p-3 text-sm text-stone-700">
                <span className="font-semibold">{S.sessionPitfall}:</span> {item.german_pitfall}
              </p>
            )}
            <button
              onClick={() => advance()}
              className="mt-5 w-full rounded-lg bg-accent-600 py-2.5 text-sm font-semibold text-white active:scale-[0.98]"
            >
              {S.sessionUnderstood}
            </button>
          </>
        )}

        {/* ---------- fix: tu frase real, corrígela ---------- */}
        {item.kind === "fix" && (
          <>
            <p className="text-xs uppercase tracking-wide text-stone-400">
              {S.sessionFixIntro} · {item.concept_label}
            </p>
            <p className="mt-2 text-xl font-medium text-red-700">{item.prompt}</p>
            {revealed && (
              <p className="mt-4 border-t border-stone-100 pt-4 text-xl font-semibold text-green-700">
                {item.answer}
              </p>
            )}
            <button
              onClick={() => (revealed ? advance() : setRevealed(true))}
              className="mt-5 w-full rounded-lg bg-stone-900 py-2.5 text-sm font-semibold text-white active:scale-[0.98]"
            >
              {revealed ? S.sessionNext : S.sessionReveal}
            </button>
          </>
        )}

        {/* ---------- exercise: mcq / cloze, corrige el backend (mueve el estado) ---------- */}
        {item.kind === "exercise" && (
          <>
            <p className="mb-4 text-lg">{item.prompt}</p>

            {item.etype === "mcq" && item.options && (
              <div className="space-y-2">
                {item.options.map((o) => {
                  const chosen = verdict && o === answer;
                  const isSolution = verdict && o === verdict.solution;
                  return (
                    <button
                      key={o}
                      onClick={() => submitExercise(o)}
                      disabled={busy || !!verdict}
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

            {item.etype === "cloze" && !verdict && (
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
                  placeholder={S.sessionWrite}
                  autoFocus
                  autoCapitalize="none"
                  autoCorrect="off"
                  className="w-full rounded-lg border border-stone-300 p-3 text-base outline-none focus:border-accent-500"
                />
                <button
                  type="submit"
                  disabled={busy || !answer.trim()}
                  className="shrink-0 rounded-lg bg-accent-600 px-4 py-2 text-sm font-semibold text-white disabled:opacity-40 active:scale-95"
                >
                  {S.sessionCheck}
                </button>
              </form>
            )}

            {verdict && (
              <>
                <div className={`mt-4 rounded-lg p-3 ${verdict.correct ? "bg-green-50" : "bg-red-50"}`}>
                  {verdict.correct ? (
                    <p className="font-medium text-green-800">{S.sessionCorrect}</p>
                  ) : (
                    <p className="font-medium text-red-700">
                      {S.sessionSolution} <span className="text-green-800">{verdict.solution}</span>
                    </p>
                  )}
                  <p className="mt-1 text-sm text-stone-600">{verdict.explanation}</p>
                </div>
                <button
                  onClick={() => advance(verdict.correct)}
                  autoFocus
                  className="mt-3 w-full rounded-lg bg-accent-600 py-2.5 text-sm font-semibold text-white active:scale-[0.98]"
                >
                  {S.sessionNext}
                </button>
              </>
            )}
          </>
        )}
      </div>

      {/* cambiar sesión — acción consciente del usuario (re-tirar los dados) */}
      <p className="mt-5 text-center">
        <button onClick={reroll} className="text-xs text-stone-400 underline-offset-2 hover:underline">
          {S.sessionChange}
        </button>
      </p>
    </>
  );
}
