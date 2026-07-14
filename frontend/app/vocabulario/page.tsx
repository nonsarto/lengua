"use client";

/**
 * Vocabulario/Vocabulari — estanterías por situación + (si existe) el Diccionari bàsic
 * del idioma: el fondo de palabras frecuentes del que cada día suben unas pocas al SRS.
 * "Nueva situación" pasa por LA misma puerta que todo: un capture "prepara'm per a…".
 */

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { apiFetch } from "@/lib/api";
import { S } from "@/lib/strings";

type Shelf = { id: string; name: string; is_seed: boolean; item_count: number };
type Loose = { id: string; term: string; translation: string; register: string; region: string | null };
type DictTopic = { topic: string; count: number; added: number };

export default function Vocabulario() {
  const router = useRouter();
  const [shelves, setShelves] = useState<Shelf[] | null>(null);
  const [loose, setLoose] = useState<Loose[]>([]);
  const [due, setDue] = useState(0);
  const [dict, setDict] = useState<DictTopic[]>([]);
  const [newName, setNewName] = useState("");
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState(false);

  useEffect(() => {
    apiFetch(`/vocabulario`)
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then((d) => {
        setShelves(d.situations);
        setLoose(d.sueltas);
        setDue(d.due ?? 0);
        setDict(d.diccionari ?? []);
      })
      .catch(() => setShelves([]));
  }, []);

  async function createShelf() {
    if (!newName.trim()) return;
    setCreating(true);
    setError(false);
    try {
      const res = await apiFetch(`/capture`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: `${S.briefPrefix} ${newName.trim()}`, source: "web" }),
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
      <h1 className="mb-1 text-2xl font-bold">{S.vocabularioTitle}</h1>
      {due > 0 ? (
        <Link href="/practicar" className="mb-4 inline-block text-xs text-accent-700 underline-offset-2 hover:underline">
          {S.dueToday(due)}
        </Link>
      ) : (
        <p className="mb-4 text-xs text-stone-400">{S.allReviewed}</p>
      )}

      {/* nueva situación — la IA la monta (vía analyze, modo brief) */}
      <div className="mb-6 flex gap-2">
        <input
          value={newName}
          onChange={(e) => setNewName(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && createShelf()}
          placeholder={S.newSituationPlaceholder}
          className="min-w-0 flex-1 rounded-lg border border-stone-300 bg-white px-3 py-2 text-sm outline-none focus:border-accent-500"
        />
        <button
          onClick={createShelf}
          disabled={creating || !newName.trim()}
          className="shrink-0 rounded-lg bg-accent-600 px-4 py-2 text-sm font-semibold text-white disabled:opacity-40 active:scale-95"
        >
          {creating ? S.creating : S.createBtn}
        </button>
      </div>
      {error && <p className="-mt-4 mb-4 text-xs text-red-600">{S.createFailed}</p>}

      {shelves === null ? (
        <p className="text-sm text-stone-400">{S.loading}</p>
      ) : (
        <>
          {shelves.length > 0 && (
            <section className="mb-6">
              <h2 className="mb-2 text-sm font-semibold uppercase tracking-wide text-stone-500">
                {S.situationsTitle}
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
                        {S.items(s.item_count)}
                        {s.is_seed ? S.seedTag : ""}
                      </p>
                    </div>
                    <span className="text-stone-300">→</span>
                  </Link>
                ))}
              </div>
            </section>
          )}

          {/* Diccionari bàsic — nur wenn die Instanz Seed-Vokabular hat (llengua) */}
          {dict.length > 0 && (
            <section className="mb-6">
              <h2 className="mb-2 text-sm font-semibold uppercase tracking-wide text-stone-500">
                {S.dictTitle}
              </h2>
              <div className="divide-y divide-stone-100 rounded-xl border border-stone-200 bg-white">
                {dict.map((t) => (
                  <Link
                    key={t.topic}
                    href={`/vocabulario/diccionari/${encodeURIComponent(t.topic)}`}
                    className="flex items-center justify-between p-3.5 active:bg-stone-50"
                  >
                    <div>
                      <p className="font-medium capitalize">{t.topic}</p>
                      <p className="mt-0.5 text-xs text-stone-400">
                        {t.added}/{t.count} {S.dictAdded}
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
                {S.looseTitle}
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

          {shelves.length === 0 && loose.length === 0 && dict.length === 0 && (
            <p className="text-sm text-stone-500">{S.vocabEmpty}</p>
          )}
        </>
      )}
    </>
  );
}
