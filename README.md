# The public landing page

The page is live at **https://selvage-protocol.vercel.app**, which is its home;
`selvageprotocol.com` is not registered and registering it is not being pursued (see "The live
origin").

The landing page for **Selvage** (the project) and the **Selvage Session Protocol** (the protocol
it publishes). A Next.js App Router project with one route (`/`): the page component carries the
prose, the product figures live in one component of their own, the global stylesheet carries the
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
editor clients. This repository holds the page, the four checks that gate it, the one
browser proof the runner cannot run, and nothing else.

| Path | What it is |
|---|---|
| `app/page.tsx` | the page: the prose, the section order, and nothing else. Hero (promise, three landed facts, two CTAs, the room figure), *See it working* (four cards), *How it works* (four steps), *The session layer has no specification* (why the specification is the artifact), *Run it* (two commands in the open, the three long routes folded into one `details`), *What is built, and what is not* (the honest ledger), then the footer |
| `app/layout.tsx` | the root layout: `lang`, title, description and Open Graph metadata, the one origin the metadata resolves against (`metadataBase`, `alternates.canonical`, `openGraph.url`; see "The live origin"), and the global stylesheet. The favicons are deliberately absent: they are Next file conventions, so the framework writes their tags and `sizes` from the files themselves |
| `style.css` | the one stylesheet, dark-only Catppuccin Mocha with a mauve accent: the Tailwind v4 entry (`@import "tailwindcss"` plus a `@theme` block pinning the palette) followed by the page's own rules under CSS variables, and a system font stack, so no font is fetched from a third party. Two widths are named there and the page keeps to them: `--measure` for running prose and `--column` for everything that is not prose (section rules, code blocks, the repo grid), so a wide figure is deliberate inside a narrow measure |
| `app/icon.png` / `app/icon1.png` / `app/icon2.png` / `app/apple-icon.png` | the favicon set: the owner's opaque export resized to the four sizes a browser asks for (32, 16 and 48 px, and the 180 px home-screen icon), named for Next's file convention so the framework writes their `<link>` tags and `sizes`. Nothing here is redrawn; there is no vector favicon (see "The site mark") |
| `app/opengraph-image.png` | the social card image (Next file convention, served as `/opengraph-image.png`): the owner's opaque export at full size, so cards crop owner's pixels |
| `public/mark-transparent.png` | the mark as served in the page body: the owner's transparent 800×800 export, vendored byte-identical (see "The site mark"). The opaque export was vendored beside it while the hero panel was light; it is no longer served; `app/opengraph-image.png` is the same file |
| `postcss.config.mjs` | the one PostCSS plugin (`@tailwindcss/postcss`), so `style.css` compiles on build |
| `next.config.ts` | the one build setting that is not a default: `poweredByHeader: false`, so the framework's `X-Powered-By: Next.js` banner is not on the page's HTML response |
| `components/ui/button.tsx` | the button primitive (shadcn-style `cva` variants: filled default, tinted secondary, ghost; renders an anchor when given `href`): the nav CTA and the two hero CTAs, nothing else |
| `components/ui/badge.tsx` | the pill primitive: the hero status line, a mono caps chip |
| `components/room-visuals.tsx` | the product figures: the hero's room window (the guest's mirrored tree, one open file, the two carets in it, the invite chip) and the three smaller drawings the cards carry. Inline markup and the page's own CSS, with no image, no dependency and nothing fetched (see "The product figures") |
| `components/ui/card.tsx` | the card primitive: the hero panel's glass card |
| `lib/utils.ts` | the one shared helper (`cn`: `clsx` + `tailwind-merge`) |
| `package.json` / `package-lock.json` | the only dependencies: `next`, `react`, `react-dom`, `tailwindcss` (+ its PostCSS plugin), `clsx`, `tailwind-merge`, `class-variance-authority` and `lucide-react` for icons, `typescript` and `@types/*`. No Radix, no component library, nothing else without a written reason |
| `.nvmrc` | the pinned Node version for local work and CI (`nvm use` reads it); `package.json` `engines` carries the major (`24.x`), because Vercel only deploys major versions |
| `scripts/check-claims.py` | the claim check: the phrases the page must not carry, each with its reason |
| `scripts/check-button-props.tsx` | the button check: renders the button and anchor variants and asserts their props reach the DOM (run by `npm run check:button` inside the gate) |
| `scripts/check-contrast.py` | the contrast check: parses the theme tokens out of `style.css` — including the sample's `selvage-mocha` token colours, the ground the code figure draws them on, and the alpha a peer's selection fill is drawn at — reads the token a selection fill sits under out of `components/room-visuals.tsx`, and asserts the rendered pairs sit at or above WCAG AA, with measured ratios (run by `scripts/ci-local.sh contrast` inside the gate) |
| `scripts/check-csp.py` | the policy check: reads the Content-Security-Policy out of `vercel.json` and the served HTML, and fails when the policy would refuse a script, stylesheet or image the page carries (run by `scripts/ci-local.sh csp` inside the gate; see "The Content-Security-Policy") |
| `scripts/check-csp-browser.mjs` | the browser proof: serves the built page with the headers out of `vercel.json`, drives headless Chromium over CDP, and asserts zero `securitypolicyviolation` events, `window.__next_f` an object, the header's concealment on scroll and no `X-Powered-By`. Not in the gate (the runner has no browser), and it needs `npm run build` first |
| `scripts/ci-local.sh` | the gate, running the same commands as the workflow |
| `lychee.toml` | what the link check does not check, and why |
| `vercel.json` | platform configuration: the Next.js framework preset, and three response headers: the Content-Security-Policy the page's own scripts are permitted by, the file it was once refused by (see "The Content-Security-Policy"), plus `X-Content-Type-Options: nosniff` and `Referrer-Policy: strict-origin-when-cross-origin` |
| `.github/workflows/ci.yml` | the gate, on `push` to `main` and on `pull_request` |

## The site mark

The page serves the owner's raster mark at every size: the body from the owner's transparent
800×800 PNG export, vendored byte-identical under `public/` (its checksum matches the owner's
file) and never hotlinked; the icons and the social card from the same export's opaque twin.
The one surface that carries the page-body mark is dark, and the opaque export's
baked `#1e1e2e` base would draw a visible chip inside it, so the transparent
glyphs are the ones that sit on the surface:

| Surface | File | Why |
|---|---|---|
| Nav header on dark Mocha | `public/mark-transparent.png` | the bar is translucent Mocha over the page; the opaque export's baked `#1e1e2e` base would draw a visible box against it, while the transparent glyphs sit straight on the bar |
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

## The page, and its copy

The page is a product page, not a numbered document: seven parts in order, each one doing a job
the reader can name.

| Part | Its job |
|---|---|
| Hero | the promise, three landed facts, two CTAs, and the room figure. The `h1`, *Edit the same file together, on a server you run.*, says what the product does and carries the self-hosted wedge from the design record's hook |
| See it working | four cards, each with a drawing of the thing it claims: anyone with the link is in, two carets in one text, the paths a guest sees, multiple clients on one engine |
| How it works | the four moves in order (host a folder, send the invite, type in the same file, close the window), under the design record's one-sentence workflow |
| The session layer has no specification | the wedge: language tooling has the Language Server Protocol and debugging the Debug Adapter Protocol, document sync has `y-protocols`, and the session layer is unspecified, so every collaborative tool decides those for itself. The specification is the flagship artifact, and the corpus counts appear here once, as the evidence they are |
| Run it | two commands in the open (`git clone`, `cargo run`), the client routes named in a sentence, and the three long routes folded into one `details` |
| What is built, and what is not | the honest ledger, two columns: four things that exist, six that do not |
| Footer | the licences, the four repository cards, and the page's own privacy line |

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

The must-not-say table below still binds every line. Two rows moved with what is now true:

- **The browser client.** `web_client`, Monaco in a page, guests only, is
  built and served over the project's own private network, so "nothing runs in a web page" is no
  longer true and the filter no longer forbids the bare word. What the filter forbids instead is
  both of the lies that replaced it: that a reader can open a page (there is no public URL on that
  network), and the stale denial itself. The page says the browser page is guests-only and served
  over a private network, and that there is no public demo to open. The
  pattern also holds the route shape neither a verb nor a denial covers (a browser mention sharing
  a sentence with a URL or a host name, in either order), because that is what "a page a reader can
  open" looks like in prose. The `clean` fixtures on that pattern are the honest sentences, and the
  last of them puts the browser mention and the server's own loopback address in different
  sentences, so a widening past the sentence bound fails the gate.
- **The corpus counts.** Still exactly the numbers `specification/schema/validate.py` pins (31
  vectors, 34858 frame checks, 8642 assertions), and they now appear in one place, as the evidence
  for the specification, instead of three. The vector count is pinned with up to two words between
  the number and the word, so the page's "conformance vectors" and "wire vectors" are both gated.

## The product figures

The page shows the product instead of describing it, without an image, a font, a dependency or a
third-party request: `components/room-visuals.tsx` draws the room window from inline markup styled
by `style.css`. The hero figure is the whole surface at once: the guest's mirrored tree, one open
file, the two carets in it (a 2 px bar in the peer's colour at a column between two characters of
the line, the peer's name in the gutter lane on that line, and a quarter-alpha fill behind what one
of them has selected), and the invite chip that put them there. Each card in *See it
working* carries one smaller drawing of the thing it claims.

Four rules hold it together:

- **It is an illustration, and it says so.** The caption under the hero figure names it. Each code
  sample is a short function against the client crate's own API, with the `use` line left out, and
  each peer's caret is drawn where the browser client draws it (`renderCursors` in
  `web_client/src/browser/editor.ts`): a 2 px bar at the caret's own range, a badge in the left
  gutter on the line the caret is on, and a fill behind the characters the peer holds. A name is
  never written into the text of a line: inside Rust it would read as syntax, which is a claim
  about the source that is not true — so it stays in the lane beside the line number, where that
  client's glyph-margin badge goes.
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
default-src 'none'; script-src 'self' 'unsafe-inline'; img-src 'self' data:; style-src 'self'; base-uri 'none'; frame-ancestors 'none'
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
and a stale hash fails the same silent way the missing directive did. The cost of the compromise
is stated rather than hidden: `'unsafe-inline'` permits an inline `on*` attribute too, the page
carries none, and one appearing is counted into the checker's summary line.

What the policy still refuses: every origin that is not this one, `eval`, a `<base>` that would
retarget the page's relative URLs, framing, and every resource kind the page does not name.
`data:` is allowed for `img-src` alone.

Two pieces of evidence, with their limits:

- `scripts/check-csp.py` runs in the gate over the HTML the production server renders. It takes
  the policy *from* `vercel.json`, not a copy of it, and decides every script, stylesheet and image
  against the directive that governs it, following the fallback chains a browser follows. The
  policy as it read without `script-src` is one of its own fixtures, so it fails on the defect
  it was written for. It is a model of the policy, not a browser, and a source expression it
  does not model is an error rather than an assumption.
- A real Chromium run against the built page served with these exact headers, kept runnable as
  `scripts/check-csp-browser.mjs`: it applies the `headers` block out of `vercel.json` through a
  local proxy (`next start` does not apply it, only the host does) and asserts zero
  `securitypolicyviolation` events, `window.__next_f` an object, the header concealed
  (`translate: 0px -100%`) at `scrollY` 900 and back at 300, and no `X-Powered-By`. Point
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
- **No `form-action` in the Content-Security-Policy.** The CSP in `vercel.json` would have had to
  name the endpoint to keep a form working, which would have been a second place to edit
  and a way to ship a form the policy blocks. The page renders no user input into itself,
  so the directive would defend against an injection that has no path in.

## What the page must never say

The page's job is to be checkable, so the rule is mechanical where it can be:
`scripts/check-claims.py` fails the build on each of the known wordings below, carries the reason
beside each, and normalises the served HTML before matching: comments, tags, scripts and styles
removed, entities decoded, whitespace collapsed. So a phrase cannot pass by wrapping across a
line or by encoding a character. The scan runs against what the server renders, not the source:
the gate builds, starts the production server, fetches `/` over HTTP and checks that HTML.
**It is a filter, not a proof.** It cannot see meaning: a false claim in different words, a
synonym outside the list, a superlative, an unbacked sentence or a wrong number the list does not
pin all pass it. A green gate means the known wordings are absent, nothing more. The reasons are
summarised here so that the constraint survives without the file that produced it.

| Must not appear | Why not |
|---|---|
| "open source" of the server or the project | The server binary is `FSL-1.1-MIT`: source-available, not OSI-approved, free for non-competing use and under MIT two years after each release. The specification and the clients are the open ones, and the page names their licences instead of reaching for the phrase |
| "SSP" | The abbreviation is taken by stack-smashing protection and by supply-side platforms. The protocol is the Selvage Session Protocol, written out |
| `salvage/1` | The wire version is `selvage/1`. "Selvage" is heard as "salvage", which is why the full protocol title appears at least once in the page's first paragraph |
| end-to-end encryption, E2EE | Version 1 has no encryption layer: frames travel through the server as unencrypted bytes, and the slice has no transport security either. The relay is payload-opaque but not confidential |
| "the server cannot read it" / "the text never reaches the server" | The relay routes opaque bytes and keeps no document text, but it can read a frame as it passes and there is no transport security. It is not a confidential relay |
| a browser route a reader can open | The browser client exists (`web_client`, Monaco in a page, guests only), but it is served over the project's own private network, so there is no public URL to open one at, and no install-free route to a page. The page says what the browser client is and where it is served, and that the two desktop clients are the published ones. It may not say "nothing runs in a web page" either: that sentence was true when the filter forbade the bare word and it is false now |
| file create, rename or delete | The room carries no file mutations and nothing writes to the host's working copy. The host's own editor still changes that folder, and a Neovim guest's mirror materialises the granted paths |
| Docker, or a one-command self-host | No image, compose file or service unit exists in any repository. The documented path is `cargo run -p selvaged -- --listen …` |
| a stable 1.0 | The wire version is `selvage/1`; the compatibility rule in force is the same major. Nothing has been released and no shape is frozen. No corpus line puts the design at 0.x |
| a second implementation, or interoperability | There is none. The Neovim client drives a byte-identical copy of the same engine, so nothing yet shows a client built from the prose alone agreeing byte for byte with the Rust one |
| marketplace or extension-gallery availability | The extension is unpublished, and publishing it is a non-goal until it works with a friend |
| "guests are read-only" or "view-only" | The design inverts it: read-only scopes the host's filesystem, never the shared buffer, and every holder of the invite edits the session CRDT. Saying otherwise would be a lie about the product's central idea |
| "your code never leaves your machine" | Document payloads travel through the server to the peers that ask for them, and there is no encryption layer. What is bounded is the grant: the paths the host enumerates, and the reads it serves from inside the granted root |
| invented proof: screenshots, testimonials, user counts, a production deployment, a demo link | None of them exist. There is no recording, no user count, and no production deployment of the server or the browser client (the live origin is a deploy of this page, not of the protocol), and the only server that has ever run was a local debug build. The one image the page carries is the project's own site mark (see above), not proof of anything |
| a claim of priority ("the first protocol to specify …") | The design record surveys prior art (Eclipse Open Collaboration Tools and others). The project's claim is that the session layer is unspecified, not that this is first |
| a corpus number other than the pinned one | The counts (31 vectors, 34858 frame checks, 8642 assertions) are constants in `specification/schema/validate.py`; any other number is a claim the corpus disproves |
| a third party seeing the room | The relay is payload-opaque but plaintext with no transport security in this slice, so the operator and the network path can see the room's text. Only the page's own weak reading (no third party's cloud holding the room) is backed |
| a bare "no cloud", qualified or not ("no cloud in between" included) | A self-hosted server can itself run on a cloud VM, so only the weak reading is backed: no third party's cloud holding the room. The backed storage sentence is "nothing written to disk" |
| a proven cross-editor pairing | The first cross-editor session has run. The design notes' hand-run proof (2026-09-17) passes grant, cursors and follow in both directions, but its concurrent-edit step falls short by one trailing-newline byte, so byte-identical replicas across the two editors are not demonstrated. State what the clients are built to do rather than that it is proven |
| a speed adjective (instant, real-time, lag-free) | No performance data exists anywhere in the corpus |
| an ease claim (takes seconds, one-click, just works) | No image, compose file or service unit exists; the documented path is `cargo run`, and no ease claim is backed |
| an only-machine claim (untouched by the network) | Document payloads travel through the server to the peers that ask for them; the grant bounds which paths are served, not which machines code touches |
| a "live" / "now available" status | Nothing is released, hosted or published. The honest status line is the wire version plus the specification draft |
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
$ scripts/ci-local.sh              # typecheck, build, button, contrast, claims, csp, links, lint
$ scripts/ci-local.sh typecheck    # tsc --noEmit
$ scripts/ci-local.sh build        # next build
$ scripts/ci-local.sh button       # render the button/anchor variants and assert their props reach the DOM
$ scripts/ci-local.sh contrast     # theme token pairs at or above WCAG AA, with measured ratios
$ scripts/ci-local.sh claims       # rebuild, serve production, fetch / and scan the rendered HTML
$ scripts/ci-local.sh csp          # the policy in vercel.json over the served page: nothing it carries is refused
$ scripts/ci-local.sh links        # serve production, lychee over the rendered page and README.md
$ scripts/ci-local.sh lint         # actionlint over the workflows (nix; the workflow pins a release)
```

The claims step fetches `/` from the production server into `.tmp/rendered.html` (`PORT`
overrides the default `3100`) and scans that file by name; reaching no file is an error rather
than a pass, and every pattern must match its own sample before the scan, so a dead pattern fails
the gate instead of passing everything; named honest wordings must stay unmatched, so a broadening
that reintroduces a false positive fails it too.

The policy step reads the same rendered file, and the policy out of `vercel.json`, and fails when
the policy would refuse a script, stylesheet or image the page carries, the defect described
under "The Content-Security-Policy". Its fixtures run first: a policy without `script-src` and a
policy that drops `default-src 'none'` both have to fail it, so the check cannot have gone blind.

`.github/workflows/ci.yml` runs the same commands on `ubuntu-24.04` on every pull request (and
on demand, through `workflow_dispatch`): Node from `.nvmrc`, `npm ci`, then `typecheck`, `build`, `button`,
`contrast`, `claims`, `csp`, `links` and `lint`. It installs lychee and actionlint from pinned releases: the runner has no
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
| visited link on page | 5.81:1 | 4.5:1 |
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

Four groups the check does not parse are computed the same way, from the colours the browser
composites, and are re-measured whenever the fills around them move: inline code text on its
chip fill (`rgba(205, 214, 244, 0.07)` over `--bg`) 9.62:1; the invite chip's label and its URL
on the chip's own tint (`rgba(203, 166, 247, 0.08)` over the figure's fill over the card's) 6.77:1
and 10.41:1; the card body text on the card fill (`rgba(24, 24, 37, 0.5)` over `--bg`) 7.63:1;
the client chips and the rail label under them 10.56:1 and 8.55:1. The repo cards' muted text and
links on their fill are 7.63:1 and 8.36:1, the visited link on the same fill 6.02:1. The section
hairlines, the card borders and the status dots sit at 1.30:1 against the page on
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
  to bypass. The run-it fold is a native `details`, so it opens without a script.
- **Reduced motion.** Two things move, and both stand down under `prefers-reduced-motion`: the
  hero figure's 520 ms entrance (an `opacity`/`translateY` animation) and the 2 px hover lift on
  the figure cards and the repository cards, each inside a `prefers-reduced-motion:
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
- **Repo links.** The repository cards drop the default underline, so a link is told apart
  from the muted text beside it by its monospace face and size rather than by colour alone
  (mauve against that text is 1.10:1); the focus outline is unchanged.

## Licence

`MIT OR Apache-2.0`, the pair the clients carry; see `LICENSE-MIT` and `LICENSE-APACHE`. The
page's framing follows the project's own design record, which is private and carries no licence;
the workflow sentence is adapted from the Neovim client's README, which is `MIT OR Apache-2.0`.
The page footer says the same thing.
