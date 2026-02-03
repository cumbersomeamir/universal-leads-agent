import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Tensorblue | Universal Leads AI",
  description:
    "Universal Leads AI agent — get more clients for Tensorblue with AI-powered lead generation.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased min-h-screen bg-slate-950 text-slate-100">
        {children}
      </body>
    </html>
  );
}
