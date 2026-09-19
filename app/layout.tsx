import type { Metadata, Viewport } from "next";
import type { ReactNode } from "react";
import "../style.css";

const title = "Selvage is a live-coding collaboration protocol";
const description =
  "One Rust binary you host holds the room and an invite link is the whole permission: VS Code, Neovim and a browser page edit the same file, with no account and no third party's cloud holding the room. The flagship artifact is the written session-layer specification, with JSON Schema and conformance vectors.";

// The page's home. `metadataBase` resolves the file conventions' paths against it, and the
// canonical link and `og:url` name it, so one constant decides all three. `selvageprotocol.com`
// is not registered and registering it is not being pursued; `check-csp.py`'s own
// `DEFAULT_ORIGIN` names the same origin.
const LIVE_ORIGIN = "https://selvage-protocol.vercel.app";

export const metadata: Metadata = {
  // A crawler or a link unfurl cannot fetch the convention paths under `app/`, so the
  // framework needs an origin to write them absolute against. Without one it falls back to
  // `http://localhost:3000`, which is what a local or preview build then publishes in
  // `og:image`.
  metadataBase: new URL(LIVE_ORIGIN),
  title,
  description,
  alternates: { canonical: "/" },
  openGraph: {
    title,
    description,
    url: "/",
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
