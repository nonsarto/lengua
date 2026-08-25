"use client";

/**
 * Subir material — el quinto acceso, ahora un botón de verdad (no un enlace escondido).
 * Vive en Vocabulario Y en Gramática porque ambos flujos nacen aquí: material de estudio
 * (→ conceptos/gramática) y listas (→ vocabulario). Los dos reiter llevan a LA misma puerta.
 */

import Link from "next/link";
import { S } from "@/lib/strings";

export default function SubirMaterial() {
  return (
    <Link
      href="/vocabulario/importar"
      className="mb-6 flex items-center gap-3 rounded-xl border border-accent-300 bg-accent-50/70 p-3.5 active:scale-[0.99]"
    >
      <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-accent-100 text-lg">
        ⬆️
      </span>
      <span className="min-w-0 flex-1 font-semibold text-accent-800">{S.importEntry}</span>
      <span className="shrink-0 text-accent-400">→</span>
    </Link>
  );
}
