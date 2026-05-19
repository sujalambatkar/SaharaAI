import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "SaharaAI — Multilingual Customer Support",
  description:
    "AI-powered customer support for Sahara D2C brand. Hindi, English, and Hinglish support.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-sahara-cream">{children}</body>
    </html>
  );
}
