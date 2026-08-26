"use client";

/**
 * Session-Detail: Audio-Player (signierte URL), Transkript mit Inline-Markierungen,
 * korrigierte Fassung, Fehlerliste mit Wiederkehr-Zähler, Chunk-Liste mit Status.
 * Kein Score, keine Note. Offsets beziehen sich aufs Original-Transkript.
 */

import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { apiFetch } from "@/lib/api";
import { S } from "@/lib/strings";
import TranscriptHighlights, { germanSpans, Span } from "@/components/TranscriptHighlights";

type Detail = {
  session: {
    id: string;
    created_at: string;
    duration_sec: number | null;
    transcript: string;
    transcript_corrected: string | null;
    low_conf_spans: { model?: string; spans?: { char_start: number; char_end: number }[] } | null;
  };
  audio_url: string | null;
  errors: {
    error_type: string;
    original: string;
    corrected: string;
    explanation: string | null;
    char_start: number | null;
    char_end: number | null;
    recurrence: number;
  }[];
  chunks: {
    chunk_es: string;
    example_es: string;
    trigger_de: string | null;
    status: string;
    activated_at: string | null;
  }[];
};

const CHUNK_STYLE: Record<string, string> = {
  open: "bg-stone-100 text-stone-500",
  activated: "bg-green-50 text-green-700",
  dropped: "bg-stone-50 text-stone-300 line-through",
};

function Tile({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="mb-4 rounded-xl border border-stone-200 bg-white p-4">
      <h2 className="mb-2 text-xs font-semibold uppercase tracking-wide text-stone-500">{title}</h2>
      {children}
    </section>
  );
}

export default function HablarDetail() {
  const { id } = useParams<{ id: string }>();
  const [d, setD] = useState<Detail | null>(null);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    apiFetch(`/hablar/${id}`)
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then(setD)
      .catch(() => setFailed(true));
  }, [id]);

  if (failed)
    return (
      <>
        <p className="text-sm text-stone-400">{S.loadFailed}</p>
        <p className="mt-4">
          <Link href="/hablar" className="text-sm text-accent-700">
            ← {S.hablarTitle}
          </Link>
        </p>
      </>
    );
  if (d === null) return <p className="text-sm text-stone-400">{S.loading}</p>;

  const { session } = d;
  const spans: Span[] = [
    ...d.errors
      .filter((e) => e.char_start != null && e.char_end != null)
      .map((e) => ({ start: e.char_start!, end: e.char_end!, kind: "error" as const })),
    ...germanSpans(session.transcript, d.chunks.map((c) => c.trigger_de)),
    ...(session.low_conf_spans?.spans ?? []).map((s) => ({
      start: s.char_start, end: s.char_end, kind: "lowconf" as const,
    })),
  ];

  const date = new Date(session.created_at).toLocaleDateString("es-ES", {
    weekday: "long", day: "numeric", month: "long",
  });
  const mins = session.duration_sec
    ? `${Math.floor(session.duration_sec / 60)}:${String(session.duration_sec % 60).padStart(2, "0")}`
    : null;

  return (
    <>
      <h1 className="mb-1 text-2xl font-bold">{date}</h1>
      {mins && <p className="mb-4 text-xs text-stone-400">{mins} min</p>}

      {d.audio_url ? (
        <audio controls src={d.audio_url} className="mb-4 w-full" preload="metadata" />
      ) : (
        <p className="mb-4 text-xs text-stone-400">{S.hablarAudioMissing}</p>
      )}

      <Tile title={S.hablarTranscript}>
        <TranscriptHighlights text={session.transcript} spans={spans} />
        <p className="mt-3 text-[10px] text-stone-300">{S.hablarLegend}</p>
      </Tile>

      {session.transcript_corrected && (
        <Tile title={S.hablarCorrected}>
          <p className="whitespace-pre-wrap leading-relaxed text-stone-600">
            {session.transcript_corrected}
          </p>
        </Tile>
      )}

      {d.errors.length > 0 && (
        <Tile title={S.hablarErrorsTitle}>
          <div className="divide-y divide-stone-100">
            {d.errors.map((e, i) => (
              <div key={i} className="py-2.5 first:pt-0 last:pb-0">
                <p className="mb-1 flex items-center gap-2 text-xs">
                  <span className="rounded-full bg-red-50 px-1.5 py-px text-red-700">
                    {S.errorTypeLabels[e.error_type] ?? e.error_type}
                  </span>
                  {e.recurrence > 1 && (
                    <span className="text-stone-400">{S.hablarRecurrence(e.recurrence)}</span>
                  )}
                </p>
                <p className="text-sm">
                  <span className="text-stone-400 line-through">{e.original}</span>{" "}
                  <span className="font-medium">{e.corrected}</span>
                </p>
                {e.explanation && (
                  <p className="mt-0.5 text-xs text-stone-500">{e.explanation}</p>
                )}
              </div>
            ))}
          </div>
        </Tile>
      )}

      {d.chunks.length > 0 && (
        <Tile title={S.hablarChunksTitle}>
          <div className="divide-y divide-stone-100">
            {d.chunks.map((c, i) => (
              <div key={i} className="py-2.5 first:pt-0 last:pb-0">
                <p className="flex items-center gap-2 text-sm font-medium">
                  {c.chunk_es}
                  <span className={`rounded-full px-1.5 py-px text-xs font-normal ${CHUNK_STYLE[c.status] ?? ""}`}>
                    {S.chunkStatusLabels[c.status] ?? c.status}
                  </span>
                </p>
                {c.trigger_de && <p className="text-xs text-amber-700">{c.trigger_de}</p>}
                <p className="mt-0.5 text-xs italic text-stone-500">{c.example_es}</p>
              </div>
            ))}
          </div>
        </Tile>
      )}

      <Link href="/hablar" className="text-sm text-accent-700">
        ← {S.hablarTitle}
      </Link>
    </>
  );
}
