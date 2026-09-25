# The public landing page

The page is live at **https://selvage.dontblameme.dev**, which is its home;
`selvageprotocol.com` is not registered and registering it is not being pursued (see "The live
origin").

The landing page for **Selvage** (the project) and the **Selvage Session Protocol** (the protocol
it publishes). A Next.js App Router project with one route (`/`) and the framework's not-found
route beside it (`app/not-found.tsx`, styled from the same stylesheet): the page component carries
the prose, the product figures live in two components of their own, the global stylesheet carries
the
styling, and the browser downloads nothing beyond
the prerendered page, the stylesheet, the two fonts, the images, and the framework
runtime with the four client components (the bar, the hero's room window, the terminal,
and the demo's copy control) and their dependencies. The page runs no
analytics and makes no third-party request: the two fonts it loads are served from this
origin, and the glyph files are one of the things it holds to its budget here.

The canonical material lives in the other repositories:
[`selvage-protocol/specification`](https://github.com/selvage-protocol/specification) for the
protocol, prose and vectors, [`selvage-protocol/reference_server`](https://github.com/selvage-protocol/reference_server)
for the server and client library, and [`selvage-protocol/vscode_client`](https://github.com/selvage-protocol/vscode_client)
and [`selvage-protocol/nvim_client`](https://github.com/selvage-protocol/nvim_client) for the two
editor clients. This repository holds the page, the six check scripts that gate it, the one
browser proof the runner cannot run, and nothing else.

| Path | What it is |
|---|---|
| `app/page.tsx` | the page: the prose, the section order, and nothing else. Hero (the promise, two CTAs, four one-word facts, and the room window), *Try → Run → Rent* (the demo and its terms, the published image as one Docker command and the one wire version both artefacts speak, and the hosted tier that does not exist yet), *Get it working* (the command and each client in the tabbed terminal, what the server carries and what it still sees in the two panels beside it, and the specification as a draft), *See it working* (four cards), *How it works* (four steps), *Why a spec* (why the specification is the artifact, with the wire corpus's counts and the file that pins them, the comparison against the layers that already exist, and the repositories), then the footer |
| `app/layout.tsx` | the root layout: `lang`, title, description and Open Graph metadata, the one origin the metadata resolves against (`metadataBase`, `alternates.canonical`, `openGraph.url`; see "The live origin"), the global stylesheet, and the two fonts. `next/font/google` fetches Geist (400, 500, 600) and JetBrains Mono (400, 500) at build time and exposes them as `--font-geist-sans` and `--font-jetbrains-mono` on the document element, which the theme and the page's own rules both read, so the glyphs are served from `/_next/static/media` and no request leaves for a font host. The favicons are deliberately absent: they are Next file conventions, so the framework writes their tags and `sizes` from the files themselves |
| `app/not-found.tsx` | the not-found route: what a mistyped address renders. The framework's own 404 document is styled with a `<style>` element and four `style` attributes, every one of which the policy's `style-src 'self'` refuses; this one is styled from `style.css` and carries neither (see "The Content-Security-Policy") |
| `style.css` | the one stylesheet, dark-only Catppuccin Mocha with a mauve accent: the Tailwind v4 entry (`@import "tailwindcss"` plus a `@theme` block pinning the palette) followed by the page's own rules under CSS variables, which sit in Tailwind's `components` layer so that a utility on an element wins over the class the page gives it. One width is named there and the page keeps to it: `--measure`, where a line of running prose stops, so a wide figure is deliberate inside a narrow measure rather than an overflow |
| `app/icon.png` / `app/icon1.png` / `app/icon2.png` / `app/apple-icon.png` | the favicon set: the owner's opaque export resized to the four sizes a browser asks for (32, 16 and 48 px, and the 180 px home-screen icon), named for Next's file convention so the framework writes their `<link>` tags and `sizes`. Nothing here is redrawn; there is no vector favicon (see "The site mark") |
| `app/opengraph-image.png` | the social card image (Next file convention, served as `/opengraph-image.png`): the owner's opaque export at full size, so cards crop owner's pixels |
| `public/mark-header.png` | the mark as the page body fetches it: `scripts/make-mark.py`'s derivative of the owner's transparent export, the master area-averaged to 128×128, premultiplied by alpha and otherwise untouched, for the one surface that paints it, 30 CSS px on the dark nav bar (see "The site mark") |
| `public/mark-transparent.png` | the owner's transparent 800×800 export, vendored byte-identical (its checksum matches the owner's file) and never hotlinked. The page body no longer fetches it: it is the source the header derivative is made from, and `web_client/test/identity.test.ts` pins its bytes against that repository's own copy. The opaque export was vendored beside it while the hero panel was light; it is no longer fetched either; `app/opengraph-image.png` is the same file |
| `postcss.config.mjs` | the one PostCSS plugin (`@tailwindcss/postcss`), so `style.css` compiles on build |
| `next.config.ts` | the one build setting that is not a default: `poweredByHeader: false`, so the framework's `X-Powered-By: Next.js` banner is not on the page's HTML response |
| `tsconfig.json` | the TypeScript project: `strict`, the `@/*` alias the components import each other through, the Next plugin, and the `.next/types` glob so a generated route type is checked. `npm run typecheck` runs `tsc --noEmit` over it |
| `AGENTS.md` | a note `next dev` writes and re-adds: this framework version's documentation is in `node_modules/next/dist/docs/`, and it differs from what an older Next.js suggests. It is committed with the work rather than ignored, because removing it from a diff only re-creates it |
| `components/ui/button.tsx` | the button primitive (shadcn-style `cva` variants: filled default, tinted secondary, outlined, ghost; three sizes plus the hero's; renders an anchor when given `href`): the bar's CTA and the two hero CTAs, nothing else. The specification is a link drawn as a control rather than a third CTA, and the page renders the `outline` variant for its second hero CTA, so the tinted `secondary` and the `ghost` variants stay in the file only because `scripts/check-contrast.py` measures them there |
| `components/ui/badge.tsx` | the pill primitive: a status beside a card's own name, and a mono caps chip |
| `components/ui/card.tsx` | the card primitive: the two panels under the terminal |
| `components/site-header.tsx` | the bar: the mark, the four in-page routes, the GitHub link and the demo CTA, with the conceal-on-scroll effect and the second scrollable row a phone gets |
| `components/room-visuals.tsx` | the four smaller figures the cards carry — the invite chip, the sample with three carets in it, the guest's tree, the clients — as inline markup and the page's own CSS, with no image, no dependency and nothing fetched (see "The product figures") |
| `components/room-window.tsx` | the hero's room window, and the only place the page types: the line under the carets is written a character at a time, held, and started over, and the invite button copies the link it draws. `animatePlayground` types the line or writes it whole, and a reader who asked for less motion gets the whole line and a still caret |
| `components/setup-tabs.tsx` | the terminal in *Get it working*: the four install routes as an ARIA tab strip with arrow-key movement, one panel each (the inactive ones `hidden`, so the page still carries all four routes without scripting), the note beside each route and the command it copies |
| `components/demo-endpoint.tsx` | the demo's host, with the one control the card needs: the address an editor is pointed at, on the clipboard |
| `lib/use-copy.ts` | the copy state one or more controls share, and the clipboard write with the textarea fallback an origin without the async clipboard needs |
| `lib/selvage.ts` | the published image's reference and the one command built from it, so the two places the page hands a reader a command cannot drift, and the demo's host |
| `lib/utils.ts` | the one shared helper (`cn`: `clsx` + `tailwind-merge`) |
| `package.json` / `package-lock.json` | the only dependencies: `next`, `react`, `react-dom`, `tailwindcss` (+ its PostCSS plugin), `clsx`, `tailwind-merge`, `class-variance-authority` and `lucide-react` for icons, `typescript` and `@types/*`. No Radix, no component library, nothing else without a written reason |
| `.nvmrc` | the pinned Node version for local work and CI (`nvm use` reads it); `package.json` `engines` carries the major (`24.x`), because Vercel only deploys major versions |
| `.gitignore` | what the repository does not carry: the build output, `node_modules`, `.tmp` (the gate's artefacts, its `TMPDIR` included), the generated `next-env.d.ts`, TypeScript's build info, Python's caches, and the sibling worktrees a parallel piece of work builds in |
| `LICENSE-MIT` / `LICENSE-APACHE` | the licence pair the repository is under, `MIT OR Apache-2.0` (see "Licence") |
| `README.md` | this file: what the page is and says, what it must never say, what the gate checks, and the accessibility floor it holds itself to |
| `scripts/check-claims.py` | the claim check: the phrases the page must not carry, each with its reason, and the facts it asserts in the positive — the image tag, the demo instance, the wire version the page says each of them speaks, the disclosure a reader is owed of what the relay still sees, the file the page's corpus counts are pinned in, the identity the extension is published under with the two registries it is on, the hosted tier the page offers and does not run yet, and the word beside each repository in the grid |
| `scripts/check-button-props.tsx` | the button check: renders the button and anchor variants and asserts their props reach the DOM (run by `npm run check:button` inside the gate) |
| `scripts/tsconfig.button-check.json` | the button check's own project, which extends the site's: the same strict settings with `noEmit` off, CommonJS as the module, and the output in `.tmp/button-check`, so the component can be rendered on its own and the check can import what it transpiled |
| `scripts/check-contrast.py` | the contrast check: parses the theme tokens out of `style.css` — including the sample's `selvage-mocha` token colours, the ground the code figure draws them on, and the alpha a peer's selection fill is drawn at — reads the colours the page's own rules paint where a pair is not a token (the window's line numbers, the not-yet-available card, the repository descriptions) out of the same file, reads the token a selection fill sits under out of `components/room-visuals.tsx` and the fills and labels of the button variants out of `components/ui/button.tsx`, reads the nav mark's own pixels out of `public/mark-header.png` (a logotype, exempt from the non-text floor and held only to being visible on its ground), and asserts the rendered pairs sit at or above their floors, with measured ratios (run by `scripts/ci-local.sh contrast` inside the gate) |
| `scripts/check-csp.py` | the policy check: reads the Content-Security-Policy out of `vercel.json` and the served HTML, and fails when the policy would refuse a script, stylesheet, image or font the page carries (run by `scripts/ci-local.sh csp` inside the gate; see "The Content-Security-Policy") |
| `scripts/check-weight.py` | the weight check: reads the served HTML and the bytes on disk, and fails when an image the page body fetches out of `public/` is over its budget or declares a pixel size the file does not have (run by `scripts/ci-local.sh weight` inside the gate; see "The site mark") |
| `scripts/make-mark.py` | the mark producer: derives `public/mark-header.png` from `public/mark-transparent.png` — the master area-averaged to 128×128, premultiplied by alpha, and one 256-entry gamma table at identity, so nothing recolours it — and its `--check` mode re-derives the file and fails when the committed pixels are not that derivation (run by `scripts/ci-local.sh mark` inside the gate; see "The site mark") |
| `scripts/check-csp-browser.mjs` | the browser proof: serves the built page with the headers out of `vercel.json`, drives headless Chromium over CDP, and asserts zero `securitypolicyviolation` events, `window.__next_f` an object, the two fonts loaded and resolving with Geist as the body's family, the header's concealment on scroll and no `X-Powered-By`. Not in the gate (the runner has no browser), and it needs `npm run build` first |
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
| Nav header on dark Mocha | `public/mark-header.png` | the bar is translucent Mocha over the page; the opaque export's baked `#1e1e2e` base would draw a visible box against it, while the transparent glyphs sit straight on the bar. The bar paints it at 30 CSS px, which is what the file is sized for (see below). The export's glyphs are dark — a shaded wordmark whose dark stroke is faint on a dark ground — and the mark is a logotype, which WCAG 1.4.11 exempts from the non-text floor, so this derivative carries the owner's own tones unchanged; `scripts/check-contrast.py` reads the file's pixels and holds its median to a visibility floor instead |
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

The header mark is sized the same way the favicons are, and it is the one surface that carries the
owner's own tones with nothing applied to them. The nav bar paints it at 30 CSS px, so
`public/mark-header.png` is the 128×128 derivative `scripts/make-mark.py` builds: the master
area-averaged down to 128, premultiplied by alpha so the transparent field's white cannot bleed
into the glyph edges, and no colour change after that. 128 covers a device pixel ratio to 4 and
carries none of the master's transparent field. The master is 60,595 bytes; served there it was
26% of everything the page transferred, and a browser resampled it to a 20×9 px monogram without
saying so. The export is a shaded wordmark whose glyph tones sit between `#2d111e` and `#7cc9c0`,
so on `#1e1e2e` the derivative's median ink pixel measures **1.72:1**: the wordmark's dark stroke
is faint on a dark bar. Nothing is done about that here. The mark is a logotype, and WCAG 1.4.11 —
whose 3.0:1 non-text floor this page asserts on every mark drawn from a token — exempts logotypes,
so lifting the derivative to clear a floor the artwork is exempt from would be recolouring the
owner's own work to pass a rule that does not apply to it. A lighter plate behind the mark is the
change that would keep both the artwork's colours and a 3.0:1 mark. The file is 4,554 bytes.
`scripts/check-contrast.py` composites its own pixels over `--bg` and holds the median to a
visibility floor of **1.5:1** — the floor below which a reader cannot see it, and not a WCAG
threshold — printing the measured 1.72:1, so a derivative recoloured darker until it is a smudge
on the bar fails the gate.

The derivative had no producer until now: it was built once by hand with ImageMagick, so nothing
in the tree could reproduce or verify it. `scripts/make-mark.py` is the producer, and
`scripts/ci-local.sh mark` re-derives the file from the master inside the gate and fails when the
committed pixels are not what the master produces. The pin compares pixels rather than bytes: a
zlib release may compress the same raster differently, and the raster is the claim. With no curve
between them the two resamples agree: at 30 px, resampling the derivative and resampling the
master differ on 30 of 1,024 pixels by one level in a channel, which is the rounding of a second
averaging step and nothing else.

What the producer does not reproduce is ImageMagick's resample. `-resize` defaults to a Mitchell
window, which reaches past the box each destination pixel covers and rings a little; the producer
averages exactly that box, which is the one definition of a downscale that needs no knobs of its
own. A derivative built with the window instead of the box would differ from this one on its edge
tones, not in the artwork's colours.

The alternative the review offered — dropping the mark and keeping the wordmark alone — was not
taken because the mark is the page's only image-body surface and `scripts/check-weight.py` is
written around it: a page that fetches no image at all is an exit 2 there rather than a pass, so
removing the mark would have retired a check about image weight instead of answering a question
about tone.

`public/mark-transparent.png` stays in the tree at full size: another
repository pins its bytes, so it is the source of truth rather than a fetched asset. Only the
surfaces that paint the mark are listed above, and `scripts/check-weight.py` holds every image
the page body fetches to a budget so a master cannot come back to one of them by accident.

## The page, and its copy

The page is a product page, not a numbered document: seven parts in order, each one doing a job
the reader can name.

| Part | Its job |
|---|---|
| Hero | the promise, two CTAs, four one-word facts, and the room window beside them: the host's folder down the side, the file the room has open, the line one of them is typing, and the invite link that put them there. The CTAs come **above** the facts because of the fold: four facts, a CTA row and the version line of the order the page carried put the primary button at y≈823 on a 1280×633 screen and nothing but the header's small link in the first one, so a reader met evidence and no action. The CTAs lead with the demo — the fastest thing a stranger can do, with nothing installed — then running it in the editor, which is where the commands are; the header's own CTA points at the demo for the same reason. The specification is not a third button: it is the link that closes *Why a spec*, and nothing on the page presents a link as a disabled-looking control. The four facts are one row of one-word chips — *Sealed*, *Specified*, *Path-scoped*, *No account* — and a check mark each. They were four sentences, and three of those arguments are made below in any case: the relay's disclosure is the panel beside the terminal in *Get it working*, the specification has its own section, and the granted paths are the third card of *See it working*. *No account* is the one the page carries nowhere else, and that is the reason the row is kept rather than deleted: the fact goes with it. The relay's chip leads because what the relay reads and does not read is the claim a reader has to be able to take before the others are worth anything, and it is read against the panel below, where the detail lives — the gate reads the panel, not the chip, for exactly that reason |
| Try → Run → Rent | the three ways in, in the order they cost. *01 Try* is the one card the page draws a live border around: the demo, the host a reader pastes into a client, and the sentence that the instance's terms are non-commercial and cover that one box rather than the software. *02 Run* is the published image as one `docker run`, the wire version it and the demo both speak — `selvage/2`, the sealed one — and a link down to the routes. *03 Rent* is the tier the project does not run yet: the card offers it, the pill on it says it is not available, and the row under it is a plan rather than a control, so nothing on the page offers a hosted room and nothing presents a row as a disabled-looking button |
| Get it working | one server, any client: the four install routes in one tabbed terminal — Server, VS Code, Neovim, Browser — each with the command it copies, the note a reader needs before running it, and the repository it comes from. The strip is the ARIA tabs pattern (the arrow keys move between the four, and every panel is in the document, so the page carries all four routes without scripting), and the routes carry the facts a reader installs by: the published image's command and `ws://127.0.0.1:8080/session`, with the page on the same port; the extension's published identity (`selvage-protocol.selvage`) and the two registries it is on; the Neovim plugin-manager line and `:SelvageHost`; and the demo's address an editor hosts on. Beside the terminal the two panels say what the wire seals and what the relay still sees and still does, and that the host is a peer's signed claim rather than a server fact. The manual a reader wants next — the corpus check, the vector replay, each client's full command list — is the specification link and each repository's README, not a fold on this page; the per-client settings and the hosting routes were cut for the same reason |
| See it working | four cards, each with a drawing of the thing it claims: anyone with the link is in, the carets of three peers in one file, the paths a guest sees, multiple clients on one engine |
| How it works | the four moves in order (host a folder, send the invite, type in the same file, close the window), under the design record's one-sentence workflow. They are the sequence rather than the argument: the grant, the sealed material and the host's signed claim are all made in the sections above, where a reader meets the thing they are about. The fourth move keeps the two facts a reader closing a room needs: the room ends after a short countdown, and a dropped connection does not end it |
| Why a spec | the wedge: language tooling has the Language Server Protocol and debugging the Debug Adapter Protocol, document sync has `y-protocols`, and the session layer is unspecified, so every collaborative tool decides those for itself. The wire corpus's counts appear here once, as the evidence they are, with the file that pins them, and the section then hands the reader the specification itself, under a comparison card that sets the session layer beside the three layers that already have one. The repository grid below it is the page's own account of what exists: a word and a link for each repository, and a dashed card for the clients nobody has written yet. The peer corpus is no longer counted on the page: its counts backed the signed-host sentence, which the panels in *Get it working* still make, and one sentence of evidence under the specification is what the page's word budget buys. The heading says what the page does rather than denying what the hero's chip states: it used to read *The session layer has no specification*, which contradicted that fact for anyone skimming the two |
| Footer | the licences, the page's own privacy line and the contact address, nothing more |

The page used to end on a two-column ledger of what is built and what is not. On a product page
that reads as a to-do list, so it is gone, and its honest facts now sit where they do a job rather
than in a list: *Get it working* opens on the shape of the thing (you run the server, the invite link is
how somebody joins you), the wire version sits under the command a reader can run, and the tier the
project does not run yet is the third card of *Try → Run → Rent* rather than a line in the ledger. What the ledger
spelled out is recorded where it is a decision or a gap: the design record's non-goals for v1
(`DESIGN.md` §11, in `selvage-protocol/ai_notes`), the
specification's `NOTES.md` for what the prose leaves open, and each repository's own README for
what its checkout does and does not do.

No section carries a number. The `01`…`07` counters in front of every section, the privacy notice
and the licences included, were the clearest signal that the page was a document rather than a
product, and the numbers the page carries now belong to things rather than to sections: the three
cards of *Try → Run → Rent* and the four moves of *How it works*. The headings step up to a display
size instead (the `h1` `clamp(36px, 4.6vw, 54px)`, the `h2` `clamp(26px, 6vw, 32px)`), the standing
lede-and-checklist hero is gone, and the install guide that was a third of the page is four routes
in one terminal.

The prose still descends from the static page's, and every sentence is a paraphrase of an
already-audited true sentence or framed as direction. Two sentences differ on purpose: the static
page's "loads no JavaScript" is false once Next.js serves the route, so the page says it prerenders
to static HTML and names what the browser fetches from this origin instead: one stylesheet, the two
fonts, the mark in its header, the favicon set and the framework's runtime scripts. The sentence used to name one
stylesheet and a favicon and to leave the mark out, which is the kind of inexactness a
privacy-adjacent sentence cannot afford; and the waitlist form is gone, so
the privacy notice names its controller and collects nothing instead of carrying blanks for a
mailing service.

The must-not-say table below still binds every line. Three rows moved with what is now true:

- **The browser client, and the instance that serves it.** `web_client`, Monaco in a page, is
  served at one public origin now — the demo — so the page may name a route a reader can follow
  and the patterns that denied one are gone with the reason that produced them. The client hosts
  as well: on Chrome or Edge a page its own server serves starts a session from a folder the
  person picks, which is the demo's shape and the one way into a room with no editor running. The
  page makes neither claim about the page it serves: the demo card opens the demo and says guests
  join from the invite link with nothing installed, and the Browser route points an editor at the
  instance's address. What the filter holds instead is what is still false: hosting in a browser
  the reader may not be holding
  (Firefox and Safari have no directory picker, so they join and cannot host), joining without the
  invite link a host copies, and the project's own site as a place to join a room. The stale
  denial ("nothing runs in a web page") stays caught, because the page carried it once, and so
  does the unqualified "host a session in the browser", which is the shape that overclaim takes.
  The `clean` fixtures are the honest sentences — the hosting sentences, the demo origin itself,
  the sealed-material readings and the peer's signed host claim — so a widening that forbids the
  truth fails the gate.
- **The demo instance.** It runs, so "try the live demo" and the install-free page are truth and
  the entry that denied the instance is replaced by the overclaim that came with one: a demo
  described as a service. Its rooms are in memory on one small box, it keeps no work, and its terms
  gate it to personal and evaluation use. A second entry, new with the demo, holds the mistake the
  section makes easy: the instance is non-commercial and the software is not
  (`MIT OR Apache-2.0`, `FSL-1.1-MIT`, `CC-BY-4.0`), so a "non-commercial licence" sentence is a
  licence nobody granted.
- **The corpus counts.** Still exactly the numbers `specification/schema/validate.py` pins, and the
  two layers are pinned apart because they are two corpora: the wire layer's 24 vectors, 33760
  frame checks and 8387 assertions, and the peer layer's 26 vectors, 221 checks and 74 assertions.
  The wire layer's counts appear in one place, as the evidence for the specification, and the page
  does not carry the peer layer's. A number before `vectors`, `frame checks` or `assertions` has
  to be that layer's pin, and the peer layer's count is written with the layer named — `26 peer
  vectors`, `221 peer checks`, `74 peer assertions` — because `26 vectors` alone is read as the wire
  layer's count and fails. The window between the number and the word is any two whitespace-separated
  tokens (`\S+`, not `\w+`, so a hyphenated word in front of the noun is still a word in front of
  it), which is what the page's "conformance vectors" and "wire vectors" both need.

## The product figures

The page shows the product instead of describing it, without an image, a dependency or a
third-party request: `components/room-window.tsx` draws the hero's window and
`components/room-visuals.tsx` the four smaller figures, all of them from inline markup styled
by `style.css`. The hero figure is the whole window at once: the host's folder down the side, the
file the room has open, the line one of them is typing, and the invite link that put them there.
Two carets travel inside that text — a 2 px bar in the peer's colour at a column between two
characters of the line, the peer's name in the window's own gutter lane on that line, and a
quarter-alpha fill behind what one of them holds — and each card in *See it working* carries one
smaller drawing of the thing it claims, the middle one with three carets in it.

Seven rules hold it together:

- **The invite draws a link that works.** The strip in the window's footer and the chip *See
  working* carries both read `?room=k7m2&token=4f9c#k=…`: the query the page takes and the fragment
  the keys travel in, the shape `PROTOCOL.md` §5.1 fixes. They used to stop at the query, which is
  the link shape that cannot seal a room; the chip teaches the shape the clients hand a guest. The
  chip is one row, and the sample is one line: the fragment used to break under the query at a
  `<wbr>`, which made the chip a two-row block, and the `invite link` label is gone because with it
  the chip holds the query or the fragment on one row, not both, in a card 345 px wide. Nothing is
  lost either way: the lead above the card's chip names the link, and the window's own footer
  carries the same one.
- **It is an illustration, and it says so.** The drawings are `aria-hidden` and the card beside each
  one is the sentence it illustrates; the window's side and its code pane are hidden the same way,
  and the one control in it is the button that copies the invite, labelled for a screen reader. Each
  code sample is a short function against the client crate's own API, with the `use` line left out, and
  each peer's caret is drawn where the browser client draws it (`renderCursors` in
  `web_client/src/browser/editor.ts`): a 2 px bar at the caret's own range, a badge in the left
  gutter on the line the caret is on, and a fill behind the characters the peer holds. A name is
  never written into the text of a line: inside Rust it would read as syntax, which is a claim
  about the source that is not true — so it stays in the lane beside the line number, where that
  client's glyph-margin badge goes.
- **The open file is named twice, and nothing marks it.** The file the room has open is written in
  the guest's tree and in the window's own sidebar, both times in the figure's text colour (`--fg`).
  The tree used to carry a dot beside the name, the drawings' only shape that was not a peer's, and
  the two readings a small filled shape invites — "this file is open" and "this peer is here" — are
  not the same claim, so the name in the figure's own colour carries it alone.
- **The sample is coloured the way the editor colours it.** The token colours are the browser
  client's own `selvage-mocha` theme (`defineTheme` in `web_client/src/browser/main.ts`): comment
  `#868ca2`, keyword `#cba6f7`, function `#89b4fa`, string `#a6e3a1`, number `#fab387`, type
  `#f9e2af`, on the sample's ground and in the body colour `#cdd6f4` otherwise. Punctuation has no
  rule in that theme, so it
  keeps the body colour here too. The samples are fixed and short, so each token is a span written
  by hand in `components/room-visuals.tsx` — no highlighter, no dependency, no parser.
- **Every figure is one band.** The grid is `repeat(auto-fit, minmax(min(100%, 250px), 1fr))`, so
  the four cards are four columns at the shell's width, two or three in between, and one under
  390 px; each card is a column of the drawing's band and the sentence, and the band is a fixed
  `8rem` high — enough for the tallest drawing — so the four leads sit at one height in cards the
  grid has already made equal. A band wider than its drawing centres it, and the code sample's own
  four lines at 12 px on a 22 px line-height do not move with the font, because both numbers are
  set.
- **The drawings are `aria-hidden`; the cards' own sentences are not.** A screen reader hears the
  sentence that describes the room, not the code in it.
- **No inline `style`, no `<style>`, no font from a third party, no external image.** The policy
  in `vercel.json` refuses the first two outright and admits this origin's fonts alone through
  `font-src 'self'` (see "The Content-Security-Policy"). Every colour in a figure is a class in
  `style.css` or a theme token, which is also what lets `scripts/check-contrast.py` measure the
  figure and the glass card it draws on.

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

Production deploys on `main`, at **https://selvage.dontblameme.dev**, and every branch and pull request gets a preview URL. That is all
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

### Releasing it

A release here is a tag and a GitHub Release, and nothing else: there is no release artefact to
build or attach, no image and no registry, and Vercel serves the page from `main` without reading
tags. The deployment does build — `next build`, on Vercel, from `main` — but that build is the
deployment and not a release.

So there is no release workflow. One would only be `git tag` and `gh release create` behind a
button, and the version assertion the other repositories' release workflows carry would have
nothing to protect here: `package.json`'s version is a private, unpublished manifest that no
deployment consumes.

The tag is `package.json`'s version with a `v`, and an annotated tag is what the other
repositories' release runs create, so it is made the same way by hand:

```console
$ git tag -a v0.4.5 -m v0.4.5
$ git push origin v0.4.5
$ gh release create v0.4.5 --title v0.4.5 --generate-notes
```

The tag is a marker on the page's history rather than an input to anything. Other repositories tag
what they build and attach it to the release; this one has nothing to attach.

## The Content-Security-Policy

The header is `vercel.json`'s, applied by Vercel:

```
default-src 'none'; script-src 'self' 'unsafe-inline'; script-src-attr 'none'; img-src 'self' data:; style-src 'self'; font-src 'self'; form-action 'none'; base-uri 'none'; frame-ancestors 'none'
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

`font-src 'self'` is the one directive that does not exist for a script or an image: a font fetch
falls back to `default-src` like any other, so without it `default-src 'none'` refuses the two
families `next/font` self-hosts and a browser silently paints the fallback stack instead. `'self'`
is enough because the glyph files arrive from `/_next/static/media` on this origin, and no request
is ever made to a font host.

What the policy still refuses: every origin that is not this one, `eval`, an inline `on*`
attribute, a form submission, a `<base>` that would retarget the page's relative URLs, framing,
every resource kind the page does not name, and every font but this origin's. `data:` is allowed
for `img-src` alone.

Two pieces of evidence, with their limits:

- `scripts/check-csp.py` runs in the gate over the HTML the production server renders, and over
  the HTML its not-found route renders, because that route is a page the site serves and the
  policy has to permit it too. The framework's own 404 document is styled with a `<style>` element
  and four `style` attributes, all five of which `style-src 'self'` refuses; `app/not-found.tsx`
  is styled from `style.css` instead. The check takes the policy *from* `vercel.json`, not a copy
  of it, and decides every script, stylesheet, image and font against the directive that governs
  it, following the fallback chains a browser follows — a font fetch falls back to `default-src`
  like any other, and the `<link rel="preload" as="font">` the page carries is what names one
  that is coming. The policy as it read without `script-src` and the one as it read without
  `font-src` are both fixtures of its own, so it fails on the defect it was written for and on
  the quieter one a missing `font-src` is. It is a model of the policy, not a browser, and a
  source expression it does not model is an error rather than an assumption.
- A real Chromium run against the built page served with these exact headers, kept runnable as
  `scripts/check-csp-browser.mjs`: it applies the `headers` block out of `vercel.json` through a
  local proxy (`next start` does not apply it, only the host does) and asserts zero
  `securitypolicyviolation` events, `window.__next_f` an object, the header concealed
  (`translate: 0px -100%`) at `scrollY` 900 and back at 300, and no `X-Powered-By`. It is the
  only thing here that can see the fonts: both families have to be loaded and resolve, and the
  body's computed family has to be Geist rather than the stack under it, because a refused glyph
  file paints the fallback in the same layout and reads as a typographic choice. A violation
  naming a font is reported as what it is before the run fails on the count. It then
  requests a path no route claims and asserts the `404` it renders carries no violation either,
  which is the assertion that fails on the framework's own 404 document. Point
  `VERCEL_JSON` at the policy as it read without `script-src`, or at the one as it read without
  `font-src`, and it fails, which is checked
  rather than assumed. It needs a browser the runner does not have, so it is not in the
  workflow: `npm run build && CHROMIUM=/path/to/chromium npm run check:csp-browser`.

Neither of them can see the deployed response headers. If Vercel stops applying the `headers`
block, or applies it to a path this policy was not written for, nothing in this repository
notices.

## Privacy: controller and no collection

One thing is fixed, and one thing is gone.

**The controller.** The privacy notice names
[`selvage-protocol`](https://github.com/selvage-protocol), the GitHub
organisation, as the controller, and names the address to write to
(`selvage@dontblameme.dev`) in a paragraph of its own. Only the owner could fill
that blank, and now it is filled.

The notice keeps two statements apart, because they are about two different
things. The page's own collection is nil, and that is what "collects no personal
data of its own" scopes; the address is where mail comes back, so the paragraph
that carries it says that the controller receives the sender's address and keeps
it only to answer. A notice that invited mail without saying so would have been
the implied half again.

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
the gate builds, starts the production server, fetches `/` over HTTP and checks that HTML. It reads
the prose the page carries in its `meta` attributes — `description`, `og:*`, `twitter:*` — as text
beside the visible text, because a link unfurl prints that prose verbatim and the tags themselves
are stripped from the body: five planted overclaims in `og:description` used to pass the scan
unseen, on the surface a person deciding whether to paste a link meets first. It also
asserts facts in the positive — the image tag, the demo instance, the wire version the page says
each of them speaks, one disclosure, the file the corpus counts are pinned in, the identity
the extension is published under with the two registries it is on, that the hosted tier the page
offers is not available yet, and the word beside each repository in the grid — described just
below.
**It is a filter, not a proof.** It cannot see meaning: a false claim in different words, a
synonym outside the list, a superlative, an unbacked sentence or a wrong number the list does not
pin all pass it. A green gate means the known wordings are absent, nothing more. The reasons are
summarised here so that the constraint survives without the file that produced it.

`scripts/check-claims.py` asserts facts in the positive, because a phrase list cannot reach
them. The first is the image tag the happy path hands a reader: the check pins
`ghcr.io/selvage-protocol/selvaged` to one version, requires every reference the rendered page
carries to name it, and then asks the registry for that tag — anonymously, with no credential in
the request, because no account is the point of the command. It compares the **per-platform
manifests' layer digests**, not the index: a platform entry only states that a slot is *labelled*
arm64, and `selvaged:0.1.1` proved the difference by publishing both legs around the amd64 binary,
every layer digest identical across the two. `0.1.0` carries the same defect and `0.1.2` is the
fix; neither broken tag will be retagged or removed. The second is the
demo instance: the page points at one host, every reference to that host has to be one of the three
the page may carry, a link has to point at the instance itself, and `https://selvage-demo.dontblameme.dev/meta`
has to report a `selvaged` server offering a wire version the page names. The references are read
from the visible text *and* from the links' destinations, because a label and the place it goes
are two claims: an anchor labelled with the demo host whose `href` points elsewhere passes a
text-only scan. The allowed references are the origin, its `/terms`, and the `wss://` origin with
**no path**, because both clients append `/session` to whatever address they are given (`sessionUrl`
in the engine they vendor), so the page naming `wss://…/session` would hand a reader an address that
gets a second `/session` appended and is refused. The check asserts that path separately, by
asking `https://selvage-demo.dontblameme.dev/session` for a plain `GET` and requiring a **4xx carrying
the server's own JSON**: the path has to reach the server the page names, a redirect or a `5xx` must
not stand in for it, and the proxy's own `404` page is `text/html`. Which `4xx` the server picks is
its business, and pinning `404` would redden this gate for a change in `selvaged` that makes no
sentence on the page false. The **WebSocket upgrade itself is not asserted**, because the host's proxy answers a
hand-rolled upgrade from a runner's egress with `403` and a request the proxy refuses asserts
nothing; the upgrade was verified by hand, from a client the proxy accepts, and that is recorded in
the findings rather than claimed here. It also asks `/` for a `200` and a `text/html`, because the
browser row tells a guest the demo serves the page and the proxy's own `404` is `text/html` too, so
the media type alone would let a dead page satisfy it. It then reads the bytes `/` answered with and
requires the host card's own element in them, because the browser row also says a session can be
started from the demo's page: the card is markup the client's shell carries, so it is in the served
bytes whether or not the bundle's script has run, and a demo rolled back to a guests-only release
is that sentence going false with nothing else to say so. What the demo half no longer does is
compare the instance's release to the page: the page named one, a reader had no use for it, and it
is gone from the section. The image half still ties the page's `docker run` to the registry: the
tag it names has to be `PUBLISHED_IMAGE_TAG`, and the registry has to serve that tag. The wire version is held
to what the instance offers rather than to a constant here, because the page owns the version it
names and the instance owns the version it speaks. **That assertion couples the site's gate to a
running box**: a demo that is down or moved, a `/session` the proxy no longer routes to the
server, and a box whose `/` is not the page all fail the build, because a page claiming a demo that is not there is
the defect it exists to catch. It sends its own user agent, since the host's proxy answers `403` to
an interpreter's default signature. The image half needs egress to `ghcr.io` and exits 2 rather
than passing when it cannot reach it; the demo half does the same for an instance that does not
answer at all, and exits 1 when the instance answers something that disproves a sentence.

The next positive assertion binds the page's sealing claim to the one wire version, and it exists
because the paragraph that makes that claim sits directly under a `docker run`: a reader can take
the claim and the command together and get a server that carries the room through it in the clear.
So the page has to say, in one sentence, which wire the image under the `docker run` speaks and
which wire the demo speaks, and may name no other version. The demo's half is measured — the
version the page names for
it has to be one `/meta` offers — and the image's half is read from `IMAGE_WIRE_BY_TAG`, because no
registry says what wire version a binary speaks. A tag with no entry in that map fails the check,
so a tag a release points at a different wire has that wire declared in the same wave; the page's
sentence is checked against that declaration and not against a default. The one-wire rule is what
catches the other direction: a second version named on the page is a claim about a version this
protocol does not have, and a page that says the wire is unreleased — or that hands a reader the
plaintext wire's command — tells a guest their room is in the clear when it is not, which is the
same defect with the sign the other way round.

The relay-visibility disclosure is required rather than permitted, and it exists because the
`clean` fixtures can only prove the phrase pattern does not reject the paragraph, not that the page
carries one. The check requires the rendered page's visible text to state each of the four facts
the paragraph is there to state — the room's existence, its membership, the display names, and the
sizes and timing of what moves — as a small pattern of its own rather than the sentence, so a
rewritten paragraph that keeps the facts passes and one that drops a fact fails. Two of the four
are phrased as the disclosure's own sentence, because the page states the same two nouns a second
time in *The session layer is written down*: matched loosely, that earlier paragraph supplied
them for a page whose disclosure had been deleted, and a rewrite that dropped those two while
keeping the other two passed with them gone. Deleting the paragraph now fails the check on all
four. The facts are read from the page's own `docker run` onwards, and not over the whole page:
the hero's second fact used to state the same four facts in the same wording, and it is above the
command, so a page-wide scan let the hero satisfy a check written to require the paragraph —
deleting the paragraph passed with the hero standing in for it, which is the mutation that added
the bound. The hero states them in a word each now (*Sealed* for the relay's half), and the bound
stays: a hero line that states a fact in full still cannot stand in for the paragraph's place,
which is under the command a reader can take it together with. It asks no network.

The browser guest's own residual is the one disclosure the page carried and no longer does: a
guest who opens the page the room's own server serves trusts that server for the client code as
well as for the relay, and the installed clients are not in that position. Nothing here requires
it, and no phrase forbids it, because the page's remaining sentences about the server are about
the relay — the bytes it carries, the shape it can see — and the shape a browser guest is in is
not one the page describes any more. What the phrase list above still holds is the overclaim in
that direction: that nobody else can read the room, that the server learns nothing, or that the
relay is blind.

The extension's publication is asserted the same way, and it is the one entry here that was a
prohibition turned round. The page used to be forbidden the words "marketplace", "open vsx" and
"gallery", on the ground that publishing the extension was a non-goal (`DESIGN.md` §11:
"marketplace publication until it works with a friend"); the owner retired that non-goal, and the
extension is published as `selvage-protocol.selvage` on the VS Code Marketplace and on Open VSX,
which are the two publish steps in `vscode_client/.github/workflows/release.yml`. So what is
required is now the truth and what is forbidden is the false direction: the identity and both
registry names have to be in the row, every registry-shaped word the page carries has to be part
of one of those two names — a third registry, or "the extension gallery" without saying which,
fails — and any link the page carries to a listing has to be one of the two, because the retired
`selvage-protocol.selvage-client` listing is still live and still linkable by mistake. The row
also has to say what an install is: an install is the client and not a server, and a session pairs
with a `selvaged` the reader runs. That last fact is required rather than left to the phrase list
because the registry names alone would read as a session, and "on a server you run" is not the
sentence to read — the hero carries it. It asks no network, and that is deliberate: the page's own
link check reaches every URL it carries, and the Marketplace's listing URL answers `404` until the
release that publishes the extension has run, so requiring a listing link here would redden this
step for a release that has not been dispatched. What the check proves is that the page agrees
with the release workflow about the identity and the two registries — not that either registry
answers.

The hosted tier is required the same way, and it is the one card on the page that offers something
the project cannot hand over yet. The card, the pill on it, the sentence saying who would run it and
the row that is a plan rather than a control are read one pattern each, so a rewrite that keeps the
fact passes and a card that loses its status fails. The phrase list's `now available` entry can
only catch the other direction: a page that reads as an offer with nothing saying it cannot be
taken is the page this is for. It asks no network.

The repository grid is required the same way, and it is the page's own account of what exists. Each
row's word is pinned where the row is: the specification is the source of truth, the reference
server and the two clients the project publishes itself are available, and the extension is
published. A row's name, description, pill and destination are one claim, read together from the
row's own anchor rather than from the page's text, so a row that links a different repository fails
even though the page still carries every name and every word. That last word is the one claim here
about a registry rather than a repository, so it
cannot be read apart from the identity and the two registries above it: the page that carries the
word has to carry `selvage-protocol.selvage` too, and a grid that changed one without the other
fails. Every repository the grid names has to be linked, so a word about a repository hands a reader
something to check, and every repository the page links has to be one the grid names, so no row and
no source link beside the terminal points at a repository the project does not have. The design's
sixth row, `jetbrains_client`, is the worked example: `github.com/selvage-protocol/jetbrains_client`
answers `404` and the organisation carries no such public repository, so the row was dropped rather
than linked, and the destination rule is what keeps it — or any other repository that is not there
— off the page. It asks no network either.

| Must not appear | Why not |
|---|---|
| "open source" of the server or the project | The server binary is `FSL-1.1-MIT`: source-available, not OSI-approved, free for non-competing use and under MIT two years after each release. The specification and the clients are the open ones, and the page names their licences instead of reaching for the phrase |
| "SSP" | The abbreviation is taken by stack-smashing protection and by supply-side platforms. The protocol is the Selvage Session Protocol, written out |
| `salvage/1`, `salvage/2` | The wire version is `selvage/2`. "Selvage" is heard as "salvage", which is why the name is written out in words rather than shortened: the `<title>` opens with the project's name, the nav carries the wordmark over the hero's `h1`, and every wire version the page names is spelled `selvage/2` |
| "the session layer has no specification" | The page's own hero chip says the opposite in one word — *Specified* — and the section argues it. The layer every collaborative tool decides for itself is the subject, so a heading that reads as a denial of the fact a skimmer has just met is a contradiction rather than the argument |
| "nobody else can read it", "no one else can see it", "only the people in the room", "the server knows nothing", "fully encrypted", "zero-knowledge", a bare "end-to-end encrypted" or "e2ee", "the relay is blind" | The relay is sealed, not omniscient: it reads no text, no cursor, no file name and no role, and the keys are in the link a human pastes, but it still reads a room's existence, its membership, the display names and the sizes and timing of what moves, and it can drop, delay, reorder or end any room. Each of these wordings claims more than the wire's sealing buys, and the list alternates the subject and the verb because the paraphrase is how the sentence is written first: "no one else can see it" is the same claim as "nobody else can read it". The window between the subject and the verb is the sentence's and not a word's — 64 characters, the same unit `clause_around` reads a permit from — because "the server relays the room as ciphertext and learns nothing" puts the claim 35 characters after its subject, which a 24-character window passed: that evasion is a fixture now, and it fails the gate. No version of this protocol has less than that: `selvage/2` is the one wire version it has, and every release the page hands a reader speaks it. An "end-to-end encrypted" that names what stays visible in the same sentence is backed and stays legal; one that names it and denies it — "so the relay learns no membership and no names" — is the unqualified claim with a disclosure's noun in it, and the permit is cancelled for it |
| "the server cannot read" (unqualified) / "the server cannot read the room" / "the text never reaches the server" / the host reading, and the membership one with it | The relay is sealed, not omniscient: it reads no text, no cursor, no file name and no role, and it cannot forge, mis-attribute or replay a frame, but it still reads a room's existence, its membership, the display names and the sizes and timing of what moves, and it can drop, delay, reorder or refuse frames and end any room. A claim about named, sealed material is specific and backed — the same sentence has to name it, which is what the pattern reads rather than the determiners in front of the verb — and unqualified it must not appear, nor may the room itself or the membership be the object. A sentence that names sealed material and claims *everything* is not specific either: "the server cannot see anything, not even your text" carries a permitted noun and the widest object there is, and the permit is cancelled for it. "It cannot tell who is host" is forbidden too, and the reason is a measurement rather than a reading: `CANONICAL.md` §6.1 puts `kind` in the clear and `PROTOCOL.md` §7.1 makes `kind = 1` the host's own frame, so a relay that routes a room reads one clear byte and knows. What the page may say is what the threat model supports — the host is a peer's signed claim, and the server cannot seat a host, prove one or take the role |
| hosting from a page in any browser, a room with no invite, the project's own site as a client | The browser client is published and it hosts: on Chrome or Edge a page the room's own server serves starts a session from a folder the person picks, which is the demo's shape. The page does not make that claim itself: the demo card opens the demo and says guests join from the invite link with nothing installed, and the Browser route points an editor at the instance's address. What is not true: hosting in any browser (Firefox and Safari have no `showDirectoryPicker` and can join but cannot host), a page no Selvage server serves offering it (the client says why instead of offering a control that could only refuse), joining without the invite link a host copies, and the project's own site as a place to join a room (it is a landing page). The stale denial "nothing runs in a web page" stays caught too, and so does the unqualified "host a session in the browser", which is the shape that overclaim takes |
| file create, rename or delete | The room carries no file mutations: nothing on the wire adds, renames or removes a path, and the only write to the host's working copy is the host's own. A guest's keystroke reaches the folder through the host's client, which is what writes out the text the room settled on, and a Neovim guest's mirror materialises the granted paths |
| the server route denied: no image to pull, nothing to install on the server | The reason this entry used to give — that no Dockerfile, compose file or service unit exists in any repository — is false now. `ghcr.io/selvage-protocol/selvaged:latest` is published and pulls anonymously, `reference_server/compose.yaml` runs it, and `reference_server/packaging/systemd/selvaged.service` installs the binary. The pattern used to forbid the word `docker` itself, on that stale reason; it holds the denial of those artefacts instead, which is the sentence the page carried |
| a stable 1.0 | The wire version is `selvage/2`, and the releases are 0.x. No corpus line puts the design at 0.x. The pattern's lookbehind keeps a number inside a tag out of it: `2.1.0` carries `1.0` as a substring, and naming a tag is describing an artefact rather than claiming that 1.0 exists |
| a second implementation, or interoperability | There is none. The Neovim client drives a byte-identical copy of the same engine, so nothing yet shows a client built from the prose alone agreeing byte for byte with the Rust one |
| "the extension is unpublished", or a registry it is not published on | The extension is published as `selvage-protocol.selvage` on the VS Code Marketplace and on Open VSX, which are the two publish steps in `vscode_client/.github/workflows/release.yml`. The entry this replaces said publishing was a non-goal until the extension worked with a friend (`DESIGN.md` §11); the owner retired it, and the rule that replaced it is narrower and runs the other way: both registry names are required on the page, every registry-shaped word that is not one of them fails the gate (a third-party marketplace, "the extension gallery" named without saying which), and so does a link to a listing the release does not produce. The retired ID's listing is live and linkable by mistake, which is what the destination half is for |
| "guests are read-only" or "view-only" | The design inverts it: read-only scopes the host's filesystem, never the shared buffer, and every holder of the invite edits the session CRDT. Saying otherwise would be a lie about the product's central idea |
| "your code never leaves your machine" | Document payloads travel through the server to the peers that ask for them, and they are sealed in `selvage/2` but still leave the machine. What is bounded is the grant: the paths the host enumerates, and the reads it serves from inside the granted root. "Only the people in the room" is false whatever the version: whoever holds the link can read the room, its fragment included |
| invented proof: screenshots, testimonials, user counts, a production deployment, a demo dressed as a service | There is no recording, no user count, and no commercial deployment behind the demo: it is one small box with in-memory rooms, gated to personal and evaluation use, and the site's own origin is a deploy of this page rather than of the protocol. The demo is named as what it is, which the entry on it enforces: no "free demo", no room that persists, no team-sized instance. The one image the page carries is the project's own site mark (see above), not proof of anything |
| a claim of priority ("the first protocol to specify …") | The design record surveys prior art (Eclipse Open Collaboration Tools and others). The project's claim is that the session layer is unspecified, not that this is first |
| a non-commercial licence, or software described as non-commercial | The instance's terms are non-commercial; the software's licences are not. The workspace and the clients are `MIT OR Apache-2.0`, `crates/selvaged` is `FSL-1.1-MIT` (which forbids offering it to others as a competing commercial product or service), and the specification's prose, schema and vectors are `CC-BY-4.0`, so the demo section says what it may not: that the two are different statements about different things |
| a corpus number other than the pinned one | The counts are constants in `specification/schema/validate.py`, layer by layer: the wire corpus's 24 vectors, 33760 frame checks and 8387 assertions, and the peer corpus's 26 vectors, 221 checks and 74 assertions. Any other number is a claim the corpus disproves, and each number is pinned against its own layer's constant, so neither layer's count can be paid by the other's |
| a third party seeing the room | The relay is sealed, so the operator and the network path can see the room's existence and shape, and not its text, its file names or its roles. Only the page's own weak reading (no third party's cloud holding the room) is backed |
| a bare "no cloud", qualified or not ("no cloud in between" included) | A self-hosted server can itself run on a cloud VM, so only the weak reading is backed: no third party's cloud holding the room. The backed reading is the hero's own "No third party's cloud holds the room", which names whose cloud it is about |
| a proven cross-editor pairing | The first cross-editor session has run. The design notes' hand-run proof (2026-09-17) passes grant, cursors and follow in both directions, but its concurrent-edit step falls short by one trailing-newline byte, so byte-identical replicas across the two editors are not demonstrated. State what the clients are built to do rather than that it is proven |
| a speed adjective (instant, real-time, lag-free) | No performance data exists anywhere in the corpus |
| an ease claim (takes seconds, one-click, just works) | The image, the compose file and the systemd unit all exist; no ease claim around them is backed, because no install time, start-up time or latency has been measured or recorded anywhere in the corpus |
| an only-machine claim (untouched by the network) | Document payloads travel through the server to the peers that ask for them; the grant bounds which paths are served, not which machines code touches |
| a "live" / "now available" status | One small demo instance runs and there is no hosted service and no launch: a status reading "live" or "now available" sells the demo as a product. The honest status the page carries belongs to the hosted tier's card — *not available yet* — with the release and the wire version named under the command a reader runs, and the specification called a draft where it is offered |
| SaaS-creep words (sign in/up, get started, download, pricing) | No accounts exist, so nothing can be signed into; no package exists to download and no price exists to show. The page offers the specification to read and a server to run |

Four things the check cannot make mechanical, and which a reader of a change has to hold:

- **A number on the page has a home.** The counts the page shows (the wire layer's 24 vectors, 33760
  frame checks and 8387 assertions; the peer layer's 26 vectors, 221 checks and 74 assertions are the
  ones the check pins if they appear) are
  the constants `specification/schema/validate.py` pins; when the corpus moves,
  the page moves with it. The commands are the ones the repositories' own READMEs document.
- **No adjective does the work of a fact.** If a sentence could be true of any project, it does
  not belong on this page. "Flagship" was one: it says nothing a reader can check, and the
  sentences that carried it say what the artifact is instead.
- **Nothing a reader cannot check.** The footer's framing sentence used to say the page's framing
  follows the project's private design record, which no reader can look up; the licence facts
  beside it can be checked and stayed.
- **A false claim in other words.** The check matches a list of known wordings, so a synonym, a
  paraphrase or an assertion the list does not know about passes it. Green means those wordings
  are absent; it does not mean every sentence was checked against the corpus.

## The live origin

The page is live and public at **https://selvage.dontblameme.dev**, served by Vercel with the
three headers above. That origin is the page's home. `selvageprotocol.com` is **not registered**, and
registering it is not being pursued: nothing here is waiting on a domain.

What that decides:

- **One origin, named once.** `app/layout.tsx` holds it in `LIVE_ORIGIN` and nothing else in the
  page names a host. `metadataBase` resolves the file conventions' paths against it, so `og:image`
  and `twitter:image` read a URL that resolves,
  `https://selvage.dontblameme.dev/opengraph-image.png`, instead of the
  `http://localhost:3000/…` a local or preview build published while the layout had no
  `metadataBase` at all. `check-csp.py`'s `DEFAULT_ORIGIN` names the same origin.
- **`rel="canonical"` and `og:url` name that origin too.** Both are written from the same constant,
  so the document carries `<link rel="canonical" href="https://selvage.dontblameme.dev"/>` and
  the matching `og:url`, and a card unfurled from a branch preview names the same URL and image as
  production. Moving the page to another origin is one constant, and the two tags follow it.
- **The title, description and `og:title`/`og:description` are the page's own words, in the longer
  form a crawler and a card unfurl want.** The title is the project's name in front of the hero's
  own sentence; the description is the same account at more length — one Rust binary you host holds
  the room and an invite link is the whole permission, three clients on the same file, no account
  and no third party's cloud holding the room — with the specification clause after it. It has to
  agree with the lede, and it does: the lede is the shorter statement of the same two claims.


## The gate

```console
$ scripts/ci-local.sh              # typecheck, build, button, contrast, mark, claims, csp, weight, links, lint
$ scripts/ci-local.sh typecheck    # tsc --noEmit
$ scripts/ci-local.sh build        # next build
$ scripts/ci-local.sh button       # render the button/anchor variants and assert their props reach the DOM
$ scripts/ci-local.sh contrast     # the theme token pairs at or above WCAG AA, and the nav mark's own pixels at its visibility floor
$ scripts/ci-local.sh mark         # re-derive the nav mark from the master and compare it with the committed file
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
that reintroduces a false positive fails it too, and those fixtures include the sealed-material
readings the specification itself uses and the peer's signed host claim. The scan reads the prose
in the page's `meta` attributes beside the visible text, because a link unfurl prints it. It also
requires one disclosure in the scanned file: the relay-visibility facts, each as its own pattern,
so the paragraph cannot be deleted while the fixtures stay green. The corpus counts are required
the same way: every
count the scanned pages show has to name the file that pins it in the sentence the number sits in
or the one after it, because a number with nowhere to check it is one a reader takes on trust, and
the peer counts were the pair that named nothing. The scan reads every count in every file it was
given — a rule that returned on the first cited page, or the first cited number, would let a later
one carry a number nobody can check — and it fails when it reaches no count at all, rather than
reporting a page that states nothing as a page with nothing wrong. Both spellings the number rules
accept are read: `24 conformance vectors` and `24 wire vectors` are one pin, and a citation rule
that matched one of them would leave the other unguarded. The extension's publication is required the same way —
the identity, both registries, and what an install is and is not — and it is the one rule here
that also forbids: every registry-shaped word on the page has to belong to one of the two
registries the release publishes to, and a link to a listing has to be one of the two the release
produces, so a page offering the extension from "the extension gallery" or from somebody else's
marketplace fails rather than passing on the two names it also carries. It asks no network, and
why is in the section above. The hosted tier the page offers and does not run yet is required the
same way — the card, the pill on it, the sentence saying who would run it, and the row that is a
plan rather than a control — and so is the repository grid, where each row's word is pinned beside
the row, the `published` one against the identity the release publishes under, every repository
the grid names against a link to it, and every repository the page links against the grid, so the
dropped `jetbrains_client` row cannot come back as a link to a repository that is not there. It then reads the page's image reference, holds it to
the one tag `scripts/check-claims.py` carries, and asks `ghcr.io` for that tag; reads the page's
demo reference, holds it to the one host the check allows, and asks that instance what it reports,
whether the editor address's `/session` path is answered by the server rather than by the proxy in
front of it, and whether its `/` serves the page with a host card in its shell; and holds the
page's sentence about which wire version each of the two speaks to the artefact behind it — the
demo's half to what `/meta` offers and the image's half to the tag's declared wire — so the sealing
claim cannot be read without the command under it being read too.

The policy step reads the same rendered file, its not-found route, and the policy out of
`vercel.json`, and fails when the policy would refuse a script, stylesheet, image or font either
page carries, the defect described under "The Content-Security-Policy". Its fixtures run first: a
policy without `script-src`, a policy without `font-src` and a policy that drops `default-src
'none'` all have to fail it, so the check cannot have gone blind.

The weight step reads the same rendered file again and the bytes of every image it fetches out of
`public/`, and holds each to a budget: a surface this page paints at 30 px may not be handed the
owner's 800×800 master. It also asserts the `width`/`height` an `<img>` declares are the file's own
pixels, because a `src` swap that leaves them behind distorts the mark and no failed request says
so. It is a ceiling per image rather than a total for the page, so a framework upgrade that
changes nothing a reader sees cannot redden it.

`.github/workflows/ci.yml` runs the same commands on `ubuntu-24.04` on every pull request (and
on demand, through `workflow_dispatch`): Node from `.nvmrc`, `npm ci`, then `typecheck`, `build`, `button`,
`contrast`, `mark`, `claims`, `csp`, `weight`, `links` and `lint`. It installs lychee and actionlint from pinned releases: the runner has no
nix, so `scripts/ci-local.sh` takes both from `PATH` when they are there and from nixpkgs
otherwise, and all three places run the same checkers.

## Accessibility: the WCAG AA floor

The page holds itself to WCAG 2.2 AA. Ratios are computed from the colours the page paints — the
theme tokens in
`style.css`, the colour a rule declares where a pair is not a token, and, for the one mark that is
artwork rather than a token, the pixels of
`public/mark-header.png` — never eyeballed; `scripts/check-contrast.py` asserts them in the gate,
so a regression fails the build instead of waiting for a look. Measured today:

| Pair | Ratio | Needs |
|---|---|---|
| body text on page | 11.34:1 | 4.5:1 |
| muted prose on page | 7.37:1 | 4.5:1 |
| link on page | 8.07:1 | 4.5:1 |
| button label on its mauve fill | 8.07:1 | 4.5:1 |
| peer badge label on its mauve fill (the first peer's name in the window; the label is read from the badge's own rule rather than taken to be the page's colour) | 9.23:1 | 4.5:1 |
| peer badge label on its teal fill (the second peer's name in the window) | 12.59:1 | 4.5:1 |
| peer badge label on its peach fill (the third peer's name in the sample) | 10.59:1 | 4.5:1 |
| code comment on the sample's ground (the editor theme's `comment`) | 6.64:1 | 4.5:1 |
| code keyword on the sample's ground (`keyword`, the mauve the page already uses) | 9.23:1 | 4.5:1 |
| code string on the sample's ground (`string`) | 12.61:1 | 4.5:1 |
| code number on the sample's ground (`number`) | 10.59:1 | 4.5:1 |
| code type on the sample's ground (`type`) | 14.76:1 | 4.5:1 |
| code function on the sample's ground (`fn`, the browser client's own function colour) | 8.91:1 | 4.5:1 |
| the room window's line numbers, over the ground the hero figure actually paints, the glow included (the window's fill and the radial wash's centre, the lighter of the two; the colour the window's own rule paints, read from the stylesheet rather than taken from a token the window does not use there) | 4.58:1 | 4.5:1 |
| the not-yet-available card's number and its planned row, on the band the card is transparent over (the band's own fill, read from its rule) | 4.75:1 | 4.5:1 |
| the repository description on the repository card, on the card's hover fill, and in the planned card on the page | 6.22:1 / 5.81:1 / 5.81:1 | 4.5:1 |
| the peers' caret bars and badge fills on the sample's ground (the figure's fill over the card's over the page) | 9.23:1 / 12.59:1 / 10.59:1 | 3.0:1 |
| the peers' caret bars and badge fills on the room window, over the ground the hero figure is drawn on | 8.55:1 / 11.67:1 / 9.82:1 | 3.0:1 |
| code type under a peer's selection fill, on the sample's ground | 7.92:1 | 4.5:1 |
| code type under a peer's selection fill, on the window | 7.20:1 | 4.5:1 |
| the selection tint itself, at the client's quarter alpha (mauve / teal, on the window: 1.70:1 / 1.90:1) | 1.67:1 / 1.86:1 | 1.5:1 |
| code text on code background | 12.14:1 | 4.5:1 |
| muted text on code background | 7.89:1 | 4.5:1 |
| badge text on its fill (the primitive's default chip, computed as the palette's mauve over its own 10% wash; the page's own badges are the pills the cards carry, measured in the groups below) | 6.63:1 | 4.5:1 |
| secondary-button text on its fill, the primitive's own (the page renders the `outline` variant, so this pair is the component's; hover state, the worst of rest `15` at 5.98:1) | 5.32:1 | 4.5:1 |
| ghost-button text on its hover fill (`bg-surface0/60`; the variant is parsed from the component, and the page carries no ghost button) | 9.75:1 | 4.5:1 |
| secondary button boundary, the primitive's own (`border-mauve/60`, parsed from the component) | 3.82:1 | 3.0:1 |
| outline button boundary on the page (`border-surface1`, parsed from the component; below the 3.0:1 a boundary that *identifies* a control would need and above the floor a reader loses it at — the button's own label and focus ring identify it) | 1.80:1 | 1.5:1 |
| focus outline against the page | 8.07:1 | 3.0:1 |
| window text on the window, over the ground the hero figure is drawn on | 12.02:1 (muted 7.81:1) | 4.5:1 |
| hero figure text on the figure's own ground (the figure sits on the page, so its ground is `--bg`) | 11.34:1 (muted 7.37:1) | 4.5:1 |
| the nav mark's median ink pixel on the header's ground (the owner's artwork, a logotype and so exempt from WCAG 1.4.11's non-text floor; its own pixels read out of `public/mark-header.png` and composited over `--bg`) | 1.72:1 | 1.5:1 |

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
the gate: the stylesheet as it stood before the underline went in measures 1.40:1 against the
prose beside it and fails the check.

A link wears one colour, `--link`, in every state, a followed link included: the underline is the
affordance, so nothing about a link's state is carried by colour, and two links that differ only
in whether they have been visited do not read as two different things.

Four groups the check does not parse are computed the same way, from the colours the browser
composites, and are re-measured whenever the fills around them move: inline code text on its chip
fill (`--color-surface0`) 8.69:1; the small text on the page's own ground — the try cards' numbers,
their footnote, the invite strip's label and the host the copy control hands over — 7.37:1; the card
body text on the card fill (`#181825`) 7.89:1; and the client chips 12.97:1 on the figure band they
are drawn on. The status pills the cards carry are the same shape — their own colour over their own
wash, on the card each one sits in — and the lowest of them is 6.38:1 (the specification's mauve on a
hovered repository card). The two overlay tones are used only where they clear the floor of the ground they are
painted on: `--color-overlay1` carries the copy control's own label on the card fill (4.75:1) and
the planned-clients chip on the figure band (5.07:1), and `--color-overlay2` carries the terminal's
comments on the terminal's fill (6.64:1). The washes the page paints its own marks over are measured
the same way: the panels' chips sit at 9.50:1 (green) and 8.10:1 (peach) on their own washes, the
highlighted row of the comparison card at 10.70:1, and the open file's row in the window at
10.42:1. The section hairlines sit at 1.30:1 against the page on purpose: they are decorative
separators, they
carry no state, and nothing is identified by them. The panel and card borders the design draws in
`--color-surface1` are 1.80:1, which is below the 3.0:1 a boundary that *identifies* something
would need, and the page does not use one to identify anything; the one such boundary on a control
is the outline hero button, which the check measures and holds to that same visibility floor rather
than to a floor the design's own tone cannot clear.

The selection tint is the one colour on the page that cannot clear the floor it would be given
as a mark, and the check says so rather than pretending. It wears the alpha the client itself
builds for a selection (`translucent(colour, 0.25)`, `web_client/src/bridge/cursors.ts`), which
measures 1.67:1 mauve and 1.86:1 teal against the sample's ground and 1.70:1 / 1.90:1 against the
window's; the alpha that would reach the
non-text 3.0:1 is about a half, and at that alpha the sample's own text on it falls below
4.5:1. The two floors cannot both hold for a translucent fill, so the fill is asserted where it
matters — the token it sits under, read out of `components/room-visuals.tsx` so that moving it
over the dimmer comment colour fails the build — and its own pair is a floor of 1.5:1, which only
fails a tint nobody can see. The opaque caret bar is what carries a peer at 3.0:1.

What no ratio proves is read against the code by a person on every change:

- **Visible focus.** Every link and button carries a 2 px mauve `:focus-visible`
  outline at a 2 px offset; the `Button` primitive repeats it as a utility, so both spellings
  agree. Verified in the browser: the first three tabs land on the nav's own anchors with that
  ring.
- **Keyboard.** Every control is a native anchor or button; the page carries no form, no scripted
  widget and no fold. The sticky header
  slides away
  on scroll-down but carries `focus-within:translate-y-0`, so a tabbed-to link is never
  focused off-screen. That slide is the `SiteHeader` client boundary running, so it is only as
  true as the page's scripts being permitted. "The Content-Security-Policy" records the
  interval in which they were not, and the gate step that now fails if it happens again.
  No skip link: the page is one route, so there is no repeated block
  to bypass.
- **Reduced motion.** Four things move and all four stand down under `prefers-reduced-motion`: the
  line the hero's window types (under `reduce` it is written whole and never restarts), the caret's
  blink (an `animation: none` in the `reduce` block), the 2 px hover lift on the figure cards, and
  the header's slide (a `motion-reduce:transition-none` utility, so `transition-property` is `none`
  and the bar still hides and returns, without the slide). `scroll-behavior: smooth` goes to `auto`
  in the same block, and the buttons' own lift is a `motion-safe:` utility. Verified in the browser:
  under emulated `reduce` the typed line is 27 characters on the first frame and still 27 a second
  later, the caret's `animation-name` is `none`, the header's `transition-property` is `none`, and
  `scroll-behavior` is `auto`.
- **Touch targets.** Nav links are `text-sm` (20 px line box) with `py-1`, for 28 px of
  target height against the 24 px minimum; buttons are 32–44 px tall. In-prose links are inline and
  exempt.
- **Decorative only.** The hero figure and the cards' drawings are `aria-hidden`: the window and
  its glow, the guest's tree, one open file, the carets and the invite chip. Their
  worst-case ratios still clear AA (above), and each drawing is followed by the sentence that
  describes the room rather than four lines of code.
- **The figure grid is a list.** Each card's drawing is followed by a bold lead and a sentence, so
  the four claims are readable as a list before they are readable as a picture.
- **Client links.** The routes, the repositories and the specification are links drawn as controls
  — a tab, a card with a border and a fill, a `Source` label with an arrow — and the stylesheet
  takes the prose underline off that group (`.repo`, `.demo-link`, `.spec-link`, `.source-link`,
  `.try-link`, `.cta`), because their affordance is the control's own shape. Every link in running
  prose keeps it, so a link there is not told apart by its colour and monospace face alone; the
  focus outline is unchanged.

## Licence

`MIT OR Apache-2.0`, the pair the clients carry; see `LICENSE-MIT` and `LICENSE-APACHE`. The
page's framing follows the project's own design record, which is private and carries no licence;
the workflow sentence is adapted from the Neovim client's README, which is `MIT OR Apache-2.0`.
Where the wording came from is recorded here and not in the footer: the page states the licence a
visitor is bound by, and provenance is a note for whoever maintains the page.
