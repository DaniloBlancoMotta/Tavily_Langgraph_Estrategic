import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "StratGov AI | Consultoria Estratégica",
  description: "Agente de governança estratégica baseado em evidências MBB + Gartner",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="pt-BR">
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}
