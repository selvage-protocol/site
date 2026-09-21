# The public landing page

The page is live at **https://selvage-protocol.vercel.app**, which is its home;
`selvageprotocol.com` is not registered and registering it is not being pursued (see "The live
origin").

The landing page for **Selvage** (the project) and the **Selvage Session Protocol** (the protocol
it publishes). A Next.js App Router project with one route (`/`) and the framework's not-found
route beside it (`app/not-found.tsx`, styled from the same stylesheet): the page component carries
the prose, the product figures live in one component of their own, the global stylesheet carries
the
styling, and the browser downloads nothing beyond
the prerendered page, the stylesheet, the images, and the framework runtime with the
`SiteHeader` client boundary and its dependencies (header, buttons, and the arrow
icon). The page fetches no web font, runs no
analytics and makes no third-party request.

The canonical material lives in the other repositories:
[`selvage-protocol/specification`](https://github.com/selvage-protocol/specification) for the
protocol, prose and vectors, [`selvage-protocol/reference_server`](https://github.com/selvage-protocol/reference_server)
for the server and client library, and [`selvage-protocol/vscode_client`](https://github.com/selvage-protocol/vscode_client)
and [`selvage-protocol/nvim_client`](https://github.com/selvage-protocol/nvim_client) for the two
editor clients. This repository holds the page, the five checks that gate it, the one
browser proof the runner cannot run, and nothing else.

| Path | What it is |
|---|---|
| `app/page.tsx` | the page: the prose, the section order, and nothing else. Hero (promise, three landed facts, two CTAs, the room figure, and the version line under them), *Get it working* (the server commands, one folded row per editor, the demo instance and the address an editor hosts on, and the long routes folded into one `details`), *See it working* (four cards), *How it works* (four steps), *The session layer has no specification* (why the specification is the artifact), then the footer |
| `app/layout.tsx` | the root layout: `lang`, title, description and Open Graph metadata, the one origin the metadata resolves against (`metadataBase`, `alternates.canonical`, `openGraph.url`; see "The live origin"), and the global stylesheet. The favicons are deliberately absent: they are Next file conventions, so the framework writes their tags and `sizes` from the files themselves |
| `app/not-found.tsx` | the not-found route: what a mistyped address renders. The framework's own 404 document is styled with a `<style>` element and four `style` attributes, every one of which the policy's `style-src 'self'` refuses; this one is styled from `style.css` and carries neither (see "The Content-Security-Policy") |
| `style.css` | the one stylesheet, dark-only Catppuccin Mocha with a mauve accent: the Tailwind v4 entry (`@import "tailwindcss"` plus a `@theme` block pinning the palette) followed by the page's own rules under CSS variables, and a system font stack, so no font is fetched from a third party. Two widths are named there and the page keeps to them: `--measure` for running prose and `--column` for everything that is not prose (section rules, code blocks, the repo grid), so a wide figure is deliberate inside a narrow measure |
| `app/icon.png` / `app/icon1.png` / `app/icon2.png` / `app/apple-icon.png` | the favicon set: the owner's opaque export resized to the four sizes a browser asks for (32, 16 and 48 px, and the 180 px home-screen icon), named for Next's file convention so the framework writes their `<link>` tags and `sizes`. Nothing here is redrawn; there is no vector favicon (see "The site mark") |
| `app/opengraph-image.png` | the social card image (Next file convention, served as `/opengraph-image.png`): the owner's opaque export at full size, so cards crop owner's pixels |
| `public/mark-header.png` | the mark as the page body fetches it: the owner's transparent export resized to 128×128 for the one surface that paints it, 32 CSS px in the nav header (see "The site mark") |
| `public/mark-transparent.png` | the owner's transparent 800×800 export, vendored byte-identical (its checksum matches the owner's file) and never hotlinked. The page body no longer fetches it: it is the source the header derivative is made from, and `web_client/test/identity.test.ts` pins its bytes against that repository's own copy. The opaque export was vendored beside it while the hero panel was light; it is no longer fetched either; `app/opengraph-image.png` is the same file |
| `postcss.config.mjs` | the one PostCSS plugin (`@tailwindcss/postcss`), so `style.css` compiles on build |
| `next.config.ts` | the one build setting that is not a default: `poweredByHeader: false`, so the framework's `X-Powered-By: Next.js` banner is not on the page's HTML response |
| `components/ui/button.tsx` | the button primitive (shadcn-style `cva` variants: filled default, tinted secondary, ghost; renders an anchor when given `href`): the nav CTA and the two hero CTAs, nothing else |
| `components/ui/badge.tsx` | the pill primitive: the hero status line, a mono caps chip |
| `components/room-visuals.tsx` | the product figures: the hero's room window (the guest's mirrored tree, one open file, the two carets in it, the invite chip) and the three smaller drawings the cards carry. Inline markup and the page's own CSS, with no image, no dependency and nothing fetched (see "The product figures") |
| `components/ui/card.tsx` | the card primitive: the hero panel's glass card |
| `lib/utils.ts` | the one shared helper (`cn`: `clsx` + `tailwind-merge`) |
| `package.json` / `package-lock.json` | the only dependencies: `next`, `react`, `react-dom`, `tailwindcss` (+ its PostCSS plugin), `clsx`, `tailwind-merge`, `class-variance-authority` and `lucide-react` for icons, `typescript` and `@types/*`. No Radix, no component library, nothing else without a written reason |
| `.nvmrc` | the pinned Node version for local work and CI (`nvm use` reads it); `package.json` `engines` carries the major (`24.x`), because Vercel only deploys major versions |
| `scripts/check-claims.py` | the claim check: the phrases the page must not carry, each with its reason, the image tag it must carry, and the demo instance the page's sentences are checked against |
| `scripts/check-button-props.tsx` | the button check: renders the button and anchor variants and asserts their props reach the DOM (run by `npm run check:button` inside the gate) |
| `scripts/check-contrast.py` | the contrast check: parses the theme tokens out of `style.css` — including the sample's `selvage-mocha` token colours, the ground the code figure draws them on, and the alpha a peer's selection fill is drawn at — reads the token a selection fill sits under out of `components/room-visuals.tsx`, and asserts the rendered pairs sit at or above WCAG AA, with measured ratios (run by `scripts/ci-local.sh contrast` inside the gate) |
| `scripts/check-csp.py` | the policy check: reads the Content-Security-Policy out of `vercel.json` and the served HTML, and fails when the policy would refuse a script, stylesheet or image the page carries (run by `scripts/ci-local.sh csp` inside the gate; see "The Content-Security-Policy") |
| `scripts/check-weight.py` | the weight check: reads the served HTML and the bytes on disk, and fails when an image the page body fetches out of `public/` is over its budget or declares a pixel size the file does not have (run by `scripts/ci-local.sh weight` inside the gate; see "The site mark") |
| `scripts/check-csp-browser.mjs` | the browser proof: serves the built page with the headers out of `vercel.json`, drives headless Chromium over CDP, and asserts zero `securitypolicyviolation` events, `window.__next_f` an object, the header's concealment on scroll and no `X-Powered-By`. Not in the gate (the runner has no browser), and it needs `npm run build` first |
| `scripts/ci-local.sh` | the gate, running the same commands as the workflow |
| `lychee.toml` | what the link check does not check, and why |
| `vercel.json` | platform configuration: the Next.js framework preset, and three response headers: the Content-Security-Policy the page's own scripts are permitted by, the file it was once refused by (see "The Content-Security-Policy"), plus `X-Content-Type-Options: nosniff` and `Referrer-Policy: strict-origin-when-cross-origin` |
| `.github/workflows/ci.yml` | the gate, on every pull request and on demand (`workflow_dispatch`) |

## The site mark

The page serves the owner's raster mark at every size from the owner's own pixels: `public/`
carries the transparent 800×800 PNG export byte-identical (its checksum matches the owner's
file) and never hotlinked, and every surface that paints the mark is a derivative of it or of
its opaque twin. The one surface that carries the page-body mark is dark, and the opaque
export's baked `#1e1e2e` base would draw a visible chip inside it, so the transparent
glyphs are the ones that sit on the surface:

| Surface | File | Why |
|---|---|---|
| Nav header on dark Mocha | `public/mark-header.png` | the bar is translucent Mocha over the page; the opaque export's baked `#1e1e2e` base would draw a visible box against it, while the transparent glyphs sit straight on the bar. The bar paints it at 32 CSS px, which is what the file is sized for (see below) |
| Favicon and social card | `app/icon1.png` / `app/icon.png` / `app/icon2.png` / `app/apple-icon.png` / `app/opengraph-image.png` | tab bars and link unfurls crop unpredictably, so these stay opaque: the four favicon sizes are the opaque export resized, the social card the full-size opaque export |

The hero panel used to be the second surface. It is now a figure of the product itself (see
"The product figures") and carries no mark: a watermark on a drawing of an editor window is one
more thing between the reader and the thing the drawing shows.

There is no vector favicon. `app/icon.svg` was one: the owner's Comfortaa Bold `svp`
monogram (Catppuccin mauve/teal/red on a Mocha base) with the live `<text>` converted to
paths and Inkscape's filter and clip markup kept. It was the first icon the page
declared. Its `<clipPath>` contains a `<use>` that points at a `<g>`, which contributes no
shape to the clip, so both Chromium and librsvg clip the glyph group away and the only thing
an SVG-aware browser can draw from the file is the baked `#1e1e2e` rect: a blank dark square
at 16, 32 and 48 px, verified by rasterising the file in both. (Which candidate a browser
really paints in a tab is its own scoring of an SVG that declares no `sizes`; the point is
that one of the two icons was undrawable rather than merely small.) The paths themselves
were faithful to the owner's framing (at 2% fuzz their glyph box is the owner's opaque
export's own rectangle, 516×229+137+280 of 800), but the file still fell short of the
artwork: rasterised with Inkscape's shadow filter left in, the letters come out glowing
(RMSE 8% from the export at 800 px), and with the filter dropped they come out flat (11%),
because the export's dark stroke and soft shadow are baked into its pixels and not into the
paths. A redraw is a second copy of the artwork that nothing keeps in step with the first,
and the owner's pixels are the source of truth: it was removed rather than repaired.

The favicon set is the owner's own pixels at each size a browser asks for: `app/icon1.png`
(16), `app/icon.png` (32), `app/icon2.png` (48) and `app/apple-icon.png` (180) are the opaque
800×800 export resized with ImageMagick (`magick app/opengraph-image.png -resize <N>x<N>`),
each verified pixel-identical to a fresh resize (RMSE 0 at all four sizes) and rendered 1:1
by the browser, so no surface is an upscale of another. The mark sits where the owner put
it: its box is centred to within 1.5 px at every size, spanning 62–67% of the width and
25–29% of the height, because the export is a wide wordmark on a square field. At 16 px that
leaves the monogram 10×4 px, the smallest this artwork gets and the reason the 180 px and
the social card carry it best. Giving the tab more of the mark would mean cropping the
export's field, a re-framing of the owner's composition, so it is not done here.

The header mark is sized the same way the favicons are. The nav bar paints it at 32 CSS px, so
`public/mark-header.png` is the transparent export resized to 128 —
`magick public/mark-transparent.png -resize 128x128`, byte-identical to a fresh resize (RMSE 0)
— which covers a device pixel ratio to 4 and carries none of the master's transparent field.
The master is 60,595 bytes; served there it was 26% of everything the page transferred, and a
browser resampled it to a 20×9 px monogram without saying so. The derivative is 6,573 bytes, and
resampling it to the painted size differs from resampling the master by RMSE 0.15%, under the
favicon set's own margins. `public/mark-transparent.png` stays in the tree at full size: another
repository pins its bytes, so it is the source of truth rather than a fetched asset. Only the
surfaces that paint the mark are listed above, and `scripts/check-weight.py` holds every image
the page body fetches to a budget so a master cannot come back to one of them by accident.

## The page, and its copy

The page is a product page, not a numbered document: six parts in order, each one doing a job
the reader can name.

| Part | Its job |
|---|---|
| Hero | the promise, three landed facts, two CTAs, the room figure, and one line under the CTAs naming the specification as a draft at wire version `selvage/1`. The `h1`, *Edit the same file together, on a server you run.*, says what the product does and carries the self-hosted wedge from the design record's hook |
| Get it working | the published image as one `docker run`, and a link to the compose file and the source build — then one folded row per editor: VS Code, Neovim and the browser page, each with its prerequisites, its exact commands and its repository, and the browser row linking the demo, which serves the same page. The long routes (the corpus check, the vector replay) fold into one `details`. It closes on *Try the demo*, the one small instance the project runs, last in the section so the command and the editor rows keep the ground the hero points at; that section gives the address an editor hosts on and the setting each client takes it in, and leaves the guest to the invite link. It opens on the product's own shape: you run the server and the invite link is how somebody joins you, and the demo is a guest's way into a room somebody else hosts |
| See it working | four cards, each with a drawing of the thing it claims: anyone with the link is in, two carets in one text, the paths a guest sees, multiple clients on one engine |
| How it works | the four moves in order (host a folder, send the invite, type in the same file, close the window), under the design record's one-sentence workflow |
| The session layer has no specification | the wedge: language tooling has the Language Server Protocol and debugging the Debug Adapter Protocol, document sync has `y-protocols`, and the session layer is unspecified, so every collaborative tool decides those for itself. The specification is the flagship artifact, and the corpus counts appear here once, as the evidence they are |
| Footer | the licences and the page's own privacy line, nothing more |

The page used to end on a two-column ledger of what is built and what is not. On a product page
that reads as a to-do list, so it is gone, and its honest facts now sit where they do a job rather
than in a list: *Get it working* opens on the shape of the thing (you run the server, the invite link is
how somebody joins you), and the hero's line under the CTAs carries the version. What the ledger
spelled out is recorded where it is a decision or a gap: the design record's non-goals for v1
(`DESIGN.md` §11, in `selvage-protocol/ai_notes`), the
specification's `NOTES.md` for what the prose leaves open, and each repository's own README for
what its checkout does and does not do.

No section carries a number. The `01`…`07` counters in front of every section, the privacy notice
and the licences included, were the clearest signal that the page was a document rather than a
product. The headings step up to a display size instead (the `h1` 32/38/40 px, the `h2` 24/30 px),
the standing lede-and-checklist hero is gone, and the install guide that was a third of the page is
one foldable block.

The prose still descends from the static page's, and every sentence is a paraphrase of an
already-audited true sentence or framed as direction. Two sentences differ on purpose: the static
page's "loads no JavaScript" is false once Next.js serves the route, so the page says it prerenders
to static HTML and names the framework runtime scripts instead; and the waitlist form is gone, so
the privacy notice names its controller and collects nothing instead of carrying blanks for a
mailing service.

The must-not-say table below still binds every line. Three rows moved with what is now true:

- **The browser client, and the instance that serves it.** `web_client`, Monaco in a page, guests
  only, is served at one public origin now — the demo — so the page may name a route a reader can
  follow and the patterns that denied one are gone with the reason that produced them. What the
  filter holds instead is what is still false about that page: it is a guest join form, so joining
  needs the invite link a host copies and hosting stays in the two editors. The stale denial
  ("nothing runs in a web page") stays caught, because the page carried it once, and so does the
  claim that the project's own landing page is somewhere a room is joined — the route-shaped
  overclaim left now that a real one exists. The `clean` fixtures are the honest sentences, one of
  them the demo origin itself, so a widening that forbids the truth fails the gate.
- **The demo instance.** It runs, so "try the live demo" and the install-free page are truth and
  the entry that denied the instance is replaced by the overclaim that came with one: a demo
  described as a service. Its rooms are in memory on one small box, it keeps no work, and its terms
  gate it to personal and evaluation use. A second entry, new with the demo, holds the mistake the
  section makes easy: the instance is non-commercial and the software is not
  (`MIT OR Apache-2.0`, `FSL-1.1-MIT`, `CC-BY-4.0`), so a "non-commercial licence" sentence is a
  licence nobody granted.
- **The corpus counts.** Still exactly the numbers `specification/schema/validate.py` pins (31
  vectors, 34858 frame checks, 8642 assertions), and they now appear in one place, as the evidence
  for the specification, instead of three. The vector count is pinned with up to two words between
  the number and the word, so the page's "conformance vectors" and "wire vectors" are both gated.

## The product figures

The page shows the product instead of describing it, without an image, a font, a dependency or a
third-party request: `components/room-visuals.tsx` draws the room window from inline markup styled
by `style.css`. The hero figure is the whole surface at once: the guest's mirrored tree with the
open file marked by the figure's only dot, the two carets in it (a 2 px bar in the peer's colour at
a column between two characters of the line, the peer's name in the gutter lane on that line, and a
quarter-alpha fill behind what one of them has selected), and the invite chip that put them there.
Each card in *See it working* carries one smaller drawing of the thing it claims.

Five rules hold it together:

- **It is an illustration, and it says so.** The caption under the hero figure names it. Each code
  sample is a short function against the client crate's own API, with the `use` line left out, and
  each peer's caret is drawn where the browser client draws it (`renderCursors` in
  `web_client/src/browser/editor.ts`): a 2 px bar at the caret's own range, a badge in the left
  gutter on the line the caret is on, and a fill behind the characters the peer holds. A name is
  never written into the text of a line: inside Rust it would read as syntax, which is a claim
  about the source that is not true — so it stays in the lane beside the line number, where that
  client's glyph-margin badge goes.
- **The open file is named twice and marked once.** The file the room has open is written in the
  guest's tree and in the room bar, both times in the panel's own text colour (`--fg`), and the dot
  beside it in the tree is the figure's only mark for it, in that same colour. It used to be two
  dots, one in each peer's colour, beside the same filename: two identical shapes in two peer
  colours read either as the peers themselves or as an inconsistency, and a peer's colour belongs
  to their caret. The caption names the dot, and the peers keep mauve and teal to themselves.
- **The sample is coloured the way the editor colours it.** The token colours are the browser
  client's own `selvage-mocha` theme (`defineTheme` in `web_client/src/browser/main.ts`): comment
  `#868ca2`, keyword `#cba6f7`, string `#a6e3a1`, number `#fab387`, type `#f9e2af`, on the sample's
  ground and in the body colour `#cdd6f4` otherwise. Punctuation has no rule in that theme, so it
  keeps the body colour here too. The samples are fixed and short, so each token is a span written
  by hand in `components/room-visuals.tsx` — no highlighter, no dependency, no parser.
- **The drawings are `aria-hidden`; the captions are not.** A screen reader hears the sentence that
  describes the room, not the code in it.
- **No inline `style`, no `<style>`, no webfont, no external image.** The policy in `vercel.json`
  refuses all four (see "The Content-Security-Policy"). Every colour in a figure is a class in
  `style.css` or a theme token, which is also what lets `scripts/check-contrast.py` measure the
  panel and the glass card it draws on.

## Running it

```console
$ npm ci --no-audit --no-fund
$ npm run dev
# then open http://localhost:3000/
```

Production, the way the gate checks it:

```console
$ npm run build && npm start
# then open http://localhost:3000/
```

`npm run dev` is the framework's development server, and its page can reload itself: Next's dev
client calls `window.location.reload()` when it decides the server it was talking to has been
replaced (a new session id, a changed compilation hash) or after twelve failed attempts to hold
its hot-reload channel. A dev server restarted underneath a reader therefore looks like a page
that keeps refreshing on its own. That is the dev server being a dev server, and it is nothing a
visitor to the deployed site can see: the `next build` output carries no way to reload a page —
no meta refresh, no service worker, no polling script — and the policy below refuses every origin
but its own.

Node comes from `.nvmrc` (`nvm use`, or any manager that reads it); CI installs exactly that
version. `package.json` `engines` carries only the major (`24.x`): Vercel deploys major
versions alone, and an exact pin fails the deployment before anything builds. Telemetry is off
in the gate (`NEXT_TELEMETRY_DISABLED=1`).

## Deploying it

Vercel, connected to this repository over the GitHub integration, building the Next.js project:
`vercel.json` carries `"framework": "nextjs"` so the dashboard does not have to, plus the three
response headers: the `Content-Security-Policy` (its own section, below), `X-Content-Type-Options:
nosniff` and `Referrer-Policy: strict-origin-when-cross-origin`. `next.config.ts` turns the
framework's own `X-Powered-By: Next.js` banner off, so the HTML response does not name the stack
it was rendered by. There is nothing to configure beyond connecting the repository.

Production deploys on `main`, at **https://selvage-protocol.vercel.app**, and every branch and pull request gets a preview URL. That is all
Vercel is used for. It does not run the checks; the workflow does, and those are the ones worth
making required status checks under branch protection.

Two things about the host plan are the owner's call, not this page's. The page no longer
advertises anything, but should that change the plan question returns with it:

- Vercel's terms restrict the **Hobby** plan to personal, non-commercial use, and their Fair Use
  Guidelines count "advertising the sale of a product or service" as commercial. A page that
  advertised a future paid tier would sit on the commercial side of that line by their own definition,
  so Hobby may not be the right plan if that returns, even before anything is sold. [Fair Use
  Guidelines](https://vercel.com/docs/limits/fair-use-guidelines), [Terms](https://vercel.com/legal/terms).
- The Hobby terms also allow Hobby content to be used for model training. A paid plan turns that
  off by default.

## The Content-Security-Policy

The header is `vercel.json`'s, applied by Vercel:

```
default-src 'none'; script-src 'self' 'unsafe-inline'; script-src-attr 'none'; img-src 'self' data:; style-src 'self'; form-action 'none'; base-uri 'none'; frame-ancestors 'none'
```

It read without `script-src` until this was found, and that absence is the whole reason this
section exists. With `default-src 'none'` and nothing for scripts to fall back to, the page's
own seven chunks and all fifteen of its inline scripts were refused: `window.__next_f` stayed
the string `undefined`, the page never hydrated, and `SiteHeader`'s hide-on-scroll silently did
nothing while the accessibility section below read as if it worked. A policy that refuses the
page it ships with is not strict, it is broken, and nothing in the gate said so.

`script-src 'self' 'unsafe-inline'` is the smallest thing that is also true, and the route
itself is why it cannot be narrower. `'self'` is the seven chunks. `'unsafe-inline'` is the
bootstrap and the flight data Next writes into the HTML: a **nonce** would permit those instead,
but a nonce has to be fresh per request, which means dynamic rendering, and the page is a static
prerender (`○ /`), so the route would be traded for the directive. A committed **hash list** is
worse than it looks: any prose edit rewrites the flight payload the hashes are computed over,
and a stale hash fails the same silent way the missing directive did.

`script-src-attr 'none'` narrows that token to the elements the route actually needs. Without
the directive it covers an inline `on*` attribute on any element as well as an inline `<script>`,
and with it the two are decided separately: `script-src` carries the bootstrap, and every inline
handler attribute is refused. The page carries none, so it costs the page nothing.

`form-action 'none'` closes the one element kind `default-src 'none'` does not reach: a Form
Action has no fallback to `default-src`, so without the directive any `<form>` the page carried
could submit to any origin. The page renders no form and no user input into itself, so the
directive cannot break anything.

What the policy still refuses: every origin that is not this one, `eval`, an inline `on*`
attribute, a form submission, a `<base>` that would retarget the page's relative URLs, framing,
and every resource kind the page does not name. `data:` is allowed for `img-src` alone.

Two pieces of evidence, with their limits:

- `scripts/check-csp.py` runs in the gate over the HTML the production server renders, and over
  the HTML its not-found route renders, because that route is a page the site serves and the
  policy has to permit it too. The framework's own 404 document is styled with a `<style>` element
  and four `style` attributes, all five of which `style-src 'self'` refuses; `app/not-found.tsx`
  is styled from `style.css` instead. The check takes the policy *from* `vercel.json`, not a copy
  of it, and decides every script, stylesheet and image against the directive that governs it,
  following the fallback chains a browser follows. The
  policy as it read without `script-src` is one of its own fixtures, so it fails on the defect
  it was written for. It is a model of the policy, not a browser, and a source expression it
  does not model is an error rather than an assumption.
- A real Chromium run against the built page served with these exact headers, kept runnable as
  `scripts/check-csp-browser.mjs`: it applies the `headers` block out of `vercel.json` through a
  local proxy (`next start` does not apply it, only the host does) and asserts zero
  `securitypolicyviolation` events, `window.__next_f` an object, the header concealed
  (`translate: 0px -100%`) at `scrollY` 900 and back at 300, and no `X-Powered-By`. It then
  requests a path no route claims and asserts the `404` it renders carries no violation either,
  which is the assertion that fails on the framework's own 404 document. Point
  `VERCEL_JSON` at the policy as it read without `script-src` and it fails, which is checked
  rather than assumed. It needs a browser the runner does not have, so it is not in the
  workflow: `npm run build && CHROMIUM=/path/to/chromium npm run check:csp-browser`.

Neither of them can see the deployed response headers. If Vercel stops applying the `headers`
block, or applies it to a path this policy was not written for, nothing in this repository
notices.

## Privacy: controller and no collection

One thing is fixed, and one thing is gone.

**The controller.** The privacy notice names
[`selvage-protocol`](https://github.com/selvage-protocol), the GitHub
organisation, as the controller, with a link and no other contact. Only the
owner could fill that blank, and now it is filled.

**The collection.** There is none. The waitlist form is removed (no form, no
endpoint, no mailing service, no processor), so the notice's collection,
basis, retention and erasure paragraphs went with it. What remains is the
page-level statement the footer already carried: the page sets no cookie,
makes no third-party request, and sends nothing anywhere. If collection ever
returns, the notice grows back with it: controller, processor, purpose, basis
and erasure path, before the form, not after.

Two decisions taken here, stated so that they are not re-litigated silently:

- **No honeypot field.** Had a form stayed, a hidden field would only have worked because
  whatever received the submission discarded the ones that filled it, and each service
  spells that field its own way. Naming one service's convention before the service was
  chosen would have baked the provider in, exactly what the one-endpoint rule existed to
  avoid; so spam filtering would have been configured at the service, where it belongs.
  With no form there is no field to debate; the reasoning stays so a reintroduced form
  does not re-litigate it.
- **`form-action 'none'`.** The page renders no form, so a Form Action could only ever carry an
  injected one, and the directive is what refuses it. The waitlist form and its endpoint are
  gone, which is what made the directive free: naming an endpoint to keep a form working was the
  reason not to set it, and there is no endpoint to name.

## What the page must never say

The page's job is to be checkable, so the rule is mechanical where it can be:
`scripts/check-claims.py` fails the build on each of the known wordings below, carries the reason
beside each, and normalises the served HTML before matching: comments, tags, scripts and styles
removed, entities decoded, whitespace collapsed. So a phrase cannot pass by wrapping across a
line or by encoding a character. The scan runs against what the server renders, not the source:
the gate builds, starts the production server, fetches `/` over HTTP and checks that HTML. It also
asserts two claims in the positive, the image tag and the demo instance, described just below.
**It is a filter, not a proof.** It cannot see meaning: a false claim in different words, a
synonym outside the list, a superlative, an unbacked sentence or a wrong number the list does not
pin all pass it. A green gate means the known wordings are absent, nothing more. The reasons are
summarised here so that the constraint survives without the file that produced it.

`scripts/check-claims.py` asserts two claims in the positive, because a phrase list cannot reach
either. The first is the image tag the happy path hands a reader: the check pins
`ghcr.io/selvage-protocol/selvaged` to one version, requires every reference the rendered page
carries to name it, and then asks the registry for that tag — anonymously, with no credential in
the request, because no account is the point of the command. It compares the **per-platform
manifests' layer digests**, not the index: a platform entry only states that a slot is *labelled*
arm64, and `selvaged:0.1.1` proved the difference by publishing both legs around the amd64 binary,
every layer digest identical across the two. The two versions a page must never name are `0.1.0`
and `0.1.1`; `0.1.2` was correct and is superseded by `0.2.0`, which is the pin. The second is the
demo instance: the page points at one host, every reference to that host has to be one of the three
the page may carry, a link has to point at the instance itself, and `https://selvage.dontblameme.dev/meta`
has to report a `selvaged` server offering a wire version the page names. The references are read
from the visible text *and* from the links' destinations, because a label and the place it goes
are two claims: an anchor labelled with the demo host whose `href` points elsewhere passes a
text-only scan. The allowed references are the origin, its `/terms`, and the `wss://` origin with
**no path**, because both clients append `/session` to whatever address they are given (`sessionUrl`
in the engine they vendor), so the page naming `wss://…/session` would hand a reader an address that
gets a second `/session` appended and is refused. The check asserts that path separately, by
asking `https://selvage.dontblameme.dev/session` for a plain `GET` and requiring a **4xx carrying
the server's own JSON**: the path has to reach the server the page names, a redirect or a `5xx` must
not stand in for it, and the proxy's own `404` page is `text/html`. Which `4xx` the server picks is
its business, and pinning `404` would redden this gate for a change in `selvaged` that makes no
sentence on the page false. The **WebSocket upgrade itself is not asserted**, because the host's proxy answers a
hand-rolled upgrade from a runner's egress with `403` and a request the proxy refuses asserts
nothing; the upgrade was verified by hand, from a client the proxy accepts, and that is recorded in
the findings rather than claimed here. It also asks `/` for a `200` and a `text/html`, because the
browser row tells a guest the demo serves the page and the proxy's own `404` is `text/html` too, so
the media type alone would let a dead page satisfy it. What the demo half no longer does is compare the instance's
release to the page: the page named one, a reader had no use for it, and it is gone from the
section. `PINNED_IMAGE_VERSION` still ties the page's `docker run` to the registry. The wire version is held
to what the instance offers rather than to a constant here, because the page owns the version it
names and the instance owns the version it speaks. **That assertion couples the site's gate to a
running box**: a demo that is down or moved, a `/session` the proxy no longer routes to the
server, and a box whose `/` is not the page all fail the build, because a page claiming a demo that is not there is
the defect it exists to catch. It sends its own user agent, since the host's proxy answers `403` to
an interpreter's default signature. The image half needs egress to `ghcr.io` and exits 2 rather
than passing when it cannot reach it; the demo half does the same for an instance that does not
answer at all, and exits 1 when the instance answers something that disproves a sentence.

| Must not appear | Why not |
|---|---|
| "open source" of the server or the project | The server binary is `FSL-1.1-MIT`: source-available, not OSI-approved, free for non-competing use and under MIT two years after each release. The specification and the clients are the open ones, and the page names their licences instead of reaching for the phrase |
| "SSP" | The abbreviation is taken by stack-smashing protection and by supply-side platforms. The protocol is the Selvage Session Protocol, written out |
| `salvage/1` | The wire version is `selvage/1`. "Selvage" is heard as "salvage", which is why the full protocol title appears at least once in the page's first paragraph |
| end-to-end encryption, E2EE | Version 1 has no encryption layer: frames travel through the server as unencrypted bytes, and the slice has no transport security either. The relay is payload-opaque but not confidential |
| "the server cannot read it" / "the text never reaches the server" | The relay routes opaque bytes and keeps no document text, but it can read a frame as it passes and there is no transport security. It is not a confidential relay |
| a browser route a reader can open, hosting in a browser, a room without an invite | The browser client exists (`web_client`, Monaco in a page, guests only) and the demo instance serves it at a public origin, so naming the demo page is truth, and the browser row may link it as the page a guest reaches with nothing installed. What is not: hosting in a browser (hosting is the two editors plus a server), joining without the invite link a host copies (the page is a guest join form), and the project's own site as a place to join a room (it is a landing page). The stale denial "nothing runs in a web page" stays caught too: that sentence was true when the filter forbade the bare word and it is false now |
| file create, rename or delete | The room carries no file mutations and nothing writes to the host's working copy. The host's own editor still changes that folder, and a Neovim guest's mirror materialises the granted paths |
| the server route denied: no image to pull, nothing to install on the server | The reason this entry used to give — that no Dockerfile, compose file or service unit exists in any repository — is false now. `ghcr.io/selvage-protocol/selvaged:0.2.0` is published and pulls anonymously, `reference_server/compose.yaml` runs it, and `reference_server/packaging/systemd/selvaged.service` installs the binary. The pattern used to forbid the word `docker` itself, on that stale reason; it holds the denial of those artefacts instead, which is the sentence the page carried |
| a stable 1.0 | The wire version is `selvage/1`; the compatibility rule in force is the same major. No corpus line puts the design at 0.x. The pattern's lookbehind keeps `0.2.0` out of it: that is the version of the published image, a number inside a number, not a claim that 1.0 exists |
| a second implementation, or interoperability | There is none. The Neovim client drives a byte-identical copy of the same engine, so nothing yet shows a client built from the prose alone agreeing byte for byte with the Rust one |
| marketplace or extension-gallery availability | The extension is unpublished, and publishing it is a non-goal until it works with a friend |
| "guests are read-only" or "view-only" | The design inverts it: read-only scopes the host's filesystem, never the shared buffer, and every holder of the invite edits the session CRDT. Saying otherwise would be a lie about the product's central idea |
| "your code never leaves your machine" | Document payloads travel through the server to the peers that ask for them, and there is no encryption layer. What is bounded is the grant: the paths the host enumerates, and the reads it serves from inside the granted root |
| invented proof: screenshots, testimonials, user counts, a production deployment, a demo dressed as a service | There is no recording, no user count, and no commercial deployment behind the demo: it is one small box with in-memory rooms, gated to personal and evaluation use, and the site's own origin is a deploy of this page rather than of the protocol. The demo is named as what it is, which the entry on it enforces: no "free demo", no room that persists, no team-sized instance. The one image the page carries is the project's own site mark (see above), not proof of anything |
| a claim of priority ("the first protocol to specify …") | The design record surveys prior art (Eclipse Open Collaboration Tools and others). The project's claim is that the session layer is unspecified, not that this is first |
| a non-commercial licence, or software described as non-commercial | The instance's terms are non-commercial; the software's licences are not. The workspace and the clients are `MIT OR Apache-2.0`, `crates/selvaged` is `FSL-1.1-MIT` (which reserves commercial hosting for its licensor), and the specification's prose, schema and vectors are `CC-BY-4.0`, so the demo section says what it may not: that the two are different statements about different things |
| a corpus number other than the pinned one | The counts (31 vectors, 34858 frame checks, 8642 assertions) are constants in `specification/schema/validate.py`; any other number is a claim the corpus disproves |
| a third party seeing the room | The relay is payload-opaque but plaintext with no transport security in this slice, so the operator and the network path can see the room's text. Only the page's own weak reading (no third party's cloud holding the room) is backed |
| a bare "no cloud", qualified or not ("no cloud in between" included) | A self-hosted server can itself run on a cloud VM, so only the weak reading is backed: no third party's cloud holding the room. The backed storage sentence is "nothing written to disk" |
| a proven cross-editor pairing | The first cross-editor session has run. The design notes' hand-run proof (2026-09-17) passes grant, cursors and follow in both directions, but its concurrent-edit step falls short by one trailing-newline byte, so byte-identical replicas across the two editors are not demonstrated. State what the clients are built to do rather than that it is proven |
| a speed adjective (instant, real-time, lag-free) | No performance data exists anywhere in the corpus |
| an ease claim (takes seconds, one-click, just works) | The image, the compose file and the systemd unit all exist; no ease claim around them is backed, because no install time, start-up time or latency has been measured or recorded anywhere in the corpus |
| an only-machine claim (untouched by the network) | Document payloads travel through the server to the peers that ask for them; the grant bounds which paths are served, not which machines code touches |
| a "live" / "now available" status | One small demo instance runs and there is no hosted service and no launch: a status reading "live" or "now available" sells the demo as a product. The honest status line names the release and the specification draft |
| SaaS-creep words (sign in/up, get started, download, pricing) | No accounts exist, so nothing can be signed into; no package exists to download and no price exists to show. The page offers the specification to read and a server to run |

Three things the check cannot make mechanical, and which a reader of a change has to hold:

- **A number on the page has a home.** The corpus counts (31 vectors, 34858 frame checks, 8642
  assertions) are the constants `specification/schema/validate.py` pins; when the corpus moves,
  the page moves with it. The commands are the ones the repositories' own READMEs document.
- **No adjective does the work of a fact.** If a sentence could be true of any project, it does
  not belong on this page.
- **A false claim in other words.** The check matches a list of known wordings, so a synonym, a
  paraphrase or an assertion the list does not know about passes it. Green means those wordings
  are absent; it does not mean every sentence was checked against the corpus.

## The live origin

The page is live and public at **https://selvage-protocol.vercel.app**, served by Vercel with the
two headers above. That origin is the page's home. `selvageprotocol.com` is **not registered**, and
registering it is not being pursued: nothing here is waiting on a domain.

What that decides:

- **One origin, named once.** `app/layout.tsx` holds it in `LIVE_ORIGIN` and nothing else in the
  page names a host. `metadataBase` resolves the file conventions' paths against it, so `og:image`
  and `twitter:image` read a URL that resolves,
  `https://selvage-protocol.vercel.app/opengraph-image.png`, instead of the
  `http://localhost:3000/…` a local or preview build published while the layout had no
  `metadataBase` at all. `check-csp.py`'s `DEFAULT_ORIGIN` names the same origin.
- **`rel="canonical"` and `og:url` name that origin too.** Both are written from the same constant,
  so the document carries `<link rel="canonical" href="https://selvage-protocol.vercel.app"/>` and
  the matching `og:url`, and a card unfurled from a branch preview names the same URL and image as
  production. Moving the page to another origin is one constant, and the two tags follow it.
- **The title, description and `og:title`/`og:description` mirror the page's own heading and lede.**


## The gate

```console
$ scripts/ci-local.sh              # typecheck, build, button, contrast, claims, csp, weight, links, lint
$ scripts/ci-local.sh typecheck    # tsc --noEmit
$ scripts/ci-local.sh build        # next build
$ scripts/ci-local.sh button       # render the button/anchor variants and assert their props reach the DOM
$ scripts/ci-local.sh contrast     # theme token pairs at or above WCAG AA, with measured ratios
$ scripts/ci-local.sh claims       # rebuild, serve production, fetch / and scan the rendered HTML
$ scripts/ci-local.sh csp          # the policy in vercel.json over the served page and its not-found route, refusing nothing either carries
$ scripts/ci-local.sh weight       # every image the page body fetches, against its byte budget
$ scripts/ci-local.sh links        # serve production, lychee over the rendered page and README.md
$ scripts/ci-local.sh lint         # actionlint over the workflows (nix; the workflow pins a release)
```

The claims step fetches `/` from the production server into `.tmp/rendered.html` (`PORT`
overrides the default `3100`) and scans that file by name; reaching no file is an error rather
than a pass, and every pattern must match its own sample before the scan, so a dead pattern fails
the gate instead of passing everything; named honest wordings must stay unmatched, so a broadening
that reintroduces a false positive fails it too. The scan also reads the page's image reference,
holds it to the version pinned in `scripts/check-claims.py`, and asks `ghcr.io` for that tag, and
reads the page's demo reference, holds it to the one host the check allows, and asks that instance
what it reports, whether the editor address's `/session` path is answered by the server rather than
by the proxy in front of it, and whether its `/` serves the page.

The policy step reads the same rendered file, its not-found route, and the policy out of
`vercel.json`, and fails when the policy would refuse a script, stylesheet or image either page
carries, the defect described under "The Content-Security-Policy". Its fixtures run first: a
policy without `script-src` and a policy that drops `default-src 'none'` both have to fail it, so
the check cannot have gone blind.

The weight step reads the same rendered file again and the bytes of every image it fetches out of
`public/`, and holds each to a budget: a surface this page paints at 32 px may not be handed the
owner's 800×800 master. It also asserts the `width`/`height` an `<img>` declares are the file's own
pixels, because a `src` swap that leaves them behind distorts the mark and no failed request says
so. It is a ceiling per image rather than a total for the page, so a framework upgrade that
changes nothing a reader sees cannot redden it.

`.github/workflows/ci.yml` runs the same commands on `ubuntu-24.04` on every pull request (and
on demand, through `workflow_dispatch`): Node from `.nvmrc`, `npm ci`, then `typecheck`, `build`, `button`,
`contrast`, `claims`, `csp`, `weight`, `links` and `lint`. It installs lychee and actionlint from pinned releases: the runner has no
nix, so `scripts/ci-local.sh` takes both from `PATH` when they are there and from nixpkgs
otherwise, and all three places run the same checkers.

## Accessibility: the WCAG AA floor

The page holds itself to WCAG 2.2 AA. Ratios are computed from the theme tokens in
`style.css`, never eyeballed; `scripts/check-contrast.py` asserts them in the gate, so a
regression fails the build instead of waiting for a look. Measured today:

| Pair | Ratio | Needs |
|---|---|---|
| body text on page | 11.34:1 | 4.5:1 |
| muted prose on page | 7.37:1 | 4.5:1 |
| link on page | 8.07:1 | 4.5:1 |
| visited link on page | 5.18:1 | 4.5:1 |
| button label on its mauve fill | 8.07:1 | 4.5:1 |
| peer badge label on its mauve fill (the first caret in the hero figure) | 8.07:1 | 4.5:1 |
| peer badge label on its teal fill (the second caret in the hero figure) | 11.01:1 | 4.5:1 |
| code comment on the sample's ground (the editor theme's `comment`) | 5.07:1 | 4.5:1 |
| code keyword on the sample's ground (`keyword`, the mauve the page already uses) | 8.34:1 | 4.5:1 |
| code string on the sample's ground (`string`) | 11.39:1 | 4.5:1 |
| code number on the sample's ground (`number`) | 9.57:1 | 4.5:1 |
| code type on the sample's ground (`type`) | 13.33:1 | 4.5:1 |
| the peers' caret bars and badge fills on the code figure's ground | 8.55:1 / 11.67:1 | 3.0:1 |
| the peers' caret bars and badge fills on the glass card, worst stop | 8.34:1 / 11.37:1 | 3.0:1 |
| code type under a peer's selection fill (the fill's own ground) | 6.97:1 | 4.5:1 |
| code string under a peer's selection fill (the fill's own ground) | 5.95:1 | 4.5:1 |
| the selection tint itself, at the client's quarter alpha | 1.71:1 / 1.91:1 | 1.5:1 |
| code text on code background | 12.14:1 | 4.5:1 |
| muted text on code background | 7.89:1 | 4.5:1 |
| badge text on its fill | 6.63:1 | 4.5:1 |
| secondary-button text on its fill (hover state, the worst of rest `15` at 5.98:1) | 5.32:1 | 4.5:1 |
| secondary button boundary (`border-mauve/60`, parsed from the component) | 3.82:1 | 3.0:1 |
| focus outline against the page | 8.07:1 | 3.0:1 |
| glass-card text, worst of the five panel stops | 11.71:1 (muted 7.61:1) | 4.5:1 |
| panel text, worst stop (the tree, the file bar and the figure's caption sit on the panel, not on the card) | 9.08:1 (muted 5.90:1) | 4.5:1 |
| the open file's dot on the panel, worst stop (the figure's one mark that is not a peer's) | 9.08:1 | 3.0:1 |

WCAG 1.4.1 is the one criterion measured the other way round, because both of its floors cannot
hold at once here. It asks for 3.0:1 between a link and the text beside it when colour is the only
thing distinguishing the two, and the link's own text is separately floored at 4.5:1 against its
background. `--fg` is 11.34:1 on `--bg`, so a colour that just clears the text floor is
11.34 / 4.5 = 2.52:1 from the prose, and a colour 3.0:1 from the prose is at most 3.78:1 on the
page, below the text floor. The page takes 1.4.1's other allowed affordance instead: every prose
link is underlined (`text-decoration-line` named in `style.css`, because preflight's
`text-decoration: inherit` had left every link colour-only, which is why the thickness and offset
already there drew nothing). `scripts/check-contrast.py` reads that declaration out of the
stylesheet and asserts the 3.0:1 pair whenever it is missing, so a colour-only link scheme fails
the gate: the stylesheet as it stood before the underline went in measures 1.40:1 unvisited and
1.95:1 visited and fails the check.

`--link-visited` is a deeper mauve, `#a181d6`, rather than the neutral `#9399b2` it was: that grey
sat 1.27:1 from `--muted`, so a visited link was the colour of the prose around it, and every
repository link is on the org's own history the moment anyone has browsed it. The underline
carries the affordance now; the colour keeps a visited link looking like a link, at 5.18:1 on the
page.

Four groups the check does not parse are computed the same way, from the colours the browser
composites, and are re-measured whenever the fills around them move: inline code text on its
chip fill (`rgba(205, 214, 244, 0.07)` over `--bg`) 9.62:1; the invite chip's label and its URL
on the chip's own tint (`rgba(203, 166, 247, 0.08)` over the figure's fill over the card's) 6.77:1
and 10.41:1; the card body text on the card fill (`rgba(24, 24, 37, 0.5)` over `--bg`) 7.63:1;
the client chips and the rail label under them 10.56:1 and 8.55:1. The section
hairlines and the card borders sit at 1.30:1 against the page on
purpose: they are decorative separators, they carry no state, and nothing is identified by
them.

The selection tint is the one colour on the page that cannot clear the floor it would be given
as a mark, and the check says so rather than pretending. It wears the alpha the client itself
builds for a selection (`translucent(colour, 0.25)`, `web_client/src/bridge/cursors.ts`), which
measures 1.70:1 mauve and 1.90:1 teal against the code ground; the alpha that would reach the
non-text 3.0:1 is about a half, and at that alpha the sample's own text on it falls below
4.5:1. The two floors cannot both hold for a translucent fill, so the fill is asserted where it
matters — the token it sits under, read out of `components/room-visuals.tsx` so that moving it
over the dimmer comment colour fails the build — and its own pair is a floor of 1.5:1, which only
fails a tint nobody can see. The opaque caret bar is what carries a peer at 3.0:1.

What no ratio proves is read against the code by a person on every change:

- **Visible focus.** Every link, button and `summary` carries a 2 px mauve `:focus-visible`
  outline at a 2 px offset; the `Button` primitive repeats it as a utility, so both spellings
  agree. Verified in the browser: the first three tabs land on the nav's own anchors with that
  ring.
- **Keyboard.** Every control is a native anchor, button or `details`/`summary`. The sticky header
  slides away
  on scroll-down but carries `focus-within:translate-y-0`, so a tabbed-to link is never
  focused off-screen. That slide is the `SiteHeader` client boundary running, so it is only as
  true as the page's scripts being permitted. "The Content-Security-Policy" records the
  interval in which they were not, and the gate step that now fails if it happens again.
  No skip link: the page is one route, so there is no repeated block
  to bypass. The folds in *Get it working* are native `details`, so they open without a script.
- **Reduced motion.** Two things move, and both stand down under `prefers-reduced-motion`: the
  hero figure's 520 ms entrance (an `opacity`/`translateY` animation) and the 2 px hover lift on
  the figure cards, each inside a `prefers-reduced-motion:
  no-preference` query, with `scroll-behavior: smooth` and the header slide switched off in a
  `reduce` block. The buttons' lift is a `motion-safe:` utility for the same reason. Verified in
  the browser: under emulated `reduce` the hero's `animation-name` is `none` and `scroll-behavior`
  is `auto`.
- **Touch targets.** Nav links are `text-sm` (20 px line box) with `py-1`, for 28 px of
  target height against the 24 px minimum; buttons are 32–44 px tall, and the `summary` is a
  full-width 45 px row. In-prose links are inline and exempt.
- **Decorative only.** The hero figure and the cards' drawings are `aria-hidden`: a matte field
  of fine rules, the mirrored tree, one open file, the carets and the invite chip. Their
  worst-case ratios still clear AA (above), and the figure carries a visible caption, so a screen
  reader hears the sentence describing the room rather than four lines of code.
- **The figure grid is a list.** Each card's drawing is followed by a bold lead and a sentence, so
  the four claims are readable as a list before they are readable as a picture.
- **Client links.** The per-editor rows keep the underline every other prose link carries, so a
  link is not told apart by its colour and monospace face alone; the focus outline is unchanged.

## Licence

`MIT OR Apache-2.0`, the pair the clients carry; see `LICENSE-MIT` and `LICENSE-APACHE`. The
page's framing follows the project's own design record, which is private and carries no licence;
the workflow sentence is adapted from the Neovim client's README, which is `MIT OR Apache-2.0`.
The page footer says the same thing.
