import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI Analytics Platform",
  description: "Natural language analytics workspace for enterprise teams.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

