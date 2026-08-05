"use client";

/**
 * Capturar — la única puerta de entrada. UNA superficie, SIN menú de modo:
 * el usuario tira lo que sea (texto o foto) y analyze() infiere la intención.
 * Microdosis de vuelta + archivo silencioso. Textos de lib/strings (es/ca).
 * Deep-link: /capturar?mode=camera|voz|texto
 */

import { Suspense, useEffect, useRef, useState } from "react";
import { useSearchParams } from "next/navigation";
import { apiFetch } from "@/lib/api";
import { S } from "@/lib/strings";

type Correction = { wrong: string; correct: string; why: string; concept_slug: string };

type CaptureResult = {
  mode: string;
  gist: string | null;
  correction: Correction | null;
  word: { term: string; translation: string; added: boolean } | null;
  transcript: string | null;
  notes: string;
  concepts: { slug: string; label: string }[];
  written?: {
    situation?: { id: string; name: string; vocab: number; phrases: number; concepts: string[] };
  };
};

type HistoryItem = {
  id: string;
  text: string;
  mode: string;
  created_at: string;
  correction: { wrong: string; correct: string } | null;
};

type CaptureDetail = {
  id: string;
  raw_text: string;
  kind: string;
  created_at: string;
  persisted: boolean;
  gist: string | null;
  notes: string;
  correction: { wrong: string; correct: string; why: string | null } | null;
  concepts: { slug: string; label: string; evidence: string | null }[];
  lemmas: { term: string; translation: string; register: string | null; region: string | null }[];
  word: { term: string; translation: string } | null;
};

/** Blob → base64 (sin prefijo data:) — para el audio grabado. */
async function blobToB64(blob: Blob): Promise<string> {
  const buf = new Uint8Array(await blob.arrayBuffer());
  let bin = "";
  const chunk = 0x8000;
  for (let i = 0; i < buf.length; i += chunk) {
    bin += String.fromCharCode(...buf.subarray(i, i + chunk));
  }
  return btoa(bin);
}

/** Foto → JPEG base64, reducida (el iPhone manda HEIC de 12MP; el canvas lo normaliza). */
async function fileToJpegB64(file: File, maxSide = 1568): Promise<string> {
  const bitmap = await createImageBitmap(file);
  const scale = Math.min(1, maxSide / Math.max(bitmap.width, bitmap.height));
  const canvas = document.createElement("canvas");
  canvas.width = Math.round(bitmap.width * scale);
  canvas.height = Math.round(bitmap.height * scale);
  canvas.getContext("2d")!.drawImage(bitmap, 0, 0, canvas.width, canvas.height);
  return canvas.toDataURL("image/jpeg", 0.85).split(",")[1];
}

function timeAgo(iso: string): string {
  const mins = Math.max(0, Math.round((Date.now() - new Date(iso).getTime()) / 60000));
  if (mins < 1) return S.timeNow;
  if (mins < 60) return S.timeMin(mins);
  const hours = Math.round(mins / 60);
  if (hours < 24) return S.timeH(hours);
  return S.timeD(Math.round(hours / 24));
}

function CapturarInner() {
  const params = useSearchParams();
  const mode = params.get("mode"); // deep-link del Action Button / Shortcut
  const [text, setText] = useState("");
  const [photo, setPhoto] = useState<File | null>(null);
  const [photoUrl, setPhotoUrl] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<CaptureResult | null>(null);
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [detail, setDetail] = useState<CaptureDetail | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [audio, setAudio] = useState<Blob | null>(null);
  const [recording, setRecording] = useState(false);
  const recRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<BlobPart[]>([]);
  const fileRef = useRef<HTMLInputElement>(null);
  const textRef = useRef<HTMLTextAreaElement>(null);

  async function startRec() {
    setError(null);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mime = MediaRecorder.isTypeSupported("audio/webm")
        ? "audio/webm"
        : MediaRecorder.isTypeSupported("audio/mp4")
          ? "audio/mp4"
          : "";
      const rec = new MediaRecorder(stream, mime ? { mimeType: mime } : undefined);
      chunksRef.current = [];
      rec.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data);
      };
      rec.onstop = () => {
        setAudio(new Blob(chunksRef.current, { type: rec.mimeType || "audio/webm" }));
        stream.getTracks().forEach((t) => t.stop());
      };
      rec.start();
      recRef.current = rec;
      setRecording(true);
    } catch {
      setError(S.micDenied);
    }
  }

  function stopRec() {
    recRef.current?.stop();
    recRef.current = null;
    setRecording(false);
  }

  // Historial clicable: abre el detalle (análisis completo) de una captura.
  async function openDetail(id: string) {
    setDetailLoading(true);
    setDetail(null);
    try {
      const r = await apiFetch(`/captures/${id}`);
      if (r.ok) setDetail(await r.json());
    } catch {
      /* si falla, el overlay se cierra solo al no haber datos */
    } finally {
      setDetailLoading(false);
    }
  }

  function closeDetail() {
    setDetail(null);
    setDetailLoading(false);
  }

  useEffect(() => {
    if (mode === "camera") fileRef.current?.click();
    else if (mode === "voz") startRec();  // Deep-link: directo a grabar (permiso mediante)
    else textRef.current?.focus();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [mode]);

  useEffect(() => {
    apiFetch(`/captures?limit=15`)
      .then((r) => (r.ok ? r.json() : []))
      .then(setHistory)
      .catch(() => {});
  }, []);

  useEffect(() => {
    if (!photo) {
      setPhotoUrl(null);
      return;
    }
    const url = URL.createObjectURL(photo);
    setPhotoUrl(url);
    return () => URL.revokeObjectURL(url);
  }, [photo]);

  async function submit() {
    if (!text.trim() && !photo && !audio) return;
    setBusy(true);
    setError(null);
    setResult(null);
    const sentText = text;
    try {
      const body: Record<string, unknown> = { text, source: "web" };
      if (photo) {
        body.image_b64 = await fileToJpegB64(photo);
        body.image_media_type = "image/jpeg";
      }
      if (audio) {
        body.audio_b64 = await blobToB64(audio);
        body.audio_media_type = audio.type || "audio/webm";
      }
      const res = await apiFetch(`/capture`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data: CaptureResult & { capture_id: string } = await res.json();
      setResult(data);
      setHistory((h) => [
        {
          id: data.capture_id,
          text: data.transcript || sentText || S.photoFallback,
          mode: data.mode,
          created_at: new Date().toISOString(),
          correction: data.correction,
        },
        ...h,
      ]);
      setText("");
      setPhoto(null);
      setAudio(null);
      if (fileRef.current) fileRef.current.value = "";
    } catch (e) {
      setError(e instanceof Error ? e.message : "?");
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <h1 className="mb-4 text-2xl font-bold">{S.capturarTitle}</h1>

      {/* LA superficie — sin menú previo. Texto, foto, lo que sea. */}
      <div className="rounded-xl border border-stone-300 bg-white focus-within:border-accent-500">
        {photoUrl && (
          <div className="flex items-center gap-3 border-b border-stone-100 p-3">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src={photoUrl} alt="Foto" className="h-16 w-16 rounded-lg object-cover" />
            <span className="text-sm text-stone-500">{S.photoReady}</span>
            <button
              onClick={() => setPhoto(null)}
              aria-label={S.photoRemove}
              className="ml-auto flex h-8 w-8 items-center justify-center rounded-full text-stone-400 hover:bg-stone-100"
            >
              ✕
            </button>
          </div>
        )}
        {audio && !recording && (
          <div className="flex items-center gap-3 border-b border-stone-100 p-3">
            <span className="text-xl">🎙</span>
            <span className="text-sm text-stone-500">{S.audioReady}</span>
            <button
              onClick={() => setAudio(null)}
              aria-label={S.audioRemove}
              className="ml-auto flex h-8 w-8 items-center justify-center rounded-full text-stone-400 hover:bg-stone-100"
            >
              ✕
            </button>
          </div>
        )}
        <textarea
          ref={textRef}
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder={
            mode === "voz"
              ? S.placeholderVoice
              : photoUrl
                ? S.placeholderPhotoContext
                : S.placeholderDefault
          }
          rows={4}
          className="w-full resize-none rounded-xl bg-transparent p-4 text-base outline-none"
        />
      </div>

      <div className="mt-3 flex items-center gap-3">
        <button
          onClick={() => fileRef.current?.click()}
          className="rounded-lg border border-stone-300 bg-white px-4 py-2 text-sm active:scale-95"
        >
          📷 {S.cameraBtn}
        </button>
        <button
          onClick={recording ? stopRec : startRec}
          className={`rounded-lg border px-4 py-2 text-sm active:scale-95 ${
            recording
              ? "animate-pulse border-red-300 bg-red-50 text-red-700"
              : "border-stone-300 bg-white"
          }`}
        >
          {recording ? `⏹ ${S.voiceStop}` : `🎤 ${S.voiceBtn}`}
        </button>
        <input
          ref={fileRef}
          type="file"
          accept="image/*"
          capture="environment"
          hidden
          onChange={(e) => setPhoto(e.target.files?.[0] ?? null)}
        />
        <button
          onClick={submit}
          disabled={busy || recording || (!text.trim() && !photo && !audio)}
          className="ml-auto rounded-lg bg-accent-600 px-6 py-2 text-sm font-semibold text-white disabled:opacity-40 active:scale-95"
        >
          {busy ? S.analyzing : S.captureBtn}
        </button>
      </div>

      {error && (
        <p className="mt-4 rounded-lg bg-red-50 p-3 text-sm text-red-700">
          {S.captureFailed(error)}
        </p>
      )}

      {/* La microdosis — corrección + traducción + una frase. Nada de lección completa. */}
      {result && (
        <div className="mt-6 rounded-xl border border-stone-200 bg-white p-4">
          <span className="mb-2 inline-block rounded-full bg-stone-100 px-2 py-0.5 text-[11px] uppercase tracking-wide text-stone-500">
            {S.modeLabels[result.mode] ?? result.mode}
          </span>

          {result.correction && (
            <div className="mb-2">
              <p className="text-base">
                <span className="text-red-600 line-through">{result.correction.wrong}</span>
              </p>
              <p className="text-lg font-semibold text-green-700">{result.correction.correct}</p>
              <p className="mt-1 text-sm text-stone-600">{result.correction.why}</p>
            </div>
          )}

          {!result.correction && result.mode === "check" && (
            <p className="text-base text-green-700">{S.correctMark}</p>
          )}

          {/* word: la entrada de diccionario — término, traducción, ¿nueva o ya tuya? */}
          {result.word && (
            <div className="mb-2">
              <p className="text-lg font-semibold">{result.word.term}</p>
              <p className="text-base text-stone-700">🇩🇪 {result.word.translation}</p>
              <p className={`mt-1 text-xs ${result.word.added ? "text-green-700" : "text-stone-400"}`}>
                {result.word.added ? S.wordAdded : S.wordKnown}
              </p>
            </div>
          )}

          {/* brief: paquete listo — un enlace, no la lección entera */}
          {result.written?.situation && (
            <a
              href={`/vocabulario/${result.written.situation.id}`}
              className="mb-2 block rounded-lg border border-accent-300 bg-accent-50/70 p-3 active:scale-[0.99]"
            >
              <p className="font-medium">📦 {result.written.situation.name}</p>
              <p className="mt-0.5 text-sm text-stone-600">
                {S.packageReady(
                  result.written.situation.vocab,
                  result.written.situation.phrases,
                  result.written.situation.concepts.length,
                )}
              </p>
            </a>
          )}

          {/* Lo que Whisper oyó — para poder juzgar la traducción */}
          {result.transcript && (
            <p className="mb-1 text-sm italic text-stone-500">
              🎙 {S.heard} “{result.transcript}”
            </p>
          )}

          {/* La traducción alemana — del texto descifrado o de la frase corregida */}
          {result.gist && (
            <p className="mt-2 rounded-lg bg-stone-50 p-3 text-base text-stone-800">
              🇩🇪 {result.gist}
            </p>
          )}

          {result.notes && <p className="mt-2 text-sm text-stone-600">{result.notes}</p>}

          {result.concepts.length > 0 && (
            <div className="mt-3 flex flex-wrap gap-1.5">
              {result.concepts.map((c) => (
                <span
                  key={c.slug}
                  className="rounded-full border border-stone-200 px-2 py-0.5 text-[11px] text-stone-500"
                >
                  {c.label}
                </span>
              ))}
            </div>
          )}

          <p className="mt-3 flex items-center justify-between text-xs text-stone-400">
            <span>{S.savedSilently}</span>
            {result.correction && (
              <a
                href={`/gramatica/${result.correction.concept_slug}`}
                className="text-stone-500 underline-offset-2 hover:underline"
              >
                {S.seeLesson}
              </a>
            )}
          </p>
        </div>
      )}

      {/* Historial — lo que has ido tirando, lo más nuevo arriba */}
      {history.length > 0 && (
        <section className="mt-8">
          <h2 className="mb-2 text-sm font-semibold uppercase tracking-wide text-stone-500">
            {S.historyTitle}
          </h2>
          <ul className="divide-y divide-stone-100 rounded-xl border border-stone-200 bg-white">
            {history.map((h) => (
              <li key={h.id}>
                <button
                  type="button"
                  onClick={() => openDetail(h.id)}
                  className="w-full p-3 text-left active:bg-stone-50"
                >
                  <p className="flex items-baseline justify-between gap-2">
                    <span className="truncate text-sm text-stone-700">{h.text}</span>
                    <span className="shrink-0 text-[11px] text-stone-400">
                      {S.modeLabels[h.mode] ?? h.mode} · {timeAgo(h.created_at)}
                    </span>
                  </p>
                  {h.correction && (
                    <p className="mt-0.5 truncate text-sm font-medium text-green-700">
                      → {h.correction.correct}
                    </p>
                  )}
                </button>
              </li>
            ))}
          </ul>
        </section>
      )}

      {/* Detalle de una captura: el análisis completo, tocando en el historial */}
      {(detailLoading || detail) && (
        <div
          className="fixed inset-0 z-50 flex items-end justify-center bg-black/30 p-0 sm:items-center sm:p-4"
          onClick={closeDetail}
        >
          <div
            className="max-h-[85vh] w-full max-w-lg overflow-y-auto rounded-t-2xl bg-white p-5 sm:rounded-2xl"
            onClick={(e) => e.stopPropagation()}
          >
            {detailLoading && !detail && (
              <p className="py-8 text-center text-sm text-stone-400">{S.detailLoading}</p>
            )}

            {detail && (
              <>
                <div className="mb-3 flex items-center justify-between gap-2">
                  <span className="inline-block rounded-full bg-stone-100 px-2 py-0.5 text-[11px] uppercase tracking-wide text-stone-500">
                    {S.modeLabels[detail.kind] ?? detail.kind} · {timeAgo(detail.created_at)}
                  </span>
                  <button
                    type="button"
                    onClick={closeDetail}
                    className="text-sm text-stone-400 active:text-stone-600"
                  >
                    {S.detailClose}
                  </button>
                </div>

                {/* Lo que tiraste */}
                <p className="mb-3 whitespace-pre-wrap rounded-lg bg-stone-50 p-3 text-sm text-stone-700">
                  {detail.raw_text}
                </p>

                {!detail.persisted && (
                  <p className="mb-3 text-xs text-stone-400">{S.detailPartial}</p>
                )}

                {detail.correction && (
                  <div className="mb-3">
                    <h3 className="mb-1 text-xs font-semibold uppercase tracking-wide text-stone-400">
                      {S.detailCorrection}
                    </h3>
                    <p className="text-red-600 line-through">{detail.correction.wrong}</p>
                    <p className="text-lg font-semibold text-green-700">
                      {detail.correction.correct}
                    </p>
                    {detail.correction.why && (
                      <p className="mt-1 text-sm text-stone-600">{detail.correction.why}</p>
                    )}
                  </div>
                )}

                {detail.word && (
                  <div className="mb-3">
                    <h3 className="mb-1 text-xs font-semibold uppercase tracking-wide text-stone-400">
                      {S.detailWord}
                    </h3>
                    <p className="text-lg font-semibold">{detail.word.term}</p>
                    <p className="text-base text-stone-700">🇩🇪 {detail.word.translation}</p>
                  </div>
                )}

                {detail.gist && (
                  <div className="mb-3">
                    <h3 className="mb-1 text-xs font-semibold uppercase tracking-wide text-stone-400">
                      {S.detailMeaning}
                    </h3>
                    <p className="rounded-lg bg-stone-50 p-3 text-base text-stone-800">
                      🇩🇪 {detail.gist}
                    </p>
                  </div>
                )}

                {detail.notes && (
                  <div className="mb-3">
                    <h3 className="mb-1 text-xs font-semibold uppercase tracking-wide text-stone-400">
                      {S.detailNotes}
                    </h3>
                    <p className="text-sm text-stone-600">{detail.notes}</p>
                  </div>
                )}

                {detail.concepts.length > 0 && (
                  <div className="mb-3">
                    <h3 className="mb-1 text-xs font-semibold uppercase tracking-wide text-stone-400">
                      {S.detailConcepts}
                    </h3>
                    <div className="flex flex-wrap gap-1.5">
                      {detail.concepts.map((c) => (
                        <a
                          key={c.slug}
                          href={`/gramatica/${c.slug}`}
                          className="rounded-full border border-stone-200 px-2 py-0.5 text-[11px] text-stone-500 active:bg-stone-50"
                        >
                          {c.label}
                        </a>
                      ))}
                    </div>
                  </div>
                )}

                {detail.lemmas.length > 0 && (
                  <div className="mb-1">
                    <h3 className="mb-1 text-xs font-semibold uppercase tracking-wide text-stone-400">
                      {S.detailVocab}
                    </h3>
                    <ul className="divide-y divide-stone-100 rounded-lg border border-stone-200">
                      {detail.lemmas.map((l, i) => (
                        <li key={`${l.term}-${i}`} className="flex items-baseline justify-between gap-2 p-2">
                          <span className="text-sm font-medium text-stone-700">{l.term}</span>
                          <span className="text-sm text-stone-500">{l.translation}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {!detail.correction && !detail.word && !detail.gist && !detail.notes &&
                  detail.concepts.length === 0 && detail.lemmas.length === 0 && (
                    <p className="text-sm text-stone-400">{S.detailEmpty}</p>
                  )}
              </>
            )}
          </div>
        </div>
      )}
    </>
  );
}

export default function Capturar() {
  return (
    <Suspense>
      <CapturarInner />
    </Suspense>
  );
}
