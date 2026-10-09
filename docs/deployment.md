# Deploying it

Vercel, connected to this repository over the GitHub integration, building the Next.js project:
[`vercel.json`](../vercel.json) carries `"framework": "nextjs"` so the dashboard does not have to,
plus the three response headers — `Content-Security-Policy`,
`X-Content-Type-Options: nosniff` and `Referrer-Policy: strict-origin-when-cross-origin` — and
[`next.config.ts`](../next.config.ts) turns the framework's own `X-Powered-By: Next.js` banner off,
so the HTML response does not name the stack it was rendered by. There is nothing to configure
beyond connecting the repository.

Production deploys on `main`, at **https://selvage.dontblameme.dev**, and every branch and pull
request gets a preview URL. That origin is the page's home: [`app/layout.tsx`](../app/layout.tsx)
holds it in `LIVE_ORIGIN`, and `metadataBase` plus `rel="canonical"` and `og:url` are written from
the same constant, so a card unfurled from a branch preview names the same URL and image as
production, and moving the page to another origin is one constant. `selvageprotocol.com` is **not
registered** and registering it is not being pursued: nothing here is waiting on a domain.

The `Content-Security-Policy` is the one header that breaks the page rather than hardening it if it
is wrong: with `default-src 'none'` and nothing for scripts to fall back to, the page's own chunks
and its inline bootstrap are refused, it never hydrates, and the header's conceal-on-scroll does
nothing while the page reads as if it worked. `scripts/check-csp.py` decides every script,
stylesheet, image and font the served page and its not-found route carry against the policy in
`vercel.json`, so a policy that would refuse something the page loads fails the gate instead, and
`scripts/check-csp-browser.mjs` then drives a real headless Chromium over the same two served
documents — zero `securitypolicyviolation` events, the glyph files fetched, the conceal-on-scroll
effect firing only if the page hydrated. The gate runs both, so the model is backed by a browser;
the runner image carries the Chromium the second one needs.

The page is not a released artefact: there is nothing to build or attach, no image and no registry,
no tag and no GitHub Release, and no release workflow. Vercel deploys it from `main` on every push
and reads no tag.

**The host plan is the owner's call, not this page's.** The page advertises nothing, but should that
change the plan question returns with it: Vercel's terms restrict the **Hobby** plan to personal,
non-commercial use, and their Fair Use Guidelines count "advertising the sale of a product or
service" as commercial, so a page that advertised a future paid tier would sit on the commercial
side of that line by their own definition, even before anything is sold
([Fair Use Guidelines](https://vercel.com/docs/limits/fair-use-guidelines),
[Terms](https://vercel.com/legal/terms)). The Hobby terms also allow Hobby content to be used for
model training; a paid plan turns that off by default.
