"use client";

/**
 * Test de nivel/nivell — 12 preguntas, ~3 minutos, una por concepto-firma (A1-B2).
 * Un toque por pregunta. La evaluación determinista SIEMBRA tus estados.
 */

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { apiFetch, updateStoredUser } from "@/lib/api";
import { S } from "@/lib/strings";

type Question = { id: string; band: string; q: string; options: string[] };
type Result = { level: string; correct: number; total: number;
                weak: { slug: string; label: string }[] };

export default function Nivel() {
  const router = useRouter();
  const [questions, setQuestions] = useState<Question[] | null>(null);
  const [idx, setIdx] = useState(0);
  const [answers, setAnswers] = useState<Record<string, number>>({});
  const [result, setResult] = useState<Result | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    apiFetch("/onboarding")
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then((d) => {
        if (d.done) router.replace("/");
        else setQuestions(d.questions);
      })
      .catch(() => {});
  }, [router]);

  async function submit(all: Record<string, number>) {
    setBusy(true);
    try {
      const res = await apiFetch("/onboarding", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ answers: all }),
      });
      if (!res.ok) throw new Error();
      const r: Result = await res.json();
      setResult(r);
      updateStoredUser({ onboarded: true, level_estimate: r.level });
    } catch {
      setBusy(false); // botón reaparece, se puede reintentar
    }
  }

  function answer(choice: number) {
    if (!questions) return;
    const all = { ...answers, [questions[idx].id]: choice };
    setAnswers(all);
    if (idx + 1 < questions.length) setIdx(idx + 1);
    else submit(all);
  }

  if (result) {
    return (
      <div className="flex min-h-[70dvh] flex-col justify-center">
        <div className="rounded-xl border border-green-200 bg-green-50/60 p-6 text-center">
          <p className="text-sm uppercase tracking-wide text-stone-500">{S.yourLevel}</p>
          <p className="mt-1 text-4xl font-bold text-green-800">{result.level}</p>
          <p className="mt-2 text-sm text-stone-600">{S.correctOf(result.correct, result.total)}</p>
        </div>
        {result.weak.length > 0 && (
          <div className="mt-4 rounded-xl border border-accent-200 bg-accent-50/60 p-4">
            <p className="text-sm font-semibold text-accent-800">{S.weakIntro}</p>
            <ul className="mt-1 text-sm text-stone-700">
              {result.weak.map((w) => (
                <li key={w.slug}>· {w.label}</li>
              ))}
            </ul>
          </div>
        )}
        <Link
          href="/"
          className="mt-6 rounded-xl bg-accent-600 py-3 text-center text-base font-semibold text-white active:scale-[0.99]"
        >
          {S.startBtn}
        </Link>
      </div>
    );
  }

  if (!questions) return <p className="text-sm text-stone-400">{S.loading}</p>;

  const q = questions[idx];

  return (
    <>
      <div className="mb-2 flex items-baseline justify-between">
        <h1 className="text-2xl font-bold">{S.nivelTitle}</h1>
        <span className="text-sm text-stone-400">{idx + 1} / {questions.length}</span>
      </div>
      <p className="mb-4 text-xs text-stone-400">{S.nivelHint}</p>

      <div className="mb-5 h-1 rounded-full bg-stone-200">
        <div
          className="h-1 rounded-full bg-accent-600 transition-all"
          style={{ width: `${(idx / questions.length) * 100}%` }}
        />
      </div>

      <div className="rounded-xl border border-stone-200 bg-white p-5">
        <p className="text-xs uppercase tracking-wide text-stone-400">{q.band}</p>
        <p className="mt-2 text-xl font-medium">{q.q}</p>
        <div className="mt-5 space-y-2">
          {q.options.map((opt, i) => (
            <button
              key={i}
              onClick={() => answer(i)}
              disabled={busy}
              className="block w-full rounded-lg border border-stone-200 bg-white px-4 py-3 text-left text-base active:scale-[0.99] active:border-accent-500 disabled:opacity-40"
            >
              {opt}
            </button>
          ))}
        </div>
      </div>
      {busy && <p className="mt-3 text-center text-sm text-stone-400">{S.evaluating}</p>}
    </>
  );
}
