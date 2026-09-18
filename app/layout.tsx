import type { Metadata, Viewport } from "next";
import type { ReactNode } from "react";
import "../style.css";

const title = "Selvage Session Protocol";
const description =
  "A written, versioned specification for the session layer of collaborative editing: rooms, participants, presence and open documents. With JSON Schema, wire vectors and a language-neutral conformance runner.";

export const metadata: Metadata = {
  // The file conventions under `app/` — the icons and `opengraph-image.png` — are served from
  // paths that a crawler or a link unfurl cannot fetch, so the framework needs an origin to
  // write them absolute against. Without this it falls back to `http://localhost:3000`, which
  // is what a local or preview build then publishes in `og:image`. `metadataBase` writes no tag
  // of its own: `rel="canonical"` and `og:url` stay absent until the domain exists (README,
  // "The domain and canonical metadata").
  metadataBase: new URL("https://selvageprotocol.com"),
  title,
  description,
  openGraph: {
    title,
    description,
    type: "website",
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
