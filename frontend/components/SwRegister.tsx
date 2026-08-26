"use client";

/** Registriert den minimalen Service Worker (Offline-Fallback statt weißer Seite).
 *  Rendert nichts; Fehler sind egal (dann eben ohne SW — wie vorher). */

import { useEffect } from "react";

export default function SwRegister() {
  useEffect(() => {
    if ("serviceWorker" in navigator) {
      navigator.serviceWorker.register("/sw.js").catch(() => {});
    }
  }, []);
  return null;
}
