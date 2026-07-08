import type { MetadataRoute } from "next";

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: "lengua",
    short_name: "lengua",
    description: "La vida trae el contenido, la app le da estructura.",
    start_url: "/",
    display: "standalone",
    background_color: "#faf7f2",
    theme_color: "#faf7f2",
    icons: [
      { src: "/icon-192.png", sizes: "192x192", type: "image/png" },
      { src: "/icon-512.png", sizes: "512x512", type: "image/png" },
    ],
  };
}
