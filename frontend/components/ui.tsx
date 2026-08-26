/**
 * Azulejo-Primitive (Designkonzept, Abschnitt 04): die kleinen Bausteine,
 * aus denen jeder Screen besteht. Eine Antwort pro Aufgabe:
 * StateDots (Lernstand als Tinte) · DeChip (deutsche Inhalte) · PageHead
 * (Header-Regel) · Progress · EmptyState/ErrorState · Button-Klassen · Finale.
 */

import Link from "next/link";
import { S } from "@/lib/strings";
import { IconArrowLeft } from "./icons";

/* ---------- Button-Rollen (Klassen, damit disabled/handler frei bleiben) ---------- */
export const btnPrimary =
  "rounded-xl bg-accent-600 px-5 py-2.5 text-sm font-semibold text-white " +
  "disabled:opacity-40 active:scale-[.97] transition-transform";
export const btnPrimaryFull = `${btnPrimary} w-full py-3`;
export const btnSecondary =
  "rounded-xl border border-stone-300 bg-white px-4 py-2 text-sm text-stone-600 " +
  "disabled:opacity-40 active:scale-[.97] transition-transform";
export const btnGhost =
  "text-sm text-stone-500 underline-offset-4 hover:underline active:opacity-70";
export const btnVerdictNo =
  "flex-1 rounded-xl border border-red-200 bg-white py-2.5 text-sm font-semibold " +
  "text-red-700 active:scale-[.97] transition-transform disabled:opacity-40";
export const btnVerdictSi =
  "flex-1 rounded-xl border border-green-200 bg-white py-2.5 text-sm font-semibold " +
  "text-green-700 active:scale-[.97] transition-transform disabled:opacity-40";

/* ---------- Karten ---------- */
export const cardQuiet = "rounded-2xl border border-stone-200 bg-white";
export const cardLift = "rounded-2xl bg-accent-600 text-white";

/* ---------- Lernstand: Tinte statt Ampel ---------- */
const DOT_FILL: Record<string, number> = {
  sin_ver: 0, visto: 1, flojo: 1, aprendiendo: 2, dominado: 3,
};

export function StateDots({ state }: { state: string }) {
  const filled = DOT_FILL[state] ?? 0;
  const needful = state === "flojo" || state === "aprendiendo";
  const tone = needful ? "text-accent-600" : state === "dominado" ? "text-stone-900" : "text-stone-400";
  return (
    <span className={`shrink-0 text-[11px] tracking-[2px] ${tone}`} aria-label={S.stateLabels[state] ?? state}>
      {"●".repeat(filled)}{"○".repeat(3 - filled)}
    </span>
  );
}

/** Die eine akzentfarbene Zeile: nur "braucht dich" darf Farbe tragen. */
export function NeedLine({ state, needCount }: { state: string; needCount: number }) {
  if (state !== "flojo" && state !== "aprendiendo") return null;
  return (
    <span className="text-xs font-semibold text-accent-600">
      {S.needsPractice}{needCount > 0 ? ` · ${S.errorsCaptured(needCount)}` : ""}
    </span>
  );
}

/* ---------- DE-Ebene ---------- */
export function DeChip() {
  return (
    <span className="mr-1.5 inline-block rounded-[5px] bg-amber-100 px-1.5 py-px align-[3px] text-[9px] font-bold tracking-[.08em] text-amber-700">
      DE
    </span>
  );
}

/* ---------- Header-Regel: Zurück + Herkunft links, Zähler rechts; Titel darunter ---------- */
export function PageHead({ backHref, backLabel, title, counter, serif = false }: {
  backHref?: string; backLabel?: string; title?: string; counter?: string; serif?: boolean;
}) {
  return (
    <>
      {(backHref || counter) && (
        <p className="mb-1 flex items-center justify-between text-xs text-stone-500">
          {backHref ? (
            <Link href={backHref} className="flex items-center gap-1.5 underline-offset-4 hover:underline">
              <IconArrowLeft className="h-3.5 w-3.5" />
              {backLabel}
            </Link>
          ) : <span />}
          {counter && <span className="tabular-nums text-stone-400">{counter}</span>}
        </p>
      )}
      {title && (
        <h1 className={`mb-4 text-2xl font-bold ${serif ? "font-display" : ""}`}>{title}</h1>
      )}
    </>
  );
}

/* ---------- Fortschritt: DER eine Balken ---------- */
export function Progress({ value, total }: { value: number; total: number }) {
  return (
    <div className="mb-5 h-[3px] overflow-hidden rounded-full bg-stone-200">
      <div
        className="h-full rounded-full bg-accent-600 transition-all duration-300"
        style={{ width: `${total > 0 ? (value / total) * 100 : 0}%` }}
      />
    </div>
  );
}

/* ---------- Leer & Fehler: je EIN Muster ---------- */
export function EmptyState({ title, hint }: { title: string; hint?: string }) {
  return (
    <div className="rounded-2xl border border-stone-200 bg-white p-5 text-center">
      <p className="text-sm font-semibold text-stone-700">{title}</p>
      {hint && <p className="mt-0.5 text-xs text-stone-400">{hint}</p>}
    </div>
  );
}

export function ErrorState({ text, onRetry }: { text?: string; onRetry?: () => void }) {
  return (
    <div className="rounded-2xl border border-stone-200 bg-white p-5 text-center">
      <p className="text-sm font-semibold text-stone-700">{text ?? S.loadFailed}</p>
      {onRetry && (
        <button onClick={onRetry} className={`mt-2 ${btnGhost}`}>
          {S.retryBtn}
        </button>
      )}
    </div>
  );
}

/* ---------- Session-Finale: Kreis zeichnet sich, Kacheln rieseln einmalig ---------- */
export function Finale({ children }: { children: React.ReactNode }) {
  return (
    <div className="relative">
      <div className="finale-tiles" aria-hidden="true">
        {Array.from({ length: 12 }, (_, i) => <i key={i} />)}
      </div>
      <div className="rounded-2xl border border-stone-200 bg-white p-8 text-center">
        <svg className="finale-check mx-auto mb-3 h-12 w-12" viewBox="0 0 48 48" aria-hidden="true">
          <circle cx="24" cy="24" r="20" />
          <path d="M15 24.5l6.5 6.5L33 17" />
        </svg>
        {children}
      </div>
    </div>
  );
}
