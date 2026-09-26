import type { Metadata, Viewport } from "next";
import type { ReactNode } from "react";
import { Geist, JetBrains_Mono } from "next/font/google";
import "../style.css";

// Both families are served from this origin: `next/font` fetches the glyphs at build
// time and writes no request to a font host into the page. The two variables are what
// `style.css` reads from, so the Tailwind classes and the page's own rules resolve to
// the same families.
const geistSans = Geist({
  subsets: ["latin"],
  weight: ["400", "500", "600"],
  variable: "--font-geist-sans",
  display: "swap",
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  weight: ["400", "500"],
  variable: "--font-jetbrains-mono",
  display: "swap",
});

const title = "Selvage: edit the same file together, on a server you run";
const description =
  "One Rust binary you host holds the room. An invite link is the whole permission: VS Code, Neovim and a browser page edit the same file, with no account and no third party's cloud holding the room. The session layer is written down as a specification, with JSON Schema and conformance vectors.";

// The page's home. `metadataBase` resolves the file conventions' paths against it, and the
// canonical link and `og:url` name it, so one constant decides all three. `check-csp.py`'s own
// `DEFAULT_ORIGIN` names the same origin.
const LIVE_ORIGIN = "https://selvage.dontblameme.dev";

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
    <html
      lang="en"
      className={`${geistSans.variable} ${jetbrainsMono.variable}`}
    >
      <body>{children}</body>
    </html>
  );
}
