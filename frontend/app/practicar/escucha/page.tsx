"use client";

/**
 * Escucha — comprensión oral. Un audio generado a partir de TU vocabulario (TTS),
 * 2-3 frases, y preguntas de opción múltiple. La corrección es del backend
 * (determinista); la transcripción solo aparece al final.
 */

import { useCallback, useEffect, useRef, useState } from "react";
import Link from "next/link";
import { apiFetch } from "@/lib/api";
import { S } from "@/lib/strings";

type Question = { index: number; q: string; options: string[] };
type Session = {
  item_id: string;
  audio_b64: string;
  audio_media_type: string;
  targets: string[];
  questions: Question[];
};
type Result = { index: number; correct: boolean; answer: string };
type Graded = { score: number; total: number; results: Result[]; transcript: string; gist: string };

export default function Escucha() {
  const [session, setSession] = useState<Session | null>(null);
  const [answers, setAnswers] = useState<(string | null)[]>([]);
  const [graded, setGraded] = useState<Graded | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(false);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  const load = useCallback(() => {
    setSession(null);
    setGraded(null);
    setError(false);
    apiFetch(`/escucha/session`)
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then((d: Session) => {
        setSession(d);
        setAnswers(new Array(d.questions.length).fill(null));
      })
      .catch(() => setError(true));
  }, []);

  useEffect(load, [load]);

  // Autoplay beim Laden (best effort — iOS erlaubt es evtl. erst nach Tap)
  useEffect(() => {
    if (session && audioRef.current) audioRef.current.play().catch(() => {});
  }, [session]);

  function pick(qIndex: number, option: string) {
    if (graded) return;
    setAnswers((a) => a.map((x, i) => (i === qIndex ? option : x)));
  }

  async function submit() {
    if (busy || !session || answers.some((a) => a === null)) return;
    setBusy(true);
    try {
      const res = await apiFetch(`/escucha/${session.item_id}/grade`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ answers }),
      });
      if (!res.ok) throw new Error();
      setGraded(await res.json());
    } catch {
      setError(true);
    } finally {
      setBusy(false);
    }
  }

  if (error && !session)
    return (
      <>
        <p className="text-sm text-red-700">{S.escuchaFailed}</p>
        <button onClick={load} className="mt-3 text-sm text-stone-500 underline-offset-2 hover:underline">
          {S.escuchaAgain}
        </button>
      </>
    );
  if (!session) return <p className="text-sm text-stone-400">{S.escuchaPreparing}</p>;

  const allAnswered = answers.every((a) => a !== null);

  return (
    <>
      <p className="mb-1 text-xs text-stone-400">
        <Link href="/practicar" className="underline-offset-2 hover:underline">
          {S.practicarTitle}
        </Link>
        {" / "}{S.escuchaTitle}
      </p>
      <h1 className="mb-4 text-2xl font-bold">🎧 {S.escuchaListen}</h1>

      {/* Reproductor — sin mostrar el texto */}
      <div className="mb-5 flex items-center gap-3 rounded-xl border border-stone-200 bg-white p-4">
        <button
          onClick={() => audioRef.current?.play()}
          className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-accent-600 text-xl text-white active:scale-95"
          aria-label="Play"
        >
          ▶
        </button>
        <button
          onClick={() => {
            if (audioRef.current) {
              audioRef.current.currentTime = 0;
              audioRef.current.play();
            }
          }}
          className="text-sm text-stone-500 underline-offset-2 hover:underline"
        >
          {S.escuchaReplay}
        </button>
        <audio
          ref={audioRef}
          src={`data:${session.audio_media_type};base64,${session.audio_b64}`}
          preload="auto"
        />
      </div>

      {/* Preguntas MC */}
      <div className="space-y-4">
        {session.questions.map((q) => {
          const res = graded?.results.find((r) => r.index === q.index);
          return (
            <div key={q.index} className="rounded-xl border border-stone-200 bg-white p-4">
              <p className="mb-3 font-medium">{q.q}</p>
              <div className="space-y-2">
                {q.options.map((o) => {
                  const chosen = answers[q.index] === o;
                  let cls = "border-stone-200 bg-white";
                  if (graded) {
                    if (o === res?.answer) cls = "border-green-600 bg-green-50 font-medium text-green-800";
                    else if (chosen) cls = "border-red-400 bg-red-50 text-red-700 line-through";
                    else cls = "border-stone-200 bg-white opacity-60";
                  } else if (chosen) {
                    cls = "border-accent-500 bg-accent-50";
                  }
                  return (
                    <button
                      key={o}
                      onClick={() => pick(q.index, o)}
                      disabled={!!graded}
                      className={`block w-full rounded-lg border p-3 text-left text-base active:scale-[0.99] ${cls}`}
                    >
                      {o}
                    </button>
                  );
                })}
              </div>
            </div>
          );
        })}
      </div>

      {/* Corregir / resultado */}
      {!graded ? (
        <button
          onClick={submit}
          disabled={busy || !allAnswered}
          className="mt-5 w-full rounded-lg bg-accent-600 py-3 text-sm font-semibold text-white disabled:opacity-40 active:scale-95"
        >
          {S.escuchaSubmit}
        </button>
      ) : (
        <div className="mt-5">
          <div className="rounded-xl border border-stone-200 bg-white p-5 text-center">
            <p className="text-2xl font-bold">{S.escuchaScore(graded.score, graded.total)}</p>
          </div>
          {/* Reveal: transcripción + contexto alemán */}
          <div className="mt-3 rounded-xl border border-stone-200 bg-stone-50 p-4">
            <p className="mb-1 text-xs font-semibold uppercase tracking-wide text-stone-500">
              {S.escuchaTranscript}
            </p>
            <p className="text-base text-stone-800">{graded.transcript}</p>
            <p className="mt-2 text-sm text-stone-500">🇩🇪 {graded.gist}</p>
          </div>
          <button
            onClick={load}
            className="mt-4 w-full rounded-lg border border-accent-300 py-3 text-sm font-semibold text-accent-700 active:scale-95"
          >
            {S.escuchaAgain}
          </button>
        </div>
      )}
    </>
  );
}
