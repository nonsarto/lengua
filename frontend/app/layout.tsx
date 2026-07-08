import type { Metadata, Viewport } from "next";
import { Geist } from "next/font/google";
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
        {/* pb-28: espacio para la navegación inferior fija */}
        <main className="mx-auto max-w-lg min-h-dvh px-5 pt-6 pb-28">{children}</main>
        <BottomNav />
      </body>
    </html>
  );
}
