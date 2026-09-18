import type { Metadata, Viewport } from "next";
import type { ReactNode } from "react";
import "../style.css";

const title = "Selvage — a live-coding collaboration protocol";
const description =
  "One Rust binary you host holds the room and an invite link is the whole permission: VS Code, Neovim and a browser page edit the same file, with no account and no third party's cloud holding the room. The flagship artifact is the written session-layer specification, with JSON Schema and conformance vectors.";

export const metadata: Metadata = {
  // The file conventions under `app/` — the icons and `opengraph-image.png` — are served from
  // paths that a crawler or a link unfurl cannot fetch, so the framework needs an origin to
  // write them absolute against. This is the origin the page is served from today. Without it
  // the framework falls back to `http://localhost:3000`, which is what a local or preview build
  // then publishes in `og:image`. `metadataBase` writes no tag of its own: `rel="canonical"`
  // and `og:url` stay absent until the intended domain exists (README, "The live origin").
  metadataBase: new URL("https://selvage-protocol.vercel.app"),
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
