"use client";

/**
 * Cuatro LUGARES donde vive el aprendizaje acumulado + UNA acción persistente en el centro.
 * Los cuatro motivos de captura NO son cuatro pestañas — todos pasan por Capturar.
 * Iconos: SVG monocromo (currentColor), targets táctiles generosos (44px+).
 */

import Link from "next/link";
import { usePathname } from "next/navigation";

const stroke = {
  fill: "none",
  stroke: "currentColor",
  strokeWidth: 1.8,
  strokeLinecap: "round" as const,
  strokeLinejoin: "round" as const,
};

const ICONS: Record<string, React.ReactNode> = {
  inicio: (
    <svg viewBox="0 0 24 24" className="h-7 w-7" {...stroke}>
      <path d="M3 10.5 12 3l9 7.5" />
      <path d="M5.5 9.5V20a1 1 0 0 0 1 1H10v-6h4v6h3.5a1 1 0 0 0 1-1V9.5" />
    </svg>
  ),
  gramatica: (
    <svg viewBox="0 0 24 24" className="h-7 w-7" {...stroke}>
      <path d="M12 6.5C10.5 5 8.5 4.5 6 4.5c-1 0-2 .15-3 .5v14c1-.35 2-.5 3-.5 2.5 0 4.5.5 6 2 1.5-1.5 3.5-2 6-2 1 0 2 .15 3 .5v-14c-1-.35-2-.5-3-.5-2.5 0-4.5.5-6 2Z" />
      <path d="M12 6.5v14" />
    </svg>
  ),
  vocabulario: (
    <svg viewBox="0 0 24 24" className="h-7 w-7" {...stroke}>
      <rect x="3" y="4" width="18" height="5" rx="1" />
      <rect x="3" y="13" width="18" height="7" rx="1" />
      <path d="M9 16.5h6" />
    </svg>
  ),
  practicar: (
    <svg viewBox="0 0 24 24" className="h-7 w-7" {...stroke}>
      <circle cx="12" cy="12" r="8.5" />
      <circle cx="12" cy="12" r="4.5" />
      <circle cx="12" cy="12" r="1" fill="currentColor" stroke="none" />
    </svg>
  ),
};

function PlaceLink({ href, label, icon }: { href: string; label: string; icon: string }) {
  const pathname = usePathname();
  const active = pathname === href;
  return (
    <Link
      href={href}
      className={`flex min-w-14 flex-col items-center gap-1 rounded-lg px-2 py-1.5 text-[11px] ${
        active ? "text-stone-900 font-semibold" : "text-stone-400"
      }`}
    >
      {ICONS[icon]}
      {label}
    </Link>
  );
}

export default function BottomNav() {
  const pathname = usePathname();
  // sin nav en login y durante el test de nivel — primero entrar/terminar
  if (pathname === "/login" || pathname === "/nivel") return null;
  return (
    <nav className="fixed bottom-0 inset-x-0 z-50 border-t border-stone-200 bg-[#faf7f2]/95 backdrop-blur pb-[max(env(safe-area-inset-bottom),0.75rem)]">
      <div className="mx-auto flex max-w-lg items-end justify-between px-3 py-1.5">
        <PlaceLink href="/" label="Inicio" icon="inicio" />
        <PlaceLink href="/gramatica" label="Gramática" icon="gramatica" />
        {/* La acción — grande, en el centro, siempre a mano (el momento del bar) */}
        <Link
          href="/capturar"
          aria-label="Capturar"
          className="-mt-6 flex h-14 w-14 shrink-0 items-center justify-center rounded-full bg-amber-600 text-3xl font-light text-white shadow-lg shadow-amber-600/30 active:scale-95 transition-transform"
        >
          +
        </Link>
        <PlaceLink href="/vocabulario" label="Vocabulario" icon="vocabulario" />
        <PlaceLink href="/practicar" label="Practicar" icon="practicar" />
      </div>
    </nav>
  );
}
