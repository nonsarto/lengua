import type { Metadata, Viewport } from "next";
import { Geist } from "next/font/google";
import Link from "next/link";
import "./globals.css";
import BottomNav from "@/components/BottomNav";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "lengua",
  description: "La vida trae el contenido, la app le da estructura.",
  appleWebApp: {
    capable: true,
    statusBarStyle: "default",
    title: "lengua",
  },
  icons: {
    apple: "/apple-touch-icon.png",
  },
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 1, // se siente nativo: sin pinch-zoom en la chrome
  themeColor: "#faf7f2",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="es">
      <body className={`${geistSans.variable} antialiased bg-[#faf7f2] text-stone-900`}>
        {/* Wordmark arriba a la izquierda — también es el camino de vuelta a Inicio */}
        <header className="mx-auto max-w-lg px-5 pt-[calc(env(safe-area-inset-top)+0.75rem)]">
          <Link href="/" className="text-xl font-bold tracking-tight">
            lengua<span className="text-amber-600">.</span>
          </Link>
        </header>
        {/* pb-28: espacio para la navegación inferior fija */}
        <main className="mx-auto max-w-lg min-h-dvh px-5 pt-4 pb-28">{children}</main>
        <BottomNav />
      </body>
    </html>
  );
}
