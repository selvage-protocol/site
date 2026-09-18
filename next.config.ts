import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Next.js answers every HTML response with `X-Powered-By: Next.js` by default. A reader of
  // the page has no use for it; the one directory that does is a crawler fingerprinting the
  // framework rather than reading the specification.
  poweredByHeader: false,
};

export default nextConfig;
