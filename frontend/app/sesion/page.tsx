"use client";

/**
 * Sesión diaria — el arco de 20 min: entrada suave (vocabulario) → núcleo (UN concepto de
 * gramática: explicación + ejercicios de tus errores) → cierre (vocabulario de situación).
 * El plan viene congelado de GET /session/today; la corrección va por los caminos de siempre
 * (SRS / grading de ejercicios). El progreso se guarda tras cada ítem → cortar y continuar.
 * Azulejo: Verdict-Effekte, DE-Ebene, Finale mit Kachel-Moment.
 */

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { apiFetch } from "@/lib/api";
import { S } from "@/lib/strings";
import { IconCheckDraw } from "@/components/icons";
import {
  DeChip, Finale, PageHead, Progress,
  btnGhost, btnPrimary, btnPrimaryFull, btnVerdictNo, btnVerdictSi, cardQuiet,
} from "@/components/ui";

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

  const [regenBusy, setRegenBusy] = useState(false);

  // Estado por ítem
  const [revealed, setRevealed] = useState(false);
  const [answer, setAnswer] = useState("");
  const [verdict, setVerdict] = useState<Verdict | null>(null);
  const [writeResult, setWriteResult] = useState<boolean | null>(null);

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
    setWriteResult(null);
  }

  // Acentos/mayúsculas no cuentan en el recall escrito (drill, no examen).
  const norm = (s: string) =>
    s.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase().trim();

  function coreConceptSlug(): string | undefined {
    const it = session?.items.find((i) => i.kind === "exercise" || i.kind === "explain");
    return it && "concept_slug" in it ? it.concept_slug : undefined;
  }

  async function regenerate(replaceIndex: number | null, n: number) {
    if (!session || regenBusy) return;
    const slug = coreConceptSlug();
    if (!slug) return;
    setRegenBusy(true);
    try {
      const res = await apiFetch(`/session/${session.id}/exercises`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ slug, n, replace_index: replaceIndex }),
      });
      if (!res.ok) throw new Error();
      const data: { items: Item[]; replaced: boolean } = await res.json();
      if (!data.items?.length) return;
      const wasDone = idx >= session.items.length;
      setSession((s) => {
        if (!s) return s;
        const items = [...s.items];
        if (data.replaced && replaceIndex != null) items[replaceIndex] = data.items[0];
        else items.push(...data.items);
        return { ...s, items };
      });
      if (data.replaced) resetItem();
      else if (wasDone) setDone(false);
    } catch {
      /* si falla, no pasa nada — el usuario sigue */
    } finally {
      setRegenBusy(false);
    }
  }

  async function complete(id: string) {
    setDone(true);
    try {
      await apiFetch(`/session/${id}/complete`, { method: "POST" });
    } catch {
      /* la marca se reintenta al reabrir */
    }
  }

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
      /* la nota se pierde en silencio */
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

  // ---------- cierre: Finale (resultados ya transferidos durante la sesión) ----------
  if (done || idx >= total) {
    const stats = progress.reduce(
      (a, p) => {
        const kind = session.items[p.index]?.kind;
        if (kind === "exercise" && "correct" in p) { a.exTotal++; if (p.correct) a.exOk++; }
        if (kind === "vocab") a.vocab++;
        return a;
      },
      { exTotal: 0, exOk: 0, vocab: 0 },
    );
    return (
      <Finale>
        <p className="font-display text-2xl font-semibold">{S.sessionDoneToday}</p>
        <p className="mt-1 text-sm text-stone-500">{S.sessionDoneSub}</p>
        <div className="mt-3 space-y-0.5 text-sm tabular-nums text-stone-600">
          {stats.exTotal > 0 && <p>{S.sessionSummaryExercises(stats.exOk, stats.exTotal)}</p>}
          {stats.vocab > 0 && <p>{S.sessionSummaryVocab(stats.vocab)}</p>}
        </div>
        <p className="mt-2 text-xs text-stone-400">{S.sessionSaved}</p>
        <div className="mt-6 flex flex-col items-center gap-3">
          <button onClick={reroll} className={btnPrimary}>
            {S.sessionNewTraining}
          </button>
          {coreConceptSlug() && (
            <button onClick={() => regenerate(null, 3)} disabled={regenBusy}
                    className={`${btnGhost} text-accent-700 disabled:opacity-40`}>
              {regenBusy ? S.sessionRegenerating : S.sessionMore}
            </button>
          )}
        </div>
        <p className="mt-5">
          <Link href="/" className={btnGhost}>{S.sessionToInicio.replace("← ", "")}</Link>
        </p>
      </Finale>
    );
  }

  const item = session.items[idx];
  // Vocabulario: alternar recall (mostrar) y escritura (teclear). Cada segunda palabra se escribe.
  const vocabOrdinal = session.items.slice(0, idx).filter((i) => i.kind === "vocab").length;
  const writeMode = item.kind === "vocab" && vocabOrdinal % 2 === 1;

  const cardVerdict =
    (item.kind === "exercise" && verdict) ? (verdict.correct ? "verdict-good" : "verdict-bad")
    : (writeMode && writeResult !== null) ? (writeResult ? "verdict-good" : "verdict-bad")
    : "";

  return (
    <>
      <div className="mb-1 flex items-baseline justify-between gap-3">
        <h1 className="min-w-0 truncate font-display text-lg font-semibold">
          {session.headline || S.sessionVocabLabel}
        </h1>
        <span className="shrink-0 whitespace-nowrap text-xs tabular-nums text-stone-400">
          {idx + 1} / {total}
        </span>
      </div>
      <Progress value={idx} total={total} />

      <div className={`${cardQuiet} p-5 ${cardVerdict}`}>
        {/* ---------- vocab: recall (mostrar) o escritura (teclear) — ambos mueven SRS ---------- */}
        {item.kind === "vocab" && (
          <>
            <p className="text-xs uppercase tracking-[.12em] text-stone-400">
              {writeMode ? S.sessionWriteWord : S.sessionSaidWord}
            </p>
            <p className="mt-2 font-display text-xl font-medium"><DeChip />{item.prompt}</p>

            {writeMode ? (
              writeResult === null ? (
                <form
                  onSubmit={(e) => {
                    e.preventDefault();
                    if (answer.trim()) setWriteResult(norm(answer) === norm(item.answer));
                  }}
                  className="mt-5 flex gap-2"
                >
                  <input
                    value={answer}
                    onChange={(e) => setAnswer(e.target.value)}
                    placeholder={S.sessionWrite}
                    autoFocus
                    autoCapitalize="none"
                    autoCorrect="off"
                    className="w-full rounded-xl border border-stone-300 p-3 text-base outline-none focus:border-accent-500"
                  />
                  <button type="submit" disabled={!answer.trim()}
                          className="shrink-0 rounded-xl bg-accent-600 px-4 py-2 text-sm font-semibold text-white disabled:opacity-40 active:scale-[.97]">
                    {S.sessionCheck}
                  </button>
                </form>
              ) : (
                <>
                  <div className={`mt-4 rounded-xl p-3 ${writeResult ? "bg-green-50" : "bg-red-50"}`}>
                    {writeResult ? (
                      <p className="flex items-center gap-2 font-medium text-green-800">
                        <IconCheckDraw className="check-draw h-4 w-4" />
                        {S.sessionCorrect.replace("✓ ", "")}
                      </p>
                    ) : (
                      <p className="font-medium text-red-700">
                        {S.sessionSolution} <span className="text-green-800">{item.answer}</span>
                      </p>
                    )}
                  </div>
                  <button onClick={() => gradeVocab(writeResult)} disabled={busy} autoFocus
                          className={`mt-3 ${btnPrimaryFull}`}>
                    {S.sessionNext}
                  </button>
                </>
              )
            ) : (
              <>
                {revealed && (
                  <p className="mt-4 border-t border-stone-100 pt-4 font-display text-xl font-semibold text-green-700">
                    {item.answer}
                  </p>
                )}
                <div className="mt-5 flex gap-3">
                  {!revealed ? (
                    <button onClick={() => setRevealed(true)} className={btnPrimaryFull}>
                      {S.sessionReveal}
                    </button>
                  ) : (
                    <>
                      <button onClick={() => gradeVocab(false)} disabled={busy} className={btnVerdictNo}>
                        {S.sessionBad}
                      </button>
                      <button onClick={() => gradeVocab(true)} disabled={busy} className={btnVerdictSi}>
                        {S.sessionGood}
                      </button>
                    </>
                  )}
                </div>
              </>
            )}
          </>
        )}

        {/* ---------- explain: el núcleo, la regla detrás de tu error ---------- */}
        {item.kind === "explain" && (
          <>
            <p className="text-xs font-semibold uppercase tracking-[.12em] text-accent-600">{item.label}</p>
            <p className="mt-2 text-base text-stone-800">{item.explanation}</p>
            {item.rule_of_thumb && (
              <p className="mt-3 rounded-xl bg-stone-50 p-3 text-sm text-stone-700">
                <span className="font-semibold">{S.sessionRule}:</span> {item.rule_of_thumb}
              </p>
            )}
            {item.german_pitfall && (
              <p className="mt-2 rounded-xl bg-amber-50 p-3 text-sm text-stone-700">
                <DeChip />
                {item.german_pitfall}
              </p>
            )}
            <button onClick={() => advance()} className={`mt-5 ${btnPrimaryFull}`}>
              {S.sessionUnderstood}
            </button>
          </>
        )}

        {/* ---------- fix: tu frase real, corrígela ---------- */}
        {item.kind === "fix" && (
          <>
            <p className="text-xs uppercase tracking-[.12em] text-stone-400">
              {S.sessionFixIntro} · {item.concept_label}
            </p>
            <p className="mt-2 font-display text-xl font-medium text-red-600">{item.prompt}</p>
            {revealed && (
              <p className="mt-4 border-t border-stone-100 pt-4 font-display text-xl font-semibold text-green-700">
                {item.answer}
              </p>
            )}
            <button onClick={() => (revealed ? advance() : setRevealed(true))}
                    className={`mt-5 ${btnPrimaryFull}`}>
              {revealed ? S.sessionNext : S.sessionReveal}
            </button>
          </>
        )}

        {/* ---------- exercise: mcq / cloze, corrige el backend ---------- */}
        {item.kind === "exercise" && (
          <>
            {!verdict && (
              <p className="mb-1 text-right">
                <button onClick={() => regenerate(idx, 1)} disabled={regenBusy || busy}
                        className={`${btnGhost} text-xs disabled:opacity-50`}>
                  {regenBusy ? S.sessionRegenerating : S.sessionOtra}
                </button>
              </p>
            )}
            <p className="mb-4 font-display text-lg">{item.prompt}</p>

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
                  className="w-full rounded-xl border border-stone-300 p-3 text-base outline-none focus:border-accent-500"
                />
                <button type="submit" disabled={busy || !answer.trim()}
                        className="shrink-0 rounded-xl bg-accent-600 px-4 py-2 text-sm font-semibold text-white disabled:opacity-40 active:scale-[.97]">
                  {S.sessionCheck}
                </button>
              </form>
            )}

            {verdict && (
              <>
                <div className={`mt-4 rounded-xl p-3 ${verdict.correct ? "bg-green-50" : "bg-red-50"}`}>
                  {verdict.correct ? (
                    <p className="flex items-center gap-2 font-medium text-green-800">
                      <IconCheckDraw className="check-draw h-4 w-4" />
                      {S.sessionCorrect.replace("✓ ", "")}
                    </p>
                  ) : (
                    <p className="font-medium text-red-700">
                      {S.sessionSolution} <span className="text-green-800">{verdict.solution}</span>
                    </p>
                  )}
                  <p className="mt-1 text-sm text-stone-600">{verdict.explanation}</p>
                </div>
                <button onClick={() => advance(verdict.correct)} autoFocus
                        className={`mt-3 ${btnPrimaryFull}`}>
                  {S.sessionNext}
                </button>
              </>
            )}
          </>
        )}
      </div>

      {/* cambiar sesión — acción consciente del usuario */}
      <p className="mt-5 text-center">
        <button onClick={reroll} className={`${btnGhost} text-xs`}>
          {S.sessionChange}
        </button>
      </p>
    </>
  );
}
