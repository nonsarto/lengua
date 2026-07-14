import type { MetadataRoute } from "next";
import { LANG, S } from "@/lib/strings";

export default function manifest(): MetadataRoute.Manifest {
  const suffix = LANG === "ca" ? "-ca" : "";
  return {
    name: S.appName,
    short_name: S.appName,
    description:
      LANG === "ca"
        ? "La vida porta el contingut, l'app li dona estructura."
        : "La vida trae el contenido, la app le da estructura.",
    start_url: "/",
    display: "standalone",
    background_color: "#faf7f2",
    theme_color: "#faf7f2",
    icons: [
      { src: `/icon${suffix}-192.png`, sizes: "192x192", type: "image/png" },
      { src: `/icon${suffix}-512.png`, sizes: "512x512", type: "image/png" },
    ],
  };
}
