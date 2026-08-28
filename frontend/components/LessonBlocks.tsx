/**
 * LessonBlocks — el renderizador de lecciones del Temario. Typisierte Blöcke statt
 * Markdown: Tabellen brauchen auf dem Handy eine eigene, horizontal scrollbare Komponente
 * (sticky erste Spalte — die Personen bleiben stehen), und die ES/DE-Beispielpaare sind
 * später als Übungsmaterial wiederverwendbar.
 * Spiegelbild des Block-Schemas in backend/app/grammar_catalog.py — synchron halten.
 */

import { DeChip } from "@/components/ui";
import { S } from "@/lib/strings";

export type Block =
  | { type: "paragraph"; text: string }
  | { type: "heading"; text: string }
  | { type: "table"; caption?: string; headers: string[]; rows: string[][] }
  | { type: "usecases"; items: { title: string; es: string; de: string }[] }
  | { type: "examples"; items: { es: string; de: string }[] }
  | { type: "note"; variant: "tip" | "warning"; text: string };

function TableBlock({ b }: { b: Extract<Block, { type: "table" }> }) {
  return (
    <div className="mb-4 rounded-2xl border border-stone-200 bg-white p-4">
      {b.caption && (
        <h3 className="mb-2 text-xs font-semibold uppercase tracking-wide text-stone-500">
          {b.caption}
        </h3>
      )}
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-xs text-stone-400">
              {b.headers.map((h, i) => (
                <th
                  key={i}
                  className={`whitespace-nowrap py-1 pr-3 font-semibold ${
                    i === 0 ? "sticky left-0 bg-white font-normal" : ""
                  }`}
                >
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {b.rows.map((row, ri) => (
              <tr key={ri} className="border-t border-stone-100">
                {row.map((cell, ci) => (
                  <td
                    key={ci}
                    className={`whitespace-nowrap py-1 pr-3 ${
                      ci === 0 ? "sticky left-0 bg-white text-stone-400" : ""
                    }`}
                  >
                    {cell}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function NoteBlock({ b }: { b: Extract<Block, { type: "note" }> }) {
  if (b.variant === "warning")
    return (
      <div className="mb-4 rounded-2xl border border-orange-200 bg-amber-50 p-4">
        <h3 className="mb-1 text-xs font-semibold uppercase tracking-[.12em] text-amber-700">
          <DeChip />{S.germanPitfall}
        </h3>
        <p className="text-base">{b.text}</p>
      </div>
    );
  return (
    <div className="mb-4 rounded-2xl border border-stone-200 bg-white p-4">
      <p className="text-base">💡 {b.text}</p>
    </div>
  );
}

export default function LessonBlocks({ blocks }: { blocks: Block[] }) {
  return (
    <>
      {blocks.map((b, i) => {
        switch (b.type) {
          case "paragraph":
            return <p key={i} className="mb-4 text-base leading-relaxed">{b.text}</p>;
          case "heading":
            return (
              <h2 key={i} className="mb-2 mt-6 text-xs font-semibold uppercase tracking-[.12em] text-stone-500">
                {b.text}
              </h2>
            );
          case "table":
            return <TableBlock key={i} b={b} />;
          case "usecases":
            return (
              <ul key={i} className="mb-4 space-y-3">
                {b.items.map((u, j) => (
                  <li key={j} className="rounded-2xl border border-stone-200 bg-white p-4">
                    <p className="mb-1 text-xs font-semibold uppercase tracking-wide text-stone-500">
                      {u.title}
                    </p>
                    <p className="text-base">{u.es}</p>
                    <p className="text-sm text-stone-400">{u.de}</p>
                  </li>
                ))}
              </ul>
            );
          case "examples":
            return (
              <ul key={i} className="mb-4 space-y-2">
                {b.items.map((ex, j) => (
                  <li key={j}>
                    <p className="text-base">{ex.es}</p>
                    <p className="text-sm text-stone-400">{ex.de}</p>
                  </li>
                ))}
              </ul>
            );
          case "note":
            return <NoteBlock key={i} b={b} />;
        }
      })}
    </>
  );
}
