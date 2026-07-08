"use client";

/**
 * Cuatro LUGARES donde vive el aprendizaje acumulado + UNA acción persistente en el centro.
 * Los cuatro motivos de captura NO son cuatro pestañas — todos pasan por Capturar.
 */

import Link from "next/link";
import { usePathname } from "next/navigation";

const places = [
  { href: "/", label: "Inicio", icon: "🏠" },
  { href: "/gramatica", label: "Gramática", icon: "📖" },
  // ← Capturar se inserta aquí, en el centro
  { href: "/vocabulario", label: "Vocabulario", icon: "🗂️" },
  { href: "/practicar", label: "Practicar", icon: "🎯" },
];

function PlaceLink({ href, label, icon }: { href: string; label: string; icon: string }) {
  const pathname = usePathname();
  const active = pathname === href;
  return (
    <Link
      href={href}
      className={`flex flex-col items-center gap-0.5 px-2 py-1 text-[11px] ${
        active ? "text-stone-900 font-semibold" : "text-stone-400"
      }`}
    >
      <span className="text-xl leading-none">{icon}</span>
      {label}
    </Link>
  );
}

export default function BottomNav() {
  return (
    <nav className="fixed bottom-0 inset-x-0 z-50 border-t border-stone-200 bg-[#faf7f2]/95 backdrop-blur pb-[env(safe-area-inset-bottom)]">
      <div className="mx-auto flex max-w-lg items-end justify-between px-4 py-2">
        <PlaceLink {...places[0]} />
        <PlaceLink {...places[1]} />
        {/* La acción — grande, en el centro, siempre a mano (el momento del bar) */}
        <Link
          href="/capturar"
          aria-label="Capturar"
          className="-mt-6 flex h-14 w-14 items-center justify-center rounded-full bg-amber-600 text-2xl text-white shadow-lg shadow-amber-600/30 active:scale-95 transition-transform"
        >
          +
        </Link>
        <PlaceLink {...places[2]} />
        <PlaceLink {...places[3]} />
      </div>
    </nav>
  );
}
