"use client";

/**
 * Subir material — der fünfte Eingang. Lebt in Vocabulario UND Gramática,
 * beide führen zu derselben Tür. Azulejo: ruhige Karte, Stroke-Icon.
 */

import Link from "next/link";
import { S } from "@/lib/strings";
import { IconChevronRight, IconUpload } from "./icons";

export default function SubirMaterial() {
  return (
    <Link
      href="/vocabulario/importar"
      className="mb-6 flex items-center gap-3 rounded-2xl border border-stone-200 bg-white p-3.5 active:scale-[0.99] transition-transform"
    >
      <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-accent-50 text-accent-700">
        <IconUpload className="h-4 w-4" />
      </span>
      <span className="min-w-0 flex-1 text-sm font-semibold text-stone-700">{S.importEntry}</span>
      <IconChevronRight className="h-4 w-4 shrink-0 text-stone-300" />
    </Link>
  );
}
