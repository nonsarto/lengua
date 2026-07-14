import type { Metadata, Viewport } from "next";
import { Geist } from "next/font/google";
import Link from "next/link";
import "./globals.css";
import BottomNav from "@/components/BottomNav";
import HeaderUser from "@/components/HeaderUser";
import { LANG, S } from "@/lib/strings";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const DESCRIPTION =
  LANG === "ca"
    ? "La vida porta el contingut, l'app li dona estructura."
    : "La vida trae el contenido, la app le da estructura.";

export const metadata: Metadata = {
  title: S.appName,
  description: DESCRIPTION,
  appleWebApp: {
    capable: true,
    statusBarStyle: "default",
    title: S.appName,
  },
  icons: {
    apple: LANG === "ca" ? "/apple-touch-icon-ca.png" : "/apple-touch-icon.png",
  },
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 1, // se siente nativo: sin pinch-zoom en la chrome
  themeColor: "#faf7f2",
  viewportFit: "cover", // sin esto, env(safe-area-inset-*) es 0 y la nav pega al borde
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang={LANG} data-lang={LANG}>
      <body className={`${geistSans.variable} antialiased bg-[#faf7f2] text-stone-900`}>
        {/* Wordmark oben links — auch der Weg zurück zu Inicio/Inici */}
        <header className="border-b border-accent-600/70">
          <div className="mx-auto flex max-w-lg items-center justify-between px-5 pt-[calc(env(safe-area-inset-top)+0.75rem)] pb-2.5">
            <Link href="/" className="text-xl font-bold tracking-tight">
              {S.appName}<span className="text-accent-600">.</span>
            </Link>
            <HeaderUser />
          </div>
        </header>
        {/* pb-28: Platz für die fixe untere Navigation */}
        <main className="mx-auto max-w-lg min-h-dvh px-5 pt-4 pb-28">{children}</main>
        <BottomNav />
      </body>
    </html>
  );
}
