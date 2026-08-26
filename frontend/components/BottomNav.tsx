"use client";

/**
 * Vier ORTE + Capturar INTEGRIERT in der Mitte (Azulejo, Konzept-Nachtrag):
 * kein schwebender FAB — die Aktion sitzt auf der Grundlinie der Tabs, trägt als
 * einziges Element die Akzentfläche und hat ein Label wie alle anderen.
 * Hablar hat keinen Tab mehr — der Zugang ist die Feedback-Karte auf Inicio.
 * Symmetrie: 2 Orte links, 2 rechts.
 */

import Link from "next/link";
import { usePathname } from "next/navigation";
import { S } from "@/lib/strings";
import { IconBook, IconCards, IconHome, IconPlus, IconTarget } from "./icons";

function PlaceLink({ href, label, icon }: { href: string; label: string; icon: React.ReactNode }) {
  const pathname = usePathname();
  const active = pathname === href || (href !== "/" && pathname.startsWith(`${href}/`));
  return (
    <Link
      href={href}
      className={`flex min-w-12 flex-col items-center gap-0.5 rounded-lg px-1.5 py-1.5 text-[11px] ${
        active ? "font-semibold text-stone-900" : "text-stone-400"
      }`}
    >
      {icon}
      {label}
    </Link>
  );
}

export default function BottomNav() {
  const pathname = usePathname();
  // sense nav al login ni durant el test de nivell
  if (pathname === "/login" || pathname === "/nivel") return null;
  return (
    <nav className="fixed bottom-0 inset-x-0 z-50 border-t border-stone-200 bg-background/95 backdrop-blur pb-[max(env(safe-area-inset-bottom),0.75rem)]">
      <div className="mx-auto flex max-w-lg items-center justify-between px-3 py-1.5">
        <PlaceLink href="/" label={S.navInicio} icon={<IconHome className="h-6 w-6" />} />
        <PlaceLink href="/gramatica" label={S.navGramatica} icon={<IconBook className="h-6 w-6" />} />
        {/* Die eine Geste — integriert, nicht schwebend */}
        <Link
          href="/capturar"
          className={`flex flex-col items-center gap-0.5 px-1.5 py-1.5 text-[11px] font-semibold ${
            pathname === "/capturar" ? "text-accent-700" : "text-accent-600"
          }`}
        >
          <span className="flex h-8 w-8 items-center justify-center rounded-xl bg-accent-600 text-white transition-transform active:scale-95">
            <IconPlus className="h-4.5 w-4.5" />
          </span>
          {S.navCapturar}
        </Link>
        <PlaceLink href="/vocabulario" label={S.navVocabulario} icon={<IconCards className="h-6 w-6" />} />
        <PlaceLink href="/practicar" label={S.navPracticar} icon={<IconTarget className="h-6 w-6" />} />
      </div>
    </nav>
  );
}
