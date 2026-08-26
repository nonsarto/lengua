/* Minimaler Service Worker (UX-Audit B2): kein Daten-Caching, nur ein ehrlicher
 * Offline-Fallback für Navigationen — vorher war jede Offline-Navigation eine
 * komplett weiße Seite, obwohl die App als PWA installierbar ist. */

self.addEventListener("install", () => self.skipWaiting());
self.addEventListener("activate", (event) => event.waitUntil(self.clients.claim()));

const OFFLINE_HTML = `<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Sin conexión</title>
<style>
  body { margin: 0; min-height: 100dvh; display: flex; align-items: center; justify-content: center;
         background: #faf7f2; color: #1c1917; font-family: -apple-system, "Segoe UI", sans-serif; }
  main { text-align: center; padding: 2rem; }
  h1 { font-size: 1.25rem; margin: 0 0 .5rem; }
  p  { color: #78716c; font-size: .9rem; margin: 0 0 1.5rem; }
  button { background: #ea7317; color: #fff; border: 0; border-radius: .75rem;
           padding: .75rem 1.5rem; font-size: .9rem; font-weight: 600; }
</style>
</head>
<body>
<main>
  <h1>Sin conexión</h1>
  <p>No hay red ahora mismo — tus datos están a salvo en el servidor.</p>
  <button onclick="location.reload()">reintentar</button>
</main>
</body>
</html>`;

self.addEventListener("fetch", (event) => {
  if (event.request.mode !== "navigate") return;
  event.respondWith(
    fetch(event.request).catch(
      () => new Response(OFFLINE_HTML, {
        status: 503,
        headers: { "Content-Type": "text/html; charset=utf-8" },
      }),
    ),
  );
});
