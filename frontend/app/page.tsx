"use client";

/**
 * Inicio — el pulso. Tres bandas: en caliente / para repasar / prep para hoy.
 * En 3 segundos sabes qué toca hoy. Los datos vienen de GET /inicio (todo determinista).
 */

import { useEffect, useState } from "react";
import Link from "next/link";
import { API } from "@/lib/api";

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
    fetch(`${API}/inicio`)
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then(setData)
      .catch(() => setFailed(true));
  }, []);

  return (
    <>
      <h1 className="mb-6 text-2xl font-bold">Inicio</h1>

      <Band title="En caliente">
        {!data?.en_caliente?.length ? (
          <Empty hint="Los conceptos recién promovidos aparecerán aquí." />
        ) : (
          <ul className="space-y-2">
            {data.en_caliente.map((c) => (
              <li key={c.slug}>
                <Link
                  href={`/gramatica/${c.slug}`}
                  className="flex items-center justify-between rounded-xl border border-amber-200 bg-amber-50/60 p-4 active:scale-[0.99]"
                >
                  <div>
                    <p className="font-medium">{c.label}</p>
                    <p className="mt-0.5 text-xs text-stone-500">
                      {c.need_count} {c.need_count === 1 ? "fallo" : "fallos"} capturados
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

      <Band title="Para repasar">
        {!data || data.para_repasar.due === 0 ? (
          <Empty hint="Tu repaso del día, cuando haya vocabulario que repasar." />
        ) : (
          <Link
            href="/practicar"
            className="block rounded-xl border border-stone-200 bg-white p-4 active:scale-[0.99]"
          >
            <p className="font-medium">
              {data.para_repasar.due} {data.para_repasar.due === 1 ? "palabra" : "palabras"} para repasar
            </p>
            <p className="mt-0.5 truncate text-xs text-stone-500">
              {data.para_repasar.preview.join(" · ")}
            </p>
          </Link>
        )}
      </Band>

      <Band title="Prep para hoy">
        {!data?.prep_hoy?.length ? (
          <Empty hint="Preparación para tus citas de hoy." />
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

      {failed && (
        <p className="mt-2 text-center text-xs text-stone-400">
          (no se pudo cargar — ¿backend corriendo?)
        </p>
      )}

      <p className="mt-8 text-center text-sm text-stone-400">
        Captura algo de tu día con el botón <span className="font-semibold text-amber-600">+</span>
      </p>
    </>
  );
}
