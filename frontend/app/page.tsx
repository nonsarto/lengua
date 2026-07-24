"use client";

/**
 * Inicio/Inici — saludo con tu nombre, luego lo de hoy: los 3 temas de gramática más
 * urgentes, un test de vocabulario y una escucha. Datos de GET /inicio (determinista);
 * el saludo se arma en el cliente (nombre + hora local). Textos de lib/strings (es/ca).
 */

import { useEffect, useState } from "react";
import Link from "next/link";
import { apiFetch, getUser, STATE_LABEL, STATE_STYLE } from "@/lib/api";
import { S } from "@/lib/strings";

type Grammar = { slug: string; label: string; cefr: string | null; state: string; need_count: number };
type Inicio = { top_grammar: Grammar[]; vocab: { due: number; preview: string[] } };

function greeting(): string {
  const h = new Date().getHours();
  return h < 12 ? S.greetMorning : h < 20 ? S.greetAfternoon : S.greetEvening;
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="mb-6">
      <h2 className="mb-2 text-sm font-semibold uppercase tracking-wide text-stone-500">{title}</h2>
      {children}
    </section>
  );
}

export default function InicioPage() {
  const [data, setData] = useState<Inicio | null>(null);
  const [failed, setFailed] = useState(false);
  const [name, setName] = useState("");

  useEffect(() => {
    const u = getUser();
    setName(u?.display_name || u?.username || "");
    apiFetch(`/inicio`)
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then(setData)
      .catch(() => setFailed(true));
  }, []);

  return (
    <>
      {/* Saludo */}
      <h1 className="mb-6 text-2xl font-bold">
        {greeting()}{name ? `, ${name}` : ""} <span className="font-normal">👋</span>
      </h1>

      {/* 1. Los 3 temas de gramática más urgentes */}
      <Section title={S.inicioGrammar}>
        {!data?.top_grammar?.length ? (
          <div className="rounded-xl border border-dashed border-stone-300 p-4 text-sm text-stone-400">
            {S.emptyGrammar}
          </div>
        ) : (
          <ul className="space-y-2">
            {data.top_grammar.map((c) => (
              <li key={c.slug}>
                <Link
                  href={`/gramatica/${c.slug}`}
                  className="flex items-center justify-between rounded-xl border border-accent-200 bg-accent-50/60 p-4 active:scale-[0.99]"
                >
                  <div className="min-w-0">
                    <p className="truncate font-medium">{c.label}</p>
                    <p className="mt-0.5 flex items-center gap-1.5 text-xs text-stone-500">
                      {c.cefr && <span>{c.cefr}</span>}
                      {c.state !== "sin_ver" && (
                        <span className={`rounded-full px-1.5 py-px ${STATE_STYLE[c.state]}`}>
                          {STATE_LABEL[c.state]}
                        </span>
                      )}
                      {c.need_count > 0 && <span>· {S.errorsCaptured(c.need_count)}</span>}
                    </p>
                  </div>
                  <span className="shrink-0 text-stone-400">→</span>
                </Link>
              </li>
            ))}
          </ul>
        )}
      </Section>

      {/* 2. Test de vocabulario */}
      <Section title={S.inicioVocab}>
        <Link
          href="/practicar"
          className="flex items-center justify-between rounded-xl border border-stone-200 bg-white p-4 active:scale-[0.99]"
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
          <span className="shrink-0 text-stone-400">→</span>
        </Link>
      </Section>

      {/* 3. Comprensión oral */}
      <Section title={S.inicioListen}>
        <Link
          href="/practicar/escucha"
          className="flex items-center justify-between rounded-xl border border-stone-200 bg-white p-4 active:scale-[0.99]"
        >
          <div>
            <p className="font-medium">{S.escuchaBtn}</p>
            <p className="mt-0.5 text-xs text-stone-500">{S.escuchaDesc}</p>
          </div>
          <span className="shrink-0 text-stone-400">→</span>
        </Link>
      </Section>

      {failed && <p className="mt-2 text-center text-xs text-stone-400">{S.loadFailed}</p>}

      <p className="mt-8 text-center text-sm text-stone-400">
        {S.captureHint} <span className="font-semibold text-accent-600">+</span>
      </p>
    </>
  );
}
