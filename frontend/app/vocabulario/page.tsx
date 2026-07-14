"use client";

/**
 * Vocabulario — estanterías por situación, no una lista plana. "Nueva situación" pasa
 * por LA misma puerta que todo lo demás: un capture "prepárame para …" — analyze()
 * reconoce el modo brief y monta el estante.
 */

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { API } from "@/lib/api";

type Shelf = { id: string; name: string; is_seed: boolean; item_count: number };
type Loose = { id: string; term: string; translation: string; register: string; region: string | null };

export default function Vocabulario() {
  const router = useRouter();
  const [shelves, setShelves] = useState<Shelf[] | null>(null);
  const [loose, setLoose] = useState<Loose[]>([]);
  const [due, setDue] = useState(0);
  const [newName, setNewName] = useState("");
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState(false);

  useEffect(() => {
    fetch(`${API}/vocabulario`)
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then((d) => {
        setShelves(d.situations);
        setLoose(d.sueltas);
        setDue(d.due ?? 0);
      })
      .catch(() => setShelves([]));
  }, []);

  async function createShelf() {
    if (!newName.trim()) return;
    setCreating(true);
    setError(false);
    try {
      const res = await fetch(`${API}/capture`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: `prepárame para ${newName.trim()}`, source: "web" }),
      });
      if (!res.ok) throw new Error();
      const data = await res.json();
      const sid = data.written?.situation?.id;
      if (sid) router.push(`/vocabulario/${sid}`);
      else throw new Error();
    } catch {
      setError(true);
      setCreating(false);
    }
  }

  return (
    <>
      <h1 className="mb-1 text-2xl font-bold">Vocabulario</h1>
      {due > 0 ? (
        <Link href="/practicar" className="mb-4 inline-block text-xs text-amber-700 underline-offset-2 hover:underline">
          {due} para repasar hoy → Practicar
        </Link>
      ) : (
        <p className="mb-4 text-xs text-stone-400">todo repasado por hoy ✓</p>
      )}

      {/* nueva situación — la IA la monta (vía analyze, modo brief) */}
      <div className="mb-6 flex gap-2">
        <input
          value={newName}
          onChange={(e) => setNewName(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && createShelf()}
          placeholder="Nueva situación… (p.ej. cita con el dentista)"
          className="min-w-0 flex-1 rounded-lg border border-stone-300 bg-white px-3 py-2 text-sm outline-none focus:border-amber-500"
        />
        <button
          onClick={createShelf}
          disabled={creating || !newName.trim()}
          className="shrink-0 rounded-lg bg-amber-600 px-4 py-2 text-sm font-semibold text-white disabled:opacity-40 active:scale-95"
        >
          {creating ? "montando…" : "crear"}
        </button>
      </div>
      {error && (
        <p className="-mt-4 mb-4 text-xs text-red-600">No se pudo crear — ¿backend corriendo?</p>
      )}

      {shelves === null ? (
        <p className="text-sm text-stone-400">cargando…</p>
      ) : (
        <>
          {shelves.length > 0 && (
            <section className="mb-6">
              <h2 className="mb-2 text-sm font-semibold uppercase tracking-wide text-stone-500">
                Situaciones
              </h2>
              <div className="divide-y divide-stone-100 rounded-xl border border-stone-200 bg-white">
                {shelves.map((s) => (
                  <Link
                    key={s.id}
                    href={`/vocabulario/${s.id}`}
                    className="flex items-center justify-between p-3.5 active:bg-stone-50"
                  >
                    <div>
                      <p className="font-medium">{s.name}</p>
                      <p className="mt-0.5 text-xs text-stone-400">
                        {s.item_count} {s.item_count === 1 ? "elemento" : "elementos"}
                        {s.is_seed ? " · estándar" : ""}
                      </p>
                    </div>
                    <span className="text-stone-300">→</span>
                  </Link>
                ))}
              </div>
            </section>
          )}

          {loose.length > 0 && (
            <section>
              <h2 className="mb-2 text-sm font-semibold uppercase tracking-wide text-stone-500">
                Sueltas — de tus capturas
              </h2>
              <ul className="divide-y divide-stone-100 rounded-xl border border-stone-200 bg-white">
                {loose.map((v) => (
                  <li key={v.id} className="flex items-baseline justify-between gap-3 p-3">
                    <span className="font-medium">{v.term}</span>
                    <span className="min-w-0 truncate text-right text-sm text-stone-500">
                      {v.translation}
                      {v.region ? ` · ${v.region}` : ""}
                    </span>
                  </li>
                ))}
              </ul>
            </section>
          )}

          {shelves.length === 0 && loose.length === 0 && (
            <p className="text-sm text-stone-500">
              Aún no hay vocabulario — captura algo o crea una situación arriba.
            </p>
          )}
        </>
      )}
    </>
  );
}
