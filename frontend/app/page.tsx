"use client";

/**
 * Inicio/Inici — saludo con tu nombre, luego lo de hoy: la sesión (die eine Lift-Karte),
 * los 3 temas de gramática más urgentes, el repaso, y el feedback de Hablar (es-only).
 * Datos de GET /inicio (determinista); el saludo se arma en el cliente.
 * Azulejo: Serif fürs Spanische, Lernstand als Tinte (Dots), eine Akzentfläche.
 */

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { apiFetch, getUser } from "@/lib/api";
import { LANG, S } from "@/lib/strings";
import { IconChevronRight, IconPlay } from "@/components/icons";
import { NeedLine, StateDots, btnPrimary, cardLift, cardQuiet } from "@/components/ui";

type Grammar = { slug: string; label: string; cefr: string | null; state: string; need_count: number };
type Inicio = { top_grammar: Grammar[]; vocab: { due: number; preview: string[] } };
type HablarOverview = {
  top_errors: { error_type: string; count: number }[];
  sessions: { id: string; created_at: string; snippet: string; error_count: number }[];
};
type SessionToday = {
  id: string;
  status: "active" | "completed";
  headline: string;
  budget_seconds: number;
  cursor: number;
  items: { kind: string }[];
};

/** El acceso a la sesión diaria — arriba del todo. Carga aparte: nunca bloquea el resto. */
function SessionCard() {
  const router = useRouter();
  const [session, setSession] = useState<SessionToday | null>(null);
  const [failed, setFailed] = useState(false);
  const [rerolling, setRerolling] = useState(false);

  useEffect(() => {
    apiFetch(`/session/today`)
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then(setSession)
      .catch(() => setFailed(true));
  }, []);

  async function newTraining() {
    setRerolling(true);
    try {
      const res = await apiFetch(`/session/reroll`, { method: "POST" });
      if (!res.ok) throw new Error();
      router.push("/sesion");
    } catch {
      setRerolling(false);
    }
  }

  if (failed) {
    return <p className="mb-6 text-sm text-stone-400">{S.sessionError}</p>;
  }
  if (!session) {
    return (
      <div className={`${cardQuiet} mb-6 p-4 text-sm text-stone-400`}>
        {S.sessionPreparing}
      </div>
    );
  }
  if (session.status === "completed") {
    return (
      <div className={`${cardQuiet} mb-6 p-4`}>
        <p className="font-semibold text-green-700">{S.sessionDoneToday} ✓</p>
        <p className="mt-0.5 text-sm text-stone-500">{S.sessionDoneSub}</p>
        <button onClick={newTraining} disabled={rerolling} className={`mt-3 ${btnPrimary}`}>
          {rerolling ? S.sessionPreparing : S.sessionNewTraining}
        </button>
      </div>
    );
  }

  const total = session.items.length;
  const min = Math.round(session.budget_seconds / 60);
  const what = session.headline
    ? `${S.sessionVocabLabel} + ${session.headline}`
    : S.sessionVocabLabel;
  const label = session.cursor > 0 ? S.sessionContinue(session.cursor, total) : S.sessionButton(min, what);

  return (
    <Link
      href="/sesion"
      className={`${cardLift} mb-6 flex items-center justify-between gap-3 p-5 active:scale-[0.99] transition-transform`}
    >
      <div className="min-w-0">
        <p className="font-semibold leading-snug">{label}</p>
        {session.cursor > 0 && (
          <p className="mt-0.5 text-sm text-accent-200">{S.sessionButton(min, what)}</p>
        )}
      </div>
      <IconPlay className="h-5 w-5 shrink-0 text-accent-200" />
    </Link>
  );
}

/** Hablar-Feedback (ES-only): letzte Bot-Session + Fehler-Top-3. Lädt getrennt. */
function HablarCard() {
  const [data, setData] = useState<HablarOverview | null>(null);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    apiFetch(`/hablar`)
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then(setData)
      .catch(() => setFailed(true));
  }, []);

  if (failed) return null;
  const last = data?.sessions?.[0];
  if (data && !last) {
    return (
      <div className={`${cardQuiet} p-4 text-sm text-stone-400`}>
        {S.inicioHablarEmpty}
      </div>
    );
  }
  if (!last) return null;

  const date = new Date(last.created_at).toLocaleDateString("es-ES", {
    weekday: "short", day: "numeric", month: "short",
  });
  const top = (data!.top_errors ?? []).slice(0, 3)
    .map((t) => S.errorTypeLabels[t.error_type] ?? t.error_type);
  return (
    <Link
      href={`/hablar/${last.id}`}
      className={`${cardQuiet} flex items-center justify-between gap-3 p-4 active:scale-[0.99] transition-transform`}
    >
      <div className="min-w-0">
        <p className="font-medium">
          {date} · {S.hablarSessionErrors(last.error_count)}
        </p>
        <p className="mt-0.5 truncate text-xs text-stone-500">
          {top.length > 0 ? top.join(" · ") : last.snippet}
        </p>
      </div>
      <IconChevronRight className="h-4 w-4 shrink-0 text-stone-300" />
    </Link>
  );
}

function greeting(): string {
  const h = new Date().getHours();
  return h < 12 ? S.greetMorning : h < 20 ? S.greetAfternoon : S.greetEvening;
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="mb-6">
      <h2 className="mb-2 text-xs font-semibold uppercase tracking-[.12em] text-stone-400">{title}</h2>
      {children}
    </section>
  );
}

export default function InicioPage() {
  const [data, setData] = useState<Inicio | null>(null);
  const [failed, setFailed] = useState(false);
  const [name, setName] = useState("");
  const [today, setToday] = useState("");

  useEffect(() => {
    const u = getUser();
    setName(u?.display_name || u?.username || "");
    setToday(new Date().toLocaleDateString(LANG === "ca" ? "ca-ES" : "es-ES", {
      weekday: "long", day: "numeric", month: "long",
    }));
    apiFetch(`/inicio`)
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then(setData)
      .catch(() => setFailed(true));
  }, []);

  return (
    <>
      {/* Saludo — Serif, das Spanische ist der Schmuck */}
      <h1 className="font-display text-[26px] font-semibold leading-tight">
        {greeting()}{name ? `, ${name}` : ""}
      </h1>
      <p className="mb-6 mt-0.5 text-sm text-stone-400">{today}</p>

      <SessionCard />

      {/* 1. Los 3 temas de gramática más urgentes */}
      <Section title={S.inicioGrammar}>
        {!data?.top_grammar?.length ? (
          <div className={`${cardQuiet} p-4 text-sm text-stone-400`}>
            {S.emptyGrammar}
          </div>
        ) : (
          <div className={`${cardQuiet} divide-y divide-stone-100`}>
            {data.top_grammar.map((c) => (
              <Link
                key={c.slug}
                href={`/gramatica/${c.slug}`}
                className="flex items-center justify-between gap-3 p-3.5 active:bg-stone-50"
              >
                <div className="min-w-0">
                  <p className="truncate font-medium">{c.label}</p>
                  <p className="mt-0.5 flex items-center gap-1.5 text-xs text-stone-400">
                    <NeedLine state={c.state} needCount={c.need_count} />
                    {c.state !== "flojo" && c.state !== "aprendiendo" && c.cefr && (
                      <span>{c.cefr} · {S.stateLabels[c.state]}</span>
                    )}
                  </p>
                </div>
                <StateDots state={c.state} />
              </Link>
            ))}
          </div>
        )}
      </Section>

      {/* 2. Repaso */}
      <Section title={S.inicioVocab}>
        <Link
          href="/practicar"
          className={`${cardQuiet} flex items-center justify-between gap-3 p-4 active:scale-[0.99] transition-transform`}
        >
          <div className="min-w-0">
            <p className="font-medium">
              {data && data.vocab.due > 0 ? S.wordsToReview(data.vocab.due) : S.vocabTestCta}
            </p>
            {data && data.vocab.due > 0 && data.vocab.preview.length > 0 && (
              <p className="mt-0.5 truncate text-xs text-stone-500">
                {data.vocab.preview.join(" · ")}
              </p>
            )}
          </div>
          <IconChevronRight className="h-4 w-4 shrink-0 text-stone-300" />
        </Link>
      </Section>

      {/* 3. Hablar-Feedback (Speaking Bot — ES-only) */}
      {LANG === "es" && (
        <Section title={S.inicioHablar}>
          <HablarCard />
        </Section>
      )}

      {failed && <p className="mt-2 text-center text-xs text-stone-400">{S.loadFailed}</p>}

      <p className="mt-8 text-center text-sm text-stone-400">
        {S.captureHint} <span className="font-semibold text-accent-600">+</span>
      </p>
    </>
  );
}
