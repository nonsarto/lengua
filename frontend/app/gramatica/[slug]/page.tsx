"use client";

/**
 * Una lección del Temario = dos capas: MANTO personal (deine Fehler zuerst, wenn das
 * Thema heiß ist — Connect Layer) + CUERPO compartido (die eingefrorenen Lektions-Blöcke).
 * Unten die Dudas-Box: Klärungsfragen, gegroundet in Lektion + eigenen Fehlern; bewegt
 * NIE Lernstand. Die URL darf auch einen Konzept-Slug tragen — das Backend löst auf.
 */

import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { apiFetch } from "@/lib/api";
import { S } from "@/lib/strings";
import { IconArrowLeft, IconSend } from "@/components/icons";
import LessonBlocks, { Block } from "@/components/LessonBlocks";
import { NeedLine, StateDots } from "@/components/ui";

type Detail = {
  slug: string;
  level: string;
  title_es: string;
  subtitle_de: string | null;
  lesson: { blocks: Block[]; version: number } | null;
  corrections: { wrong: string; correct: string; created_at: string }[];
  state: string;
  need_count: number;
};

type ChatMsg = { role: "user" | "assistant"; content: string };

export default function Tema() {
  const { slug } = useParams<{ slug: string }>();
  const [d, setD] = useState<Detail | null>(null);
  const [missing, setMissing] = useState(false);
  const [chat, setChat] = useState<ChatMsg[]>([]);
  const [question, setQuestion] = useState("");
  const [chatBusy, setChatBusy] = useState(false);
  const [chatError, setChatError] = useState(false);

  useEffect(() => {
    apiFetch(`/grammar/topics/${slug}`)
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then(setD)
      .catch(() => setMissing(true));
  }, [slug]);

  async function ask() {
    const q = question.trim();
    if (!q || chatBusy || !d) return;
    setChatBusy(true);
    setChatError(false);
    setChat((c) => [...c, { role: "user", content: q }]);
    setQuestion("");
    try {
      const res = await apiFetch(`/grammar/topics/${d.slug}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: q, history: chat }),
      });
      if (!res.ok) throw new Error();
      const { answer } = await res.json();
      setChat((c) => [...c, { role: "assistant", content: answer }]);
    } catch {
      setChatError(true);
      setChat((c) => c.slice(0, -1)); // la pregunta vuelve al input
      setQuestion(q);
    } finally {
      setChatBusy(false);
    }
  }

  if (missing)
    return (
      <>
        <p className="text-sm text-stone-400">{S.temarioTopicMissing}</p>
        <p className="mt-4">
          <Link href="/gramatica" className="text-sm text-stone-500 underline-offset-2 hover:underline">
            ← {S.gramaticaTitle}
          </Link>
        </p>
      </>
    );
  if (!d) return <p className="text-sm text-stone-400">{S.loading}</p>;

  const promoted = d.state === "aprendiendo" || d.state === "flojo";

  return (
    <>
      <p className="mb-1 flex items-center gap-2 text-xs text-stone-400">
        <span>{d.level}</span>
        <StateDots state={d.state} />
        <NeedLine state={d.state} needCount={d.need_count} />
      </p>
      <h1 className="font-display text-2xl font-bold">{d.title_es}</h1>
      {d.subtitle_de && <p className="mb-4 mt-0.5 text-sm text-stone-400">{d.subtitle_de}</p>}

      {/* EL MANTO — tus errores primero, si el tema está caliente (Connect Layer) */}
      {promoted && d.corrections.length > 0 && (
        <section className="mb-6 rounded-xl border border-accent-300 bg-accent-50/70 p-4">
          <h2 className="mb-2 text-sm font-semibold uppercase tracking-wide text-accent-800">
            {S.yourProblem}
          </h2>
          <ul className="space-y-2">
            {d.corrections.slice(0, 3).map((c, i) => (
              <li key={i}>
                <p className="text-sm text-red-700 line-through">{c.wrong}</p>
                <p className="font-medium text-green-800">{c.correct}</p>
              </li>
            ))}
          </ul>
          <p className="mt-2 text-xs text-accent-700">{S.timesCaptured(d.need_count)}</p>
        </section>
      )}

      {/* EL CUERPO — die geteilte, eingefrorene Lektion */}
      {d.lesson ? (
        <LessonBlocks blocks={d.lesson.blocks} />
      ) : (
        <div className="mb-4 rounded-xl border border-dashed border-stone-300 bg-white p-5 text-center">
          <p className="text-sm text-stone-500">{S.temarioLessonPending}</p>
        </div>
      )}

      {/* Dudas — preguntas de aclaración, ancladas a la lección. Efímero: vive en el cliente. */}
      <div className="mb-4 rounded-2xl border border-stone-200 bg-white p-4">
        <h3 className="mb-2 text-xs font-semibold uppercase tracking-wide text-stone-500">
          {S.chatTitle}
        </h3>
        {chat.length > 0 && (
          <div className="mb-3 space-y-2">
            {chat.map((m, i) => (
              <div
                key={i}
                className={`max-w-[85%] whitespace-pre-wrap rounded-xl p-3 text-sm ${
                  m.role === "user"
                    ? "ml-auto bg-accent-50 text-stone-800"
                    : "bg-stone-50 text-stone-700"
                }`}
              >
                {m.content}
              </div>
            ))}
            {chatBusy && <p className="text-xs text-stone-400">{S.chatThinking}</p>}
          </div>
        )}
        <form
          onSubmit={(e) => {
            e.preventDefault();
            ask();
          }}
          className="rounded-xl border border-stone-300 focus-within:border-accent-500"
        >
          <textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={(e) => {
              // Enter sendet, Shift+Enter macht einen Zeilenumbruch
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                ask();
              }
            }}
            placeholder={S.chatPlaceholder}
            rows={3}
            className="w-full resize-none rounded-t-xl bg-transparent p-3 text-sm outline-none"
          />
          <div className="flex justify-end p-2 pt-0">
            <button
              type="submit"
              aria-label={S.chatSend}
              disabled={chatBusy || !question.trim()}
              className="flex h-9 w-9 items-center justify-center rounded-full bg-accent-600 text-lg text-white disabled:opacity-40 active:scale-95"
            >
              <IconSend className="h-4 w-4" />
            </button>
          </div>
        </form>
        {chatError && <p className="mt-2 text-sm text-red-700">{S.chatFailed}</p>}
      </div>

      <p className="mt-6">
        <Link href="/gramatica" className="inline-flex items-center gap-1.5 text-sm text-stone-400 underline-offset-4 hover:underline">
          <IconArrowLeft className="h-3.5 w-3.5" />{S.gramaticaTitle}
        </Link>
      </p>
    </>
  );
}
