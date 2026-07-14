"use client";

/** El circulito con tu inicial, arriba a la derecha → Perfil. Render tras montar
 *  (localStorage) para no romper la hidratación. */

import { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { getUser } from "@/lib/api";

export default function HeaderUser() {
  const pathname = usePathname();
  const [initial, setInitial] = useState<string | null>(null);

  // re-lee el login en cada navegación — tras entrar, el círculo aparece al instante
  useEffect(() => {
    const u = getUser();
    setInitial(u ? (u.display_name || u.username || "?")[0].toUpperCase() : null);
  }, [pathname]);

  if (!initial) return null;

  return (
    <Link
      href="/perfil"
      aria-label="Perfil"
      className="flex h-8 w-8 items-center justify-center rounded-full bg-stone-800 text-sm font-semibold text-white"
    >
      {initial}
    </Link>
  );
}
