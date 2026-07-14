/** Una sola fuente para la URL del backend: env explícita o el mismo host en el puerto 8000
 *  (funciona en localhost Y desde el iPhone en la red local sin configurar nada). */
export const API =
  process.env.NEXT_PUBLIC_API_URL ??
  (typeof window !== "undefined" ? `http://${window.location.hostname}:8000` : "http://localhost:8000");

export const STATE_LABEL: Record<string, string> = {
  sin_ver: "sin ver",
  visto: "visto",
  flojo: "flojo",
  aprendiendo: "aprendiendo",
  dominado: "dominado",
};

export const STATE_STYLE: Record<string, string> = {
  aprendiendo: "bg-amber-100 text-amber-800",
  flojo: "bg-orange-50 text-orange-700",
  visto: "bg-stone-100 text-stone-500",
  dominado: "bg-green-50 text-green-700",
  sin_ver: "bg-stone-50 text-stone-400",
};
