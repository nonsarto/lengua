"use client";

/**
 * Ejercicios interactivos de UN capítulo: mcq (opciones) + cloze (escribir).
 * La corrección viene del backend (determinista) y mueve el estado del concepto.
 * Sin ejercicios → botón de generar (mismo patrón que el capítulo borrador).
 */

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { apiFetch } from "@/lib/api";
import { S } from "@/lib/strings";

type Exercise = { id: string; etype: "mcq" | "cloze"; prompt: string; options: string[] | null };
type Session = { slug: string; label: string; total: number; exercises: Exercise[] };
type Verdict = { correct: boolean; solution: string; explanation: string };

export default function Ejercicios() {
  const { slug } = useParams<{ slug: string }>();
  const [session, setSession] = useState<Session | null>(null);
  const [idx, setIdx] = useState(0);
  const [answer, setAnswer] = useState("");
  const [verdict, setVerdict] = useState<Verdict | null>(null);
  const [okCount, setOkCount] = useState(0);
  const [busy, setBusy] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(() => {
    setSession(null);
    setIdx(0);
    setAnswer("");
    setVerdict(null);
    setOkCount(0);
    apiFetch(`/concepts/${slug}/exercises`)
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then(setSession)
      .catch(() => setError(S.situationMissing));
  }, [slug]);

  useEffect(load, [load]);

  async function generate() {
    setGenerating(true);
    setError(null);
    try {
      const res = await apiFetch(`/concepts/${slug}/exercises/generate`, { method: "POST" });
      if (!res.ok) throw new Error();
      load();
    } catch {
      setError(S.exGenFailed);
    } finally {
      setGenerating(false);
    }
  }

  async function submit(a: string) {
    if (busy || verdict) return;
    setBusy(true);
    try {
      const res = await apiFetch(`/exercises/${current!.id}/answer`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ answer: a }),
      });
      if (!res.ok) throw new Error();
      const v: Verdict = await res.json();
      setAnswer(a);
      setVerdict(v);
      if (v.correct) setOkCount((n) => n + 1);
    } catch {
      setError(S.exGenFailed);
    } finally {
      setBusy(false);
    }
  }

  function next() {
    setVerdict(null);
    setAnswer("");
    setIdx((i) => i + 1);
  }

  if (error && !session) return <p className="text-sm text-stone-400">{error}</p>;
  if (!session) return <p className="text-sm text-stone-400">{S.loading}</p>;

  const current = session.exercises[idx];
  const done = idx >= session.exercises.length;

  return (
    <>
      <p className="mb-1 text-xs text-stone-400">
        <Link href={`/gramatica/${slug}`} className="underline-offset-2 hover:underline">
          {session.label}
        </Link>
        {" / "}{S.exTitle}
      </p>

      {/* Sin ejercicios todavía — generar la primera tanda */}
      {session.exercises.length === 0 && (
        <div className="rounded-xl border border-stone-200 bg-white p-6 text-center">
          <p className="mb-4 text-sm text-stone-500">{S.exEmpty}</p>
          <button
            onClick={generate}
            disabled={generating}
            className="rounded-lg bg-accent-600 px-6 py-2 text-sm font-semibold text-white disabled:opacity-40 active:scale-95"
          >
            {generating ? S.exGenerating : S.exGenerate}
          </button>
          {error && <p className="mt-3 text-sm text-red-700">{error}</p>}
        </div>
      )}

      {/* La sesión */}
      {!done && current && (
        <>
          <p className="mb-3 text-xs text-stone-400">
            {idx + 1} / {session.exercises.length}
          </p>
          <div className="rounded-xl border border-stone-200 bg-white p-4">
            <p className="mb-4 text-lg">{current.prompt}</p>

            {/* mcq: opciones como botones */}
            {current.etype === "mcq" && current.options && (
              <div className="space-y-2">
                {current.options.map((o) => {
                  const chosen = verdict && o === answer;
                  const isSolution = verdict && o === verdict.solution;
                  return (
                    <button
                      key={o}
                      onClick={() => submit(o)}
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

            {/* cloze: escribir la respuesta */}
            {current.etype === "cloze" && !verdict && (
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  if (answer.trim()) submit(answer);
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
                  disabled={busy || !answer.trim()}
                  className="shrink-0 rounded-lg bg-accent-600 px-4 py-2 text-sm font-semibold text-white disabled:opacity-40 active:scale-95"
                >
                  {S.exCheck}
                </button>
              </form>
            )}

            {/* Feedback: veredicto + solución + por qué (en alemán) */}
            {verdict && (
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
            )}
          </div>

          {verdict && (
            <button
              onClick={next}
              autoFocus
              className="mt-3 w-full rounded-lg bg-accent-600 py-3 text-sm font-semibold text-white active:scale-95"
            >
              {S.exNext}
            </button>
          )}
        </>
      )}

      {/* Resumen final */}
      {done && session.exercises.length > 0 && (
        <div className="rounded-xl border border-stone-200 bg-white p-6 text-center">
          <p className="mb-4 text-2xl font-bold">{S.exDone(okCount, session.exercises.length)}</p>
          <div className="flex justify-center gap-3">
            <button
              onClick={load}
              className="rounded-lg border border-accent-300 px-4 py-2 text-sm font-semibold text-accent-700 active:scale-95"
            >
              {S.exAgain}
            </button>
            <button
              onClick={generate}
              disabled={generating}
              className="rounded-lg bg-accent-600 px-4 py-2 text-sm font-semibold text-white disabled:opacity-40 active:scale-95"
            >
              {generating ? S.exGenerating : S.exMore}
            </button>
          </div>
          {error && <p className="mt-3 text-sm text-red-700">{error}</p>}
          <p className="mt-4">
            <Link
              href={`/gramatica/${slug}`}
              className="text-sm text-stone-400 underline-offset-2 hover:underline"
            >
              ← {session.label}
            </Link>
          </p>
        </div>
      )}
    </>
  );
}
