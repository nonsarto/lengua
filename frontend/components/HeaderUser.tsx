"use client";

/** El circulito con tu inicial, arriba a la derecha → Perfil. Render tras montar
 *  (localStorage) para no romper la hidratación. */

import { useEffect, useState } from "react";
import Link from "next/link";
import { getUser } from "@/lib/api";

export default function HeaderUser() {
  const [initial, setInitial] = useState<string | null>(null);

  useEffect(() => {
    const u = getUser();
    if (u) setInitial((u.display_name || u.username || "?")[0].toUpperCase());
  }, []);

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
