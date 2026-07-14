"use client";

/**
 * Inicio/Inici — el pulso. Tres bandas: en caliente / para repasar / prep para hoy.
 * Datos de GET /inicio (todo determinista); textos de lib/strings (es/ca).
 */

import { useEffect, useState } from "react";
import Link from "next/link";
import { apiFetch } from "@/lib/api";
import { S } from "@/lib/strings";

type Inicio = {
  en_caliente: { slug: string; label: string; cefr: string | null; need_count: number; success_count: number }[];
  para_repasar: { due: number; preview: string[] };
  prep_hoy: { id: string; name: string }[];
};

function Band({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="mb-6">
      <h2 className="mb-2 text-sm font-semibold uppercase tracking-wide text-stone-500">{title}</h2>
      {children}
    </section>
  );
}

function Empty({ hint }: { hint: string }) {
  return (
    <div className="rounded-xl border border-dashed border-stone-300 p-4 text-sm text-stone-400">
      {hint}
    </div>
  );
}

export default function InicioPage() {
  const [data, setData] = useState<Inicio | null>(null);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    apiFetch(`/inicio`)
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then(setData)
      .catch(() => setFailed(true));
  }, []);

  return (
    <>
      <h1 className="mb-6 text-2xl font-bold">{S.inicioTitle}</h1>

      <Band title={S.bandHot}>
        {!data?.en_caliente?.length ? (
          <Empty hint={S.emptyHot} />
        ) : (
          <ul className="space-y-2">
            {data.en_caliente.map((c) => (
              <li key={c.slug}>
                <Link
                  href={`/gramatica/${c.slug}`}
                  className="flex items-center justify-between rounded-xl border border-accent-200 bg-accent-50/60 p-4 active:scale-[0.99]"
                >
                  <div>
                    <p className="font-medium">{c.label}</p>
                    <p className="mt-0.5 text-xs text-stone-500">
                      {S.errorsCaptured(c.need_count)}
                      {c.cefr ? ` · ${c.cefr}` : ""}
                    </p>
                  </div>
                  <span className="text-stone-400">→</span>
                </Link>
              </li>
            ))}
          </ul>
        )}
      </Band>

      <Band title={S.bandReview}>
        {!data || data.para_repasar.due === 0 ? (
          <Empty hint={S.emptyReview} />
        ) : (
          <Link
            href="/practicar"
            className="block rounded-xl border border-stone-200 bg-white p-4 active:scale-[0.99]"
          >
            <p className="font-medium">{S.wordsToReview(data.para_repasar.due)}</p>
            <p className="mt-0.5 truncate text-xs text-stone-500">
              {data.para_repasar.preview.join(" · ")}
            </p>
          </Link>
        )}
      </Band>

      <Band title={S.bandPrep}>
        {!data?.prep_hoy?.length ? (
          <Empty hint={S.emptyPrep} />
        ) : (
          <ul className="space-y-2">
            {data.prep_hoy.map((s) => (
              <li key={s.id}>
                <Link
                  href={`/vocabulario/${s.id}`}
                  className="flex items-center justify-between rounded-xl border border-stone-200 bg-white p-4 active:scale-[0.99]"
                >
                  <p className="font-medium">📦 {s.name}</p>
                  <span className="text-stone-400">→</span>
                </Link>
              </li>
            ))}
          </ul>
        )}
      </Band>

      {failed && <p className="mt-2 text-center text-xs text-stone-400">{S.loadFailed}</p>}

      <p className="mt-8 text-center text-sm text-stone-400">
        {S.captureHint} <span className="font-semibold text-accent-600">+</span>
      </p>
    </>
  );
}
