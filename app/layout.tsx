import type { Metadata, Viewport } from "next";
import type { ReactNode } from "react";
import "../style.css";

const title = "Selvage Session Protocol";
const description =
  "A written, versioned specification for the session layer of collaborative editing: rooms, participants, presence and open documents. With JSON Schema, wire vectors and a language-neutral conformance runner.";

export const metadata: Metadata = {
  title,
  description,
  openGraph: {
    title,
    description,
    type: "website",
  },
  icons: {
    icon: [
      { url: "/icon.svg", type: "image/svg+xml" },
      { url: "/icon.png", type: "image/png", sizes: "32x32" },
    ],
    apple: [{ url: "/apple-icon.png", type: "image/png", sizes: "180x180" }],
  },
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
