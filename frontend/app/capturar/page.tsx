"use client";

/**
 * Capturar — la única puerta de entrada. UNA superficie, SIN menú de modo:
 * el usuario tira lo que sea (texto o foto) y analyze() infiere la intención después.
 * La respuesta es una microdosis: corrección + traducción + una frase de porqué —
 * y el resto se archiva en silencio. Debajo: el historial de capturas recientes.
 * Deep-link: /capturar?mode=camera|voz|texto
 */

import { Suspense, useEffect, useRef, useState } from "react";
import { useSearchParams } from "next/navigation";
import { API } from "@/lib/api";

type Correction = { wrong: string; correct: string; why: string; concept_slug: string };

type CaptureResult = {
  mode: string;
  gist: string | null;
  correction: Correction | null;
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

const MODE_LABEL: Record<string, string> = {
  check: "revisado",
  decode: "descifrado",
  brief: "preparación",
  listen: "escuchado",
};

function timeAgo(iso: string): string {
  const mins = Math.max(0, Math.round((Date.now() - new Date(iso).getTime()) / 60000));
  if (mins < 1) return "ahora";
  if (mins < 60) return `hace ${mins} min`;
  const hours = Math.round(mins / 60);
  if (hours < 24) return `hace ${hours} h`;
  return `hace ${Math.round(hours / 24)} d`;
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
  const fileRef = useRef<HTMLInputElement>(null);
  const textRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (mode === "camera") fileRef.current?.click();
    else textRef.current?.focus();
  }, [mode]);

  // Historial al entrar (silencioso — si el backend no está, simplemente no hay lista)
  useEffect(() => {
    fetch(`${API}/captures?limit=15`)
      .then((r) => (r.ok ? r.json() : []))
      .then(setHistory)
      .catch(() => {});
  }, []);

  // Vista previa de la foto (y limpieza del object URL)
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
    if (!text.trim() && !photo) return;
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
      const res = await fetch(`${API}/capture`, {
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
          text: sentText || "(foto)",
          mode: data.mode,
          created_at: new Date().toISOString(),
          correction: data.correction,
        },
        ...h,
      ]);
      setText("");
      setPhoto(null);
      if (fileRef.current) fileRef.current.value = "";
    } catch (e) {
      setError(e instanceof Error ? e.message : "algo falló");
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <h1 className="mb-4 text-2xl font-bold">Capturar</h1>

      {/* LA superficie — sin menú previo. Texto, foto, lo que sea. */}
      <div className="rounded-xl border border-stone-300 bg-white focus-within:border-amber-500">
        {photoUrl && (
          <div className="flex items-center gap-3 border-b border-stone-100 p-3">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={photoUrl}
              alt="Foto capturada"
              className="h-16 w-16 rounded-lg object-cover"
            />
            <span className="text-sm text-stone-500">Foto lista para analizar</span>
            <button
              onClick={() => setPhoto(null)}
              aria-label="Quitar foto"
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
              ? "La voz llega pronto — de momento, escribe lo que oíste…"
              : photoUrl
                ? "Contexto opcional para la foto…"
                : "Lo que dijiste, lo que viste, lo que no entendiste…"
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
          📷 Cámara
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
          disabled={busy || (!text.trim() && !photo)}
          className="ml-auto rounded-lg bg-amber-600 px-6 py-2 text-sm font-semibold text-white disabled:opacity-40 active:scale-95"
        >
          {busy ? "analizando…" : "Capturar"}
        </button>
      </div>

      {error && (
        <p className="mt-4 rounded-lg bg-red-50 p-3 text-sm text-red-700">
          No se pudo capturar ({error}). ¿Está corriendo el backend?
        </p>
      )}

      {/* La microdosis — corrección + traducción + una frase. Nada de lección completa. */}
      {result && (
        <div className="mt-6 rounded-xl border border-stone-200 bg-white p-4">
          <span className="mb-2 inline-block rounded-full bg-stone-100 px-2 py-0.5 text-[11px] uppercase tracking-wide text-stone-500">
            {MODE_LABEL[result.mode] ?? result.mode}
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
            <p className="text-base text-green-700">✓ Correcto.</p>
          )}

          {/* brief: el paquete de preparación está montado — un enlace, no la lección entera */}
          {result.written?.situation && (
            <a
              href={`/vocabulario/${result.written.situation.id}`}
              className="mb-2 block rounded-lg border border-amber-300 bg-amber-50/70 p-3 active:scale-[0.99]"
            >
              <p className="font-medium">📦 {result.written.situation.name}</p>
              <p className="mt-0.5 text-sm text-stone-600">
                {result.written.situation.vocab} palabras · {result.written.situation.phrases} frases
                · {result.written.situation.concepts.length} conceptos activados → ver paquete
              </p>
            </a>
          )}

          {/* La traducción alemana — del texto descifrado o de la frase corregida */}
          {result.gist && (
            <p className="mt-2 rounded-lg bg-stone-50 p-3 text-base text-stone-800">
              🇩🇪 {result.gist}
            </p>
          )}

          {/* Particularidades gramaticales del texto */}
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
            <span>guardado en silencio ✓</span>
            {result.correction && (
              <a
                href={`/gramatica/${result.correction.concept_slug}`}
                className="text-stone-500 underline-offset-2 hover:underline"
              >
                → ver lección
              </a>
            )}
          </p>
        </div>
      )}

      {/* Historial — lo que has ido tirando, lo más nuevo arriba */}
      {history.length > 0 && (
        <section className="mt-8">
          <h2 className="mb-2 text-sm font-semibold uppercase tracking-wide text-stone-500">
            Últimas capturas
          </h2>
          <ul className="divide-y divide-stone-100 rounded-xl border border-stone-200 bg-white">
            {history.map((h) => (
              <li key={h.id} className="p-3">
                <p className="flex items-baseline justify-between gap-2">
                  <span className="truncate text-sm text-stone-700">{h.text}</span>
                  <span className="shrink-0 text-[11px] text-stone-400">
                    {MODE_LABEL[h.mode] ?? h.mode} · {timeAgo(h.created_at)}
                  </span>
                </p>
                {h.correction && (
                  <p className="mt-0.5 truncate text-sm font-medium text-green-700">
                    → {h.correction.correct}
                  </p>
                )}
              </li>
            ))}
          </ul>
        </section>
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
