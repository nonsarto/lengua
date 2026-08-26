"use client";

/**
 * Subir material — el quinto acceso, un momento de "sentarse" (aquí SÍ hay menú, a diferencia
 * de Capturar). Dos vías:
 *  · Material de estudio (PDF/imagen/texto) → analyze() propone modo (Gramática/Vocabulario/
 *    Ambos), muestra qué CONCEPTOS existentes toca (enlaza, nunca copia la explicación) y qué
 *    vocabulario es nuevo. Solo tras confirmar se escribe (boost + import en frío).
 *  · Lista de vocabulario (CSV/TSV) → parseo determinista, sin IA (importar en frío).
 */

import { useCallback, useEffect, useRef, useState } from "react";
import Link from "next/link";
import { apiFetch } from "@/lib/api";
import { S } from "@/lib/strings";
import { PageHead } from "@/components/ui";

// ---------------------------------------------------------------- tipos
type Sample = { term: string; translation: string; status: "new" | "dup" };
type CsvPreview = {
  delimiter: string; columns: number; has_header: boolean;
  term_col: number; translation_col: number;
  total: number; new_count: number; dup_count: number; sample: Sample[];
};
type DocConcept = { slug: string; label: string; cefr: string | null; why: string; in_backbone: boolean };
type DocLemma = { term: string; translation: string; register: string; region: string | null; new: boolean };
type DocPreview = {
  suggested_mode: "grammar" | "vocab" | "both"; summary: string | null; kind: string;
  concepts: DocConcept[]; lemmas: DocLemma[];
  linked_count: number; new_concept_count: number; new_vocab_count: number;
  analysis: Record<string, unknown>;
};
type UploadFile = { media_type: string; data: string; filename: string };

function fileToB64(file: File): Promise<UploadFile> {
  return new Promise((resolve, reject) => {
    const r = new FileReader();
    r.onload = () => {
      const s = String(r.result);
      resolve({
        media_type: file.type || "application/octet-stream",
        data: s.slice(s.indexOf(",") + 1),
        filename: file.name,
      });
    };
    r.onerror = reject;
    r.readAsDataURL(file);
  });
}

export default function Subir() {
  const [tab, setTab] = useState<"doc" | "list">("doc");
  return (
    <>
      <PageHead backHref="/vocabulario" backLabel={S.vocabularioTitle} />
      <h1 className="mb-3 font-display text-2xl font-bold">{S.importTitle}</h1>

      <div className="mb-5 flex gap-1 rounded-2xl bg-stone-100 p-1 text-sm">
        {(["doc", "list"] as const).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`flex-1 rounded-xl px-3 py-1.5 font-medium transition ${
              tab === t ? "bg-white text-stone-900 shadow-sm" : "text-stone-500"
            }`}
          >
            {t === "doc" ? S.uploadTabDoc : S.uploadTabList}
          </button>
        ))}
      </div>

      {tab === "doc" ? <DocLane /> : <CsvLane />}
    </>
  );
}

// ==================================================================== material de estudio (IA)
function DocLane() {
  const [text, setText] = useState("");
  const [files, setFiles] = useState<UploadFile[]>([]);
  const [analyzing, setAnalyzing] = useState(false);
  const [preview, setPreview] = useState<DocPreview | null>(null);
  const [mode, setMode] = useState<"grammar" | "vocab" | "both">("both");
  const [committing, setCommitting] = useState(false);
  const [done, setDone] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function onFiles(e: React.ChangeEvent<HTMLInputElement>) {
    const picked = Array.from(e.target.files ?? []);
    if (picked.length) setFiles(await Promise.all(picked.map(fileToB64)));
  }

  async function analyze() {
    if (!text.trim() && files.length === 0) {
      setError(S.uploadNothing);
      return;
    }
    setAnalyzing(true);
    setError(null);
    setDone(null);
    try {
      const res = await apiFetch(`/upload/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text, files }),
      });
      if (!res.ok) throw new Error();
      const p: DocPreview = await res.json();
      if (p.concepts.length === 0 && p.lemmas.length === 0) {
        setError(S.uploadNothing);
        setPreview(null);
      } else {
        setPreview(p);
        setMode(p.suggested_mode);
      }
    } catch {
      setError(S.uploadFailed);
    } finally {
      setAnalyzing(false);
    }
  }

  async function commit() {
    if (!preview) return;
    setCommitting(true);
    setError(null);
    try {
      const res = await apiFetch(`/upload/commit`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          mode,
          analysis: preview.analysis,
          kind: preview.kind,
          filename: files[0]?.filename ?? null,
        }),
      });
      if (!res.ok) throw new Error();
      const d = await res.json();
      setDone(S.uploadDone((d.concepts_boosted ?? []).length, d.vocab_imported ?? 0));
      setPreview(null);
      setText("");
      setFiles([]);
    } catch {
      setError(S.uploadFailed);
    } finally {
      setCommitting(false);
    }
  }

  const showConcepts = mode !== "vocab";
  const showVocab = mode !== "grammar";

  return (
    <>
      <p className="mb-3 text-sm text-stone-500">{S.uploadDocHint}</p>

      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder={S.uploadDocPlaceholder}
        rows={4}
        className="w-full resize-y rounded-xl border border-stone-300 bg-white px-3 py-2 text-sm outline-none focus:border-accent-500"
      />
      <div className="mt-2 flex items-center gap-3">
        <label className="cursor-pointer rounded-lg border border-stone-300 bg-white px-3 py-1.5 text-sm active:scale-95">
          {S.importFileBtn}
          <input type="file" accept=".pdf,application/pdf,image/*" multiple
                 onChange={onFiles} className="hidden" />
        </label>
        {files.length > 0 && <span className="text-xs text-stone-400">{S.uploadFilesPicked(files.length)}</span>}
        <button
          onClick={analyze}
          disabled={analyzing || (!text.trim() && files.length === 0)}
          className="ml-auto rounded-xl bg-accent-600 px-4 py-1.5 text-sm font-semibold text-white disabled:opacity-40 active:scale-[.97] transition-transform"
        >
          {analyzing ? S.uploadAnalyzing : S.uploadAnalyzeBtn}
        </button>
      </div>

      {done && <p className="mt-4 rounded-lg bg-green-50 px-3 py-2 text-sm text-green-700">{done}</p>}
      {error && <p className="mt-4 text-sm text-red-600">{error}</p>}

      {preview && (
        <section className="mt-6">
          {preview.summary && <p className="mb-4 text-sm italic text-stone-500">{preview.summary}</p>}

          {/* Modo — la excepción consciente a "sin menú": la análisis propone, tú confirmas. */}
          <p className="mb-2 text-sm font-semibold">{S.uploadModeQ}</p>
          <div className="mb-5 flex gap-2">
            {(["grammar", "vocab", "both"] as const).map((m) => (
              <button
                key={m}
                onClick={() => setMode(m)}
                className={`flex-1 rounded-lg border px-3 py-2 text-sm font-medium ${
                  mode === m
                    ? "border-accent-500 bg-accent-50 text-accent-800"
                    : "border-stone-200 bg-white text-stone-600"
                }`}
              >
                {m === "grammar" ? S.uploadModeGrammar : m === "vocab" ? S.uploadModeVocab : S.uploadModeBoth}
                {preview.suggested_mode === m && (
                  <span className="ml-1 text-[10px] text-stone-400">· {S.uploadSuggested}</span>
                )}
              </button>
            ))}
          </div>

          {showConcepts && preview.concepts.length > 0 && (
            <div className="mb-5">
              <h2 className="mb-2 text-sm font-semibold uppercase tracking-wide text-stone-500">
                {S.uploadConceptsTitle}
              </h2>
              <ul className="divide-y divide-stone-100 rounded-2xl border border-stone-200 bg-white">
                {preview.concepts.map((c) => (
                  <li key={c.slug} className="p-3">
                    <div className="flex items-baseline justify-between gap-3">
                      <span className="font-medium">{c.label}</span>
                      <span
                        className={`shrink-0 rounded-full px-2 py-0.5 text-[10px] font-medium ${
                          c.in_backbone ? "bg-accent-100 text-accent-800" : "bg-orange-50 text-orange-700"
                        }`}
                      >
                        {c.in_backbone ? S.uploadConceptLinked : S.uploadConceptNew}
                      </span>
                    </div>
                    {c.why && <p className="mt-0.5 text-xs text-stone-400">{c.why}</p>}
                  </li>
                ))}
              </ul>
              <p className="mt-2 text-xs text-stone-400">{S.uploadBoostNote}</p>
            </div>
          )}

          {showVocab && preview.lemmas.length > 0 && (
            <div className="mb-5">
              <h2 className="mb-2 text-sm font-semibold uppercase tracking-wide text-stone-500">
                {S.uploadVocabTitle} · {S.uploadVocabCounts(preview.new_vocab_count, preview.lemmas.length)}
              </h2>
              <ul className="divide-y divide-stone-100 rounded-2xl border border-stone-200 bg-white">
                {preview.lemmas.slice(0, 12).map((l, i) => (
                  <li key={i} className="flex items-baseline justify-between gap-3 p-3">
                    <span className="min-w-0 flex-1 truncate">
                      <span className="font-medium">{l.term}</span>
                      <span className="text-stone-400"> — {l.translation}</span>
                    </span>
                    <span
                      className={`shrink-0 rounded-full px-2 py-0.5 text-[10px] font-medium ${
                        l.new ? "bg-accent-100 text-accent-800" : "bg-stone-100 text-stone-400"
                      }`}
                    >
                      {l.new ? S.importBadgeNew : S.importBadgeDup}
                    </span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          <button
            onClick={commit}
            disabled={committing}
            className="w-full rounded-xl bg-accent-600 px-4 py-3 text-sm font-semibold text-white disabled:opacity-40 active:scale-[.97] transition-transform"
          >
            {committing ? S.uploadCommitting : S.uploadCommitBtn}
          </button>
        </section>
      )}
    </>
  );
}

// ==================================================================== lista CSV/TSV (determinista)
function CsvLane() {
  const [text, setText] = useState("");
  const [termCol, setTermCol] = useState(0);
  const [translationCol, setTranslationCol] = useState(1);
  const [hasHeader, setHasHeader] = useState<boolean | null>(null);
  const [situation, setSituation] = useState("");
  const [preview, setPreview] = useState<CsvPreview | null>(null);
  const [committing, setCommitting] = useState(false);
  const [done, setDone] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const debounce = useRef<ReturnType<typeof setTimeout> | null>(null);

  const runPreview = useCallback(async () => {
    if (!text.trim()) {
      setPreview(null);
      return;
    }
    try {
      const res = await apiFetch(`/import/vocab/preview`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text, term_col: termCol, translation_col: translationCol, has_header: hasHeader }),
      });
      if (!res.ok) throw new Error();
      const p: CsvPreview = await res.json();
      setPreview(p);
      if (hasHeader === null) setHasHeader(p.has_header);
      setError(null);
    } catch {
      setError(S.importFailed);
    }
  }, [text, termCol, translationCol, hasHeader]);

  useEffect(() => {
    setDone(null);
    if (debounce.current) clearTimeout(debounce.current);
    debounce.current = setTimeout(runPreview, 350);
    return () => {
      if (debounce.current) clearTimeout(debounce.current);
    };
  }, [runPreview]);

  function onFile(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => {
      const content = String(reader.result ?? "");
      // Binärdateien landen sonst als Müll im Feld und die Dup-Meldung behauptet
      // "alles schon vorhanden" -- hier ehrlich abfangen. Leere Datei ebenso.
      if (!content.trim()) {
        setError(S.importEmpty);
        return;
      }
      if (/[\u0000-\u0008\u000E-\u001F\uFFFD]/.test(content)) {
        setError(S.importUnreadable);
        return;
      }
      setError(null);
      setHasHeader(null);
      setText(content);
    };
    reader.readAsText(file);
  }

  async function commit() {
    if (!preview || preview.new_count === 0) return;
    setCommitting(true);
    setError(null);
    try {
      const res = await apiFetch(`/import/vocab/commit`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          text,
          delimiter: preview.delimiter,
          term_col: termCol,
          translation_col: translationCol,
          has_header: !!hasHeader,
          situation_name: situation.trim() || null,
        }),
      });
      if (!res.ok) throw new Error();
      const d = await res.json();
      setDone(S.importDone(d.imported, d.skipped));
      setText("");
      setPreview(null);
      setSituation("");
      setHasHeader(null);
    } catch {
      setError(S.importFailed);
    } finally {
      setCommitting(false);
    }
  }

  const colOptions = preview ? Array.from({ length: preview.columns }, (_, i) => i) : [0, 1];

  return (
    <>
      <p className="mb-3 text-sm text-stone-500">{S.importHint}</p>
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder={S.importPastePlaceholder}
        rows={6}
        className="w-full resize-y rounded-xl border border-stone-300 bg-white px-3 py-2 font-mono text-sm outline-none focus:border-accent-500"
      />

      <div className="mt-2 flex items-center gap-3">
        <label className="cursor-pointer rounded-lg border border-stone-300 bg-white px-3 py-1.5 text-sm active:scale-95">
          {S.importFileBtn}
          <input type="file" accept=".csv,.tsv,.txt,text/csv,text/tab-separated-values,text/plain"
                 onChange={onFile} className="hidden" />
        </label>
        {preview && <span className="text-xs text-stone-400">{S.importDetected(preview.delimiter)}</span>}
      </div>

      {done && <p className="mt-4 rounded-lg bg-green-50 px-3 py-2 text-sm text-green-700">{done}</p>}
      {error && <p className="mt-4 text-sm text-red-600">{error}</p>}

      {/* 0 erkannte Zeilen ≠ "alles schon vorhanden" — ehrlich unterscheiden */}
      {preview && preview.total === 0 && (
        <p className="mt-6 text-sm text-stone-500">{S.importNoRows}</p>
      )}

      {preview && preview.total > 0 && (
        <section className="mt-6">
          <div className="mb-3 flex flex-wrap items-end gap-3">
            <label className="text-xs text-stone-500">
              {S.importColTerm}
              <select value={termCol} onChange={(e) => setTermCol(Number(e.target.value))}
                      className="ml-2 rounded border border-stone-300 bg-white px-2 py-1 text-sm">
                {colOptions.map((i) => <option key={i} value={i}>{i + 1}</option>)}
              </select>
            </label>
            <label className="text-xs text-stone-500">
              {S.importColTranslation}
              <select value={translationCol} onChange={(e) => setTranslationCol(Number(e.target.value))}
                      className="ml-2 rounded border border-stone-300 bg-white px-2 py-1 text-sm">
                {colOptions.map((i) => <option key={i} value={i}>{i + 1}</option>)}
              </select>
            </label>
            <label className="flex items-center gap-1.5 text-xs text-stone-500">
              <input type="checkbox" checked={!!hasHeader} onChange={(e) => setHasHeader(e.target.checked)} />
              {S.importHasHeader}
            </label>
          </div>

          <input
            value={situation}
            onChange={(e) => setSituation(e.target.value)}
            placeholder={S.importSituationPlaceholder}
            aria-label={S.importSituation}
            className="mb-4 w-full rounded-lg border border-stone-300 bg-white px-3 py-2 text-sm outline-none focus:border-accent-500"
          />

          <h2 className="mb-2 text-sm font-semibold uppercase tracking-wide text-stone-500">
            {S.importPreviewTitle} · {S.importCounts(preview.new_count, preview.dup_count)}
          </h2>
          <ul className="mb-4 divide-y divide-stone-100 rounded-2xl border border-stone-200 bg-white">
            {preview.sample.map((row, i) => (
              <li key={i} className="flex items-baseline justify-between gap-3 p-3">
                <span className="min-w-0 flex-1 truncate">
                  <span className="font-medium">{row.term}</span>
                  <span className="text-stone-400"> — {row.translation}</span>
                </span>
                <span
                  className={`shrink-0 rounded-full px-2 py-0.5 text-[10px] font-medium ${
                    row.status === "new" ? "bg-accent-100 text-accent-800" : "bg-stone-100 text-stone-400"
                  }`}
                >
                  {row.status === "new" ? S.importBadgeNew : S.importBadgeDup}
                </span>
              </li>
            ))}
          </ul>

          {preview.new_count > 0 ? (
            <button onClick={commit} disabled={committing}
                    className="w-full rounded-xl bg-accent-600 px-4 py-3 text-sm font-semibold text-white disabled:opacity-40 active:scale-[.97] transition-transform">
              {committing ? S.importing : S.importCommitBtn(preview.new_count)}
            </button>
          ) : (
            <p className="text-sm text-stone-500">{S.importNothingNew}</p>
          )}
        </section>
      )}
    </>
  );
}
